from src.database import get_user_by_id
from flask import Blueprint, render_template, request,redirect, url_for, session
from src.Chatbot.helper import download_hugging_face_embeddings
from langchain_pinecone import PineconeVectorStore
from langchain.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains import RetrievalQA
from dotenv import load_dotenv
from src.Chatbot.prompt import *
from langchain_community.vectorstores import Pinecone
import os
bot_bp = Blueprint('medical', __name__)

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_API_ENV = os.getenv("PINECONE_API_ENV")
from pinecone.grpc import PineconeGRPC as Pinecone

pc = Pinecone(api_key=PINECONE_API_KEY)

embeddings = download_hugging_face_embeddings()

index_name = "medical-bot"

index = pc.Index(index_name)
docsearch = PineconeVectorStore(index=index, embedding=embeddings)

PROMPT = PromptTemplate(template=prompt_template, input_variables=["context", "question"])

chain_type_kwargs = {"prompt": PROMPT}

llm = ChatGoogleGenerativeAI(model="models/gemini-1.5-flash", temperature=0.8, google_api_key=GOOGLE_API_KEY)

qa = RetrievalQA.from_chain_type(
    llm=llm, 
    chain_type="stuff", 
    retriever=docsearch.as_retriever(search_kwargs={'k': 2}),
    return_source_documents=True, 
    chain_type_kwargs=chain_type_kwargs
)


@bot_bp.route("/chat")
def index():
    user_id = session.get('user', {}).get('_id')  # Access user ID from the session
    if not user_id:
        return redirect(url_for('auth.login'))  # Redirect if not logged in
    
    user_data = get_user_by_id(user_id)  # Retrieve user data from the database
    display_data = {
        'profile_pic': user_data.get('profile_pic'),
        'name': user_data.get('name')
    }

    return render_template('chat.html', display_data=display_data)  # Pass user data to the template

@bot_bp.route("/get", methods=["GET", "POST"])
def chat():
    msg = request.form["msg"]
    input = msg
    result = qa.invoke({"query": input})
    return str(result["result"])