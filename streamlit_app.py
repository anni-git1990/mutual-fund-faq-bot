import streamlit as st
import datetime
import os
from groq import Groq
from dotenv import load_dotenv

# Load local environment variables (for local runs)
load_dotenv()

# Set page config
st.set_page_config(
    page_title="Mutual Fund FAQ Assistant",
    page_icon="📈",
    layout="wide",
)

# App Title
st.title("📈 Mutual Fund FAQ Assistant")
st.markdown("##### Facts-only Q&A for Groww target schemes")

# Import RAG components inside a cached function to prevent reloading model resources
@st.cache_resource
def get_retriever_and_client():
    from src.api.retriever import MutualFundRetriever
    
    retriever = None
    try:
        retriever = MutualFundRetriever()
    except Exception as e:
        st.warning(f"Chroma Index is not initialized: {e}. Running ingestion might be required.")
        
    # Get API Key from environment or streamlit secrets
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        try:
            api_key = st.secrets["GROQ_API_KEY"]
        except Exception:
            pass
            
    return retriever, api_key

retriever, api_key = get_retriever_and_client()

# Check GROQ API Key
if not api_key:
    st.error("GROQ_API_KEY not found. Please set it in your environment variables or Streamlit Secrets.")
    st.stop()

client = Groq(api_key=api_key)

# Compliance Refusal Texts & Instructions
from src.api.guardrails import ADVISORY_REFUSAL_TEXT, OUT_OF_SCOPE_TEXT
from src.api.chat import SYSTEM_INSTRUCTIONS

# Initialize chat session history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Sidebar FAQ Suggestions panel
with st.sidebar:
    st.header("Frequently Asked Questions")
    st.markdown("Select any card below to ask instantly:")
    
    suggestions = [
        "What is the expense ratio of Nippon India Large Cap?",
        "What is the lock-in period for ELSS?",
        "What is the minimum SIP of Groww Nifty Total Market Index Fund?",
        "What is the exit load of HDFC Nifty 50?",
        "What is the risk level and benchmark of ICICI Prudential Nifty Index Fund?",
        "How to download capital-gains statement?",
    ]
    
    selected_query = None
    for s in suggestions:
        if st.button(s, use_container_width=True):
            selected_query = s
            
    st.divider()
    if st.button("🗑️ Clear Chat History", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# Display chat messages from history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Function to run the query through RAG & compliance guardrails
def process_query(user_query):
    # Add user message
    st.session_state.messages.append({"role": "user", "content": user_query})
    with st.chat_message("user"):
        st.markdown(user_query)
        
    from src.api.guardrails import classify_query, validate_and_format_output
    
    current_date = datetime.datetime.now().strftime("%d-%b-%Y")
    
    with st.spinner("Checking compliance..."):
        intent = classify_query(user_query, client)
        
    if intent == "ADVISORY":
        ans = (
            f"{ADVISORY_REFUSAL_TEXT}\n\n"
            f"**Source**: https://groww.in/blog/mutual-funds-for-beginners-investor-education\n\n"
            f"**Last updated**: {current_date}"
        )
        st.session_state.messages.append({"role": "assistant", "content": ans})
        with st.chat_message("assistant"):
            st.markdown(ans)
        return
        
    if intent == "OUT_OF_SCOPE":
        ans = (
            f"{OUT_OF_SCOPE_TEXT}\n\n"
            f"**Source**: https://groww.in\n\n"
            f"**Last updated**: {current_date}"
        )
        st.session_state.messages.append({"role": "assistant", "content": ans})
        with st.chat_message("assistant"):
            st.markdown(ans)
        return
        
    # Factual Query Flow
    if not retriever:
        st.error("Retriever is not initialized. Please build the index first.")
        return
        
    with st.spinner("Retrieving facts..."):
        results = retriever.retrieve(user_query, limit=3)
        if not results:
            ans = "I could not retrieve any factual information for this query. Please check the scope."
            st.session_state.messages.append({"role": "assistant", "content": ans})
            with st.chat_message("assistant"):
                st.markdown(ans)
            return
            
        context_text = "\n\n".join([r["text"] for r in results])
        primary_url = results[0]["metadata"].get("source_url", "https://groww.in")
        last_updated = results[0]["metadata"].get("last_updated", current_date)
        
        # Invoke LLM
        prompt = SYSTEM_INSTRUCTIONS.format(
            context_text=context_text,
            last_updated_date=last_updated
        )
        
        response = client.chat.completions.create(
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": user_query}
            ],
            model=os.environ.get("GROQ_MODEL", "llama-3.3-70b-versatile"),
            temperature=0.0
        )
        
        raw_answer = response.choices[0].message.content.strip()
        formatted_answer = validate_and_format_output(raw_answer, primary_url, last_updated)
        
        st.session_state.messages.append({"role": "assistant", "content": formatted_answer})
        with st.chat_message("assistant"):
            st.markdown(formatted_answer)

# If query clicked from suggestions
if selected_query:
    process_query(selected_query)

# Accept user chat input
elif prompt_input := st.chat_input("Type your mutual fund question here..."):
    process_query(prompt_input)

# Safety disclaimer footer
st.divider()
st.caption("⚖️ **Disclaimer**: Facts-only. No investment advice. This bot is compliant with SEBI mutual fund guidelines.")
