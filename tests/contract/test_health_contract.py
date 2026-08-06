import inspect
import opticargo_agents.health as health_module

def test_health_response_schema():
    """Memastikan kontrak fungsi health (liveness/readiness) tersedia di health.py."""
    funcs = dict(inspect.getmembers(health_module, inspect.isfunction))
    
    has_health_func = any(
        "live" in k.lower() or "ready" in k.lower() or "health" in k.lower() 
        for k in funcs.keys()
    )
    assert has_health_func, "Contract bocor: Harus ada fungsi liveness/readiness di health.py"