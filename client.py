from langserve import RemoteRunnable

chain = RemoteRunnable("http://localhost:8000/summarize/c/N4XyA")
res=chain.invoke({"text":"Building an LLM-based application is more complex than simply calling an API. While integrating an LLM into your project can significantly enhance its capabilities, it comes with a unique set of challenges that require careful consideration. Below, we'll break down the primary obstacles you might encounter and highlight the aspects of deployment that need attention."})
print(res)