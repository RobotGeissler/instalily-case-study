from langchain_community.vectorstores import Chroma
### DeepSeek is a hypothetical embedding model for this example.
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.embeddings import Embeddings
from langchain_community.document_loaders import TextLoader
# from langchain.embeddings import OpenAIEmbeddings
# from langchain.vectorstores import Chroma
# from langchain.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from typing import List, Dict, Any
import os, requests, torch
DATA_DIR = "./data/refrigerator-manuals" 

### Chroma vectorstore doesn't have a built-in retriever yet directly with deepseek api, so we need to implement it 
### ourselves. This is a boiler placeholder implementation for a more direct integration with DeepSeek.
class DeepSeekEmbeddings(Embeddings):
    def __init__(self, model_name="DeepSeek"):
        # Initialize your embeddings model here
        self.model_name = model_name
        self.api_key = os.getenv("DEEPSEEK_API_KEY")
        if not self.api_key:
            raise ValueError("API key for DeepSeek is not set.")
        else:
            self.endpoint = "https://api.deepseek.com/v1/embeddings"

    def embed_documents(self, documents: list[str]) -> list[list[float]]:
        # Implement the method to embed documents
        headers = {"Authorization": f"Bearer {self.api_key}"}
        response = requests.post(
            self.endpoint, headers=headers, json={"documents": documents}
        )
        if response.status_code != 200:
            raise Exception(f"Error embedding documents: {response.text}")
        return response.json().get("embeddings", [])

    def embed_query(self, query: str) -> list[float]:
        # Implement the method to embed a query
        return self.embed_documents([query])[0]

def build_retriever():
    model_name = "deepseek-ai/deepseek-coder-1.3b-base"
    model_kwargs = {
        "device": "cuda:0" if torch.cuda.is_available() else "cpu",
        "model_name": model_name,
    }
    encode_kwargs = {
        'normalize_embeddings': False
    }
    hf = HuggingFaceEmbeddings(
        model_name=model_name,
        model_kwargs=model_kwargs,
        encode_kwargs=encode_kwargs
    )

    all_docs = []
    for filename in os.listdir(DATA_DIR):
        if filename.endswith(".txt"):
            loader = TextLoader(os.path.join(DATA_DIR, filename))
            docs = loader.load()
            splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
            chunks = splitter.split_documents(docs)
            all_docs.extend(chunks)

    vectordb = Chroma.from_documents(all_docs, hf, persist_directory="./db")
    return vectordb.as_retriever()

retriever = build_retriever()
query = "Is PS11752778 compatible with Whirlpool WDT780SAEM1?"
docs = retriever.get_relevant_documents(query)

for doc in docs:
    print(doc.metadata.get("source"), doc.page_content[:300])
