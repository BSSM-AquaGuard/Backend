import time
from threading import Lock
from dataclasses import asdict
from typing import Optional, Dict

class SimpleCache:
    def __init__(self, ttl: Optional[float] = None):
        self._data: Dict[int, tuple] = {}
        self._ttl = ttl
        self._lock = Lock()

    def set(self, id: int, packet) -> None:
        with self._lock:
            self._data[id] = (packet, time.time())

    def get(self, id: int):
        with self._lock:
            v = self._data.get(id)
            if not v:
                return None
            packet, ts = v
            if self._ttl is not None and time.time() - ts > self._ttl:
                del self._data[id]
                return None
            return packet

    def all(self):
        now = time.time()
        out = {}
        with self._lock:
            keys = list(self._data.keys())
            for k in keys:
                packet, ts = self._data.get(k)
                if self._ttl is not None and now - ts > self._ttl:
                    del self._data[k]
                else:
                    out[k] = packet
        return out

def packet_to_dict(packet):
    try:
        return asdict(packet)
    except Exception:
        # Fallback: try attribute access
        return {k: getattr(packet, k) for k in ("id", "temperature", "turbidity", "timestamp") if hasattr(packet, k)}
