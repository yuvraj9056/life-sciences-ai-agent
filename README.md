                    User
                      │
                      ▼
               FastAPI Backend
                      │
                      ▼
              Planner Agent
                      │
      ┌───────────────┼────────────────┐
      │               │                │
      ▼               ▼                ▼
 SQL Agent      RAG Agent      Analytics Agent
      │               │                │
      ▼               ▼                ▼
 Azure SQL     Azure AI Search     Pandas/SQL
      │               │                │
      └───────────────┼────────────────┘
                      ▼
            Response Composer
                      │
                      ▼
                 Final Answer


Project Roadmap:
✅ Project Setup
✅ LLM Factory
✅ Planner Agent
Shared Models & LangGraph State
LangGraph Workflow
Azure SQL + Data Ingestion
Azure AI Search + RAG
SQL Agent
RAG Agent
Analytics Agent
Response Agent
MCP Tools
FastAPI APIs
Frontend
Azure Deployment
GitHub Documentation

Azure Architecture:
Azure
│
├── Resource Group
│
├── Azure SQL
│      │
│      └── LifeSciencesDB
│
├── Storage Account
│      │
│      └── documents/
│
├── Azure AI Search
│
└── Azure AI Foundry

SQL Agent → Azure SQL
RAG Agent → Azure AI Search
Blob Storage → Document source
FastAPI → Azure App Service (later)

