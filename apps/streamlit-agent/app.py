from __future__ import annotations

import streamlit as st

from agent.graph import run_agent


st.set_page_config(page_title="Agentic Workshop Quickstarter", page_icon="🤖")
st.title("Agentic Workshop Quickstarter")
st.caption("Python + Streamlit + LangGraph + OpenRouter")

if "history" not in st.session_state:
    st.session_state.history = []

with st.form("prompt_form"):
    user_prompt = st.text_area(
        "Ask the assistant",
        placeholder="Try: Calculate (12 * 8) + 5 and explain briefly.",
        height=100,
    )
    submitted = st.form_submit_button("Run agent")

if submitted:
    prompt = user_prompt.strip()
    if not prompt:
        st.warning("Please enter a prompt.")
    else:
        with st.spinner("Running agent..."):
            try:
                result = run_agent(prompt)
                st.session_state.history.append(
                    {
                        "prompt": prompt,
                        "plan": result["plan"],
                        "response": result["response"],
                    }
                )
            except Exception as exc:  # noqa: BLE001
                st.error(f"Agent failed: {exc}")

if st.session_state.history:
    st.subheader("Recent Runs")
    for idx, item in enumerate(reversed(st.session_state.history), start=1):
        st.markdown(f"### Run {idx}")
        st.markdown(f"**Prompt**: {item['prompt']}")
        with st.expander("Planner output"):
            st.write(item["plan"])
        st.markdown("**Response**")
        st.write(item["response"])
