from opticargo_agents.prompts import INTENT_PROMPT, SYSTEM_GUARDRAIL_PROMPT, SYNTHESIS_PROMPT


def test_prompts_define_core_agent_boundaries() -> None:
    assert "Never claim booking" in SYSTEM_GUARDRAIL_PROMPT
    assert "regulation" in INTENT_PROMPT
    assert "citations" in SYNTHESIS_PROMPT
