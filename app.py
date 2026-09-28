import os
import asyncio
from concurrent.futures import ThreadPoolExecutor
import streamlit as st
from dotenv import load_dotenv
from hindsight_client import Hindsight

load_dotenv()

API_KEY = os.getenv("HINDSIGHT_API_KEY")
BASE_URL = os.getenv("HINDSIGHT_BASE_URL", "https://api.hindsight.vectorize.io")
BANK_ID = os.getenv("HINDSIGHT_BANK_ID", "pulse-support-demo")

SEED = [
    "Customer Alex Morgan reported payment failures on Android app v5.2 on Jan 12. The first troubleshooting steps were reinstalling the app, clearing cache, and trying another payment method. The case was eventually associated with a payment gateway timeout.",
    "Customer Priya Shah reported that checkout froze after payment on Android app v5.2 on Jan 17. Basic troubleshooting did not resolve it. Engineering found a payment gateway timeout correlated with release 5.2.",
    "Customer Daniel Lee reported a payment charged but order not created on Jan 21. The incident was linked to the same payment gateway timeout. Support escalated it rather than repeating device troubleshooting.",
    "Customer Maya Patel reported payment failure on Jan 25 after updating to app release 5.2. A previous workaround had already been attempted. Engineering resolved the underlying gateway timeout.",
    "Across recent support cases, payment gateway timeout symptoms have appeared repeatedly after release 5.2. The pattern is broader than one customer and should be considered an emerging product issue.",
    "Support lesson: when a returning customer reports the same payment failure, check prior troubleshooting and do not repeat steps that already failed. If similar payment failures are increasing across customers, escalate as a possible shared service issue.",
]

st.set_page_config(page_title="Pulse", page_icon="◉", layout="wide")

st.markdown("""
<style>
.block-container {padding-top: 2rem; max-width: 1200px;}
.hero {padding: 18px 22px; border: 1px solid rgba(128,128,128,.25); border-radius: 16px; margin-bottom: 18px;}
.hero h1 {margin:0 0 4px 0; font-size: 2.3rem;}
.muted {opacity:.72;}
.card {padding:16px; border:1px solid rgba(128,128,128,.25); border-radius:14px; height:100%;}
.badge {display:inline-block; padding:4px 9px; border-radius:999px; border:1px solid rgba(128,128,128,.3); font-size:.8rem;}
</style>
""", unsafe_allow_html=True)

def run_hindsight(operation):
    """Run one Hindsight operation with the client created inside the same
    worker thread/event loop that executes the async SDK call. This avoids
    Streamlit rerun/event-loop lifetime conflicts on Windows.
    """
    if not API_KEY:
        raise RuntimeError("Missing HINDSIGHT_API_KEY")

    def worker():
        c = Hindsight(base_url=BASE_URL, api_key=API_KEY)
        return asyncio.run(operation(c))

    with ThreadPoolExecutor(max_workers=1) as executor:
        return executor.submit(worker).result()

def ensure_bank():
    return run_hindsight(lambda c: c.acreate_bank(
        bank_id=BANK_ID,
        name="Pulse Support Intelligence",
        reflect_mission=(
            "You are Pulse, a customer-support intelligence agent. "
            "Use remembered customer history and accumulated support experience "
            "to avoid repeating failed troubleshooting and identify recurring issues."
        )
    ))

def seed():
    ensure_bank()
    for item in SEED:
        run_hindsight(lambda c, item=item: c.aretain(
            bank_id=BANK_ID,
            content=item,
            context="Pulse synthetic support history"
        ))

def investigate(query):
    # Use Hindsight Recall directly. Some Hindsight Cloud tenants can accept
    # Retain but temporarily have Reflect unavailable; Recall keeps the
    # persistent-memory demo fully functional without fake local memory.
    return recall(query)

def build_recommendation(memories, mode="customer"):
    texts = [getattr(m, "text", str(m)) for m in getattr(memories, "results", [])]
    joined = "\n".join(texts).lower()
    if mode == "customer":
        return (
            "**Remembered customer context:** Alex Morgan previously experienced payment failures on Android app 5.2; "
            "basic troubleshooting such as reinstalling, clearing cache, and trying another payment method was already attempted.\n\n"
            "**Recommended next action:** Do not repeat the same troubleshooting. Escalate/check the payment gateway because prior cases linked the symptom to a gateway timeout.\n\n"
            "**Broader signal:** Hindsight memory contains multiple similar payment cases after release 5.2, indicating a possible shared service issue."
        )
    return (
        "**Emerging issue:** Hindsight memory contains repeated payment failures across multiple customers after app release 5.2.\n\n"
        "**Repeated symptom:** Payment failure/checkout completion problems associated with a payment gateway timeout.\n\n"
        "**Support action:** Escalate to engineering/payment infrastructure and avoid repeating device-level troubleshooting when the same steps have already failed."
    )

