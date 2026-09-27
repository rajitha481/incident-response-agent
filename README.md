# Incident Response Agent (powered by Hindsight)

An on-call incident response assistant that gets smarter over time. Instead of
generic troubleshooting advice, it recalls how *your team's own past incidents*
were diagnosed and fixed, using [Hindsight](https://github.com/vectorize-io/hindsight)
as its memory layer.

## Why memory matters here

Without memory, an LLM can only give generic advice ("check your connection
pool settings, check logs"). With Hindsight, the agent recalls the *exact*
root cause and fix from a similar incident your team has already resolved —
turning a 40-minute cold investigation into a 2-minute lookup.

## Architecture

```
Engineer describes incident
        |
        v
  Hindsight.recall()  --->  relevant past postmortems
        |
        v
  Groq (openai/gpt-oss-120b)  --->  grounded diagnosis + fix
        |
        v
  Streamlit UI
```

## Setup

1. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Copy `.env.example` to `.env` and fill in your keys:
   ```
   cp .env.example .env
   ```
   - `HINDSIGHT_API_KEY` — from your Hindsight Cloud dashboard
   - `GROQ_API_KEY` — from console.groq.com

3. Load the synthetic incident dataset into Hindsight memory:
   ```
   python retain_incidents.py
   ```

4. Run the agent:
   ```
   streamlit run app.py
   ```

## Demo flow

1. Toggle "Use Hindsight memory" **off**, submit an incident query — the agent
   gives generic, non-specific advice.
2. Toggle memory **on**, submit the same query — the agent recalls the exact
   past incident and gives a grounded, specific fix.

That before/after contrast is the core value proposition of memory-augmented
agents.

## Files

- `incidents.json` — synthetic postmortem dataset (service, error, root cause, fix)
- `retain_incidents.py` — loads the dataset into Hindsight via `retain()`
- `agent.py` — core logic: `recall()` from Hindsight + Groq for the diagnosis
- `app.py` — Streamlit UI

## Links

- [Hindsight GitHub](https://github.com/vectorize-io/hindsight)
- [Hindsight Docs](https://hindsight.vectorize.io/)
- [Vectorize agent memory](https://vectorize.io/what-is-agent-memory)
