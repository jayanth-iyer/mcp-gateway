from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class AuditRecord:
    timestamp: datetime
    client_id: str
    tool_name: str
    mcp_id: str
    prompt_hash: str
    execution_latency_ms: int


class AuditStore:
    """Append-only (WORM-style) audit log backed by SQLite. Not implemented in scaffolding."""

    async def write(self, record: AuditRecord) -> None:
        raise NotImplementedError
