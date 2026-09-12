#!/usr/bin/env python3
"""Read-only Sortier-Analyse und persistente Vorschau für PROVOWARE HEADQUARTER."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
import json
import os
from pathlib import Path
import threading
import uuid

from data_core import DataCore, DataNotFoundError, DataValidationError
from job_manager import JobManager

FEATURE_SCHEMA_VERSION = 1
MAX_PATH_CHARS = 4096
MAX_RULES = 200
MAX_RULE_LIST_ITEMS = 100
SCAN_BATCH_SIZE = 50
CONTROL_CHECK_EVERY = 10

CATEGORY_EXTENSIONS = {
    "Bilder": {
        ".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp", ".tif", ".tiff",
        ".svg", ".heic", ".avif", ".raw", ".cr2", ".nef", ".arw",
    },
    "Video": {
        ".mp4", ".mkv", ".mov", ".avi", ".webm", ".m4v", ".wmv", ".flv",
        ".mpeg", ".mpg", ".mts", ".m2ts", ".ts",
    },
    "Audio": {
        ".mp3", ".wav", ".flac", ".ogg", ".opus", ".m4a", ".aac", ".wma",
        ".aiff", ".aif", ".alac",
    },
    "Dokumente": {
        ".pdf", ".odt", ".ods", ".odp", ".doc", ".docx", ".xls", ".xlsx",
        ".ppt", ".pptx", ".rtf", ".epub",
    },
    "Archive": {
        ".zip", ".7z", ".rar", ".tar", ".gz", ".bz2", ".xz", ".tgz", ".tbz2",
    },
    "Text / Code": {
        ".txt", ".md", ".csv", ".json", ".yaml", ".yml", ".xml", ".html", ".htm",
        ".css", ".js", ".ts", ".py", ".sh", ".bash", ".zsh", ".ini", ".toml",
        ".sql", ".log", ".conf", ".desktop",
    },
}
VALID_CATEGORIES = set(CATEGORY_EXTENSIONS) | {"Sonstige"}
SYSTEM_OR_CACHE_DIRS = {
    ".cache", "cache", "__pycache__", ".trash", ".trash-1000", ".trash-1001",
    "$recycle.bin", "system volume information", "lost+found", ".thumbnails",
    "node_modules", ".git",
}
VALID_DECISIONS = {"matched", "conflict", "unmatched", "skipped"}


@dataclass(frozen=True)
class NormalizedRule:
    rule_id: str
    name: str
    priority: int
    target_group: str
    extensions: tuple[str, ...]
    contains_any: tuple[str, ...]
    category: str | None

    def as_dict(self) -> dict:
        return {
            "id": self.rule_id,
            "name": self.name,
            "priority": self.priority,
            "target_group": self.target_group,
            "extensions": list(self.extensions),
            "contains_any": list(self.contains_any),
            "category": self.category,
        }


class SorterPreviewService:
    """Analysiert Dateisystem-Metadaten, verändert aber niemals Nutzdateien."""

    def __init__(self, data_core: DataCore, jobs: JobManager) -> None:
        self.data = data_core
        self.jobs = jobs
        self._lock = threading.RLock()
        self._ensure_feature_schema()

    @staticmethod
    def _now() -> str:
        return datetime.now().astimezone().isoformat(timespec="seconds")

    @staticmethod
    def _json(value: object) -> str:
        return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))

    @staticmethod
    def _json_value(raw: str) -> object:
        try:
            return json.loads(raw or "[]")
        except json.JSONDecodeError:
            return []

    def _ensure_feature_schema(self) -> None:
        self.data.ensure_ready()
        with self._lock:
            with self.data.read_connection() as conn:
                exists = conn.execute(
                    "SELECT 1 FROM sqlite_master WHERE type='table' AND name='sort_scan_entries'"
                ).fetchone() is not None
            if not exists:
                self.data.create_verified_backup("sorter-preview-schema-v1")
            with self.data.transaction() as conn:
                conn.execute(
                    """CREATE TABLE IF NOT EXISTS sorter_feature_meta (
                        feature TEXT PRIMARY KEY,
                        schema_version INTEGER NOT NULL CHECK(schema_version > 0),
                        updated_at TEXT NOT NULL
                    )"""
                )
                conn.execute(
                    """CREATE TABLE IF NOT EXISTS sort_scan_entries (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        job_id TEXT NOT NULL,
                        relative_path TEXT NOT NULL,
                        name TEXT NOT NULL,
                        extension TEXT NOT NULL DEFAULT '',
                        category TEXT NOT NULL DEFAULT 'Sonstige',
                        entry_kind TEXT NOT NULL DEFAULT 'file'
                            CHECK(entry_kind IN ('file','symlink','directory')),
                        size_bytes INTEGER NOT NULL DEFAULT 0 CHECK(size_bytes >= 0),
                        mtime_ns INTEGER NOT NULL DEFAULT 0 CHECK(mtime_ns >= 0),
                        decision TEXT NOT NULL
                            CHECK(decision IN ('matched','conflict','unmatched','skipped')),
                        target_group TEXT NOT NULL DEFAULT '',
                        matches_json TEXT NOT NULL DEFAULT '[]',
                        skip_reason TEXT NOT NULL DEFAULT '',
                        seen_run TEXT NOT NULL,
                        captured_at TEXT NOT NULL,
                        FOREIGN KEY(job_id) REFERENCES jobs(id) ON DELETE RESTRICT,
                        UNIQUE(job_id, relative_path)
                    )"""
                )
                conn.execute(
                    """CREATE INDEX IF NOT EXISTS idx_sort_scan_job_decision
                       ON sort_scan_entries(job_id, decision, id)"""
                )
                conn.execute(
                    """CREATE INDEX IF NOT EXISTS idx_sort_scan_job_category
                       ON sort_scan_entries(job_id, category, id)"""
                )
                conn.execute(
                    """INSERT INTO sorter_feature_meta(feature,schema_version,updated_at)
                       VALUES('sorter-preview',?,?)
                       ON CONFLICT(feature) DO UPDATE SET
                         schema_version=excluded.schema_version,updated_at=excluded.updated_at""",
                    (FEATURE_SCHEMA_VERSION, self._now()),
                )

    def feature_status(self) -> dict:
        with self.data.read_connection() as conn:
            row = conn.execute(
                "SELECT schema_version,updated_at FROM sorter_feature_meta WHERE feature='sorter-preview'"
            ).fetchone()
        if row is None:
            raise DataNotFoundError("Sortier-Vorschau-Schema fehlt.")
        return {
            "schema_version": int(row["schema_version"]),
            "updated_at": row["updated_at"],
            "read_only_source": True,
        }

    @staticmethod
    def _normalize_source(source_path: str) -> Path:
        raw = str(source_path or "").strip()
        if not raw:
            raise DataValidationError("Quellordner fehlt.")
        if "\x00" in raw:
            raise DataValidationError("Quellordner enthält ein ungültiges Nullzeichen.")
        if len(raw) > MAX_PATH_CHARS:
            raise DataValidationError("Quellordner ist zu lang.")
        source = Path(raw).expanduser()
        if source.is_symlink():
            raise DataValidationError("Ein Symlink darf nicht als Quellwurzel verwendet werden.")
        try:
            resolved = source.resolve(strict=True)
        except (FileNotFoundError, OSError) as exc:
            raise DataValidationError("Quellordner existiert nicht oder ist nicht erreichbar.") from exc
        if not resolved.is_dir():
            raise DataValidationError("Der gewählte Quellpfad ist kein Verzeichnis.")
        return resolved

    @staticmethod
    def _normalize_text_list(value: object, label: str, *, extensions: bool = False) -> tuple[str, ...]:
        if value is None:
            return ()
        if not isinstance(value, list):
            raise DataValidationError(f"{label} muss eine Liste sein.")
        if len(value) > MAX_RULE_LIST_ITEMS:
            raise DataValidationError(f"{label} enthält zu viele Einträge.")
        result: list[str] = []
        for raw in value:
            item = str(raw or "").strip().lower()
            if not item:
                continue
            if len(item) > 120:
                raise DataValidationError(f"Ein Eintrag in {label} ist zu lang.")
            if extensions and not item.startswith("."):
                item = "." + item
            if item not in result:
                result.append(item)
        return tuple(result)

    def normalize_rules(self, rules: object | None) -> tuple[NormalizedRule, ...]:
        if rules is None:
            return ()
        if not isinstance(rules, list):
            raise DataValidationError("Regeln müssen als Liste übergeben werden.")
        if len(rules) > MAX_RULES:
            raise DataValidationError("Zu viele Regeln für eine Vorschau.")
        normalized: list[NormalizedRule] = []
        ids: set[str] = set()
        for index, raw in enumerate(rules, start=1):
            if not isinstance(raw, dict):
                raise DataValidationError("Jede Regel muss ein Objekt sein.")
            if raw.get("enabled", True) is False:
                continue
            rule_id = str(raw.get("id") or f"regel-{index}").strip()
            if not rule_id or len(rule_id) > 80 or any(ch not in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_." for ch in rule_id):
                raise DataValidationError("Regel-ID ist ungültig.")
            if rule_id in ids:
                raise DataValidationError("Regel-IDs müssen eindeutig sein.")
            ids.add(rule_id)
            name = " ".join(str(raw.get("name") or rule_id).split())[:160]
            target = " ".join(str(raw.get("target_group") or "").split())
            if not target or len(target) > 160:
                raise DataValidationError("Jede aktive Regel benötigt eine gültige Zielgruppe.")
            try:
                priority = int(raw.get("priority", 0))
            except (TypeError, ValueError) as exc:
                raise DataValidationError("Regel-Priorität muss eine ganze Zahl sein.") from exc
            if not -9999 <= priority <= 9999:
                raise DataValidationError("Regel-Priorität liegt außerhalb des erlaubten Bereichs.")
            category = str(raw.get("category") or "").strip() or None
            if category is not None and category not in VALID_CATEGORIES:
                raise DataValidationError("Regel-Kategorie ist ungültig.")
            normalized.append(
                NormalizedRule(
                    rule_id=rule_id,
                    name=name,
                    priority=priority,
                    target_group=target,
                    extensions=self._normalize_text_list(raw.get("extensions"), "Dateiendungen", extensions=True),
                    contains_any=self._normalize_text_list(raw.get("contains_any"), "Suchwörter"),
                    category=category,
                )
            )
        return tuple(normalized)

    @staticmethod
    def classify_extension(name: str) -> tuple[str, str]:
        extension = Path(name).suffix.lower()
        for category, extensions in CATEGORY_EXTENSIONS.items():
            if extension in extensions:
                return extension, category
        return extension, "Sonstige"

    @staticmethod
    def _rule_matches(name: str, extension: str, category: str, rule: NormalizedRule) -> bool:
        lowered_name = name.casefold()
        if rule.extensions and extension not in rule.extensions:
            return False
        if rule.contains_any and not any(term.casefold() in lowered_name for term in rule.contains_any):
            return False
        if rule.category and category != rule.category:
            return False
        return True

    def evaluate_rules(self, name: str, extension: str, category: str, rules: tuple[NormalizedRule, ...]) -> tuple[str, str, list[dict]]:
        matches = [rule for rule in rules if self._rule_matches(name, extension, category, rule)]
        matches.sort(key=lambda item: (-item.priority, item.rule_id))
        rendered = [rule.as_dict() for rule in matches]
        if not matches:
            return "unmatched", "", rendered
        top_priority = matches[0].priority
        top_targets = {rule.target_group for rule in matches if rule.priority == top_priority}
        if len(top_targets) > 1:
            return "conflict", "", rendered
        return "matched", matches[0].target_group, rendered

    @staticmethod
    def _relative(path: Path, root: Path) -> str:
        try:
            return path.relative_to(root).as_posix()
        except ValueError:
            return path.name

    @staticmethod
    def _should_skip_name(name: str, *, include_hidden: bool) -> str | None:
        lowered = name.casefold()
        if not include_hidden and name.startswith("."):
            return "versteckt"
        if lowered in SYSTEM_OR_CACHE_DIRS:
            return "System-/Cachebereich"
        return None

    def create_scan_job(
        self,
        source_path: str,
        *,
        rules: object | None = None,
        recursive: bool = False,
        include_hidden: bool = False,
    ) -> dict:
        source = self._normalize_source(source_path)
        normalized_rules = self.normalize_rules(rules)
        payload = {
            "source": str(source),
            "recursive": bool(recursive),
            "include_hidden": bool(include_hidden),
            "rules": [rule.as_dict() for rule in normalized_rules],
            "read_only": True,
        }
        return self.jobs.create_job("sort-preview-scan", payload)

    def _require_scan_job(self, job_id: str) -> dict:
        job = self.jobs.get_job(job_id)
        if job["kind"] != "sort-preview-scan":
            raise DataValidationError("Job gehört nicht zur Sortier-Vorschau.")
        return job

    def _entry_tuple(
        self,
        *,
        job_id: str,
        relative_path: str,
        name: str,
        extension: str,
        category: str,
        entry_kind: str,
        size_bytes: int,
        mtime_ns: int,
        decision: str,
        target_group: str,
        matches: list[dict],
        skip_reason: str,
        seen_run: str,
    ) -> tuple:
        return (
            job_id,
            relative_path,
            name,
            extension,
            category,
            entry_kind,
            max(0, int(size_bytes)),
            max(0, int(mtime_ns)),
            decision,
            target_group,
            self._json(matches),
            skip_reason,
            seen_run,
            self._now(),
        )

    def _flush_entries(self, rows: list[tuple]) -> None:
        if not rows:
            return
        with self.data.transaction() as conn:
            conn.executemany(
                """INSERT INTO sort_scan_entries(
                    job_id,relative_path,name,extension,category,entry_kind,size_bytes,mtime_ns,
                    decision,target_group,matches_json,skip_reason,seen_run,captured_at
                ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)
                ON CONFLICT(job_id,relative_path) DO UPDATE SET
                    name=excluded.name,
                    extension=excluded.extension,
                    category=excluded.category,
                    entry_kind=excluded.entry_kind,
                    size_bytes=excluded.size_bytes,
                    mtime_ns=excluded.mtime_ns,
                    decision=excluded.decision,
                    target_group=excluded.target_group,
                    matches_json=excluded.matches_json,
                    skip_reason=excluded.skip_reason,
                    seen_run=excluded.seen_run,
                    captured_at=excluded.captured_at""",
                rows,
            )
        rows.clear()

    def _control_requested(self, job_id: str) -> str:
        job = self.jobs.get_job(job_id)
        if job["status"] == "cancelling" or job["requested_control"] == "cancel":
            return "cancel"
        if job["status"] == "running" and job["requested_control"] == "pause":
            return "pause"
        if job["status"] == "interrupted":
            return "interrupt"
        return "none"

    def run_scan(self, job_id: str) -> dict:
        with self._lock:
            job = self._require_scan_job(job_id)
            if job["status"] == "queued":
                job = self.jobs.start_job(job_id)
            elif job["status"] == "interrupted":
                job = self.jobs.resume_job(job_id)
            elif job["status"] != "running":
                raise DataValidationError("Scan kann in diesem Jobzustand nicht ausgeführt werden.")

            payload = job["payload"]
            source = self._normalize_source(str(payload.get("source", "")))
            rules = self.normalize_rules(payload.get("rules", []))
            recursive = bool(payload.get("recursive", False))
            include_hidden = bool(payload.get("include_hidden", False))
            seen_run = uuid.uuid4().hex
            batch: list[tuple] = []
            seen = 0
            file_count = 0
            bytes_seen = 0
            skipped = 0

            stack = [source]
            try:
                while stack:
                    directory = stack.pop()
                    try:
                        iterator = os.scandir(directory)
                    except OSError as exc:
                        relative = self._relative(directory, source) or "."
                        batch.append(self._entry_tuple(
                            job_id=job_id,
                            relative_path=relative,
                            name=directory.name or str(directory),
                            extension="",
                            category="Sonstige",
                            entry_kind="directory",
                            size_bytes=0,
                            mtime_ns=0,
                            decision="skipped",
                            target_group="",
                            matches=[],
                            skip_reason=f"Ordner nicht lesbar: {exc.__class__.__name__}",
                            seen_run=seen_run,
                        ))
                        skipped += 1
                        self._flush_entries(batch)
                        continue

                    with iterator:
                        entries = sorted(iterator, key=lambda item: item.name.casefold())
                    for entry in entries:
                        seen += 1
                        entry_path = Path(entry.path)
                        relative = self._relative(entry_path, source)
                        skip_reason = self._should_skip_name(entry.name, include_hidden=include_hidden)

                        try:
                            if entry.is_symlink():
                                batch.append(self._entry_tuple(
                                    job_id=job_id,
                                    relative_path=relative,
                                    name=entry.name,
                                    extension=Path(entry.name).suffix.lower(),
                                    category="Sonstige",
                                    entry_kind="symlink",
                                    size_bytes=0,
                                    mtime_ns=0,
                                    decision="skipped",
                                    target_group="",
                                    matches=[],
                                    skip_reason="Symlink wird aus Sicherheitsgründen nicht verfolgt",
                                    seen_run=seen_run,
                                ))
                                skipped += 1
                            elif entry.is_dir(follow_symlinks=False):
                                if skip_reason:
                                    batch.append(self._entry_tuple(
                                        job_id=job_id,
                                        relative_path=relative,
                                        name=entry.name,
                                        extension="",
                                        category="Sonstige",
                                        entry_kind="directory",
                                        size_bytes=0,
                                        mtime_ns=0,
                                        decision="skipped",
                                        target_group="",
                                        matches=[],
                                        skip_reason=skip_reason,
                                        seen_run=seen_run,
                                    ))
                                    skipped += 1
                                elif recursive:
                                    stack.append(entry_path)
                            elif entry.is_file(follow_symlinks=False):
                                if skip_reason:
                                    batch.append(self._entry_tuple(
                                        job_id=job_id,
                                        relative_path=relative,
                                        name=entry.name,
                                        extension=Path(entry.name).suffix.lower(),
                                        category="Sonstige",
                                        entry_kind="file",
                                        size_bytes=0,
                                        mtime_ns=0,
                                        decision="skipped",
                                        target_group="",
                                        matches=[],
                                        skip_reason=skip_reason,
                                        seen_run=seen_run,
                                    ))
                                    skipped += 1
                                else:
                                    stat = entry.stat(follow_symlinks=False)
                                    extension, category = self.classify_extension(entry.name)
                                    decision, target, matches = self.evaluate_rules(
                                        entry.name, extension, category, rules
                                    )
                                    size = max(0, int(stat.st_size))
                                    batch.append(self._entry_tuple(
                                        job_id=job_id,
                                        relative_path=relative,
                                        name=entry.name,
                                        extension=extension,
                                        category=category,
                                        entry_kind="file",
                                        size_bytes=size,
                                        mtime_ns=max(0, int(stat.st_mtime_ns)),
                                        decision=decision,
                                        target_group=target,
                                        matches=matches,
                                        skip_reason="",
                                        seen_run=seen_run,
                                    ))
                                    file_count += 1
                                    bytes_seen += size
                            else:
                                batch.append(self._entry_tuple(
                                    job_id=job_id,
                                    relative_path=relative,
                                    name=entry.name,
                                    extension="",
                                    category="Sonstige",
                                    entry_kind="file",
                                    size_bytes=0,
                                    mtime_ns=0,
                                    decision="skipped",
                                    target_group="",
                                    matches=[],
                                    skip_reason="Nicht unterstützter Dateisystemeintrag",
                                    seen_run=seen_run,
                                ))
                                skipped += 1
                        except (FileNotFoundError, PermissionError, OSError) as exc:
                            batch.append(self._entry_tuple(
                                job_id=job_id,
                                relative_path=relative,
                                name=entry.name,
                                extension=Path(entry.name).suffix.lower(),
                                category="Sonstige",
                                entry_kind="file",
                                size_bytes=0,
                                mtime_ns=0,
                                decision="skipped",
                                target_group="",
                                matches=[],
                                skip_reason=f"Eintrag während Analyse nicht verfügbar: {exc.__class__.__name__}",
                                seen_run=seen_run,
                            ))
                            skipped += 1

                        if len(batch) >= SCAN_BATCH_SIZE:
                            self._flush_entries(batch)

                        if seen % CONTROL_CHECK_EVERY == 0:
                            self._flush_entries(batch)
                            control = self._control_requested(job_id)
                            if control == "pause":
                                self.jobs.checkpoint(
                                    job_id,
                                    phase="scan-pausing",
                                    progress_done=file_count,
                                    progress_total=0,
                                    bytes_done=bytes_seen,
                                    bytes_total=0,
                                    checkpoint={"seen": seen, "files": file_count, "run": seen_run},
                                )
                                return self.jobs.acknowledge_pause(job_id)
                            if control == "cancel":
                                return self.jobs.acknowledge_cancel(job_id)
                            if control == "interrupt":
                                return self.jobs.get_job(job_id)
                            self.jobs.checkpoint(
                                job_id,
                                phase="scan",
                                progress_done=file_count,
                                progress_total=0,
                                bytes_done=bytes_seen,
                                bytes_total=0,
                                checkpoint={"seen": seen, "files": file_count, "run": seen_run},
                            )

                self._flush_entries(batch)
                with self.data.transaction() as conn:
                    conn.execute(
                        "DELETE FROM sort_scan_entries WHERE job_id=? AND seen_run<>?",
                        (job_id, seen_run),
                    )
                self.jobs.checkpoint(
                    job_id,
                    phase="scan-finished",
                    progress_done=file_count,
                    progress_total=file_count,
                    bytes_done=bytes_seen,
                    bytes_total=bytes_seen,
                    checkpoint={"seen": seen, "files": file_count, "run": seen_run},
                )
                summary = self.scan_summary(job_id)
                summary.update({"source": str(source), "recursive": recursive, "skipped": skipped})
                return self.jobs.complete_job(job_id, summary)
            except Exception as exc:
                self._flush_entries(batch)
                current = self.jobs.get_job(job_id)
                if current["status"] in {"running", "cancelling"}:
                    return self.jobs.fail_job(job_id, "SORT-SCAN-FAILED", str(exc))
                raise

    def scan_summary(self, job_id: str) -> dict:
        self._require_scan_job(job_id)
        with self.data.read_connection() as conn:
            total = int(conn.execute(
                "SELECT count(*) FROM sort_scan_entries WHERE job_id=?", (job_id,)
            ).fetchone()[0])
            files = int(conn.execute(
                "SELECT count(*) FROM sort_scan_entries WHERE job_id=? AND entry_kind='file' AND decision<>'skipped'",
                (job_id,),
            ).fetchone()[0])
            bytes_total = int(conn.execute(
                "SELECT COALESCE(sum(size_bytes),0) FROM sort_scan_entries WHERE job_id=? AND entry_kind='file' AND decision<>'skipped'",
                (job_id,),
            ).fetchone()[0])
            decision_rows = conn.execute(
                "SELECT decision,count(*) AS n FROM sort_scan_entries WHERE job_id=? GROUP BY decision",
                (job_id,),
            ).fetchall()
            category_rows = conn.execute(
                """SELECT category,count(*) AS n,COALESCE(sum(size_bytes),0) AS bytes
                   FROM sort_scan_entries
                   WHERE job_id=? AND entry_kind='file' AND decision<>'skipped'
                   GROUP BY category ORDER BY n DESC,category""",
                (job_id,),
            ).fetchall()
        decisions = {name: 0 for name in sorted(VALID_DECISIONS)}
        decisions.update({row["decision"]: int(row["n"]) for row in decision_rows})
        categories = [
            {"category": row["category"], "count": int(row["n"]), "bytes": int(row["bytes"])}
            for row in category_rows
        ]
        return {
            "entries": total,
            "files": files,
            "bytes": bytes_total,
            "decisions": decisions,
            "categories": categories,
            "read_only": True,
        }

    def preview(
        self,
        job_id: str,
        *,
        offset: int = 0,
        limit: int = 100,
        decision: str | None = None,
        category: str | None = None,
    ) -> dict:
        self._require_scan_job(job_id)
        try:
            offset_i = max(0, int(offset))
            limit_i = max(1, min(500, int(limit)))
        except (TypeError, ValueError) as exc:
            raise DataValidationError("Paging-Werte sind ungültig.") from exc
        if decision is not None and decision not in VALID_DECISIONS:
            raise DataValidationError("Vorschau-Entscheidungsfilter ist ungültig.")
        if category is not None and category not in VALID_CATEGORIES:
            raise DataValidationError("Vorschau-Kategoriefilter ist ungültig.")

        where = ["job_id=?"]
        params: list[object] = [job_id]
        if decision is not None:
            where.append("decision=?")
            params.append(decision)
        if category is not None:
            where.append("category=?")
            params.append(category)
        clause = " AND ".join(where)
        with self.data.read_connection() as conn:
            total = int(conn.execute(
                f"SELECT count(*) FROM sort_scan_entries WHERE {clause}", tuple(params)
            ).fetchone()[0])
            rows = conn.execute(
                f"""SELECT id,relative_path,name,extension,category,entry_kind,size_bytes,mtime_ns,
                           decision,target_group,matches_json,skip_reason,captured_at
                    FROM sort_scan_entries WHERE {clause}
                    ORDER BY relative_path COLLATE NOCASE,id LIMIT ? OFFSET ?""",
                tuple(params + [limit_i, offset_i]),
            ).fetchall()
        items = []
        for row in rows:
            item = dict(row)
            item["matches"] = self._json_value(item.pop("matches_json"))
            items.append(item)
        return {
            "job_id": job_id,
            "offset": offset_i,
            "limit": limit_i,
            "total": total,
            "items": items,
        }
