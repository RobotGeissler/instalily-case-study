# Community chroma deprecated, however there are issues with onnxruntime
from langchain_community.vectorstores import Chroma
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.embeddings import Embeddings
from langchain_openai import OpenAIEmbeddings
from typing import List
import sys, os, requests, torch, random, chromadb

DATA_DIR = "./data/refrigerator-manuals"
CHROMA_DIR = "./db"

### This is a dummy class for testing purposes only.
# class DummyEmbeddings(Embeddings):
#     def embed_documents(self, texts: List[str]) -> List[List[float]]:
#         return [[random.random() for _ in range(768)] for _ in texts]
    
#     def embed_query(self, query: str) -> List[float]:
#         return [random.random() for _ in range(768)]
    
class DeepSeekEmbeddings(Embeddings):
    def __init__(self, model_name="DeepSeek"):
        self.model_name = model_name
        self.api_key = os.getenv("DEEPSEEK_API_KEY")
        if not self.api_key:
            raise ValueError("API key for DeepSeek is not set.")
        self.endpoint = "https://api.deepseek.com/v1/embeddings"

    def embed_documents(self, documents: List[str]) -> List[List[float]]:
        headers = {"Authorization": f"Bearer {self.api_key}"}
        response = requests.post(self.endpoint, headers=headers, json={"documents": documents})
        if response.status_code != 200:
            raise Exception(f"DeepSeek embedding error: {response.text}")
        return response.json().get("embeddings", [])

    def embed_query(self, query: str) -> List[float]:
        return self.embed_documents([query])[0]
    
    ### TODO Implement similarity search for DeepSeek?
    # def similarity_search(self, query: str, k: int = 5) -> List[str]:
    #     pass
    
def is_deepseek_available() -> bool:
    try:
        response = requests.get("https://api.deepseek.com/v1/status")
        if response.status_code == 200:
            return True
    except requests.RequestException:
        pass
    return False

def select_embedding_backend() -> Embeddings:
    try:
        if os.getenv("USE_DEEPSEEK", "false").lower() == "true":
            print("🔍 Using DeepSeek Embeddings...")
            ### TODO Check if API key is valid
            if not is_deepseek_available():
                raise ValueError("DeepSeek API is not available.")
            return DeepSeekEmbeddings()
    except Exception as e:
        print(f"⚠️ DeepSeek failed, falling back to OpenAI: {e}")
    os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
    if not os.getenv("OPENAI_API_KEY"):
        raise ValueError("OpenAI API key is not set.")
    return OpenAIEmbeddings()

def build_retriever():
    embedding_backend = select_embedding_backend()

    all_docs = []
    for filename in os.listdir(DATA_DIR):
        if filename.endswith(".txt"):
            loader = TextLoader(os.path.join(DATA_DIR, filename))
            docs = loader.load()
            if not docs:
                print(f"⚠️ No documents found in {filename}. SEE DOCS.")
                continue
            splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
            chunks = splitter.split_documents(docs)
            if not chunks:
                print(f"⚠️ No chunks found in {filename}. SEE DOCS.")
                continue
            all_docs.extend(chunks)
    
    if not all_docs:
        raise RuntimeError("No documents found in the data folder. Check path and contents.")
    
    print(f"🧠 Using embedding backend: {embedding_backend.__class__.__name__}")
    if os.getenv("DEBUG", "false").lower() == "true":
        print("🔍 Debug mode enabled")
        print("📄 Sample doc:", all_docs[0].page_content[:100])
        embeddings = embedding_backend.embed_documents([doc.page_content for doc in all_docs])
        print(f"✅ Got {len(embeddings)} embeddings")
        print("✅ First embedding:", embeddings[0][:10])

    ### TODO Make sure to delete the old vector store if it exists - Doesn't work due to windows file lock
    # if os.path.exists(CHROMA_DIR):
    #     print("🗑️ Deleting old vector store...")
    #     os.remove(CHROMA_DIR)

    if os.path.exists(CHROMA_DIR):
        print("📦 Loading existing Chroma DB...")
        persistent_client = chromadb.PersistentClient()
        vectordb = Chroma(client=persistent_client, embedding_function=embedding_backend)
    else:
        print("🧠 Building new Chroma DB...")
        vectordb = Chroma.from_documents(all_docs, embedding_function=embedding_backend, persist_directory=CHROMA_DIR)

    print("✅ Vector store created")  
    if os.getenv("DEBUG", "false").lower() == "true":
        print("🔍 Debug mode enabled")
        print("🧠 Vector store doc count:", vectordb._collection.count())

    return vectordb.as_retriever()

# ✅ Run this once for test
if __name__ == "__main__":
    retriever = build_retriever()
    query = "Is PS11752778 compatible with Whirlpool WDT780SAEM1?"
    docs = retriever.invoke(query)
    for doc in docs:
        print(doc.metadata.get("source"), doc.page_content[:300])
