# Serverless Ticket Router

![Status: in progress](https://img.shields.io/badge/status-in%20progress-yellow)

An Azure Functions HTTP API that reads a support ticket and decides its department queue, priority (P1–P4), and SLA, so urgent issues reach the right team without manual triage.

## Results

**Sample output (illustrative).** This is the routing result for the example ticket below; it is also checked by [`tests/test_engine.py`](tests/test_engine.py).

Request:

```json
{
  "ticket_id": "TICK-1001",
  "sender": "user@example.com",
  "subject": "Server down after patch",
  "body": "Users get error 500 on the portal since this morning. Possibly related to CVE-2099-0001."
}
```

| Field | Value |
| :--- | :--- |
| Department / queue | IT Support & Infrastructure / `queue-it-infra` |
| Priority / SLA | P2 / 4 hours (escalated by "error 500") |
| Confidence | 0.76 |
| Matched keywords | `server down`, `error 500` |
| Tags | `CVE-2099-0001`, `HTTP-500`, `ESCALATED` |

## How it works

- **Department scoring:** each department has weighted keywords; a match in the subject counts double, a match in the body counts once. No match goes to `General Inquiries`.
- **Priority:** urgent phrases (for example `outage`, `ransomware`, `error 500`, `cannot login`) force P1 or P2 and mark the ticket escalated; otherwise the department default applies. VIP sender domains are raised to at least P2, and `priority_override` wins over everything.
- **SLA:** P1 = 1 h, P2 = 4 h, P3 = 12 h, P4 = 24 h.
- **Tags:** CVE IDs and HTTP 4xx/5xx codes found in the text, plus `ESCALATED` and `VIP-CUSTOMER`.
- **Endpoints:** `GET /api/health` and `POST /api/route_ticket` ([`function_app.py`](function_app.py)). All rules live in [`src/router/config.py`](src/router/config.py).

## Tech stack

Python 3.9+ · Azure Functions (v2 programming model) · Pydantic · pytest

## Run it

```bash
git clone https://github.com/elazarf123/serverless-ticket-router.git
cd serverless-ticket-router
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\Activate.ps1
pip install -r requirements.txt -r requirements-dev.txt

pytest                             # 6 unit tests for scoring, priority, and tagging
func start                         # needs Azure Functions Core Tools v4
```

Then send a ticket:

```bash
curl -X POST http://localhost:7071/api/route_ticket \
  -H "Content-Type: application/json" \
  -d '{"sender":"user@example.com","subject":"VPN not connecting","body":"Cannot login to VPN from home."}'
```

## What I learned

- Keyword scoring is easy to explain and tune, which matters when a support team has to trust the routing.
- Word-boundary matching needs care: `CVE-2099-0001` also matches the `cve` keyword, which nudges the Security score.
- Unit tests pinned the README example, so the docs and the code can't drift apart.

## Roadmap

- Finish the PySpark batch job ([`src/spark/spark_router.py`](src/spark/spark_router.py)) so it routes a file of tickets; today it only loads and previews a JSON file
- Load routing rules from a config file or storage instead of code

> Lab use only. Status: in progress.
