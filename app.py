"""
Streamlit demo UI for the Hindsight-powered Incident Response Agent.

Run with:
    streamlit run app.py
"""
import streamlit as st

from agent import diagnose_incident, get_pattern_insight

st.set_page_config(page_title="Incident Response Agent", page_icon="🚨", layout="centered")

st.title("🚨 Incident Response Agent")
st.caption("Powered by Hindsight memory — recalls how past incidents were resolved.")

use_memory = st.toggle("Use Hindsight memory", value=True, help="Turn off to see the generic, memory-less response.")

query = st.text_area(
    "Describe the incident",
    placeholder="e.g. redis.exceptions.ConnectionError in payments-service, connection refused",
    height=100,
)

if st.button("Diagnose", type="primary") and query.strip():
    with st.spinner("Thinking..."):
        answer, recalled_memories = diagnose_incident(query, use_memory=use_memory)

    if use_memory:
        if recalled_memories:
            st.success(f"Recalled {len(recalled_memories)} similar past incident(s) from memory")
            with st.expander("View recalled memories"):
                for i, mem in enumerate(recalled_memories, start=1):
                    st.markdown(f"**Memory {i}:**")
                    st.text(mem)
        else:
            st.info("No relevant past incidents found in memory for this query.")
    else:
        st.warning("Memory disabled — this is a generic, non-grounded response.")

    st.markdown("### Suggested diagnosis")
    st.markdown(answer)

st.divider()

st.subheader("🔍 Spot a recurring pattern")
st.caption("This goes beyond a single recall — it asks Hindsight to reflect across ALL past incidents for a service and surface systemic issues.")

pattern_topic = st.text_input("Service or topic to analyze", placeholder="e.g. payments-service, redis, auth-service")

if st.button("Find patterns") and pattern_topic.strip():
    with st.spinner("Reflecting across past incidents..."):
        insight = get_pattern_insight(pattern_topic)
    st.markdown("### Pattern insight")
    st.markdown(insight)

st.divider()
st.caption(
    "Tip for the demo: toggle memory off first to show the generic response, "
    "then toggle it on to show the agent recall a real past fix. Then use "
    "'Find patterns' on 'payments-service' or 'redis' to show it noticing "
    "the SAME service had 2 separate Redis incidents — that's the moment "
    "that makes memory feel like more than a lookup table."
)
