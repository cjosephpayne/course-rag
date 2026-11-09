"""Streamlit web interface for the course study assistant."""
import streamlit as st

from ask import answer

st.set_page_config(page_title="Course Study Assistant", page_icon="📚")
st.title("📚 Course Study Assistant")
st.caption("Ask a question about your course notes. Answers come only from the uploaded materials and cite their sources.")

question = st.text_input("Your question", placeholder="e.g., What is a foreign key?")

if st.button("Ask") and question.strip():
    with st.spinner("Searching your notes..."):
        text, hits = answer(question.strip())

    st.subheader("Answer")
    st.write(text)

    st.subheader("Sources retrieved")
    for doc, meta in hits:
        with st.expander(f"{meta['source']} — page {meta['page']}"):
            st.write(doc)