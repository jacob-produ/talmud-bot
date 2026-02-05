import threading


class ProgressManager:
    _lock = threading.Lock()
    _store = {}

    @classmethod
    def start(cls, key: str, meta: dict = None):
        with cls._lock:
            cls._store[key] = {
                "progress": 0,
                "status": "running",
                "meta": meta or {}
            }

    @classmethod
    def set_progress(cls, key: str, percent: int):
        if percent < 0:
            percent = 0
        if percent > 100:
            percent = 100
        with cls._lock:
            if key in cls._store:
                cls._store[key]["progress"] = percent
                if percent >= 100:
                    cls._store[key]["status"] = "done"

    @classmethod
    def finish(cls, key: str):
        with cls._lock:
            if key in cls._store:
                cls._store[key]["progress"] = 100
                cls._store[key]["status"] = "done"

    @classmethod
    def error(cls, key: str, message: str):
        with cls._lock:
            if key in cls._store:
                cls._store[key]["status"] = "error"
                cls._store[key]["error"] = message

    @classmethod
    def get(cls, key: str) -> dict:
        with cls._lock:
            return cls._store.get(key, {"progress": 0, "status": "idle"})



