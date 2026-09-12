#!/usr/bin/env python3
"""Persistenter Jobmanager und Aktionsjournal für PROVOWARE HEADQUARTER."""
from __future__ import annotations

from datetime import datetime, timedelta
import json
from pathlib import Path
import sqlite3
import uuid

from data_core import DataCore, DataIntegrityError, DataNotFoundError, DataValidationError

VALID_JOB_STATUSES = {
    "queued", "running", "paused", "cancelling", "cancelled",
    "completed", "failed", "interrupted",
}
TERMINAL_JOB_STATUSES = {"cancelled", "completed", "failed"}
VALID_ACTION_TYPES = {"copy", "move", "rename", "mkdir"}
VALID_ACTION_STATUSES = {"planned", "applied", "skipped", "failed", "undone"}
MAX_JSON_BYTES = 250_000
MAX_PATH_CHARS = 4096


class JobManager:
    """Zustandsmaschine auf derselben SQLite-Datenbank wie der zentrale Datenkern."""

    def __init__(self, data_core: DataCore, *, recover_incomplete: bool = True) -> None:
        self.data = data_core
        self.data.ensure_ready()
        if recover_incomplete:
            self.recover_incomplete_jobs("startup")

    @staticmethod
    def _now() -> str:
        return datetime.now().astimezone().isoformat(timespec="seconds")

    @staticmethod
    def _normalize_kind(kind: str) -> str:
        value = "-".join(str(kind or "").strip().lower().split())
        if not value or len(value) > 80:
            raise DataValidationError("Job-Typ fehlt oder ist zu lang.")
        if any(ch not in "abcdefghijklmnopqrstuvwxyz0123456789-_." for ch in value):
            raise DataValidationError("Job-Typ enthält nicht erlaubte Zeichen.")
        return value

    @staticmethod
    def _json_text(value: object, label: str) -> str:
        if value is None:
            value = {}
        if not isinstance(value, (dict, list)):
            raise DataValidationError(f"{label} muss ein JSON-Objekt oder eine JSON-Liste sein.")
        try:
            raw = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        except (TypeError, ValueError) as exc:
            raise DataValidationError(f"{label} ist nicht JSON-kompatibel.") from exc
        if len(raw.encode("utf-8")) > MAX_JSON_BYTES:
            raise DataValidationError(f"{label} ist zu groß.")
        return raw

    @staticmethod
    def _json_value(raw: str) -> object:
        try:
            return json.loads(raw or "{}")
        except json.JSONDecodeError as exc:
            raise DataIntegrityError("Persistierte Job-JSON-Daten sind beschädigt.") from exc

    @staticmethod
    def _normalize_path(value: str, *, required: bool, label: str) -> str:
        raw = str(value or "").strip()
        if "\x00" in raw:
            raise DataValidationError(f"{label} enthält ein ungültiges Nullzeichen.")
        if required and not raw:
            raise DataValidationError(f"{label} fehlt.")
        if len(raw) > MAX_PATH_CHARS:
            raise DataValidationError(f"{label} ist zu lang.")
        return raw

    @staticmethod
    def _validate_progress(done: int, total: int, bytes_done: int, bytes_total: int) -> tuple[int, int, int, int]:
        values = []
        for label, raw in (
            ("Fortschritt", done), ("Gesamt", total),
            ("Bytes bearbeitet", bytes_done), ("Bytes gesamt", bytes_total),
        ):
            try:
                value = int(raw)
            except (TypeError, ValueError) as exc:
                raise DataValidationError(f"{label} muss eine ganze Zahl sein.") from exc
            if value < 0:
                raise DataValidationError(f"{label} darf nicht negativ sein.")
            values.append(value)
        done_i, total_i, bytes_done_i, bytes_total_i = values
        if total_i and done_i > total_i:
            raise DataValidationError("Bearbeitete Einheiten dürfen Gesamt nicht überschreiten.")
        if bytes_total_i and bytes_done_i > bytes_total_i:
            raise DataValidationError("Bearbeitete Bytes dürfen Gesamtbytes nicht überschreiten.")
        return done_i, total_i, bytes_done_i, bytes_total_i

    def _job_event(self, conn: sqlite3.Connection, job_id: str, event_type: str, payload: object | None = None) -> None:
        conn.execute(
            "INSERT INTO job_events(job_id,event_type,payload_json,created_at) VALUES(?,?,?,?)",
            (job_id, event_type, self._json_text(payload or {}, "Ereignisdaten"), self._now()),
        )

    def _job_exists(self, conn: sqlite3.Connection, job_id: str) -> sqlite3.Row:
        row = conn.execute("SELECT * FROM jobs WHERE id=?", (str(job_id),)).fetchone()
        if row is None:
            raise DataNotFoundError("Job wurde nicht gefunden.")
        return row

    def _action_exists(self, conn: sqlite3.Connection, action_id: int) -> sqlite3.Row:
        row = conn.execute("SELECT * FROM file_actions WHERE id=?", (int(action_id),)).fetchone()
        if row is None:
            raise DataNotFoundError("Dateiaktion wurde nicht gefunden.")
        return row

    def _job_dict(self, row: sqlite3.Row) -> dict:
        item = dict(row)
        item["payload"] = self._json_value(item.pop("payload_json"))
        item["checkpoint"] = self._json_value(item.pop("checkpoint_json"))
        item["result"] = self._json_value(item.pop("result_json"))
        return item

    def _action_dict(self, row: sqlite3.Row) -> dict:
        item = dict(row)
        item["reversible"] = bool(item["reversible"])
        item["before"] = self._json_value(item.pop("before_json"))
        item["after"] = self._json_value(item.pop("after_json"))
        return item

    def create_job(self, kind: str, payload: object | None = None) -> dict:
        clean_kind = self._normalize_kind(kind)
        payload_json = self._json_text(payload or {}, "Job-Nutzlast")
        job_id = uuid.uuid4().hex
        now = self._now()
        with self.data.transaction() as conn:
            conn.execute(
                """INSERT INTO jobs(
                    id,kind,status,phase,payload_json,checkpoint_json,result_json,
                    created_at,updated_at
                ) VALUES(?,?,'queued','queued',?,'{}','{}',?,?)""",
                (job_id, clean_kind, payload_json, now, now),
            )
            self._job_event(conn, job_id, "created", {"kind": clean_kind})
        return self.get_job(job_id)

    def get_job(self, job_id: str) -> dict:
        with self.data.read_connection() as conn:
            row = self._job_exists(conn, job_id)
        return self._job_dict(row)

    def list_jobs(self, status: str | None = None, *, limit: int = 100) -> list[dict]:
        if status is not None and status not in VALID_JOB_STATUSES:
            raise DataValidationError("Job-Statusfilter ist ungültig.")
        try:
            limit_i = int(limit)
        except (TypeError, ValueError) as exc:
            raise DataValidationError("Job-Limit ist ungültig.") from exc
        limit_i = max(1, min(limit_i, 500))
        with self.data.read_connection() as conn:
            if status:
                rows = conn.execute(
                    "SELECT * FROM jobs WHERE status=? ORDER BY created_at DESC LIMIT ?",
                    (status, limit_i),
                ).fetchall()
            else:
                rows = conn.execute(
                    "SELECT * FROM jobs ORDER BY created_at DESC LIMIT ?", (limit_i,)
                ).fetchall()
        return [self._job_dict(row) for row in rows]

    def list_events(self, job_id: str, *, limit: int = 500) -> list[dict]:
        self.get_job(job_id)
        limit_i = max(1, min(int(limit), 2000))
        with self.data.read_connection() as conn:
            rows = conn.execute(
                "SELECT * FROM job_events WHERE job_id=? ORDER BY id LIMIT ?",
                (job_id, limit_i),
            ).fetchall()
        result = []
        for row in rows:
            item = dict(row)
            item["payload"] = self._json_value(item.pop("payload_json"))
            result.append(item)
        return result

    def start_job(self, job_id: str) -> dict:
        now = self._now()
        with self.data.transaction() as conn:
            row = self._job_exists(conn, job_id)
            if row["status"] != "queued":
                raise DataValidationError("Nur ein wartender Job kann erstmalig gestartet werden.")
            conn.execute(
                """UPDATE jobs SET status='running',phase='running',heartbeat_at=?,started_at=?,
                   requested_control='none',updated_at=? WHERE id=?""",
                (now, now, now, job_id),
            )
            self._job_event(conn, job_id, "started")
        return self.get_job(job_id)

    def request_pause(self, job_id: str) -> dict:
        now = self._now()
        with self.data.transaction() as conn:
            row = self._job_exists(conn, job_id)
            if row["status"] != "running":
                raise DataValidationError("Pause kann nur für einen laufenden Job angefordert werden.")
            conn.execute(
                "UPDATE jobs SET requested_control='pause',updated_at=? WHERE id=?",
                (now, job_id),
            )
            self._job_event(conn, job_id, "pause-requested")
        return self.get_job(job_id)

    def acknowledge_pause(self, job_id: str) -> dict:
        now = self._now()
        with self.data.transaction() as conn:
            row = self._job_exists(conn, job_id)
            if row["status"] != "running" or row["requested_control"] != "pause":
                raise DataValidationError("Für diesen Job liegt keine bestätigbare Pause vor.")
            conn.execute(
                """UPDATE jobs SET status='paused',phase='paused',requested_control='none',
                   heartbeat_at=?,updated_at=? WHERE id=?""",
                (now, now, job_id),
            )
            self._job_event(conn, job_id, "paused")
        return self.get_job(job_id)

    def resume_job(self, job_id: str) -> dict:
        now = self._now()
        with self.data.transaction() as conn:
            row = self._job_exists(conn, job_id)
            if row["status"] not in {"paused", "interrupted"}:
                raise DataValidationError("Nur pausierte oder unterbrochene Jobs können fortgesetzt werden.")
            conn.execute(
                """UPDATE jobs SET status='running',phase='running',requested_control='none',
                   heartbeat_at=?,resume_count=resume_count+1,updated_at=? WHERE id=?""",
                (now, now, job_id),
            )
            self._job_event(conn, job_id, "resumed", {"from": row["status"]})
        return self.get_job(job_id)

    def request_cancel(self, job_id: str) -> dict:
        now = self._now()
        with self.data.transaction() as conn:
            row = self._job_exists(conn, job_id)
            status = row["status"]
            if status in TERMINAL_JOB_STATUSES:
                raise DataValidationError("Ein bereits beendeter Job kann nicht abgebrochen werden.")
            if status in {"queued", "paused", "interrupted"}:
                conn.execute(
                    """UPDATE jobs SET status='cancelled',phase='cancelled',requested_control='none',
                       finished_at=?,updated_at=? WHERE id=?""",
                    (now, now, job_id),
                )
                self._job_event(conn, job_id, "cancelled", {"from": status})
            elif status == "running":
                conn.execute(
                    """UPDATE jobs SET status='cancelling',phase='cancelling',
                       requested_control='cancel',updated_at=? WHERE id=?""",
                    (now, job_id),
                )
                self._job_event(conn, job_id, "cancel-requested")
            elif status == "cancelling":
                return self._job_dict(row)
        return self.get_job(job_id)

    def acknowledge_cancel(self, job_id: str) -> dict:
        now = self._now()
        with self.data.transaction() as conn:
            row = self._job_exists(conn, job_id)
            if row["status"] != "cancelling":
                raise DataValidationError("Dieser Job wartet nicht auf Abbruchbestätigung.")
            conn.execute(
                """UPDATE jobs SET status='cancelled',phase='cancelled',requested_control='none',
                   heartbeat_at=?,finished_at=?,updated_at=? WHERE id=?""",
                (now, now, now, job_id),
            )
            self._job_event(conn, job_id, "cancelled", {"from": "cancelling"})
        return self.get_job(job_id)

    def checkpoint(
        self,
        job_id: str,
        *,
        phase: str = "running",
        progress_done: int = 0,
        progress_total: int = 0,
        bytes_done: int = 0,
        bytes_total: int = 0,
        checkpoint: object | None = None,
    ) -> dict:
        clean_phase = " ".join(str(phase or "running").split())[:120] or "running"
        done, total, byte_done, byte_total = self._validate_progress(
            progress_done, progress_total, bytes_done, bytes_total
        )
        checkpoint_json = self._json_text(checkpoint or {}, "Checkpoint")
        now = self._now()
        with self.data.transaction() as conn:
            row = self._job_exists(conn, job_id)
            if row["status"] not in {"running", "cancelling"}:
                raise DataValidationError("Checkpoint ist nur für laufende oder abbrechende Jobs erlaubt.")
            conn.execute(
                """UPDATE jobs SET phase=?,progress_done=?,progress_total=?,bytes_done=?,bytes_total=?,
                   checkpoint_json=?,heartbeat_at=?,updated_at=? WHERE id=?""",
                (clean_phase, done, total, byte_done, byte_total, checkpoint_json, now, now, job_id),
            )
            self._job_event(
                conn,
                job_id,
                "checkpoint",
                {"phase": clean_phase, "progress_done": done, "progress_total": total,
                 "bytes_done": byte_done, "bytes_total": byte_total},
            )
        return self.get_job(job_id)

    def complete_job(self, job_id: str, result: object | None = None) -> dict:
        result_json = self._json_text(result or {}, "Job-Ergebnis")
        now = self._now()
        with self.data.transaction() as conn:
            row = self._job_exists(conn, job_id)
            if row["status"] != "running" or row["requested_control"] != "none":
                raise DataValidationError("Job kann in seinem aktuellen Kontrollzustand nicht abgeschlossen werden.")
            conn.execute(
                """UPDATE jobs SET status='completed',phase='completed',result_json=?,
                   heartbeat_at=?,finished_at=?,updated_at=? WHERE id=?""",
                (result_json, now, now, now, job_id),
            )
            self._job_event(conn, job_id, "completed")
        return self.get_job(job_id)

    def fail_job(self, job_id: str, code: str, message: str) -> dict:
        clean_code = str(code or "JOB-FAILED").strip()[:80] or "JOB-FAILED"
        clean_message = str(message or "Job fehlgeschlagen.").strip()[:2000]
        now = self._now()
        with self.data.transaction() as conn:
            row = self._job_exists(conn, job_id)
            if row["status"] not in {"running", "cancelling"}:
                raise DataValidationError("Nur ein aktiver Job kann als fehlgeschlagen markiert werden.")
            conn.execute(
                """UPDATE jobs SET status='failed',phase='failed',error_code=?,error_message=?,
                   requested_control='none',heartbeat_at=?,finished_at=?,updated_at=? WHERE id=?""",
                (clean_code, clean_message, now, now, now, job_id),
            )
            self._job_event(conn, job_id, "failed", {"code": clean_code, "message": clean_message})
        return self.get_job(job_id)

    def recover_incomplete_jobs(self, reason: str = "startup") -> list[str]:
        now = self._now()
        recovered: list[str] = []
        with self.data.transaction() as conn:
            rows = conn.execute(
                "SELECT id,status FROM jobs WHERE status IN ('running','cancelling') ORDER BY created_at"
            ).fetchall()
            for row in rows:
                conn.execute(
                    """UPDATE jobs SET status='interrupted',phase='interrupted',requested_control='none',
                       updated_at=? WHERE id=?""",
                    (now, row["id"]),
                )
                self._job_event(
                    conn, row["id"], "interrupted", {"reason": str(reason)[:120], "from": row["status"]}
                )
                recovered.append(str(row["id"]))
        return recovered

    def watchdog(self, *, stale_after_seconds: int = 30, now: datetime | None = None) -> list[str]:
        try:
            threshold_seconds = int(stale_after_seconds)
        except (TypeError, ValueError) as exc:
            raise DataValidationError("Watchdog-Zeitfenster ist ungültig.") from exc
        if threshold_seconds < 5 or threshold_seconds > 86_400:
            raise DataValidationError("Watchdog-Zeitfenster muss zwischen 5 Sekunden und 24 Stunden liegen.")
        reference = now.astimezone() if now is not None else datetime.now().astimezone()
        threshold = reference - timedelta(seconds=threshold_seconds)
        stale: list[tuple[str, str]] = []
        with self.data.read_connection() as conn:
            rows = conn.execute(
                "SELECT id,status,heartbeat_at,updated_at FROM jobs WHERE status IN ('running','cancelling')"
            ).fetchall()
        for row in rows:
            raw = row["heartbeat_at"] or row["updated_at"]
            try:
                observed = datetime.fromisoformat(raw)
            except (TypeError, ValueError):
                observed = threshold - timedelta(seconds=1)
            if observed <= threshold:
                stale.append((str(row["id"]), str(row["status"])))
        if not stale:
            return []
        stamp = reference.isoformat(timespec="seconds")
        with self.data.transaction() as conn:
            for job_id, old_status in stale:
                current = self._job_exists(conn, job_id)
                if current["status"] not in {"running", "cancelling"}:
                    continue
                conn.execute(
                    """UPDATE jobs SET status='interrupted',phase='interrupted',requested_control='none',
                       updated_at=? WHERE id=?""",
                    (stamp, job_id),
                )
                self._job_event(
                    conn, job_id, "watchdog-interrupted",
                    {"stale_after_seconds": threshold_seconds, "from": old_status},
                )
        return [job_id for job_id, _ in stale]

    def summary(self) -> dict:
        with self.data.read_connection() as conn:
            rows = conn.execute("SELECT status,count(*) AS amount FROM jobs GROUP BY status").fetchall()
            action_rows = conn.execute(
                "SELECT status,count(*) AS amount FROM file_actions GROUP BY status"
            ).fetchall()
        return {
            "jobs": {str(row["status"]): int(row["amount"]) for row in rows},
            "actions": {str(row["status"]): int(row["amount"]) for row in action_rows},
        }

    def plan_action(
        self,
        job_id: str,
        action_type: str,
        *,
        source_path: str = "",
        destination_path: str = "",
        reversible: bool = False,
        before: object | None = None,
    ) -> dict:
        action = str(action_type or "").strip().lower()
        if action not in VALID_ACTION_TYPES:
            raise DataValidationError("Dateiaktion ist ungültig.")
        source_required = action in {"copy", "move", "rename"}
        source = self._normalize_path(source_path, required=source_required, label="Quellpfad")
        destination = self._normalize_path(destination_path, required=True, label="Zielpfad")
        before_json = self._json_text(before or {}, "Vorher-Metadaten")
        now = self._now()
        with self.data.transaction() as conn:
            job = self._job_exists(conn, job_id)
            if job["status"] in TERMINAL_JOB_STATUSES or job["status"] == "cancelling":
                raise DataValidationError("Für diesen Job dürfen keine neuen Dateiaktionen geplant werden.")
            sequence = int(
                conn.execute(
                    "SELECT COALESCE(max(sequence),0)+1 FROM file_actions WHERE job_id=?", (job_id,)
                ).fetchone()[0]
            )
            cursor = conn.execute(
                """INSERT INTO file_actions(
                    job_id,sequence,action_type,source_path,destination_path,status,reversible,
                    before_json,after_json,reason,created_at
                ) VALUES(?,?,?,?,?,'planned',? ,?,'{}','',?)""",
                (job_id, sequence, action, source, destination, 1 if reversible else 0, before_json, now),
            )
            action_id = int(cursor.lastrowid)
            self._job_event(
                conn, job_id, "action-planned",
                {"action_id": action_id, "sequence": sequence, "action_type": action},
            )
        return self.get_action(action_id)

    def get_action(self, action_id: int) -> dict:
        with self.data.read_connection() as conn:
            row = self._action_exists(conn, int(action_id))
        return self._action_dict(row)

    def list_actions(self, job_id: str) -> list[dict]:
        self.get_job(job_id)
        with self.data.read_connection() as conn:
            rows = conn.execute(
                "SELECT * FROM file_actions WHERE job_id=? ORDER BY sequence,id", (job_id,)
            ).fetchall()
        return [self._action_dict(row) for row in rows]

    def _finish_planned_action(
        self,
        action_id: int,
        status: str,
        *,
        reason: str = "",
        after: object | None = None,
    ) -> dict:
        if status not in {"applied", "skipped", "failed"}:
            raise DataValidationError("Ungültiger Aktionsabschluss.")
        reason_clean = str(reason or "").strip()[:2000]
        if status in {"skipped", "failed"} and not reason_clean:
            raise DataValidationError("Übersprungene oder fehlgeschlagene Aktion benötigt einen Grund.")
        after_json = self._json_text(after or {}, "Nachher-Metadaten")
        now = self._now()
        with self.data.transaction() as conn:
            row = self._action_exists(conn, int(action_id))
            if row["status"] != "planned":
                raise DataValidationError("Nur eine geplante Dateiaktion kann abgeschlossen werden.")
            applied_at = now if status == "applied" else None
            conn.execute(
                """UPDATE file_actions SET status=?,after_json=?,reason=?,applied_at=? WHERE id=?""",
                (status, after_json, reason_clean, applied_at, int(action_id)),
            )
            self._job_event(
                conn, row["job_id"], f"action-{status}",
                {"action_id": int(action_id), "sequence": int(row["sequence"]), "reason": reason_clean},
            )
        return self.get_action(int(action_id))

    def mark_action_applied(self, action_id: int, *, after: object | None = None) -> dict:
        return self._finish_planned_action(action_id, "applied", after=after)

    def mark_action_skipped(self, action_id: int, reason: str) -> dict:
        return self._finish_planned_action(action_id, "skipped", reason=reason)

    def mark_action_failed(self, action_id: int, reason: str) -> dict:
        return self._finish_planned_action(action_id, "failed", reason=reason)

    def mark_action_undone(self, action_id: int, *, after: object | None = None) -> dict:
        after_json = self._json_text(after or {}, "Undo-Nachher-Metadaten")
        now = self._now()
        with self.data.transaction() as conn:
            row = self._action_exists(conn, int(action_id))
            if row["status"] != "applied":
                raise DataValidationError("Nur eine angewendete Dateiaktion kann als rückgängig markiert werden.")
            if not bool(row["reversible"]):
                raise DataValidationError("Diese Dateiaktion ist ausdrücklich nicht reversibel.")
            conn.execute(
                "UPDATE file_actions SET status='undone',after_json=?,undone_at=? WHERE id=?",
                (after_json, now, int(action_id)),
            )
            self._job_event(
                conn, row["job_id"], "action-undone",
                {"action_id": int(action_id), "sequence": int(row["sequence"])},
            )
        return self.get_action(int(action_id))

    def undo_candidates(self, job_id: str) -> list[dict]:
        self.get_job(job_id)
        with self.data.read_connection() as conn:
            rows = conn.execute(
                """SELECT * FROM file_actions
                   WHERE job_id=? AND status='applied' AND reversible=1
                   ORDER BY sequence DESC,id DESC""",
                (job_id,),
            ).fetchall()
        return [self._action_dict(row) for row in rows]
