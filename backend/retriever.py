from langchain.vectorstores import Chroma
from langchain.embeddings import OpenAIEmbeddings
from langchain.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
import os

DATA_DIR = "./data/refrigerator-manuals" 

def build_retriever():
    all_docs = []
    for filename in os.listdir(DATA_DIR):
        if filename.endswith(".txt"):
            loader = TextLoader(os.path.join(DATA_DIR, filename))
            docs = loader.load()
            splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
            chunks = splitter.split_documents(docs)
            all_docs.extend(chunks)

    vectordb = Chroma.from_documents(all_docs, OpenAIEmbeddings(), persist_directory="./db")
    return vectordb.as_retriever()

retriever = build_retriever()
query = "Is PS11752778 compatible with Whirlpool WDT780SAEM1?"
docs = retriever.get_relevant_documents(query)

for doc in docs:
    print(doc.metadata.get("source"), doc.page_content[:300])
