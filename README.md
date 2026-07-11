# Life Sciences AI Agent

A hybrid healthcare assistant that answers questions using either:

- **SQL Agent** for structured questions over an **Azure SQL Database** (read-only, SELECT/WITH)
- **RAG Agent** for medical questions over unstructured PDFs via **Azure AI Search** vector retrieval

Routing is handled by a **Planner Agent** using **LangGraph**.

> Note: This README intentionally does **not** include any secrets or values from `.env` files.

---

## Architecture (end-to-end)

1. **Planner node** (LLM) chooses one route:
   - `sql` → structured query path
   - `rag` → document retrieval + grounded answering
2. **SQL node** runs:
   - `SQLAgent.generate_sql(question)` → SQL string
   - `SQLValidator.validate(sql)` → safety checks
   - `SQLExecutor.execute(sql)` → returns results as a `pandas.DataFrame`
3. **RAG node** runs:
   - `Retriever.retrieve(question)` → vector search over Azure AI Search
   - `RAGAgent.answer(question)` → LLM answers using only retrieved context
4. **Response node** formats the final answer from the selected agent output.

Key runtime graph: `backend/graph/workflow.py`.

---

## Project layout

- **Entry points / orchestration**
  - `final_response.py` – CLI to chat via the LangGraph workflow
  - `backend/graph/workflow.py` – LangGraph state graph and nodes

- **Agents**
  - `backend/agents/planner_agent.py` – decides route (`sql` or `rag`)
  - `backend/agents/sql_agent_main.py` – orchestration wrapper for SQLAgent
  - `backend/agents/sql_agent.py` – converts question + schema into SQL
  - `backend/agents/sql_validator.py` – SELECT-only policy enforcement
  - `backend/agents/response.py` – final response rewriting/formatting

- **RAG**
  - `backend/rag/rag_agent.py` – grounded answering from retrieved chunks
  - `backend/rag/retriever.py` – embedding + Azure AI Search vector search
  - `backend/rag/embedding_service.py` – Azure OpenAI embeddings
  - `backend/rag/pdf_reader.py` – PDF → page text extraction
  - `backend/rag/text_cleaner.py` – cleaning text (normalization)
  - `backend/rag/chunker.py` – chunking with deterministic chunk IDs
  - `backend/rag/ai_search_service.py` – create index + upload embedded chunks
  - `backend/rag/ingest_documents.py` – end-to-end ingestion pipeline

- **Structured data ingestion (ETL)**
  - `backend/data_ingestion/load_data.py` – loads Synthea CSVs into Azure SQL
  - `backend/data_ingestion/utils.py` – reads required CSV files
  - `backend/data_ingestion/db.py` – DB engine wrapper
  - `backend/data_ingestion/config.py` – list of tables to load

---

## Workflow and functions (documented in sequence)

### 1) LangGraph workflow

File: `backend/graph/workflow.py`

**Graph nodes**
- `planner_node(state: AgentState)`
  - Reads `state["question"]`
  - Calls `PlannerAgent.route(question)`
  - Returns `{ "route": route }`

- `sql_node(state: AgentState)`
  - Reads `state["question"]`
  - Calls `SQLQueryAgent.run(question)`
  - Logs intermediate results
  - Returns `{ "agent_output": result }`

- `rag_node(state: AgentState)`
  - Reads `state["question"]`
  - Calls `RAGAgent.answer(question)`
  - Returns `{ "agent_output": result["answer"], "rag_documents": result["sources"] }`

- `response_node(state: AgentState)`
  - Calls `ResponseAgent.generate_response(...)`
  - Passes:
    - `question=state["question"]`
    - `conversation_history=state["conversation_history"]`
    - `planner=state["route"]`
    - `agent_output=state["agent_output"]`
  - Returns `{ "answer": answer }`

**Graph entry**: `workflow.set_entry_point("planner")`

---

### 2) Planner Agent (SQL vs RAG)

File: `backend/agents/planner_agent.py`

Class: `PlannerAgent`

