# LangServe – Complete Guide (Beginner → Advanced)

---

## 1. What is LangServe?

**LangServe** is a framework that allows you to expose **LangChain chains as REST APIs** using **FastAPI**, with almost **zero boilerplate code**.

In simple words:

> Build a LangChain chain → Serve it as an API → LangServe handles everything else.

LangServe is a **serving layer**, not an LLM, not a vector database, and not a frontend.

---

## 2. Why LangServe Exists (Problem It Solves)

### Traditional API Approach (Without LangServe)

You would need to:

* Write FastAPI routes manually
* Parse request bodies
* Validate inputs
* Handle async execution
* Manage schemas
* Implement streaming logic
* Maintain OpenAPI docs

### With LangServe

LangServe automatically:

* Converts LangChain chains into API endpoints
* Creates `/invoke`, `/batch`, `/stream` routes
* Generates OpenAPI (Swagger) documentation
* Uses Pydantic for validation
* Handles async execution

---

## 3. Where LangServe Fits in the LangChain Ecosystem

```
User / Frontend
     ↓
LangServe (API Layer)
     ↓
LangChain Chains (LCEL)
     ↓
LLMs / Retrievers / Tools
```

LangServe’s role is **delivery**, not intelligence.

---

## 4. Core Concepts of LangServe

LangServe is built around **five core ideas**:

| Concept              | Description                         |
| -------------------- | ----------------------------------- |
| Chains as APIs       | Expose chains directly as endpoints |
| Runnable Interface   | Only runnable objects can be served |
| Input/Output Schemas | Automatic validation using Pydantic |
| Automatic Routes     | invoke, batch, stream generated     |
| Streaming & Batch    | Built-in support                    |

---

## 5. Installation

```bash
pip install langserve fastapi uvicorn
```

Install model providers separately (Ollama, HuggingFace, Groq, etc.).

---

## 6. Basic LangServe Example (Hello World)

### Step 1: Create a LangChain Chain

```python
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_community.llms import Ollama

prompt = ChatPromptTemplate.from_template(
    "Explain {topic} in simple words"
)

llm = Ollama(model="llama3")

chain = prompt | llm | StrOutputParser()
```

---

### Step 2: Serve the Chain Using LangServe

```python
from fastapi import FastAPI
from langserve import add_routes

app = FastAPI()

add_routes(
    app,
    chain,
    path="/explain"
)
```

---

### Step 3: Run the Server

```bash
uvicorn app:app --reload
```

---

### Step 4: Call the API

**POST** `/explain/invoke`

```json
{
  "input": {
    "topic": "LangServe"
  }
}
```

Response:

```json
{
  "output": "LangServe is a tool that helps you..."
}
```

---

## 7. What `add_routes()` Does Internally

This single line:

```python
add_routes(app, chain, path="/explain")
```

Automatically creates:

| Endpoint          | Purpose         |
| ----------------- | --------------- |
| `/explain/invoke` | Single request  |
| `/explain/batch`  | Multiple inputs |
| `/explain/stream` | Token streaming |
| `/docs`           | Swagger UI      |

No manual route creation required.

---

## 8. Runnable Interface (Critical Concept)

LangServe only works with **Runnable** objects.

Examples of Runnable components:

* PromptTemplate
* LLMs
* Chains (LCEL)
* Retrievers
* Custom RunnableLambda

Why Runnable?
Because it supports:

* `invoke()`
* `batch()`
* `stream()`

LangServe simply exposes these methods as APIs.

---

## 9. Input & Output Schema (Pydantic Integration)

LangServe automatically generates schemas using **Pydantic**.

Example input:

```python
chain.invoke({"topic": "AI"})
```

Auto-generated API schema:

```json
{
  "input": {
    "topic": "string"
  }
}
```

Benefits:

* Type safety
* Input validation
* Clear API contracts

---

## 10. Custom Input Schemas

When auto-generated schemas aren’t enough, define your own.

```python
from pydantic import BaseModel
from langchain_core.runnables import RunnableLambda

class ExplainInput(BaseModel):
    topic: str
    level: str

def explain_fn(data: ExplainInput):
    return f"Explain {data.topic} at {data.level} level"

chain = RunnableLambda(explain_fn)
```

LangServe enforces this schema automatically.

---

## 11. Batch Execution

### Endpoint

`POST /explain/batch`

### Request

```json
{
  "inputs": [
    { "topic": "AI" },
    { "topic": "ML" }
  ]
}
```

### Response

```json
{
  "outputs": [
    "AI explanation...",
    "ML explanation..."
  ]
}
```

Batching improves throughput significantly.

---

## 12. Streaming Responses

### Endpoint

`/explain/stream`

### Python Client Example

```python
import requests

with requests.post(
    "http://localhost:8000/explain/stream",
    json={"input": {"topic": "LangChain"}},
    stream=True
) as r:
    for chunk in r.iter_content():
        print(chunk.decode(), end="")
```

LangServe uses **Server-Sent Events (SSE)**.

---

## 13. Using LangServe with Chat Models

```python
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.chat_models import ChatOllama

prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful assistant"),
    ("human", "{question}")
])

llm = ChatOllama(model="llama3")

chain = prompt | llm
```

LangServe handles chat message formatting automatically.

---

## 14. LangServe with RAG (Retrieval-Augmented Generation)

```python
from langchain_core.runnables import RunnablePassthrough

rag_chain = (
    {"context": retriever, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)
```

Serve it:

```python
add_routes(app, rag_chain, path="/rag")
```

Fully functional RAG API with streaming support.

---

## 15. Authentication & Middleware

LangServe inherits FastAPI middleware.

```python
from fastapi import Depends, Header, HTTPException

def verify_key(x_api_key: str = Header(...)):
    if x_api_key != "secret":
        raise HTTPException(401)

app = FastAPI(dependencies=[Depends(verify_key)])
```

All LangServe routes are protected automatically.

---

## 16. API Versioning

```python
add_routes(app, chain_v1, path="/v1/explain")
add_routes(app, chain_v2, path="/v2/explain")
```

Essential for prompt or model upgrades.

---

## 17. LangServe + Frontend Integration

Frontend requirements:

* HTTP POST request
* JSON input
* Streaming handling (optional)

LangServe acts as a **backend for GenAI applications**.

---

## 18. LangServe vs Manual APIs

| Feature          | LangServe | Manual FastAPI |
| ---------------- | --------- | -------------- |
| Boilerplate      | Minimal   | High           |
| Validation       | Automatic | Manual         |
| Streaming        | Built-in  | Complex        |
| Batch            | Built-in  | Manual         |
| Swagger          | Auto      | Manual         |
| LangChain Native | Yes       | No             |

---

## 19. Common Mistakes

* Using non-runnable objects
* Forgetting output parsers
* Mixing sync and async incorrectly
* Returning raw LLM objects
* Not handling streaming on frontend

---

## 20. Production Best Practices

* Use Gunicorn + Uvicorn workers
* Enable logging and monitoring
* Add rate limiting
* Version APIs
* Cache results when possible
* Prefer async chains

---

## 21. Mental Model

> **LangChain builds intelligence**
> **LangServe delivers intelligence**

---

## 22. When NOT to Use LangServe

* Highly custom HTTP logic
* Non-LangChain workflows
* Ultra-low latency edge deployments

---

## 23. When LangServe is the Best Choice

* Chatbots
* RAG systems
* Internal LLM microservices
* AI platforms
* Rapid GenAI API deployment

---

## 24. Summary

LangServe provides a **production-ready, scalable, and clean way** to expose LangChain logic as APIs, drastically reducing backend complexity while preserving flexibility.

---

**End of Document**
