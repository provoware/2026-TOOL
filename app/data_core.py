#!/usr/bin/env python3
"""Robuster SQLite-Datenkern für PROVOWARE HEADQUARTER."""
from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass
from datetime import date, datetime
import json
import os
from pathlib import Path
import shutil
import sqlite3
import threading
from typing import Iterator

SCHEMA_VERSION = 2
DB_FILENAME = "provoware.sqlite3"
VALID_PRIORITIES = {"niedrig", "normal", "hoch"}


class DataCoreError(RuntimeError):
    """Basisklasse für kontrollierte Datenkernfehler."""


class DataValidationError(DataCoreError):
    """Ungültige Nutzdaten."""


class DataNotFoundError(DataCoreError):
    """Angeforderter Datensatz existiert nicht."""


class DataIntegrityError(DataCoreError):
    """Datenbankzustand ist nicht sicher verwendbar."""


@dataclass(frozen=True)
class HealthReport:
    status: str
    schema_version: int
    journal_mode: str
    integrity: str
    db_path: str
    size_bytes: int
    backups: int
    recovered: bool = False
    recovery_source: str | None = None

    def as_dict(self) -> dict:
        return {
            "status": self.status,
            "schema_version": self.schema_version,
            "journal_mode": self.journal_mode,
            "integrity": self.integrity,
            "db_path": self.db_path,
            "size_bytes": self.size_bytes,
            "backups": self.backups,
            "recovered": self.recovered,
            "recovery_source": self.recovery_source,
        }


