# Life Sciences AI Agent — Architecture & Production Documentation

## 1. What this project does
**life-sciences-ai-agent** is a hybrid healthcare assistant that answers user questions using one of two backends:

1. **SQL Agent (structured data)**: Generates **read-only SQL** (SELECT/WITH) against **Azure SQL Database**, validates it, executes it via SQLAlchemy + ODBC, and returns results.
2. **RAG Agent (unstructured medical documents)**: Retrieves relevant document chunks from **Azure AI Search** (vector index), then uses an LLM to answer **only from retrieved context**.

Routing between SQL and RAG is performed by an **LLM-based Planner Agent** orchestrated with **LangGraph**.

---

## 2. Runtime architecture (end-to-end flow)
### 2.1 Request flow (current implementation)
1. **LangGraph workflow** starts at the **planner node**.
2. **PlannerAgent** selects the route:
   - `sql` for patient data / database-oriented questions
   - `rag` for symptoms/guidelines/treatment information
3. LangGraph conditionally routes to:
   - **SQL node** → `SQLQueryAgent.run(question)`
   - **RAG node** → `RAGAgent.answer(question)`
4. The graph terminates (END) after producing the final answer.

### 2.2 Important files for the runtime graph
- `backend/graph/workflow.py`
  - Builds a `StateGraph(AgentState)`
  - Nodes:
    - `planner_node`
    - `sql_node`
    - `rag_node`
  - Conditional edges:
    - planner → router(state["route"]) → `sql` or `rag`

---

## 3. Repository structure (modules, files, responsibilities)

### 3.1 Entry points & server
- `main.py`
  - Entry point (not inspected in this session). Document expected behavior here when finalized.
- `backend/api/routes.py`
  - FastAPI routing placeholder (file currently empty in inspected snapshot).

### 3.2 Orchestration (LangGraph)
- `backend/graph/workflow.py`
  - Creates single instances (module-level):
    - `planner = PlannerAgent()`
    - `sql_agent = SQLQueryAgent()`
    - `rag_agent = RAGAgent()`
  - Node functions:
    - `planner_node(state: AgentState)`
      - Reads `state["question"]`
      - Calls `planner.route(question)`
      - Returns `{"route": route}`
    - `sql_node(state: AgentState)`
      - Calls `sql_agent.run(question)`
      - Returns `{"answer": result}`
    - `rag_node(state: AgentState)`
      - Calls `rag_agent.answer(question)`
      - Returns `{"answer": result["answer"], "rag_documents": result["sources"]}`
  - Router:
    - `router(state)` returns `state["route"]`

### 3.3 Shared state contract
- `backend/models/state.py`
  - `AgentState(TypedDict)`
  - Fields:
    - `messages: List[BaseMessage]`
    - `question: str`
    - `route: str`
    - `answer: str`
    - `sql_query: str`
    - `sql_result: Any`
    - `rag_documents: List[Dict]`
    - `rag_answer: str`

> **Production note**: The current workflow returns `answer` as an object sometimes (`result` dict from SQL). The `AgentState` type suggests `answer: str`. Document the current payload shape and consider aligning types.

### 3.4 Planner agent (SQL vs RAG routing)
- `backend/agents/planner_agent.py`
  - `PlannerAgent.__init__()`
    - `self.llm = LLMFactory.get_llm()`
    - `self.parser = StrOutputParser()`
  - `PlannerAgent.route(question: str) -> str`
    - Builds prompt using `backend/prompts/planner_prompt.py` constant `PLANNER_PROMPT`
    - Executes `chain = self.llm | self.parser`
    - Normalizes output: `route.strip().lower()`
    - Returns:
      - `sql` if the LLM output contains/indicates sql
      - `rag` otherwise

### 3.5 Prompt templates
- `backend/prompts/planner_prompt.py`
  - `PLANNER_PROMPT`
  - Instructs the LLM to output **exactly**: `sql` or `rag`
  - Includes guidance for when to choose sql vs rag

---

## 4. SQL capability (structured data)
### 4.1 SQL agent modules
- `backend/agents/sql_agent_main.py`
  - `SQLQueryAgent`
  - `run(question: str) -> dict`
    1. `sql = self.sql_agent.generate_sql(question)`
    2. `valid, message = SQLValidator.validate(sql)`
    3. If invalid → returns `{success: False, sql, error: message, data: None}`
    4. Else executes: `df = self.executor.execute(sql)`
    5. Returns `{success: True, sql, error: None, data: df}`

