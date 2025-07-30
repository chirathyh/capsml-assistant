import streamlit as st

from agents import MEMORY_LOG
from pipeline import build_graph

AVAILABLE_MODELS = ["llama3.1:8b", "codestral:latest", "qwen2.5-coder:32b", "llama3.3:latest", "deepseek-r1:32b", "deepseek-r1:70b"]

graph = build_graph()

st.set_page_config(page_title="CAPSML Assistant", layout="wide")
st.title("CAPSML Assistant")

user_input = st.text_input("How can I help you today?")

# Boolean feature toggles
col3, col4, col5, _, _, _ = st.columns(6)
with col3:
    use_pdf = st.toggle("📄 Use PDF", value=False)
with col4:
    use_web = st.toggle("🌐 Use Web", value=False)
with col5:
    use_code = st.toggle("💻 Use Code", value=True)

col1, col2 = st.columns(2)
with col1:
    selected_code_agent = st.selectbox("🤖 Code Agent", AVAILABLE_MODELS, index=AVAILABLE_MODELS.index("codestral:latest"))
    selected_assistant_agent = st.selectbox("🤖 Assistant Agent", AVAILABLE_MODELS, index=AVAILABLE_MODELS.index("llama3.1:8b"))

if st.button("Run") and user_input:
    with st.spinner("Thinking..."):
        
        result = graph.invoke({
                    "input": user_input,
                    "code_agent": selected_code_agent,
                    "assistant_agent": selected_assistant_agent,
                    "use_pdf": use_pdf,
                    "use_web": use_web,
                    "use_code": use_code
                })

        
        st.subheader("📘 Final Report")
        st.markdown(result["report"])

st.sidebar.title("Chat History")
for entry in reversed(MEMORY_LOG[-5:]):
    st.sidebar.markdown(f"---\n{entry}")


# streamlit run app.py