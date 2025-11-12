import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import io

# ------------------------------------------------------------------
# Helper: parse a question, build data & create a pie chart image.
#
# This is intentionally simple – you can replace it with an LLM or
# a domain‑specific parser.
# ------------------------------------------------------------------
def generate_pie_chart(question_text):
    """
    Very naive “parser”: look for the first number in the string,
    treat it as the number of categories, then build random data.

    Returns:
        BytesIO image buffer containing PNG data.
    """
    # 1. Try to extract an integer that looks like "5 categories"
    import re
    numbers = [int(num) for num in re.findall(r'\b\d+\b', question_text)]
    n_categories = numbers[0] if numbers else 3     # default 3

    labels = [f"Slice {i+1}" for i in range(n_categories)]

    # random data that sums to 100
    values = np.random.randint(5, 35, size=n_categories)
    total = values.sum()
    values = values / total * 100          # percentages

    # 2. Build the plot into a PNG buffer
    fig, ax = plt.subplots(figsize=(6, 4))
    wedges, texts, autotexts = ax.pie(
        values,
        labels=labels,
        autopct='%1.0f%%',
        startangle=90
    )
    # equal aspect ratio ensures that pie is drawn as a circle.
    ax.axis('equal')
    plt.title(f"Pie chart for: {question_text}")

    buf = io.BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight')
    plt.close(fig)
    buf.seek(0)                           # rewind the buffer so Streamlit can read it

    return buf


# ------------------------------------------------------------------
# 1. Set up UI – chat input & image placeholder
# ------------------------------------------------------------------

st.set_page_config(page_title="Pie‑Chart Chat", layout="centered")
st.title("Howdy Hey")

# Store all messages (history) in session_state so the widget persists.
if 'messages' not in st.session_state:
    st.session_state.messages = []

# 2. Create the chat box
#   - For Streamlit <1.28 you can replace this with st.text_input + a Submit button
try:
    user_question = st.chat_input("Type your question…")          # new UI widget
except AttributeError:                                            # older version fallback
    user_question = st.text_input("Maybe you wanna generate a pie chart?")

# 3. Handle the input once it appears
if user_question:
    # Append to history and clear chat_input automatically.
    st.session_state.messages.append({"role": "user", "content": user_question})

    # Call your function – in a real app you could do heavy NLP/LLM calls here.
    with st.spinner('Generating chart…'):
        image_buffer = generate_pie_chart(user_question)

    # Show the generated image
    st.subheader("Generated Pie Chart")
    st.image(image_buffer, use_container_width=True)

    # Echo back the user question in a chat‑style log (optional)
    if 'chat_log' not in st.session_state:
        st.session_state.chat_log = []

    st.session_state.chat_log.append({
        "role": "user",
        "content": user_question
    })
    st.session_state.chat_log.append({
        "role": "assistant",
        "content": "Here’s your pie‑chart!"
    })

# ------------------------------------------------------------------
# 4. Optionally show conversation history (plain text)
# ------------------------------------------------------------------
if 'chat_log' in st.session_state and st.session_state.chat_log:
    st.markdown("---")
    st.subheader("Conversation History")

    for i, msg in enumerate(st.session_state.chat_log):
        if msg["role"] == "user":
            st.markdown(f"**You:** {msg['content']}")
        else:
            st.markdown(f"**Assistant:** {msg['content']}")

# ------------------------------------------------------------------
# 5. Add a small button to reset the chat
# ------------------------------------------------------------------
if st.button("Clear Chat"):
    st.session_state.messages = []
    st.session_state.chat_log = [] 