- `__init__(self)`
  - Creates an LLM via `LLMFactory.get_llm()`
  - Uses `StrOutputParser()`

- `route(self, question: str)`
  - Builds prompt using `backend/prompts/planner_prompt.py` (`PLANNER_PROMPT`)
  - Runs `route = (self.llm | self.parser).invoke(prompt)`
  - Normalizes output with `route.strip().lower()`
  - Returns:
    - `"sql"` if output contains `sql`
    - otherwise `"rag"`

Prompt: `backend/prompts/planner_prompt.py`
- Instructs model to return exactly one word: `sql` or `rag`.

---

### 3) SQL capability (structured database)

#### 3.1 Wrapper orchestration: SQLQueryAgent

File: `backend/agents/sql_agent_main.py`

Class: `SQLQueryAgent`

- `__init__(self)`
  - `self.sql_agent = SQLAgent()`
  - `self.executor = SQLExecutor()`

- `run(self, question: str) -> dict`
  1. `sql = self.sql_agent.generate_sql(question)`
  2. `(valid, message) = SQLValidator.validate(sql)`
  3. If invalid → returns
     `{ "success": False, "sql": sql, "error": message, "data": None }`
  4. Else → `df = self.executor.execute(sql)`
  5. Returns
     `{ "success": True, "sql": sql, "error": None, "data": df }`

#### 3.2 SQL generation: SQLAgent

File: `backend/agents/sql_agent.py`

Class: `SQLAgent`

- `__init__(self)`
  - `self.llm = LLMFactory.get_llm()`
  - `self.schema = SchemaLoader.get_schema()`
  - `self.parser = StrOutputParser()`

- `generate_sql(self, question: str) -> str`
  - Builds prompt containing:
    - `backend/prompts/sql_prompt.py` (`SQL_SYSTEM_PROMPT`)
    - `Database Schema: {self.schema}`
    - `User Question: {question}`
  - Invokes chain `(self.llm | self.parser).invoke(prompt)`
  - Returns `sql.strip()`

Prompt: `backend/prompts/sql_prompt.py`
- Enforces:
  - SELECT-only
  - output is SQL only (no markdown)
  - if not answerable, return a fixed sentence.

#### 3.3 SQL safety: SQLValidator

File: `backend/agents/sql_validator.py`

Class: `SQLValidator`

- `validate(sql: str) -> tuple[bool, str]`
  - Rejects empty SQL
  - Allows only start tokens in `ALLOWED = ["SELECT", "WITH"]`
  - Blocks dangerous keywords in `BLOCKED` (INSERT/UPDATE/DELETE/DDL/DROP/ALTER/EXEC/MERGE/CREATE/etc.)
  - Uses regex word boundaries: `re.search(r"\b{keyword}\b", upper_sql)`

#### 3.4 SQL execution: SQLExecutor

File: `backend/services/sql_executor.py`

Class: `SQLExecutor`

- `__init__(self)`
  - Creates a SQLAlchemy engine via `DatabaseConnection.get_engine()`

- `execute(self, sql: str) -> pandas.DataFrame`
  - Opens a connection and executes SQLAlchemy `text(sql)`
  - Converts `result.fetchall()` and `result.keys()` into a DataFrame

Database engine:
- File: `backend/database/db_connection.py`
- Function: `DatabaseConnection.get_engine()`
  - Builds an ODBC connection string for SQL Server
  - Uses `sqlalchemy.create_engine(...)`

---

### 4) RAG capability (unstructured documents)

#### 4.1 Retrieving relevant chunks

File: `backend/rag/retriever.py`

Class: `Retriever`

- `__init__(self)`
  - Creates `EmbeddingService()`
  - Creates `SearchClient(...)` for Azure AI Search

- `vector_search(self, query_embedding, top_k=5) -> list[dict]`
  - Builds a `VectorizedQuery` over field `contentVector`
  - Calls `self.search_client.search(...)`
  - Returns documents with:
    - `content`, `source`, `page`, and `score` (`@search.score`)

