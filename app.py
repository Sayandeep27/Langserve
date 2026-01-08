import os
from dotenv import load_dotenv

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_groq import ChatGroq
from langserve import add_routes

# --------------------------------------------------
# Load environment variables
# --------------------------------------------------
load_dotenv()
groq_api_key = os.environ["GROQ_API_KEY"]

# --------------------------------------------------
# FastAPI App
# --------------------------------------------------
app = FastAPI(
    title="Text Summarizer API",
    version="1.0",
    description="Text summarization using LangServe + Groq"
)

# --------------------------------------------------
# Enable CORS (optional but useful)
# --------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# --------------------------------------------------
# Groq LLM
# --------------------------------------------------
llm = ChatGroq(
    api_key=groq_api_key,
    model="llama-3.1-8b-instant",
    temperature=0.3
)

# --------------------------------------------------
# Prompt for summarization
# --------------------------------------------------
prompt = ChatPromptTemplate.from_template(
    "Summarize the following text clearly and concisely:\n\n{text}"
)

# --------------------------------------------------
# Chain (Prompt → LLM → Output)
# --------------------------------------------------
chain = prompt | llm | StrOutputParser()

# --------------------------------------------------
# Add LangServe route
# --------------------------------------------------
add_routes(
    app,
    chain,
    path="/summarize"
)

# --------------------------------------------------
# Run server
# --------------------------------------------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=8000)
