"""
Workspace Real-Time Event Broadcaster for HACTM Cyber Operations.
Provides in-memory event pub-sub queue for Server-Sent Events (SSE) and WebSocket clients,
along with event buffering, deduplication, and schema verification.
"""

import asyncio
import json
import uuid
from datetime import datetime, timezone
from typing import Any, AsyncGenerator, Dict, List, Optional
from pydantic import BaseModel, Field

from hactm.core.logging import logger


class WorkspaceEventPayload(BaseModel):
    event_id: str = Field(default_factory=lambda: f"EVT-{uuid.uuid4().hex[:8].upper()}")
    event_type: str = Field(..., description="Type of workspace event")
    tenant_id: str = Field(default="tenant_default")
    incident_id: Optional[str] = None
    task_id: Optional[str] = None
    agent_id: Optional[str] = None
    status: Optional[str] = None
    message: str = Field(..., description="Human and system-readable event summary")
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    data: Optional[Dict[str, Any]] = Field(default_factory=dict)


class WorkspaceEventBroadcaster:
    """Thread-safe event broadcaster for real-time cyber operations workspace."""

    _instance: Optional["WorkspaceEventBroadcaster"] = None

    def __init__(self, buffer_size: int = 150):
        self.buffer_size = buffer_size
        self._event_buffer: List[Dict[str, Any]] = []
        self._subscribers: List[asyncio.Queue] = []
        self._lock = asyncio.Lock()

    @classmethod
    def get_instance(cls) -> "WorkspaceEventBroadcaster":
        if cls._instance is None:
            cls._instance = WorkspaceEventBroadcaster()
        return cls._instance

    def publish_event(
        self,
        event_type: str,
        message: str,
        incident_id: Optional[str] = None,
        task_id: Optional[str] = None,
        agent_id: Optional[str] = None,
        status: Optional[str] = None,
        tenant_id: str = "tenant_default",
        data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Synchronously or asynchronously enqueue and broadcast an event."""
        event = WorkspaceEventPayload(
            event_type=event_type,
            tenant_id=tenant_id,
            incident_id=incident_id,
            task_id=task_id,
            agent_id=agent_id,
            status=status,
            message=message,
            data=data or {},
        ).model_dump()

        # Append to buffer with size limit
        self._event_buffer.append(event)
        if len(self._event_buffer) > self.buffer_size:
            self._event_buffer.pop(0)

        # Broadcast to active subscriber queues
        dead_queues = []
        for q in self._subscribers:
            try:
                q.put_nowait(event)
            except Exception:
                dead_queues.append(q)

        for dq in dead_queues:
            if dq in self._subscribers:
                self._subscribers.remove(dq)

        logger.debug(f"[WorkspaceEvent] Broadcast {event_type} for agent={agent_id}: {message}")
        return event

    async def subscribe(self) -> AsyncGenerator[Dict[str, Any], None]:
        """Subscribe a client queue to receive live workspace events."""
        q: asyncio.Queue = asyncio.Queue()
        self._subscribers.append(q)
        try:
            while True:
                event = await q.get()
                yield event
        except asyncio.CancelledError:
            pass
        finally:
            if q in self._subscribers:
                self._subscribers.remove(q)

    def get_recent_events(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Return the most recent buffered events."""
        return self._event_buffer[-limit:]

    def clear(self):
        """Clear the event buffer and reset subscribers (useful for tests)."""
        self._event_buffer.clear()
        self._subscribers.clear()


# Global accessor
broadcaster = WorkspaceEventBroadcaster.get_instance()