class DataCore:
    """Projektbezogener SQLite-Service. Keine geteilte Langzeit-Connection."""

    def __init__(self, project_root: Path | str) -> None:
        self.project_root = Path(project_root).expanduser().resolve(strict=False)
        self.db_dir = self.project_root / "datenbanken"
        self.db_path = self.db_dir / DB_FILENAME
        self.backup_dir = self.project_root / "sicherungen" / "datenbank"
        self.log_dir = self.project_root / "logs"
        self._lock = threading.RLock()
        self._last_recovery: Path | None = None

    @staticmethod
    def _now() -> str:
        return datetime.now().astimezone().isoformat(timespec="seconds")

    @staticmethod
    def _timestamp() -> str:
        return datetime.now().astimezone().strftime("%Y%m%d-%H%M%S-%f")

    def _prepare_dirs(self) -> None:
        for path in (self.db_dir, self.backup_dir, self.log_dir):
            path.mkdir(parents=True, exist_ok=True)

    def _connect(self, path: Path | None = None, *, configure_main: bool = True) -> sqlite3.Connection:
        target = path or self.db_path
        conn = sqlite3.connect(str(target), timeout=5.0, isolation_level=None)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        conn.execute("PRAGMA busy_timeout = 5000")
        if configure_main and target == self.db_path:
            mode = str(conn.execute("PRAGMA journal_mode = WAL").fetchone()[0]).lower()
            if mode != "wal":
                conn.close()
                raise DataIntegrityError(f"SQLite-WAL konnte nicht aktiviert werden (Modus: {mode}).")
            conn.execute("PRAGMA synchronous = NORMAL")
        return conn

    @contextmanager
    def read_connection(self) -> Iterator[sqlite3.Connection]:
        """Kurzlebige, konfigurierte Leseverbindung für interne Services."""
        conn = self._connect()
        try:
            yield conn
        finally:
            conn.close()

    @contextmanager
    def transaction(self) -> Iterator[sqlite3.Connection]:
        conn = self._connect()
        try:
            conn.execute("BEGIN IMMEDIATE")
            yield conn
            conn.execute("COMMIT")
        except Exception:
            try:
                conn.execute("ROLLBACK")
            except sqlite3.Error:
                pass
            raise
        finally:
            conn.close()

    def ensure_ready(self) -> HealthReport:
        with self._lock:
            self._prepare_dirs()
            self._last_recovery = None
            try:
                self._initialize_or_migrate()
                report = self._health_report()
                if report.integrity != "ok":
                    raise DataIntegrityError(f"SQLite-Integritätsprüfung: {report.integrity}")
                return report
            except (sqlite3.DatabaseError, DataIntegrityError) as exc:
                recovered = self._recover_from_latest_verified_backup(str(exc))
                if not recovered:
                    raise DataIntegrityError(
                        "Datenbank ist nicht sicher verwendbar und es existiert keine geprüfte Wiederherstellungskopie."
                    ) from exc
                self._initialize_or_migrate()
                report = self._health_report()
                if report.integrity != "ok":
                    raise DataIntegrityError("Datenbank blieb nach Recovery inkonsistent.")
                return HealthReport(
                    **{**report.as_dict(), "recovered": True, "recovery_source": str(recovered)}
                )

    def _initialize_or_migrate(self) -> None:
        existed = self.db_path.exists() and self.db_path.stat().st_size > 0
        conn = self._connect()
        try:
            version = int(conn.execute("PRAGMA user_version").fetchone()[0])
            if version > SCHEMA_VERSION:
                raise DataIntegrityError(
                    f"Datenbankschema {version} ist neuer als unterstützt ({SCHEMA_VERSION})."
                )
        finally:
            conn.close()

        if version < SCHEMA_VERSION:
            if existed:
                self.create_verified_backup(f"schema-v{version}")
            with self.transaction() as conn:
                current = int(conn.execute("PRAGMA user_version").fetchone()[0])
                if current < 1:
                    self._migrate_0_to_1(conn)
                    conn.execute("PRAGMA user_version = 1")
                    current = 1
                if current < 2:
                    self._migrate_1_to_2(conn)
                    conn.execute("PRAGMA user_version = 2")

    @staticmethod
    def _migrate_0_to_1(conn: sqlite3.Connection) -> None:
        statements = (
            """CREATE TABLE IF NOT EXISTS todos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL CHECK(length(trim(title)) BETWEEN 1 AND 300),
                description TEXT NOT NULL DEFAULT '' CHECK(length(description) <= 5000),
                priority TEXT NOT NULL DEFAULT 'normal'
                    CHECK(priority IN ('niedrig','normal','hoch')),
                due_date TEXT NULL,
                due_time TEXT NULL,
                status TEXT NOT NULL DEFAULT 'open'
                    CHECK(status IN ('open','archived')),
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                completed_at TEXT NULL,
                archived_at TEXT NULL
            )""",
            """CREATE INDEX IF NOT EXISTS idx_todos_status_due
                ON todos(status, due_date, due_time)""",
            """CREATE TABLE IF NOT EXISTS todo_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                todo_id INTEGER NOT NULL,
                event_type TEXT NOT NULL,
                payload_json TEXT NOT NULL DEFAULT '{}',
                created_at TEXT NOT NULL,
                FOREIGN KEY(todo_id) REFERENCES todos(id) ON DELETE RESTRICT
            )""",
            """CREATE INDEX IF NOT EXISTS idx_todo_events_todo
                ON todo_events(todo_id, created_at)""",
        )
        for statement in statements:
            conn.execute(statement)

    @staticmethod
    def _migrate_1_to_2(conn: sqlite3.Connection) -> None:
        statements = (
            """CREATE TABLE IF NOT EXISTS jobs (
                id TEXT PRIMARY KEY,
                kind TEXT NOT NULL CHECK(length(trim(kind)) BETWEEN 1 AND 80),
                status TEXT NOT NULL DEFAULT 'queued'
                    CHECK(status IN ('queued','running','paused','cancelling','cancelled','completed','failed','interrupted')),
                phase TEXT NOT NULL DEFAULT 'queued' CHECK(length(phase) <= 120),
                payload_json TEXT NOT NULL DEFAULT '{}',
                checkpoint_json TEXT NOT NULL DEFAULT '{}',
                result_json TEXT NOT NULL DEFAULT '{}',
                error_code TEXT NULL,
                error_message TEXT NULL,
                progress_done INTEGER NOT NULL DEFAULT 0 CHECK(progress_done >= 0),
                progress_total INTEGER NOT NULL DEFAULT 0 CHECK(progress_total >= 0),
                bytes_done INTEGER NOT NULL DEFAULT 0 CHECK(bytes_done >= 0),
                bytes_total INTEGER NOT NULL DEFAULT 0 CHECK(bytes_total >= 0),
                requested_control TEXT NOT NULL DEFAULT 'none'
                    CHECK(requested_control IN ('none','pause','cancel')),
                heartbeat_at TEXT NULL,
                started_at TEXT NULL,
                finished_at TEXT NULL,
                resume_count INTEGER NOT NULL DEFAULT 0 CHECK(resume_count >= 0),
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )""",
            """CREATE INDEX IF NOT EXISTS idx_jobs_status_updated
                ON jobs(status, updated_at DESC)""",
            """CREATE TABLE IF NOT EXISTS job_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                job_id TEXT NOT NULL,
                event_type TEXT NOT NULL CHECK(length(trim(event_type)) BETWEEN 1 AND 80),
                payload_json TEXT NOT NULL DEFAULT '{}',
                created_at TEXT NOT NULL,
                FOREIGN KEY(job_id) REFERENCES jobs(id) ON DELETE RESTRICT
            )""",
            """CREATE INDEX IF NOT EXISTS idx_job_events_job
                ON job_events(job_id, id)""",
            """CREATE TABLE IF NOT EXISTS file_actions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                job_id TEXT NOT NULL,
                sequence INTEGER NOT NULL CHECK(sequence > 0),
                action_type TEXT NOT NULL
                    CHECK(action_type IN ('copy','move','rename','mkdir')),
                source_path TEXT NOT NULL DEFAULT '',
                destination_path TEXT NOT NULL DEFAULT '',
                status TEXT NOT NULL DEFAULT 'planned'
                    CHECK(status IN ('planned','applied','skipped','failed','undone')),
                reversible INTEGER NOT NULL DEFAULT 0 CHECK(reversible IN (0,1)),
                before_json TEXT NOT NULL DEFAULT '{}',
                after_json TEXT NOT NULL DEFAULT '{}',
                reason TEXT NOT NULL DEFAULT '',
                created_at TEXT NOT NULL,
                applied_at TEXT NULL,
                undone_at TEXT NULL,
                FOREIGN KEY(job_id) REFERENCES jobs(id) ON DELETE RESTRICT,
                UNIQUE(job_id, sequence)
            )""",
            """CREATE INDEX IF NOT EXISTS idx_file_actions_job_status
                ON file_actions(job_id, status, sequence)""",
        )
        for statement in statements:
            conn.execute(statement)

    def _health_report(self) -> HealthReport:
        conn = self._connect()
        try:
            integrity = str(conn.execute("PRAGMA quick_check").fetchone()[0]).lower()
            version = int(conn.execute("PRAGMA user_version").fetchone()[0])
            journal = str(conn.execute("PRAGMA journal_mode").fetchone()[0]).lower()
        finally:
            conn.close()
        return HealthReport(
            status="ok" if integrity == "ok" and version == SCHEMA_VERSION and journal == "wal" else "error",
            schema_version=version,
            journal_mode=journal,
            integrity=integrity,
            db_path=str(self.db_path),
            size_bytes=self.db_path.stat().st_size if self.db_path.exists() else 0,
            backups=len(list(self.backup_dir.glob("db-*.sqlite3"))),
        )

    @staticmethod
    def _database_is_valid(path: Path) -> bool:
        try:
            conn = sqlite3.connect(str(path), timeout=2.0)
            try:
                result = str(conn.execute("PRAGMA quick_check").fetchone()[0]).lower()
                return result == "ok"
            finally:
                conn.close()
        except sqlite3.Error:
            return False

    def create_verified_backup(self, label: str = "snapshot") -> Path:
        self._prepare_dirs()
        if not self.db_path.exists():
            raise DataIntegrityError("Noch keine Datenbank für Sicherung vorhanden.")
        safe_label = "".join(c if c.isalnum() or c in "-_" else "-" for c in label).strip("-") or "snapshot"
        final = self.backup_dir / f"db-{self._timestamp()}-{safe_label}.sqlite3"
        temp = final.with_suffix(".tmp")
        source = self._connect()
        target = sqlite3.connect(str(temp))
        try:
            source.backup(target)
            target.commit()
        finally:
            target.close()
            source.close()
        if not self._database_is_valid(temp):
            temp.unlink(missing_ok=True)
            raise DataIntegrityError("Erzeugte Datenbanksicherung hat die Integritätsprüfung nicht bestanden.")
        os.replace(temp, final)
        self._rotate_backups(keep=2)
        return final

    def _rotate_backups(self, keep: int = 2) -> None:
        backups = sorted(self.backup_dir.glob("db-*.sqlite3"), key=lambda p: p.stat().st_mtime, reverse=True)
        for old in backups[keep:]:
            old.unlink(missing_ok=True)

    def _recover_from_latest_verified_backup(self, reason: str) -> Path | None:
        self._prepare_dirs()
        candidates = sorted(self.backup_dir.glob("db-*.sqlite3"), key=lambda p: p.stat().st_mtime, reverse=True)
        source = next((p for p in candidates if self._database_is_valid(p)), None)
        if source is None:
            return None
        quarantine = self.db_dir / f"{DB_FILENAME}.corrupt-{self._timestamp()}"
        if self.db_path.exists():
            os.replace(self.db_path, quarantine)
        for suffix in ("-wal", "-shm"):
            sidecar = Path(str(self.db_path) + suffix)
            if sidecar.exists():
                os.replace(sidecar, Path(str(quarantine) + suffix))
        temp = self.db_path.with_suffix(".recovering")
        shutil.copy2(source, temp)
        if not self._database_is_valid(temp):
            temp.unlink(missing_ok=True)
            if quarantine.exists() and not self.db_path.exists():
                os.replace(quarantine, self.db_path)
            return None
        os.replace(temp, self.db_path)
        self._last_recovery = source
        self._record_recovery(reason, source, quarantine if quarantine.exists() else None)
        return source

    def _record_recovery(self, reason: str, source: Path, quarantine: Path | None) -> None:
        entry = {
            "at": self._now(),
            "reason": reason,
            "source": str(source),
            "quarantine": str(quarantine) if quarantine else None,
        }
        path = self.log_dir / "recovery.jsonl"
        with path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(entry, ensure_ascii=False) + "\n")
            handle.flush()
            os.fsync(handle.fileno())

    @staticmethod
    def _normalize_due(due_date: str | None, due_time: str | None) -> tuple[str | None, str | None]:
        d = (due_date or "").strip() or None
        t = (due_time or "").strip() or None
        if d:
            try:
                d = date.fromisoformat(d).isoformat()
            except ValueError as exc:
                raise DataValidationError("Termin-Datum ist ungültig.") from exc
        if t and not d:
            raise DataValidationError("Eine Uhrzeit benötigt ein Datum.")
        if t:
            try:
                t = datetime.strptime(t, "%H:%M").strftime("%H:%M")
            except ValueError as exc:
                raise DataValidationError("Termin-Uhrzeit ist ungültig.") from exc
        return d, t

    @staticmethod
    def _validate_title(title: str) -> str:
        value = " ".join(str(title).split())
        if not value:
            raise DataValidationError("Todo-Titel fehlt.")
        if len(value) > 300:
            raise DataValidationError("Todo-Titel darf höchstens 300 Zeichen lang sein.")
        return value

    def _event(self, conn: sqlite3.Connection, todo_id: int, event_type: str, payload: dict | None = None) -> None:
        conn.execute(
            "INSERT INTO todo_events(todo_id,event_type,payload_json,created_at) VALUES(?,?,?,?)",
            (todo_id, event_type, json.dumps(payload or {}, ensure_ascii=False, sort_keys=True), self._now()),
        )

    def create_todo(
        self,
        title: str,
        *,
        description: str = "",
        priority: str = "normal",
        due_date: str | None = None,
        due_time: str | None = None,
    ) -> dict:
        self.ensure_ready()
        clean_title = self._validate_title(title)
        description = str(description or "").strip()
        if len(description) > 5000:
            raise DataValidationError("Beschreibung darf höchstens 5000 Zeichen lang sein.")
        priority = str(priority or "normal").strip().lower()
        if priority not in VALID_PRIORITIES:
            raise DataValidationError("Priorität ist ungültig.")
        d, t = self._normalize_due(due_date, due_time)
        now = self._now()
        with self.transaction() as conn:
            cursor = conn.execute(
                """INSERT INTO todos(title,description,priority,due_date,due_time,status,created_at,updated_at)
                   VALUES(?,?,?,?,?,'open',?,?)""",
                (clean_title, description, priority, d, t, now, now),
            )
            todo_id = int(cursor.lastrowid)
            self._event(conn, todo_id, "created", {"due_date": d, "due_time": t, "priority": priority})
        return self.get_todo(todo_id)

    def get_todo(self, todo_id: int) -> dict:
        self.ensure_ready()
        with self.read_connection() as conn:
            row = conn.execute("SELECT * FROM todos WHERE id=?", (int(todo_id),)).fetchone()
        if row is None:
            raise DataNotFoundError("Todo wurde nicht gefunden.")
        return dict(row)

    def list_todos(self, scope: str = "active") -> list[dict]:
        self.ensure_ready()
        if scope not in {"active", "archive", "all"}:
            raise DataValidationError("Todo-Ansicht ist ungültig.")
        where = "" if scope == "all" else "WHERE status = ?"
        params: tuple = () if scope == "all" else (("open" if scope == "active" else "archived"),)
        order = (
            "ORDER BY CASE WHEN due_date IS NULL THEN 1 ELSE 0 END, due_date, "
            "CASE WHEN due_time IS NULL THEN 1 ELSE 0 END, due_time, created_at, id"
            if scope != "archive"
            else "ORDER BY archived_at DESC, id DESC"
        )
        with self.read_connection() as conn:
            rows = conn.execute(f"SELECT * FROM todos {where} {order}", params).fetchall()
        return [dict(row) for row in rows]

    def archive_todo(self, todo_id: int) -> dict:
        self.ensure_ready()
        now = self._now()
        with self.transaction() as conn:
            row = conn.execute("SELECT status FROM todos WHERE id=?", (int(todo_id),)).fetchone()
            if row is None:
                raise DataNotFoundError("Todo wurde nicht gefunden.")
            if row["status"] != "archived":
                conn.execute(
                    """UPDATE todos SET status='archived',completed_at=?,archived_at=?,updated_at=?
                       WHERE id=?""",
                    (now, now, now, int(todo_id)),
                )
                self._event(conn, int(todo_id), "archived")
        return self.get_todo(int(todo_id))

    def restore_todo(self, todo_id: int) -> dict:
        self.ensure_ready()
        now = self._now()
        with self.transaction() as conn:
            row = conn.execute("SELECT status FROM todos WHERE id=?", (int(todo_id),)).fetchone()
            if row is None:
                raise DataNotFoundError("Todo wurde nicht gefunden.")
            if row["status"] != "open":
                conn.execute(
                    """UPDATE todos SET status='open',completed_at=NULL,archived_at=NULL,updated_at=?
                       WHERE id=?""",
                    (now, int(todo_id)),
                )
                self._event(conn, int(todo_id), "restored")
        return self.get_todo(int(todo_id))

    def calendar_month(self, month: str) -> dict:
        self.ensure_ready()
        try:
            parsed = datetime.strptime(month, "%Y-%m")
            normalized = parsed.strftime("%Y-%m")
        except ValueError as exc:
            raise DataValidationError("Kalendermonat muss YYYY-MM entsprechen.") from exc
        with self.read_connection() as conn:
            rows = conn.execute(
                """SELECT id,title,priority,due_date,due_time
                   FROM todos
                   WHERE status='open' AND due_date LIKE ?
                   ORDER BY due_date,due_time,id""",
                (normalized + "-%",),
            ).fetchall()
        days: dict[str, list[dict]] = {}
        for row in rows:
            item = dict(row)
            days.setdefault(item["due_date"], []).append(item)
        return {"month": normalized, "days": days}

    def summary(self) -> dict:
        self.ensure_ready()
        today = date.today().isoformat()
        with self.read_connection() as conn:
            active = int(conn.execute("SELECT count(*) FROM todos WHERE status='open'").fetchone()[0])
            archive = int(conn.execute("SELECT count(*) FROM todos WHERE status='archived'").fetchone()[0])
            due_today = int(
                conn.execute("SELECT count(*) FROM todos WHERE status='open' AND due_date=?", (today,)).fetchone()[0]
            )
            overdue = int(
                conn.execute(
                    "SELECT count(*) FROM todos WHERE status='open' AND due_date IS NOT NULL AND due_date < ?",
                    (today,),
                ).fetchone()[0]
            )
        return {
            "active_todos": active,
            "archived_todos": archive,
            "due_today": due_today,
            "overdue": overdue,
            "database_bytes": self.db_path.stat().st_size if self.db_path.exists() else 0,
            "backups": len(list(self.backup_dir.glob("db-*.sqlite3"))),
        }
