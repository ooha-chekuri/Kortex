"""
Unit tests for Kortex agents.
"""

import pytest
from backend.agents.triage_agent import classify_intent
from backend.agents.retrieval_agent import RetrievalAgent
from backend.agents.ticket_agent import TicketAgent
from backend.core.confidence import compute_confidence, decide_action


class TestTriageAgent:
    """Tests for Triage Agent."""

    def test_classify_docs_intent(self):
        """Test document-only queries."""
        assert classify_intent("How do I configure Kafka?") in ["docs", "both"]
        assert classify_intent("What is the setup guide?") in ["docs", "both"]

    def test_classify_tickets_intent(self):
        """Test ticket-only queries."""
        result = classify_intent("What past incidents mention auth errors?")
        assert result in ["tickets", "both"]

    def test_classify_both_intent(self):
        """Test queries needing both docs and tickets."""
        result = classify_intent("How do I fix the VPN error from yesterday?")
        assert result in ["docs", "tickets", "both"]


class TestConfidence:
    """Tests for confidence computation."""

    def test_high_confidence(self):
        """Test high confidence calculation."""
        confidence = compute_confidence(0.9, 0.9, 0.9)
        assert confidence > 0.75
        assert decide_action(confidence) == "respond"

    def test_low_confidence(self):
        """Test low confidence calculation."""
        confidence = compute_confidence(0.2, 0.2, 0.2)
        assert confidence < 0.5
        assert decide_action(confidence) == "escalate"

    def test_retry_confidence(self):
        """Test retry-range confidence."""
        confidence = compute_confidence(0.6, 0.6, 0.6)
        assert 0.5 <= confidence <= 0.75
        assert decide_action(confidence) == "retry"

    def test_boundary_above_respond(self):
        """Test boundary above respond threshold."""
        confidence = compute_confidence(0.8, 0.8, 0.8)
        assert decide_action(confidence) == "respond"

    def test_boundary_at_respond_threshold(self):
        """Test boundary at respond threshold."""
        confidence = compute_confidence(0.76, 0.76, 0.76)
        assert decide_action(confidence) == "respond"

    def test_boundary_retry_threshold(self):
        """Test boundary at retry threshold."""
        confidence = compute_confidence(0.5, 0.5, 0.5)
        assert decide_action(confidence) == "retry"


class TestRetrievalAgent:
    """Tests for Retrieval Agent."""

    def test_retrieval_agent_init(self):
        """Test RetrievalAgent initialization."""
        agent = RetrievalAgent()
        assert agent is not None

    def test_retrieval_agent_search(self):
        """Test search returns list."""
        agent = RetrievalAgent()
        results = agent.search("Kafka", top_k=3)
        assert isinstance(results, list)


class TestTicketAgent:
    """Tests for Ticket Agent."""

    def test_ticket_agent_init(self):
        """Test TicketAgent initialization."""
        agent = TicketAgent()
        assert agent is not None

    def test_ticket_agent_search(self):
        """Test search returns list."""
        agent = TicketAgent()
        results = agent.search("VPN error", top_k=3)
        assert isinstance(results, list)


class TestMainAPI:
    """Tests for FastAPI endpoints."""

    def test_health_endpoint(self):
        """Test health check endpoint."""
        from fastapi.testclient import TestClient
        from backend.main import app

        client = TestClient(app)
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