- `backend/agents/sql_agent.py`
  - `SQLAgent`
  - `generate_sql(question: str) -> str`
    - Builds prompt from:
      - `backend/prompts/sql_prompt.py` → `SQL_SYSTEM_PROMPT`
      - `SchemaLoader.get_schema()` output (all tables/columns)
      - user question
    - Runs `(self.llm | self.parser).invoke(prompt)`
    - Returns `sql.strip()`

- `backend/agents/sql_validator.py`
  - `SQLValidator`
  - Policy:
    - Allowed start keywords: `SELECT`, `WITH`
    - Blocked keywords: `INSERT, UPDATE, DELETE, DROP, ALTER, TRUNCATE, EXEC, MERGE, CREATE`
    - Uses regex word boundaries `\b{keyword}\b` over uppercased SQL

- `backend/services/sql_executor.py`
  - `SQLExecutor`
  - `execute(sql: str) -> pandas.DataFrame`
    - Executes with SQLAlchemy `text(sql)`
    - Builds DataFrame from `result.fetchall()` and `result.keys()`

### 4.2 Schema context generation
- `backend/database/schema_loader.py`
  - `SchemaLoader.get_schema() -> str`
    - Queries `INFORMATION_SCHEMA.TABLES` to list base tables
    - For each table:
      - Queries `INFORMATION_SCHEMA.COLUMNS` for `COLUMN_NAME` and `DATA_TYPE`
    - Produces a large textual schema description used in the SQL LLM prompt

> **Production note**: Schema generation is dynamic and can be expensive on large databases. Consider caching (startup cache with TTL) in production.

### 4.3 SQL prompt contract
- `backend/prompts/sql_prompt.py`
  - `SQL_SYSTEM_PROMPT`:
    - Generates **valid Microsoft SQL Server query**
    - Only SELECT (no mutating statements)
    - Uses only schema-provided tables/columns
    - Returns **ONLY** SQL query text (no markdown)
    - If cannot answer with schema: `I cannot answer this question using the available database.`

---

## 5. RAG capability (unstructured documents)
### 5.1 RAG agent modules
- `backend/rag/rag_agent.py`
  - `RAGAgent.__init__()`:
    - `self.llm = LLMFactory.get_llm()`
    - `self.retriever = Retriever()`
    - `self.parser = StrOutputParser()`
  - `_build_context(documents)`:
    - Formats retrieved chunks as `Document i` with `source`, `page`, `content`
  - `answer(question: str) -> {answer, sources}`:
    - `documents = self.retriever.retrieve(question)`
    - Builds prompt using `RAG_SYSTEM_PROMPT` + `Context:` + `User Question:`
    - Invokes LLM `(self.llm | self.parser)`
    - Returns:
      - `answer`: `answer.strip()`
      - `sources`: list of `{source, page}`

- `backend/rag/retriever.py`
  - Embeds the user question with `EmbeddingService`
  - Uses Azure AI Search vector query over `contentVector`
  - Retrieves `content`, `source`, `page` with `top_k` default 5

- `backend/rag/embedding_service.py`
  - Uses `langchain_openai.AzureOpenAIEmbeddings`
  - `embed_text()` → `embed_query()`
  - `embed_documents()` for ingestion

### 5.2 Azure AI Search index + ingestion
- `backend/rag/ai_search_service.py`
  - `create_index()` creates a vector index:
    - fields: `content`, `source`, `page`, vector field `contentVector`
    - vector dimensions hard-coded to `1536`
  - `upload_documents(...)`:
    - batch embeds chunks
    - uploads docs with `{id, content, source, page, contentVector}`

> **Production note**: Ensure embedding dimension matches `1536`.

### 5.3 Document preprocessing
- `backend/rag/pdf_reader.py`:
  - Uses `fitz` (PyMuPDF) to extract page text
  - Cleans each page using `TextCleaner`
  - Supports reading folders of PDFs

- `backend/rag/text_cleaner.py`:
  - whitespace normalization, null removal, trimming

- `backend/rag/chunker.py`:
  - chunking via `RecursiveCharacterTextSplitter`
  - deterministic SHA256 chunk ids

- `backend/rag/ingest_documents.py`:
  - end-to-end ingestion script (PDF → chunk → embed → AI Search upload)

