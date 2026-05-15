"""Agent core tests."""
import pytest
from gather.agent.budget import IterationBudget
from gather.agent.router import ModelRouter, RouteDecision
def test_budget_remaining():
    budget = IterationBudget(max_iterations=5)
    assert budget.remaining() is True
    for _ in range(5): budget.record_iteration()
    assert budget.remaining() is False
def test_budget_grace_call():
    budget = IterationBudget(max_iterations=1, grace_call_enabled=True)
    budget.record_iteration()
    assert budget.remaining() is False
    assert budget.should_grace_call() is True
    budget.mark_grace_call_used()
    assert budget.should_grace_call() is False
def test_router_default():
    router = ModelRouter(config={"model": {"default": "gpt-4o", "provider": "openai"}})
    route = router.route(messages=[{"role": "user", "content": "hello"}])
    assert route.model == "gpt-4o"
    assert route.provider == "openai"
def test_router_failover():
    router = ModelRouter(config={"model": {"default": "gpt-4o", "provider": "openai", "failover": {"chain": ["openai", "anthropic", "openrouter"]}}})
    failed = RouteDecision(model="gpt-4o", provider="openai", failover_chain=["openai", "anthropic", "openrouter"])
    next_route = router.failover(failed, RuntimeError("test error"))
    assert next_route is not None
    assert next_route.provider == "anthropic"
def test_router_failover_exhausted():
    router = ModelRouter(config={"model": {"default": "gpt-4o", "provider": "openai", "failover": {"chain": ["openai"]}}})
    failed = RouteDecision(model="gpt-4o", provider="openai", failover_chain=["openai"])
    assert router.failover(failed, RuntimeError("test")) is None
