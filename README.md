# ⚡ Serverless Ticket Routing & Batch Analytics Engine

[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/downloads/)
[![Azure Functions](https://img.shields.io/badge/Azure%20Functions-Python%20v2-0078D4.svg)](https://learn.microsoft.com/azure/azure-functions/)
[![Apache Spark](https://img.shields.io/badge/Apache%20Spark-3.4+-E25A1C.svg)](https://spark.apache.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![OWASP Serverless](https://img.shields.io/badge/Security-OWASP%20Serverless%20Aligned-green.svg)](https://owasp.org/)

An enterprise-grade, dual-engine customer support ticket routing platform built with **Python**, **Azure Functions (Serverless)**, and **Apache Spark (PySpark)**.

Designed to handle real-time HTTP ingestion with sub-millisecond classification latency while scaling to distributed batch analytics across large historical ticket archives.

---

## 🌐 Live Azure Endpoints

* **Health Check (`GET`):** `https://fn-ticket-router-elazar-01.azurewebsites.net/api/health`
* **Ticket Routing API (`POST`):** `https://fn-ticket-router-elazar-01.azurewebsites.net/api/route_ticket`

---

## 📐 System Architecture & Data Flow

```mermaid
graph LR
    subgraph Ingress & Compute
        Client[HTTP Client / Service Desk] -->|POST /api/route_ticket| AzFunc[Azure Function Python v2]
        AzFunc --> Auth[Managed Identity / App Key]
    end

    subgraph Core Processing Engine
        AzFunc --> RegEx[Weighted RegEx Classifier<br/>2x Subject Weight]
        AzFunc --> SLA[Dynamic SLA & VIP Escalation]
        AzFunc --> Entity[Entity Extractor<br/>CVEs, HTTP 500/502]
    end

    subgraph Egress & Observability
        RegEx --> Queue[(Functional Queues<br/>SecOps / Infra / Billing)]
        AzFunc --> Log[Structured JSON UTC Logs]
        Log --> Insights[Azure Application Insights]
    end

    subgraph Batch Layer
        Archive[(Ticket Lake / Blob Storage)] --> Spark[PySpark Batch Engine<br/>spark_router.py]
        Spark --> Metrics[Historical KPI & SLA Analytics]
    end
