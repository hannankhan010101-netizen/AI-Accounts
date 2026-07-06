"""AI intelligence layer — provider abstraction, prompts, context, governance.

This package evolves the single-provider assistant into a modular, swappable,
governed AI substrate. Phase 1 introduces the provider abstraction so Claude,
Groq, and OpenAI-compatible models sit behind one event-dict streaming contract
(the same contract ``services/assistant/orchestrator.py`` already consumes).
"""
