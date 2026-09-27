"""
Core incident response agent logic.

diagnose_incident(query, use_memory=True) -> (answer, recalled_memories)

When use_memory=False, the agent answers cold, with no Hindsight recall,
so you can show the "before memory" generic response in your demo.
When use_memory=True, it recalls similar past incidents from Hindsight
and grounds its answer in them -- the "after memory" response.
"""
import os

from dotenv import load_dotenv
from groq import Groq
from hindsight_client import Hindsight

load_dotenv()

HINDSIGHT_API_KEY = os.environ["HINDSIGHT_API_KEY"]
HINDSIGHT_BASE_URL = os.environ.get("HINDSIGHT_BASE_URL", "https://api.hindsight.vectorize.io")
BANK_ID = os.environ.get("HINDSIGHT_BANK_ID", "incident-response-agent")

GROQ_API_KEY = os.environ["GROQ_API_KEY"]
GROQ_MODEL = os.environ.get("GROQ_MODEL", "openai/gpt-oss-120b")

SYSTEM_PROMPT = """You are an on-call incident response assistant for a software \
engineering team. An engineer will describe a production incident. Give a clear, \
concise, actionable response: likely root cause and concrete next steps to try. \
If you are given context from past incidents, ground your answer in that context \
explicitly and mention it was based on a similar past incident. If you have no \
past incident context, give your best generic troubleshooting guidance and say \
plainly that this is generic advice, not based on prior incident history."""


def _get_hindsight_client() -> Hindsight:
    return Hindsight(base_url=HINDSIGHT_BASE_URL, api_key=HINDSIGHT_API_KEY)


def _get_groq_client() -> Groq:
    return Groq(api_key=GROQ_API_KEY)


def diagnose_incident(query: str, use_memory: bool = True):
    """
    Returns a tuple: (answer_text, list_of_recalled_memory_strings)
    """
    recalled_memories = []
    context_block = ""

    if use_memory:
        hindsight = _get_hindsight_client()
        try:
            result = hindsight.recall(bank_id=BANK_ID, query=query)
            recalled_memories = [m.text for m in result.results][:5]
        finally:
            hindsight.close()

        if recalled_memories:
            context_block = (
                "Relevant past incidents recalled from memory:\n\n"
                + "\n\n---\n\n".join(recalled_memories)
            )

    user_content = query
    if context_block:
        user_content = f"{context_block}\n\nNew incident to diagnose:\n{query}"

    groq_client = _get_groq_client()
    response = groq_client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_content},
        ],
        temperature=0.3,
    )
    answer = response.choices[0].message.content
    return answer, recalled_memories


def get_pattern_insight(service_or_topic: str) -> str:
    """
    Uses Hindsight's reflect() to surface a higher-level pattern across
    multiple past incidents, rather than just retrieving one memory.
    This is the "the agent is learning, not just storing" moment for the demo:
    e.g. "payments-service has had 2 Redis-related incidents this month,
    both connection-related but with different root causes."
    """
    hindsight = _get_hindsight_client()
    try:
        response = hindsight.reflect(
            bank_id=BANK_ID,
            query=(
                f"What patterns or recurring issues do you see across past incidents "
                f"related to '{service_or_topic}'? Call out anything that suggests a "
                f"systemic issue rather than a one-off, and give one recommendation "
                f"a team could act on."
            ),
        )
        return response.text
    finally:
        hindsight.close()


if __name__ == "__main__":
    # Quick CLI test
    test_query = "redis.exceptions.ConnectionError in payments-service, connection refused"

    print("=== WITHOUT MEMORY (cold) ===")
    answer_cold, _ = diagnose_incident(test_query, use_memory=False)
    print(answer_cold)

    print("\n=== WITH MEMORY (recall) ===")
    answer_warm, memories = diagnose_incident(test_query, use_memory=True)
    print(f"Recalled {len(memories)} past incidents.")
    print(answer_warm)
