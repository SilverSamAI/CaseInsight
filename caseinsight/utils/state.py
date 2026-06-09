from __future__ import annotations
import json
import time
from pathlib import Path

DEFAULT_STATE_PATH = ".caseinsight_state.json"


class ContactState:
    """Tracks which prospects have already been contacted so repeated runs
    do not email or enroll the same person twice.

    State is keyed by lowercased email and persisted as JSON on disk.
    """

    def __init__(self, path: str = DEFAULT_STATE_PATH):
        self.path = Path(path)
        self._data: dict[str, dict] = {}
        if self.path.exists():
            try:
                self._data = json.loads(self.path.read_text())
            except (json.JSONDecodeError, OSError):
                self._data = {}

    @staticmethod
    def _key(email: str) -> str:
        return email.strip().lower()

    def seen(self, email: str | None) -> bool:
        if not email:
            return False
        return self._key(email) in self._data

    def mark(self, email: str | None, stage: str) -> None:
        """Record that a prospect reached a stage (drafted/enrolled/synced)."""
        if not email:
            return
        key = self._key(email)
        record = self._data.setdefault(key, {"stages": {}})
        record["stages"][stage] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

    def reached(self, email: str | None, stage: str) -> bool:
        if not email:
            return False
        return stage in self._data.get(self._key(email), {}).get("stages", {})

    def save(self) -> None:
        self.path.write_text(json.dumps(self._data, indent=2))
