from flask import Flask, request, jsonify
from flask_cors import CORS
from retriever import build_retriever
from langchain.chains import RetrievalQA
from langchain_openai import ChatOpenAI
from langchain_deepseek import ChatDeepSeek
from retriever import is_deepseek_available

app = Flask(__name__)
CORS(app)

retriever = build_retriever()
if is_deepseek_available():
    print("✅ DeepSeek is available")
    llm = ChatDeepSeek(model="deepseek-chat")  # Or DeepSeek if using it
else:
    print("⚠️ DeepSeek is not available. Please check your API key or network connection.")
    print("⚠️ Falling back to OpenAI GPT-4")
    print("⚠️ This is not within the spec for the case study - H.")
    llm = ChatOpenAI(model="gpt-4")
qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",
    retriever=retriever,
    return_source_documents=True,
    verbose=True,
)

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_message = data.get("message", "")
    print(f"💬 Received: {user_message}")

    docs = retriever.get_relevant_documents(user_message)

    output = qa_chain.invoke({
        "input_documents": docs,
        "query": user_message  # ✅ use "query" not "question"
    })
    result = output["result"]

    return jsonify({
        "role": "assistant",
        "content": result
    })

if __name__ == "__main__":
    app.run(port=8000, debug=True, use_reloader=False)
