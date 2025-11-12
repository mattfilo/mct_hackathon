# streamlit_app.py

import streamlit as st
from nlp import draw_pcl_piechart     # <-- your function
import base64                                  # for optional base‑64 download button


# ------------------------------------------------------------------
# 1️⃣  Page layout
# ------------------------------------------------------------------
st.set_page_config(page_title="PCL Coverage Chat", page_icon="📊", layout="centered")
st.title("⚡️ PCL Airtime Coverage Explorer")

# Session state to keep chat history & image buffers alive
if "chat_log" not in st.session_state:
    st.session_state.chat_log = []

# ------------------------------------------------------------------
# 2️⃣  Chat input (Streamlit 1.28+)
# ------------------------------------------------------------------
try:
    user_question = st.chat_input("Ask about flight coverage…")
except AttributeError:                # older Streamlit <1.28
    user_question = st.text_input("What flights are you interested in?", key="q")

# ------------------------------------------------------------------
# 3️⃣  Process the question when the user hits enter / submit
# ------------------------------------------------------------------
if user_question:
    # Append to the chat log
    st.session_state.chat_log.append({"role": "user", "content": user_question})

    # Run heavy logic inside a spinner for UX
    with st.spinner("Generating pie chart…"):
        try:
            img_buf, summary = draw_pcl_piechart(user_question)
        except Exception as e:
            st.error(f"❌ {e}")
            img_buf = None

    if img_buf:
        # Display the chart
        st.subheader("Generated Pie Chart")
        st.image(img_buf, use_container_width=True)

        # Optional: let user download the PNG
        b64_img = base64.b64encode(img_buf.getvalue()).decode()
        href = f'<a href="data:image/png;base64,{b64_img}" download="pcl_coverage.png">Download PNG</a>'
        st.markdown(href, unsafe_allow_html=True)

        # Show summary metrics
        st.write(
            f"**Flights found:** {summary['flights']} | "
            f"**Total airtime:** {summary['total_airtime_sec']:.1f}s | "
            f"**Detected airtime:** {summary['detected_airtime_sec']:.1f}s | "
            f"**Coverage:** {summary['coverage_pct']:.2f}%"
        )

        # Log assistant reply
        st.session_state.chat_log.append(
            {"role": "assistant", "content": "Here’s your chart! 👇"}
        )

# ------------------------------------------------------------------
# 4️⃣  Show chat history (optional)
# ------------------------------------------------------------------
if st.session_state.chat_log:
    st.markdown("---")
    st.subheader("Conversation History")

    for msg in st.session_state.chat_log:
        role = "You" if msg["role"] == "user" else "Assistant"
        icon = "🗨️" if msg["role"] == "user" else "🤖"
        st.markdown(f"{icon} **{role}:** {msg['content']}")

# ------------------------------------------------------------------
# 5️⃣  Reset / clear button
# ------------------------------------------------------------------
if st.button("Clear chat"):
    st.session_state.chat_log.clear()
