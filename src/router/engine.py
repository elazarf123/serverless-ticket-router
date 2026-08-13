import re
from datetime import datetime, timezone
from .config import DEPARTMENT_RULES, DEFAULT_DEPARTMENT, DEFAULT_QUEUE, DEFAULT_PRIORITY, PRIORITY_KEYWORDS, SLA_HOURS, VIP_DOMAINS
from .models import TicketRequest, RoutingResult

class TicketRouter:
    CVE_PATTERN = re.compile(r"\bCVE-\d{4}-\d{4,7}\b", re.IGNORECASE)
    HTTP_STATUS_PATTERN = re.compile(r"\b[45]\d{2}\b")

    def __init__(self):
        self._compiled_dept_keywords = {}
        for dept, data in DEPARTMENT_RULES.items():
            self._compiled_dept_keywords[dept] = {kw: (re.compile(rf"\b{re.escape(kw)}\b", re.IGNORECASE), w) for kw, w in data["keywords"].items()}
        self._compiled_priority = {p: [re.compile(rf"\b{re.escape(kw)}\b", re.IGNORECASE) for kw in kws] for p, kws in PRIORITY_KEYWORDS.items()}

    def extract_tags(self, text):
        tags = set()
        for c in self.CVE_PATTERN.findall(text): tags.add(c.upper())
        for code in self.HTTP_STATUS_PATTERN.findall(text): tags.add(f"HTTP-{code}")
        return sorted(list(tags))

    def calculate_department(self, subject, body):
        scores = {dept: 0.0 for dept in DEPARTMENT_RULES}
        all_matched = {dept: [] for dept in DEPARTMENT_RULES}
        for dept, kw_dict in self._compiled_dept_keywords.items():
            for kw, (pattern, weight) in kw_dict.items():
                if pattern.search(subject): scores[dept] += weight * 2.0; all_matched[dept].append(kw)
                if pattern.search(body): scores[dept] += weight * 1.0; all_matched[dept].append(kw)
        top_dept, top_score = sorted(scores.items(), key=lambda x: x[1], reverse=True)[0]
        if top_score <= 0: return DEFAULT_DEPARTMENT, DEFAULT_QUEUE, 0.0, []
        confidence = round(min(max(top_score / (top_score + 4.0), 0.25), 0.99), 2)
        return top_dept, DEPARTMENT_RULES[top_dept]["queue"], confidence, list(set(all_matched[top_dept]))

    def calculate_priority(self, text, dept, sender, override=None):
        if override in SLA_HOURS: return override, override in ["P1", "P2"]
        for p in self._compiled_priority.get("P1", []):
            if p.search(text): return "P1", True
        for p in self._compiled_priority.get("P2", []):
            if p.search(text): return "P2", True
        is_vip = any(sender.lower().endswith(d) for d in VIP_DOMAINS)
        assigned = DEPARTMENT_RULES[dept].get("default_priority", "P3") if dept in DEPARTMENT_RULES else DEFAULT_PRIORITY
        if is_vip and assigned in ["P3", "P4"]: assigned = "P2"
        return assigned, is_vip

    def route_ticket(self, req: TicketRequest) -> RoutingResult:
        full_text = f"{req.subject} {req.body}"
        dept, queue, conf, kws = self.calculate_department(req.subject, req.body)
        priority, is_esc = self.calculate_priority(full_text, dept, req.sender, req.priority_override)
        tags = self.extract_tags(full_text)
        if is_esc: tags.append("ESCALATED")
        if any(req.sender.lower().endswith(d) for d in VIP_DOMAINS): tags.append("VIP-CUSTOMER")
        return RoutingResult(
            department=dept, queue=queue, priority=priority,
            sla_hours=SLA_HOURS.get(priority, 12), confidence_score=conf,
            matched_keywords=kws, is_escalated=is_esc, tags=tags,
            routed_at=datetime.now(timezone.utc).isoformat()
        )

router_instance = TicketRouter()
