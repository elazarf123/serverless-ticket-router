# Serverless Ticket Router

An Azure Functions (Python v2 programming model) HTTP API that reads an incoming support ticket and decides where it goes: which department queue, what priority, and what SLA. Routing uses weighted keyword scoring, so the logic is transparent and easy to tune.

## What it does

For each ticket (`sender`, `subject`, `body`) the router:

1. **Scores departments.** Each department has weighted keywords. A keyword match in the subject counts double; a match in the body counts once. The highest score wins, with a confidence score between 0.25 and 0.99. No match sends the ticket to `General Inquiries`.
2. **Sets priority (P1–P4).** Urgent phrases (for example `outage`, `ransomware`, `error 500`, `cannot login`) force P1 or P2 and mark the ticket escalated. Otherwise the department's default priority applies. Senders from configured VIP domains are raised to at least P2. A `priority_override` in the request wins over all of this.
3. **Assigns an SLA** from the priority: P1 = 1 h, P2 = 4 h, P3 = 12 h, P4 = 24 h.
4. **Tags the ticket** with any CVE IDs and HTTP 4xx/5xx status codes found in the text, plus `ESCALATED` and `VIP-CUSTOMER` where they apply.

| Department | Queue | Default priority |
| :--- | :--- | :--- |
| Security & Compliance | `queue-secops` | P2 |
| IT Support & Infrastructure | `queue-it-infra` | P3 |
| Billing & Finance | `queue-billing` | P3 |
| Customer Success & Accounts | `queue-customer-success` | P3 |
| General Inquiries (fallback) | `queue-triage-general` | P4 |

All rules live in [`src/router/config.py`](src/router/config.py).

## Endpoints

| Method | Route | Purpose |
| :--- | :--- | :--- |
| `GET` | `/api/health` | Health check |
| `POST` | `/api/route_ticket` | Route one ticket |

### Example

Request:

```json
{
  "ticket_id": "TICK-1001",
  "sender": "user@example.com",
  "subject": "Server down after patch",
  "body": "Users get error 500 on the portal since this morning. Possibly related to CVE-2099-0001."
}
```

Routing result (the `routing` object in the response; `routed_at` will be the current time):

```json
{
  "department": "IT Support & Infrastructure",
  "queue": "queue-it-infra",
  "priority": "P2",
  "sla_hours": 4,
  "confidence_score": 0.76,
  "matched_keywords": ["error 500", "server down"],
  "is_escalated": true,
  "tags": ["CVE-2099-0001", "HTTP-500", "ESCALATED"],
  "routed_at": "2026-09-29T20:15:00+00:00"
}
```

The full response also includes `status`, `ticket_id`, `sender`, `subject`, and `execution_time_ms`. Invalid input returns HTTP 400 with an error message.

## Project structure

```text
function_app.py            # Azure Functions HTTP triggers (health, route_ticket)
host.json                  # Functions host configuration
requirements.txt           # azure-functions, pydantic, pyspark
src/router/config.py       # Departments, keyword weights, priority keywords, SLAs, VIP domains
src/router/engine.py       # TicketRouter: department scoring, priority, tags
src/router/models.py       # Pydantic request/response models
src/utils/logger.py        # JSON log formatter
src/spark/spark_router.py  # Starter PySpark batch job (currently loads and previews a JSON file)
```

## Run locally

Requires Python 3.9+ and [Azure Functions Core Tools v4](https://learn.microsoft.com/azure/azure-functions/functions-run-local).

```bash
git clone https://github.com/elazarf123/serverless-ticket-router.git
cd serverless-ticket-router
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
func start
```

Then send a ticket:

```bash
curl -X POST http://localhost:7071/api/route_ticket \
  -H "Content-Type: application/json" \
  -d '{"sender":"user@example.com","subject":"VPN not connecting","body":"Cannot login to VPN from home."}'
```

## Roadmap

- Unit tests for scoring, priority, and tagging
- Finish the PySpark batch job so it routes a file of tickets and writes the results
- Load routing rules from a config file or storage instead of code
