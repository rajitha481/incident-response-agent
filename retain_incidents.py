"""
Loads synthetic incident postmortems into Hindsight memory.

Run this once (or whenever you add new incidents) to populate your
memory bank before demoing the agent:

    python retain_incidents.py
"""
import json
import os
import time

from dotenv import load_dotenv
from hindsight_client import Hindsight

load_dotenv()

HINDSIGHT_API_KEY = os.environ["HINDSIGHT_API_KEY"]
HINDSIGHT_BASE_URL = os.environ.get("HINDSIGHT_BASE_URL", "https://api.hindsight.vectorize.io")
BANK_ID = os.environ.get("HINDSIGHT_BANK_ID", "incident-response-agent")


def format_incident(incident: dict) -> str:
    """Turn a structured incident record into a natural-language memory."""
    return (
        f"Incident postmortem for {incident['service']}.\n"
        f"Error observed: {incident['error']}\n"
        f"Root cause: {incident['root_cause']}\n"
        f"Fix applied: {incident['fix']}\n"
        f"Resolution time: {incident['resolution_minutes']} minutes."
    )


def main():
    client = Hindsight(base_url=HINDSIGHT_BASE_URL, api_key=HINDSIGHT_API_KEY)

    # Create the bank if it doesn't exist yet (safe to call repeatedly)
    try:
        client.create_bank(
            bank_id=BANK_ID,
            name="Incident Response Agent",
            background=(
                "This agent helps on-call engineers resolve production incidents "
                "faster by recalling how similar past incidents were diagnosed and fixed."
            ),
        )
        print(f"Created memory bank: {BANK_ID}")
    except Exception as e:
        print(f"Bank may already exist, continuing. ({e})")

    with open("incidents.json") as f:
        incidents = json.load(f)

    for i, incident in enumerate(incidents, start=1):
        memory_text = format_incident(incident)
        client.retain(bank_id=BANK_ID, content=memory_text)
        print(f"[{i}/{len(incidents)}] Retained: {incident['service']} - {incident['error'][:60]}...")
        time.sleep(0.3)  # be gentle on rate limits

    print("\nDone. All incidents retained into Hindsight memory.")
    client.close()


if __name__ == "__main__":
    main()
