import streamlit as st
import os
from datetime import datetime
from rag import FreshserviceRAG

st.set_page_config(page_title="Freshservice Assistant", layout="wide")

# Initialize session state
if "rag" not in st.session_state:
    st.session_state.rag = None
if "chat" not in st.session_state:
    st.session_state.chat = []

st.title("Freshservice API Assistant")
st.write("Ask questions about the Freshservice API documentation.")

docs_file = "output/freshservice_docs.json"

# Load RAG
if st.session_state.rag is None:
    if os.path.exists(docs_file):
        st.session_state.rag = FreshserviceRAG(docs_file)
        st.success("Documentation loaded successfully!")
    else:
        st.error("Documentation file not found. Run scraper first.")
        st.stop()

# Input section
query = st.text_input("Your question:", placeholder="e.g., How do I create a ticket?")

if st.button("Ask") and query.strip():
    # Add user message
    timestamp = datetime.now().strftime("%H:%M")
    st.session_state.chat.append(("user", query, timestamp))
    
    # Get response
    result = st.session_state.rag.answer_query(query)
    st.session_state.chat.append(("assistant", result, timestamp))

# Display chat
if st.session_state.chat:
    st.markdown("---")
    
    for role, content, timestamp in st.session_state.chat:
        if role == "user":
            st.markdown(f"**You ({timestamp}):** {content}")
        else:
            # Handle response format
            if isinstance(content, dict):
                answer = content.get("answer", "")
                sources = content.get("sources", [])
            else:
                answer = str(content)
                sources = []
            
            st.markdown(f"**Assistant ({timestamp}):**")
            st.write(answer)
            
            # Show sources
            if sources:
                st.markdown("**Sources:**")
                for i, source in enumerate(sources, 1):
                    section = source.get("section", f"Source {i}")
                    content_preview = source.get("content_preview", "")
                    url = source.get("url", "")
                    
                    with st.expander(f"{i}. {section}"):
                        if content_preview:
                            st.write(content_preview)
                        if url:
                            st.markdown(f"**Link:** {url}")
        
        st.markdown("---")

# Clear chat button
if st.session_state.chat:
    if st.button("Clear Chat"):
        st.session_state.chat = []
        st.rerun()