from typing import List, Optional, Dict, Any
import uuid
from pydantic import BaseModel, Field

class TicketRequest(BaseModel):
    ticket_id: Optional[str] = Field(default=None)
    sender: str = Field(...)
    subject: str = Field(...)
    body: str = Field(...)
    priority_override: Optional[str] = Field(default=None)

    def get_ticket_id(self) -> str:
        return self.ticket_id.strip() if self.ticket_id and self.ticket_id.strip() else f"TICK-{uuid.uuid4().hex[:8].upper()}"

class RoutingResult(BaseModel):
    department: str
    queue: str
    priority: str
    sla_hours: int
    confidence_score: float
    matched_keywords: List[str]
    is_escalated: bool
    tags: List[str]
    routed_at: str