- `retrieve(self, question, top_k=5) -> list[dict]`
  - Embeds the user query via `self.embedding_service.embed_text(question)`
  - Calls `vector_search(...)`

Embedding service:
- File: `backend/rag/embedding_service.py`
- Class: `EmbeddingService`
  - `embed_text(text: str)` → `embedding_model.embed_query(text)`
  - `embed_documents(documents: list[str])`

#### 4.2 Answering grounded in context

File: `backend/rag/rag_agent.py`

Class: `RAGAgent`

- `__init__(self)`
  - `self.llm = LLMFactory.get_llm()`
  - `self.retriever = Retriever()`
  - `self.parser = StrOutputParser()`

- `_build_context(self, documents)`
  - Formats each retrieved chunk into:
    - `Document i`, `Source`, `Page`, and `content`

- `answer(self, question: str) -> dict`
  1. `documents = self.retriever.retrieve(question)`
  2. `context = self._build_context(documents)`
  3. Creates a prompt that includes `RAG_SYSTEM_PROMPT` + `Context:` + `User Question:`
  4. Runs `chain = self.llm | self.parser` and invokes it
  5. Returns:
     - `"answer"`: model response (stripped)
     - `"sources"`: list of `{ "source": ..., "page": ... }`

System prompt: embedded in `RAGAgent` as `RAG_SYSTEM_PROMPT`.
- Instructs the model to answer **ONLY** from the provided context.

---

### 5) Final response formatting

File: `backend/agents/response.py`

Class: `ResponseAgent`

- `__init__(self)`
  - Creates `self.llm = LLMFactory.get_llm()`
  - Creates `self.chain = PROMPT | self.llm`

- `_format_agent_output(self, agent_output)`
  - If `agent_output` is a `pandas.DataFrame`, converts to string via `to_string(index=False)`
  - If dict: converts any DataFrame values similarly
  - Otherwise returns as-is

- `generate_response(self, question, conversation_history, planner, agent_output)`
  - Formats agent output with `_format_agent_output`
  - Invokes the chain with:
    - `question`, `conversation_history`, `planner`, `agent_output`
  - Returns `response.content`

Rules in `PROMPT`:
- Never use internal knowledge; only rewrite agent output.
- For `planner == "sql"` it summarizes/phrases results.
- For `planner == "rag"` it preserves factual content and only improves wording.

---

## CLI chat entry point

File: `final_response.py`

This provides a terminal loop using the LangGraph graph.

Main functions:
- `load_memory()` / `save_memory(memory)`
- `add_message(memory, thread_id, role, content)`
- `build_prompt(memory, thread_id, question)`
  - Builds a text block containing last `MAX_HISTORY` messages
- `run_cli()`
  - Repeatedly:
    - reads user input
    - appends message to memory
    - calls `graph.invoke({"question": ..., "conversation_history": prompt})`
    - prints assistant answer

---

## Ingestion / ETL pipelines

### 1) Structured data ingestion into Azure SQL (Synthea CSVs)

File: `main.py`

Main functions:
- `infer_sqlalchemy_types(df)`
  - Maps pandas dtypes → SQLAlchemy types (BIGINT/FLOAT/BOOLEAN/DateTime/DATE/NVARCHAR)

- `load_table(engine, table_name)`
  - Loads table CSV via `read_csv(table_name)`
  - Infers types
  - Loads into SQL with `df.to_sql(... if_exists="replace", ...)`

- `validate(engine)`
  - For each table in `backend/data_ingestion/config.py` (`FILES_TO_LOAD`) runs `SELECT COUNT(*)`

Dependencies:
- `backend/data_ingestion/utils.py` reads:
  - `datasets/structured/synthea/required_files/{table_name}.csv`

### 2) Unstructured document ingestion into Azure AI Search (PDF → chunks → embeddings → upload)

File: `backend/rag/ingest_documents.py`

Main flow in `main()`:
- `PDFReader.read_folder(PDF_FOLDER)`
- `DocumentChunker().chunk_documents(pdfs)`
- `EmbeddingService()`
- `AISearchService().upload_documents(chunks, embedding_service, batch_size=...)`

