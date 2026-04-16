# Kortex Development Roadmap

## Phase 1: Core Reliability & Validation
- [x] **Task 1: Automated Evaluation Reporting**
    - [x] Create synthetic benchmark dataset (queries + ground truth)
    - [x] Implement `scripts/run_evaluation.py`
    - [x] Generate automated performance reports (JSON/Markdown)
- [x] **Task 3: Robust Hallucination Guardrails**
    - [x] Implement Faithfulness/NLI checks for every claim
    - [x] Integrate secondary validation for "I don't know" responses

## Phase 2: Agentic Intelligence
- [x] **Task 2: Dynamic Agentic Workflow (ReAct/Plan-Execute)**
    - [x] Refactor Orchestrator to support autonomous tool selection
    - [x] Implement iterative reasoning loops
- [x] **Task 6: Dedicated Summarization Tool**
    - [x] Create specialized agent for long-form document/ticket summarization
- [x] **Task 4: Duplicate Ticket Detection**
    - [x] Implement semantic similarity flags for existing tickets

## Phase 3: Data & Infrastructure
- [x] **Task 5: Advanced Chunking Strategy**
    - [x] Implement recursive character splitting and header-aware chunking
- [x] **Task 7: Incremental Data Ingestion**
    - [x] Add hashing/timestamp tracking to avoid re-indexing
- [x] **Task 8: Operations & Deployment (DevOps)**
    - [x] Create Dockerfile and docker-compose.yml for full-stack deployment
