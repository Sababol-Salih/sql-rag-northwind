from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from ..settings import SETTINGS

def get_retriever():
    embeddings = OpenAIEmbeddings(api_key=SETTINGS.openai_api_key)
    vectordb = Chroma(persist_directory=SETTINGS.chroma_dir, embedding_function=embeddings)
    return vectordb.as_retriever(search_kwargs={"k": SETTINGS.top_k})
