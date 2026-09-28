# Pulse — Support that remembers. Intelligence that notices.

Pulse is a Hindsight-powered customer support intelligence agent.

It remembers a customer's troubleshooting journey, retrieves relevant prior experience, and identifies recurring issues across customers. The demo focuses on one workflow: a returning customer reports a payment failure, Pulse recalls what was already tried and connects it to a broader emerging pattern.

## Hindsight
- Retain: stores support interactions and resolutions.
- Recall: retrieves relevant customer and organization memories.
- Reflect: synthesizes a support recommendation from accumulated experience.

## Run
1. Create a Hindsight Cloud memory bank and API key.
2. Copy `.env.example` to `.env` and add the key.
3. `python -m pip install -r requirements.txt`
4. `streamlit run app.py`

Synthetic demo data is used; no real customer data is included.
