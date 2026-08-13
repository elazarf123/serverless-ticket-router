# ⚡ Serverless Ticket Routing & Batch Analytics Engine

[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/downloads/)
[![Azure Functions](https://img.shields.io/badge/Azure%20Functions-Python%20v2-0078D4.svg)](https://learn.microsoft.com/azure/azure-functions/)
[![Apache Spark](https://img.shields.io/badge/Apache%20Spark-3.4+-E25A1C.svg)](https://spark.apache.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

An enterprise-grade, dual-engine customer support ticket routing platform built with **Python**, **Azure Functions (Serverless)**, and **Apache Spark (PySpark)**.

Designed to handle real-time HTTP ingestion with sub-millisecond classification latency while scaling to batch analytics across large volumes of support tickets.

---

## 🌐 Live Azure Endpoints

- **Health Check (`GET`)**: `https://fn-ticket-router-elazar-01.azurewebsites.net/api/health`
- **Ticket Routing API (`POST`)**: `https://fn-ticket-router-elazar-01.azurewebsites.net/api/route_ticket`

---

## 🚀 Architecture & Core Features

- **⚡ Serverless Real-Time Compute**: Hosted on Azure Functions (Linux Consumption), ensuring rapid sub-second response times and automated scaling.
- **🎯 Weighted RegEx Department Classification**: Evaluates message subject lines (2x weight multiplier) and body text against pre-compiled regex pattern dictionaries:
  - *Security & Compliance* (`queue-secops` — CVE detection, vulnerabilities, exploits)
  - *Billing & Finance* (`queue-billing` — Invoices, refunds, chargebacks)
  - *IT Support & Infrastructure* (`queue-it-infra` — Outages, 500/502 errors, VPN, database timeouts)
  - *Customer Success & Accounts* (`queue-customer-success` — Enterprise contracts, onboarding)
- **🚨 Dynamic Priority & SLA Escalation**: Detects critical operational triggers (P1: 1-hour SLA, P2: 4-hour SLA) and checks for **VIP Customer Domains** (e.g., `@enterprise-client.com`) to elevate tickets automatically.
- **🔍 Technical Entity Extraction**: Identifies and tags CVE reference codes (`CVE-YYYY-NNNN`), HTTP error codes (`500`, `502`), and incident IDs from raw ticket text.
- **📊 Distributed PySpark Batch Engine**: Includes a dedicated batch pipeline (`spark_router.py`) to process large historical ticket archives and compute KPI metrics.
- **📝 Structured JSON Logging**: Emits UTC-timestamped JSON logs formatted for Azure Application Insights observability.

---

## 🚦 Department & SLA Matrix

| Department | Target Queue | Default Priority | Target SLA | Sample Trigger Keywords |
| :--- | :--- | :---: | :---: | :--- |
| **Security & Compliance** | `queue-secops` | **P2** | **1 – 4 hrs** | `vulnerability`, `breach`, `cve`, `exploit`, `unauthorized`, `ransomware` |
| **Billing & Finance** | `queue-billing` | **P3** | **12 hrs** | `invoice`, `refund`, `overcharge`, `subscription`, `credit card`, `pricing` |
| **IT Support & Infrastructure** | `queue-it-infra` | **P3** | **12 hrs** | `outage`, `server down`, `crash`, `error 500`, `database error`, `vpn`, `timeout` |
| **Customer Success & Accounts** | `queue-customer-success` | **P3** | **12 hrs** | `enterprise plan`, `contract`, `onboarding`, `upgrade account`, `renewal` |
| **General Inquiries** | `queue-triage-general` | **P4** | **24 hrs** | *Fallback default for routine feedback and general inquiries* |

*Note: Any ticket from a registered VIP domain (e.g., `@enterprise-client.com`) automatically receives a 1-tier priority bump and an `ESCALATED` tag.*

---

## 🧪 Testing the Live API

### 1. Health Check
```bash
curl [https://fn-ticket-router-elazar-01.azurewebsites.net/api/health](https://fn-ticket-router-elazar-01.azurewebsites.net/api/health)
