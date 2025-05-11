from langchain_deepseek import ChatDeepSeek
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import RetrievalQA
from langchain_core.prompts import PromptTemplate
import os
import re

# Configuration
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "YOUR_DEEPSEEK_API_KEY")
os.environ["DEEPSEEK_API_KEY"] = DEEPSEEK_API_KEY

# Initialize DeepSeek model
llm = ChatDeepSeek(model="deepseek-chat", temperature=0.7, max_tokens=500)

# Load and process knowledge base
try:
    with open("knowledge_base.txt", "r", encoding="utf-8") as f:
        documents = f.read()
except FileNotFoundError:
    raise FileNotFoundError("knowledge_base.txt not found. Please create the file.")

text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
texts = text_splitter.split_text(documents)
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
vectorstore = Chroma.from_texts(texts, embeddings)

# RAG prompt template
prompt_template = """
آپ اے آئی علم بوٹ ہیں، اساتذہ کے لیے ایک مددگار معاون، جو اردو اور انگریزی میں AI خواندگی فراہم کرتا ہے۔
دیے گئے سیاق و سباق کو استعمال کرتے ہوئے سوال کا جواب دیں۔ اگر ان پٹ میں اردو حروف ہوں تو اردو میں جواب دیں، ورنہ انگریزی میں۔
جوابات مختصر، تعلیمی، اور ثقافتی طور پر حساس رکھیں۔

سیاق: {context}

سوال: {question}

جواب:
"""
QA_CHAIN_PROMPT = PromptTemplate.from_template(prompt_template)

# Initialize RAG chain
qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",
    retriever=vectorstore.as_retriever(),
    chain_type_kwargs={"prompt": QA_CHAIN_PROMPT}
)

# Function to detect Urdu text (Unicode range for Urdu: U+0600 to U+06FF)
def is_urdu(text):
    return bool(re.search(r'[\u0600-\u06FF]', text))

# Function to sanitize Markdown bold syntax to plain text for WhatsApp
def sanitize_markdown(text):
    # Convert **text** to text (remove ** for WhatsApp plain text)
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
    return text

# Chat history (shared across sessions)
chat_history = {}

def process_message(sender, message):
    # Initialize chat history for sender if not exists
    if sender not in chat_history:
        chat_history[sender] = []

    # Add user message to history
    chat_history[sender].append({"role": "user", "content": message})

    # Prepare context with recent history (last 3 messages)
    history_context = "\n".join(
        [f"{msg['role']}: {msg['content']}" for msg in chat_history[sender][-3:]]
    )

    # Get response from RAG chain
    try:
        result = qa_chain.invoke({"query": f"{history_context}\nuser: {message}"})
        response_text = result["result"]
    except Exception as e:
        response_text = f"خطا: {str(e)}"

    # Add bot response to history
    chat_history[sender].append({"role": "assistant", "content": response_text})

    # Sanitize response for WhatsApp
    return sanitize_markdown(response_text)