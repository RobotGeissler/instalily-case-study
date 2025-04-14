from flask import Flask, request, jsonify
from flask_cors import CORS
from retriever import build_retriever
from langchain.chains.question_answering import load_qa_chain
from langchain.chat_models import ChatDeepSeek

app = Flask(__name__)
CORS(app)

retriever = build_retriever()
llm = ChatDeepSeek(model="gpt-4")  # Or DeepSeek if using it
qa_chain = load_qa_chain(llm)

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_message = data.get("message", "")

    docs = retriever.get_relevant_documents(user_message)
    result = qa_chain.run(input_documents=docs, question=user_message)

    return jsonify({
        "role": "assistant",
        "content": result
    })

if __name__ == "__main__":
    app.run(port=8000, debug=True)
