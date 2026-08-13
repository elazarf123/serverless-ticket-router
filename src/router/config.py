from typing import Dict, List, Any

DEPARTMENT_RULES: Dict[str, Dict[str, Any]] = {
    "Security & Compliance": {
        "queue": "queue-secops", "default_priority": "P2",
        "keywords": {"vulnerability": 3.5, "security breach": 5.0, "breach": 4.5, "exploit": 4.5, "cve": 4.0, "unauthorized": 3.5, "ransomware": 5.0}
    },
    "Billing & Finance": {
        "queue": "queue-billing", "default_priority": "P3",
        "keywords": {"invoice": 3.0, "refund": 4.0, "overcharge": 4.0, "charge": 2.5, "subscription": 2.5, "payment": 3.0, "billing": 3.5}
    },
    "IT Support & Infrastructure": {
        "queue": "queue-it-infra", "default_priority": "P3",
        "keywords": {"outage": 4.5, "server down": 4.5, "crash": 3.5, "error 500": 4.0, "502 bad gateway": 4.0, "vpn": 3.0, "database error": 4.0}
    },
    "Customer Success & Accounts": {
        "queue": "queue-customer-success", "default_priority": "P3",
        "keywords": {"enterprise plan": 3.5, "contract": 3.0, "onboarding": 3.0, "demo request": 3.0, "upgrade account": 3.0}
    }
}
DEFAULT_DEPARTMENT = "General Inquiries"
DEFAULT_QUEUE = "queue-triage-general"
DEFAULT_PRIORITY = "P4"
PRIORITY_KEYWORDS = {
    "P1": ["outage", "production down", "critical breach", "ransomware", "emergency", "critical", "exploit"],
    "P2": ["urgent", "error 500", "blocked", "vulnerability", "payment failure", "cannot login", "unauthorized"],
    "P3": ["slow", "latency", "question", "issue", "invoice update", "assistance needed"],
    "P4": ["feature suggestion", "minor typo", "cosmetic", "general inquiry", "how to", "hello"]
}
SLA_HOURS = {"P1": 1, "P2": 4, "P3": 12, "P4": 24}
VIP_DOMAINS = ["enterprise-client.com", "vip-corp.org", "strategic-partner.io"]