Key classes:
- `backend/rag/pdf_reader.py`: uses `fitz` to extract page text per PDF
- `backend/rag/chunker.py`: uses `RecursiveCharacterTextSplitter` and deterministic SHA256 chunk IDs
- `backend/rag/ai_search_service.py`:
  - `create_index()` defines:
    - fields: `id` (key), `content`, `source`, `page`, `contentVector` (vector dim = 1536)
  - `upload_documents(...)` batches embeddings and uploads documents

---

## LLM providers

LLM selection is centralized in:
- `backend/config/llm_factory.py`

Class: `LLMFactory`
- `get_llm()` chooses based on `settings.LLM_PROVIDER`:
  - `groq` → `ChatGroq`
  - `ollama` → `ChatOllama`
  - `azure` → `AzureChatOpenAI`

---

## Configuration (environment variables)

Configuration is loaded via `python-dotenv` from the environment.

Files:
- `backend/config/settings.py` (defines expected variable names)
- `backend/config/llm_factory.py` (selects provider)
- RAG/SQL/Azure clients also read variables via `os.getenv(...)`

### Important variables (names only; no values)

- **LLM**
  - `LLM_PROVIDER`
  - Groq: `GROQ_API_KEY`, `GROQ_MODEL`
  - Ollama: `OLLAMA_BASE_URL`, `OLLAMA_MODEL`
  - Azure OpenAI: `AZURE_OPENAI_API_KEY`, `AZURE_OPENAI_ENDPOINT`, `AZURE_OPENAI_DEPLOYMENT`, `AZURE_OPENAI_API_VERSION`

- **Azure SQL**
  - `AZURE_SQL_SERVER`, `AZURE_SQL_DATABASE`, `AZURE_SQL_USERNAME`, `AZURE_SQL_PASSWORD`, `AZURE_SQL_DRIVER`

- **Azure AI Search**
  - `AZURE_SEARCH_ENDPOINT`, `AZURE_SEARCH_API_KEY`, `AZURE_SEARCH_INDEX`

- **Embeddings**
  - `AZURE_OPENAI_EMBEDDING_DEPLOYMENT`

---

## Safety and constraints

- SQL generation is constrained by:
  - `SQL_SYSTEM_PROMPT` (SELECT-only requirement)
  - `SQLValidator` (allowlist/blocklist keyword checks)

- RAG answers are constrained by:
  - `RAG_SYSTEM_PROMPT` requiring answers to be based **ONLY** on retrieved context

- Final output formatting:
  - `ResponseAgent` instructs the model not to add new facts beyond the selected agent output

---

## Dependencies

From `requirements.txt` and imports, the project uses:

- Web: `fastapi`, `uvicorn`
- LLM & orchestration: `langchain`, `langchain-openai`, `langgraph`, `langchain-groq`, `langchain-ollama`
- Data/SQL: `pandas`, `sqlalchemy`, `pyodbc`
- Azure: `azure-search-documents`, `azure-storage-blob`
- PDF: `pypdf` is listed; PDF extraction code uses `fitz` (PyMuPDF)
- UI: `streamlit` (frontend under `frontend/`)

---

## Running the project

### 1) Install dependencies

```bash
pip install -r requirements.txt
```

### 2) ETL (structured + embeddings + AI Search)

- Structured SQL ETL is implemented in `main.py`.
- Unstructured document ingestion is implemented in `backend/rag/ingest_documents.py`.

### 3) Chat (CLI)

```bash
python final_response.py
```

---

## Known gaps / notes

- `backend/graph/workflow.py` uses state fields such as `conversation_history` and `agent_output`.
- `backend/models/state.py` defines a TypedDict, but the workflow passes/returns payloads that may not fully align with that type.
- Some earlier documentation is in `ARCHITECTURE_AND_PRODUCTION_DOCS.md`.
- PDF extraction code uses `fitz` (PyMuPDF), while `requirements.txt` lists `pypdf`.

---

## Devloped By-

- Yuvraj Singh