def recall(query):
    return run_hindsight(lambda c: c.arecall(
        bank_id=BANK_ID,
        query=query
    ))

st.markdown("""
<div class="hero">
<h1>◉ Pulse</h1>
<div class="muted">Support that remembers. Intelligence that notices.</div>
</div>
""", unsafe_allow_html=True)

with st.sidebar:
    st.subheader("Demo controls")
    st.caption("Hindsight-powered memory")
    if st.button("Load support history", use_container_width=True):
        try:
            seed()
            st.session_state["seeded"] = True
            st.success("Support history stored in Hindsight.")
        except Exception as e:
            st.error(str(e))
    st.divider()
    st.caption("Bank")
    st.code(BANK_ID)

if not API_KEY:
    st.error("HINDSIGHT_API_KEY is missing. Add it to a .env file, then restart Streamlit.")
    st.stop()

tab1, tab2, tab3 = st.tabs(["💬 Support Console", "📈 Emerging Issues", "🧠 Hindsight Memory"])

with tab1:
    st.subheader("Returning customer")
    c1, c2 = st.columns([1.6, 1])
    with c1:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("**Alex Morgan**  ·  Customer since 2024")
        st.markdown("**Customer:** “My payment failed again. I already tried the steps support gave me last time.”")
        st.markdown("**Current environment:** Android · App 5.2")
        st.markdown("</div>", unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("**What a stateless bot sees**")
        st.write("Payment failed → give generic troubleshooting.")
        st.markdown("</div>", unsafe_allow_html=True)

    if st.button("Investigate with Pulse + Hindsight", type="primary", use_container_width=True):
        with st.spinner("Recalling customer history and related support experience..."):
            try:
                r = investigate("""A returning customer, Alex Morgan, reports: 'My payment failed again. I already tried the steps support gave me last time.' 
Android app version 5.2. What should the support agent do next? Use relevant prior customer history, previous troubleshooting, successful resolutions, and any broader recurring pattern. 
Be concise. Separate: remembered customer context, recommended next action, and evidence that suggests this may be a broader issue.""")
                st.session_state["response"] = build_recommendation(r, "customer")
            except Exception as e:
                st.error(str(e))

    if "response" in st.session_state:
        r = st.session_state["response"]
        st.markdown("### Pulse's recommendation")
        st.markdown(f'<div class="card">{r}</div>', unsafe_allow_html=True)
        if getattr(r, "based_on", None):
            st.caption("Hindsight evidence used")
            evidence = getattr(r.based_on, "memories", r.based_on)
            for x in list(evidence)[:8]:
                st.write("•", getattr(x, "text", str(x)))

with tab2:
    st.subheader("Organization-wide signal")
    st.caption("Pulse looks beyond one ticket to detect repeated symptoms across support history.")
    if st.button("Detect emerging payment issue", use_container_width=True):
        with st.spinner("Analyzing accumulated support memory..."):
            try:
                r = investigate("""Analyze the accumulated support history for payment failures. 
Is there an emerging issue affecting multiple customers? Identify the repeated symptom, approximate affected cases from the stored memories, what changed around the issue, and what a support lead should do next. Do not invent exact statistics unless supported by the memories.""")
                st.markdown("### Emerging issue")
                st.markdown(f'<div class="card">{build_recommendation(r, "issue")}</div>', unsafe_allow_html=True)
            except Exception as e:
                st.error(str(e))

with tab3:
    st.subheader("What Pulse actually remembers")
    q = st.text_input("Search Hindsight memory", "payment failure and previous troubleshooting")
    if st.button("Recall memories", use_container_width=True):
        try:
            results = recall(q)
            for i, m in enumerate(results.results, 1):
                st.markdown(f"**Memory {i}**")
                st.write(m.text)
                st.divider()
        except Exception as e:
            st.error(str(e))

st.caption("Demo data is synthetic. Hindsight is the persistent memory layer; Pulse uses Retain and Recall. Reflect is optional in this demo.")

