import streamlit as st
from bot import process_message, is_urdu, sanitize_markdown

# Streamlit UI
st.set_page_config(page_title="اے آئی علم بوٹ", page_icon="📚", layout="wide")

# Custom CSS for Urdu text and chat input
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Nastaliq+Urdu&display=swap');
    .urdu-text {
        direction: rtl;
        font-family: 'Noto Nastaliq Urdu', sans-serif;
        font-size: 18px;
        line-height: 1.6;
    }
    .stTextInput input {
        direction: rtl;
        font-family: 'Noto Nastaliq Urdu', sans-serif;
        font-size: 16px;
    }
    </style>
""", unsafe_allow_html=True)

# Title and subtitle
st.markdown("<h1 class='urdu-text'>اے آئی علم بوٹ</h1>", unsafe_allow_html=True)
st.markdown("<div class='urdu-text'>اساتذہ کو اردو اور انگریزی میں AI خواندگی کے ساتھ بااختیار بنانا</div>", unsafe_allow_html=True)

# Initialize chat history in session state
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for message in st.session_state.messages:
    with st.chat_message("صارف" if message["role"] == "user" else "بوٹ"):
        sanitized_content = sanitize_markdown(message["content"])
        if is_urdu(sanitized_content):
            st.markdown(f"<div class='urdu-text'>{sanitized_content}</div>", unsafe_allow_html=True)
        else:
            st.markdown(sanitized_content, unsafe_allow_html=True)

# Chat input
if prompt := st.chat_input("تعلیم میں AI کے بارے میں پوچھیں..."):
    # Add user message to history
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("صارف"):
        sanitized_prompt = sanitize_markdown(prompt)
        if is_urdu(sanitized_prompt):
            st.markdown(f"<div class='urdu-text'>{sanitized_prompt}</div>", unsafe_allow_html=True)
        else:
            st.markdown(sanitized_prompt, unsafe_allow_html=True)

    # Process message using bot
    with st.spinner("اے آئی علم بوٹ سوچ رہا ہے..."):
        response_text = process_message("streamlit_user", prompt)

    # Add bot response to history
    st.session_state.messages.append({"role": "assistant", "content": response_text})
    with st.chat_message("بوٹ"):
        sanitized_response = sanitize_markdown(response_text)
        if is_urdu(sanitized_response):
            st.markdown(f"<div class='urdu-text'>{sanitized_response}</div>", unsafe_allow_html=True)
        else:
            st.markdown(sanitized_response, unsafe_allow_html=True)