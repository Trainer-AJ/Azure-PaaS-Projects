---
lab:
    title: 'Implement Retrieval Augmented Generation (RAG) with Azure OpenAI Service'
---

# Architecture 
![](./Screenshot%202024-09-27%20211820.png)

# sample env file
```py
AZURE_OAI_ENDPOINT="https://frontend-for-app.openai.azure.com/"
AZURE_OAI_KEY=""
### use embedding Model name gives error auto completion not possible
AZURE_OAI_DEPLOYMENT="gpt-35-turbo-16k"
AZURE_SEARCH_ENDPOINT="https://let-ai-search-my-docs.search.windows.net"
AZURE_SEARCH_KEY=""
AZURE_SEARCH_INDEX="my-data"
```