- `backend/rag/blob_reader.py`:
  - optional utility to list/download PDFs from Azure Blob Storage

---

## 6. Structured data ingestion (ETL to Azure SQL)
- `backend/data_ingestion/load_data.py`:
  - Infers SQLAlchemy types from pandas dtypes
  - Loads CSV tables into Azure SQL via `df.to_sql(... if_exists="replace")`
  - Validates by printing row counts

- `backend/data_ingestion/utils.py`:
  - `read_csv(table_name)` reads from `datasets/structured/synthea/required_files/`

---

## 7. Libraries used (by area)
From `requirements.txt` and code imports:
- **Web**: `fastapi`, `uvicorn`, `python-multipart`
- **LLM/Orchestration**: `langgraph`, `langchain*`, `langchain_text_splitters`
- **LLM Providers**: `langchain-groq`, `langchain-ollama`, `langchain-openai`
- **SQL**: `sqlalchemy`, `pyodbc`, `pandas`
- **Azure AI Search**: `azure-search-documents`
- **Embeddings**: `AzureOpenAIEmbeddings`
- **Storage**: `azure-storage-blob`
- **PDF**: `pypdf` in requirements; code uses `fitz` (PyMuPDF)

---

## 8. Production documentation: critical points
### 8.1 Configuration & secrets
- `backend/config/settings.py` loads environment variables via `python-dotenv`.
- LLM selection is done by `backend/config/llm_factory.py` using `settings.LLM_PROVIDER`.

Document required env vars for:
- **Groq** (`GROQ_API_KEY`, `GROQ_MODEL`)
- **Ollama** (`OLLAMA_BASE_URL`, `OLLAMA_MODEL`)
- **Azure OpenAI** (`AZURE_OPENAI_*`, `AZURE_OPENAI_DEPLOYMENT`)
- **Azure SQL** (`AZURE_SQL_*`)
- **Azure AI Search** (`AZURE_SEARCH_ENDPOINT`, `AZURE_SEARCH_INDEX`, `AZURE_SEARCH_API_KEY`)

### 8.2 Safety
- SQL safety is enforced with allowlist/blocklist in `SQLValidator`.
- RAG answers are constrained with `RAG_SYSTEM_PROMPT` (answer only from provided context).

### 8.3 Observability
Current implementation uses `print()`. Production docs should require structured logging, correlation ids, and redaction of secrets.

### 8.4 Performance & cost
- embedding batching during ingestion (`EMBEDDING_BATCH_SIZE`)
- chunk sizing/overlap (`chunk_size=1000`, `chunk_overlap=200`)
- vector retrieval `top_k=5`
- LLM `temperature=0`

### 8.5 Reliability & failure modes
Document expected outputs for:
- SQL invalid queries (`success=False`)
- empty RAG retrieval (LLM returns fallback statement)
- Azure service connectivity failures

### 8.6 Deployment on Azure
Document:
- Azure services mapping (SQL, Storage, AI Search, App Service)
- readiness/liveness endpoints and env var injection method

---

## 9. Known gaps / documentation TODOs (current snapshot)
- `backend/api/routes.py` is present but not inspected in this final pass; FastAPI endpoints should be documented once implemented.
- `backend/workflows/` directory exists, but no files were found during inspection (confirm intended workflow placement).
- `requirements.txt` includes `pypdf`, but RAG extraction uses `fitz` (PyMuPDF). Align dependencies and document the PDF engine.
- `backend/models/state.py` defines `answer: str`, but `backend/graph/workflow.py` stores SQL node output as `{"answer": result}` (a dict payload). Document the actual API/return contract and/or refactor state typing.

## 10. What to add next (recommended for true production readiness)
- **Response Contract / API Schema**: define JSON request/response bodies, including how SQL results (DataFrame) are serialized.
- **Error handling strategy**: timeouts/retries/backoff for LLM calls, Azure Search, and Azure SQL; standardized error objects.
- **Observability**: replace `print()` with structured logging and add request correlation IDs.
- **Caching**:
  - cache `SchemaLoader.get_schema()` result to avoid repeated DB metadata scans
  - optionally cache embeddings for repeated queries
- **Security hardening**:
  - improve SQL validation using SQL parsing (AST) instead of keyword regex
  - sanitize/limit LLM output length and enforce SQL max row limits



