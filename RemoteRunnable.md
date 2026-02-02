# RemoteRunnable in LangServe — Complete Guide

---

## 1. What is `RemoteRunnable`?

**`RemoteRunnable`** is a LangServe client-side utility that allows you to call a **LangChain chain running on a remote server** exactly like a **local LangChain chain**.

In simple terms:

> **RemoteRunnable = LangChain chain over HTTP**

You do not import the chain code.
You do not load the model locally.
You simply call the chain as if it were local.

---

## 2. Why Does RemoteRunnable Exist?

LangChain chains are typically **local Python objects**. However, in real-world systems:

* LLM logic usually runs on a backend server
* Frontend or other services need to consume it
* You do not want to duplicate chain logic everywhere

**RemoteRunnable** solves this by acting as a **client-side proxy** for LangServe-hosted chains.

---

## 3. Core Mental Model

```
Local Chain
    ↓
chain.invoke()

Remote Chain
    ↓
RemoteRunnable.invoke()
    ↓
HTTP Request
```

From the developer’s perspective:

> There is **no difference** between local and remote execution.

---

## 4. Basic End-to-End Example

### Backend (LangServe Server)

```python
# server.py
from fastapi import FastAPI
from langserve import add_routes
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_community.llms import Ollama

app = FastAPI()

prompt = ChatPromptTemplate.from_template(
    "Summarize the following text:\n{text}"
)

llm = Ollama(model="llama3")

chain = prompt | llm | StrOutputParser()

add_routes(app, chain, path="/summarize")
```

Run the server:

```bash
uvicorn server:app --reload
```

---

### Client (RemoteRunnable)

```python
from langserve import RemoteRunnable

chain = RemoteRunnable("http://localhost:8000/summarize")

result = chain.invoke({
    "text": "LangServe makes serving LangChain applications easy."
})

print(result)
```

You just called a **remote LLM chain** like a local function.

---

## 5. What Happens Internally?

When you run:

```python
chain.invoke({"text": "hello"})
```

Internal execution flow:

1. Input is serialized by `RemoteRunnable`
2. HTTP POST request is sent to `/summarize/invoke`
3. LangServe validates input using Pydantic
4. The chain executes on the server
5. Output is parsed and serialized
6. Response is returned as a Python object

---

## 6. Runnable Interface Support

`RemoteRunnable` fully implements the **Runnable interface**.

Supported methods:

| Method     | Description     |
| ---------- | --------------- |
| `invoke()` | Single request  |
| `batch()`  | Multiple inputs |
| `stream()` | Token streaming |

This ensures API consistency between local and remote chains.

---

## 7. Batch Execution Example

```python
chain = RemoteRunnable("http://localhost:8000/summarize")

results = chain.batch([
    {"text": "LangServe is powerful"},
    {"text": "RemoteRunnable enables scaling"}
])

for r in results:
    print(r)
```

### Why Batch Matters

* Fewer network calls
* Higher throughput
* Ideal for data pipelines

---

## 8. Streaming Example

```python
chain = RemoteRunnable("http://localhost:8000/summarize")

for chunk in chain.stream({
    "text": "Explain LangServe streaming"
}):
    print(chunk, end="")
```

### Streaming Benefits

* Real-time token delivery
* Ideal for chat interfaces
* No manual SSE or async handling required

---

## 9. RemoteRunnable with RAG Chains

### Backend

```python
rag_chain = (
    {"context": retriever, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)

add_routes(app, rag_chain, path="/rag")
```

### Client

```python
rag = RemoteRunnable("http://localhost:8000/rag")

answer = rag.invoke({
    "question": "What is LangServe?"
})

print(answer)
```

The client does not need access to:

* Vector databases
* Embeddings
* Retrieval logic

---

## 10. Understanding `/c/<id>` in URLs

You may encounter endpoints like:

```
/summarize/c/N4XyA
```

Meaning:

* `/summarize` → Base route
* `/c/N4XyA` → Compiled chain identifier

Purpose:

* Chain versioning
* Tracing
* Internal lifecycle management

Clients generally do not need to worry about this.

---

## 11. RemoteRunnable vs `requests`

| Feature           | RemoteRunnable | requests |
| ----------------- | -------------- | -------- |
| Runnable API      | Yes            | No       |
| Schema validation | Yes            | No       |
| Streaming         | Built-in       | Manual   |
| Batch support     | Built-in       | Manual   |
| LangChain-native  | Yes            | No       |

`RemoteRunnable` is **LangChain-aware**, not just HTTP-aware.

---

## 12. Common Use Cases

* Frontend → LLM backend communication
* Microservices architecture
* Centralized RAG systems
* Shared AI platforms
* Distributed ML pipelines

---

## 13. When to Use RemoteRunnable

Use it when:

* Chains are hosted remotely
* Logic reuse is required
* You want scalability and versioning
* You want clean separation of concerns

---

## 14. When NOT to Use RemoteRunnable

Avoid it when:

* All logic is local
* Ultra-low latency is critical
* Network communication is restricted

---

## 15. Key Takeaway

> **RemoteRunnable allows a remote LangChain chain to behave exactly like a local chain — without copying code, models, or infrastructure.**

If you understand this sentence, you understand RemoteRunnable.

---

## 16. Summary

RemoteRunnable is a foundational concept in LangServe that enables clean, scalable, and production-ready GenAI architectures by abstracting remote chain execution behind a familiar LangChain interface.

---

**End of Document**
