import streamlit as st
from .agent import process_user_query

st.set_page_config(page_title="DukeBot", page_icon=":robot_face:")

st.title("DukeBot  Duke University Chatbot")
st.caption("Ask me about Duke events, courses, people, and the Pratt School of Engineering!")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("What would you like to know?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        with st.spinner("Thinking..."):
            full_response = process_user_query(prompt)
            message_placeholder.markdown(full_response)
    st.session_state.messages.append({"role": "assistant", "content": full_response}) 