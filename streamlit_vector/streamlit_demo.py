import os
import streamlit as st
from llama_index import GPTSimpleVectorIndex, SimpleDirectoryReader, ServiceContext
from llama_index.llm_predictor.chatgpt import ChatGPTLLMPredictor


index_name = "./index.json"
documents_folder = "./documents"


@st.cache_resource
def initialize_index(index_name, documents_folder):
    llm_predictor = ChatGPTLLMPredictor()
    service_context = ServiceContext.from_defaults(llm_predictor=llm_predictor)
    if os.path.exists(index_name):
        index = GPTSimpleVectorIndex.load_from_disk(index_name, service_context=service_context)
    else:
        documents = SimpleDirectoryReader(documents_folder).load_data()
        index = GPTSimpleVectorIndex.from_documents(documents, service_context=service_context)
        index.save_to_disk(index_name)

    return index


@st.cache_data(max_entries=200, persist=True)
def query_index(_index, query_text):
    response = _index.query(query_text)
    return str(response)


st.title("🦙 Llama Index Demo 🦙")
st.header("Welcome to the Llama Index Streamlit Demo")
st.write("Enter a query about Paul Graham's essays. You can check out the original essay [here](https://raw.githubusercontent.com/jerryjliu/llama_index/main/examples/paul_graham_essay/data/paul_graham_essay.txt). Your query will be answered using the essay as context, using embeddings from text-ada-002 and LLM completions from ChatGPT. You can read more about Llama Index and how this works in [our docs!](https://gpt-index.readthedocs.io/en/latest/index.html)")

index = None
api_key = st.text_input("Enter your OpenAI API key here:", type="password")
if api_key:
    os.environ['OPENAI_API_KEY'] = api_key
    index = initialize_index(index_name, documents_folder)    


if index is None:
    st.warning("Please enter your api key first.")

text = st.text_input("Query text:", value="What did the author do growing up?")

if st.button("Run Query") and text is not None:
    response = query_index(index, text)
    st.markdown(response)
    
    llm_col, embed_col = st.columns(2)
    with llm_col:
        st.markdown(f"LLM Tokens Used: {index.service_context.llm_predictor._last_token_usage}")
    
    with embed_col:
        st.markdown(f"Embedding Tokens Used: {index.service_context.embed_model._last_token_usage}")
