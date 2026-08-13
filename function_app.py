import json, time, azure.functions as func
from src.router.engine import router_instance
from src.router.models import TicketRequest

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

@app.route(route="health", methods=["GET"])
def health_check(req: func.HttpRequest) -> func.HttpResponse:
    return func.HttpResponse(json.dumps({"status": "healthy", "service": "serverless-ticket-router", "version": "1.0.0"}), status_code=200, mimetype="application/json")

@app.route(route="route_ticket", methods=["POST"])
def route_ticket_http(req: func.HttpRequest) -> func.HttpResponse:
    start = time.perf_counter()
    try:
        data = req.get_json()
        ticket_req = TicketRequest(**data)
        res = router_instance.route_ticket(ticket_req)
        return func.HttpResponse(json.dumps({
            "status": "success", "ticket_id": ticket_req.get_ticket_id(),
            "sender": ticket_req.sender, "subject": ticket_req.subject,
            "routing": res.dict(), "execution_time_ms": round((time.perf_counter() - start) * 1000, 2)
        }), status_code=200, mimetype="application/json")
    except Exception as e:
        return func.HttpResponse(json.dumps({"status": "error", "message": str(e)}), status_code=400, mimetype="application/json")
