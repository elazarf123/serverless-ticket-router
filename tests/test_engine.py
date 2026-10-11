from src.router.engine import TicketRouter
from src.router.models import TicketRequest

router = TicketRouter()


def route(subject, body, sender="user@example.com", override=None):
    return router.route_ticket(
        TicketRequest(sender=sender, subject=subject, body=body, priority_override=override)
    )


def test_subject_match_counts_double():
    # "invoice" (3.0) in the subject scores 6.0 for Billing and beats
    # "vpn" (3.0) in the body for IT Support.
    dept, queue, confidence, keywords = router.calculate_department("Invoice copy", "Sent from my vpn")
    assert dept == "Billing & Finance"
    assert queue == "queue-billing"
    assert confidence == round(6.0 / 10.0, 2)
    assert keywords == ["invoice"]


def test_no_keywords_falls_back_to_general_queue():
    result = route("Hi there", "Just checking in")
    assert result.department == "General Inquiries"
    assert result.queue == "queue-triage-general"
    assert result.priority == "P4"
    assert result.sla_hours == 24
    assert result.confidence_score == 0.0


def test_urgent_phrase_forces_p1_and_escalates():
    result = route("Files encrypted", "Looks like ransomware on the file server")
    assert result.department == "Security & Compliance"
    assert result.priority == "P1"
    assert result.sla_hours == 1
    assert result.is_escalated
    assert "ESCALATED" in result.tags


def test_vip_sender_raised_to_p2_and_override_wins():
    vip = route("Invoice copy", "Please resend", sender="cfo@enterprise-client.com")
    assert vip.priority == "P2"
    assert "VIP-CUSTOMER" in vip.tags

    overridden = route("Invoice copy", "Please resend", sender="cfo@enterprise-client.com", override="P4")
    assert overridden.priority == "P4"
    assert overridden.sla_hours == 24


def test_tags_cve_ids_and_http_status_codes():
    tags = router.extract_tags("Saw cve-2024-12345 and a 502 then a 404, port 8080 is fine")
    assert tags == ["CVE-2024-12345", "HTTP-404", "HTTP-502"]


def test_readme_example():
    result = route(
        "Server down after patch",
        "Users get error 500 on the portal since this morning. Possibly related to CVE-2099-0001.",
    )
    assert result.department == "IT Support & Infrastructure"
    assert result.priority == "P2"
    assert result.sla_hours == 4
    assert result.confidence_score == 0.76
    assert sorted(result.matched_keywords) == ["error 500", "server down"]
    assert result.tags == ["CVE-2099-0001", "HTTP-500", "ESCALATED"]
