# streamlit_app.py
import streamlit as st
from nlp import draw_sensor_piechart
import base64

st.set_page_config(page_title="PCL Airtime Coverage", layout="centered")
st.title("✈️ PCL/AIR Sensor Coverage Chat")

# Chat history (optional)
if "chat_log" not in st.session_state:
    st.session_state.chat_log = []

# ------------------------------------------------------------------
# 1️⃣ Input box
# ------------------------------------------------------------------
try:
    user_query = st.chat_input("Ask for a coverage pie‑chart …")
except AttributeError:          # older Streamlit < 1.28
    user_query = st.text_input("Your question…", key="q")

if user_query:
    st.session_state.chat_log.append({"role": "user", "content": user_query})

    with st.spinner("Generating chart…"):
        try:
            img_buf, stats = draw_sensor_piechart(user_query)
        except Exception as e:   # guard against bugs in data
            st.error(f"❌ {e}")
            img_buf, stats = None, {}

    if img_buf:
        st.subheader("Generated Pie Chart")
        st.image(img_buf, use_container_width=True)

        # Show a download link (base‑64)
        b64_img = base64.b64encode(img_buf.getvalue()).decode()
        href = f'<a href="data:image/png;base64,{b64_img}" download="coverage.png">Download PNG</a>'
        st.markdown(href, unsafe_allow_html=True)

        # # Display summary
        # st.markdown("---")
        # st.subheader("Coverage Summary")
        # st.json(stats)  # nicely formatted JSON

    st.session_state.chat_log.append(
        {"role": "assistant", "content": "Here’s your chart!"}
    )

# ------------------------------------------------------------------
# 2️⃣ Optional conversation log (plain text)
# ------------------------------------------------------------------
if st.session_state.chat_log:
    st.markdown("---")
    st.subheader("Conversation History")
    for msg in st.session_state.chat_log:
        icon = "🗨️" if msg["role"] == "user" else "🤖"
        st.write(f"{icon} **{msg['role'].capitalize()}:** {msg['content']}")

# ------------------------------------------------------------------
# 3️⃣ Reset button
# ------------------------------------------------------------------
if st.button("Clear chat"):
    st.session_state.chat_log.clear()
