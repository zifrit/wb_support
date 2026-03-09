from dataclasses import dataclass, field
from time import perf_counter
from uuid import uuid4


@dataclass
class RequestMeta:
    request_id: str = field(default_factory=lambda: str(uuid4()))
    started_at: float = field(default_factory=perf_counter)

    def duration_ms(self) -> int:
        return int((perf_counter() - self.started_at) * 1000)
