# ToonDB Python Examples

Official Python examples for ToonDB - the high-performance embedded database for AI applications. This repository showcases integration patterns with popular agent frameworks and demonstrates ToonDB's unique features.

## 📂 Repository Structure

```
toondb-python-examples/
├── agent_memory/          # Production agent memory system with HNSW index
├── azure_openai/          # Azure OpenAI integration examples
├── complete_examples/     # Framework integrations (LangGraph, AutoGen, CrewAI)
├── context_builder/       # Token-budget aware context assembly
├── ecommerce/             # eCommerce product catalog RAG
├── langgraph/             # LangGraph checkpointer and memory
├── podcast/               # Podcast transcript search
├── rag/                   # Complete RAG pipeline
├── wizard_of_oz/          # Long-form text ingestion
└── zep/                   # Zep-compatible examples
```

## 🚀 Quick Start

### Prerequisites

- Python 3.10+ installed
- ToonDB Python SDK: `toondb-client>=0.3.1`

### Installation

```bash
pip install toondb-client>=0.3.1
```

## 📚 Examples by Category

### 🧠 Agent Memory & State

#### 1. Agent Memory (`agent_memory/`)

**Production-ready agent memory system** with vector search and HNSW index.

**Features**:
- Long-term memory with semantic search
- Session-based memory management  
- Time-weighted retrieval
- Performance tracking and metrics
- HNSW vector index for fast similarity search

**Use Cases**: Multi-turn conversations, customer support agents, research assistants

```bash
cd agent_memory
pip install -r requirements.txt
python main.py
```

---

#### 2. LangGraph Integration (`langgraph/`)

**Best for**: Building stateful LangGraph agents with persistent memory.

**Features**:
- Custom ToonDB checkpointer for graph state
- Long-term memory store for user interactions
- Time-weighted context retrieval
- Seamless LangGraph integration

```bash
cd langgraph
pip install -r requirements.txt  
python agent_with_toondb.py
```

---

#### 3. Context Query Builder (`context_builder/`)

**Best for**: Managing LLM context under strict token budgets.

**Features**:
- Priority-based content truncation
- Token budget management
- Intelligent context assembly
- System + user + history + retrieval

**Demonstrated Scenarios**:
- Ample budget (4000 tokens)
- Tight budget (500 tokens)
- ToonDB integration with TOON format

```bash
cd context_builder
pip install -r requirements.txt
python runner.py
```

---

### 🔍 RAG & Retrieval Examples

#### 4. RAG Pipeline (`rag/`)

**Complete production RAG system** with document ingestion, chunking, and query pipeline.

**Features**:
- Document ingestion and chunking
- Azure OpenAI embeddings
- Vector search with ToonDB
- Generation with context

```bash
cd rag
pip install -r requirements.txt
python main.py
```

---

#### 5. eCommerce RAG (`ecommerce/`)

**Best for**: Product catalogs, shopping assistants, recommendation systems.

**Features**:
- Hybrid search (semantic + metadata filtering)
- TOON format for compact results
- Structured product data ingestion
- **100% accuracy** on test queries

```bash
cd ecommerce
pip install -r requirements.txt
python runner.py
```

---

#### 6. Azure OpenAI ("California Politics") (`azure_openai/`)

**Best for**: Fact retrieval systems with Azure OpenAI.

**Features**:
- Entity-focused retrieval (Kamala Harris, Gavin Newsom)
- High-precision fact extraction
- Azure OpenAI embeddings and chat
- **100% accuracy** on political facts

```bash
cd azure_openai
pip install -r requirements.txt
python runner.py
```

---

### 📖 Document & Text Processing

#### 7. Wizard of Oz (`wizard_of_oz/`)

**Best for**: Long-context narrative understanding, book ingestion.

**Features**:
- Paragraph-based chunking
- Semantic search over narrative text
- Character and plot retrieval
- **100% accuracy** on story queries

```bash
cd wizard_of_oz
pip install -r requirements.txt
python runner.py
```

---

#### 8. Podcast Search (`podcast/`)

**Best for**: Audio transcripts, meeting notes, multi-speaker dialogue.

**Features**:
- Speaker attribution parsing
- Timestamp preservation
- Turn-based segmentation
- **100% accuracy** on speaker/topic queries

```bash
cd podcast
pip install -r requirements.txt
python runner.py
```

---

### 🛠️ Framework Integrations

#### 9. Complete Examples (`complete_examples/`)

**Multi-framework integrations** showing ToonDB with various agent frameworks.

**Included**:
- LangGraph agent with ToonDB memory
- AutoGen multi-agent with ToonDB
- Chat history management
- Graph-based examples

```bash
cd complete_examples
pip install -r requirements.txt
# Run individual examples
python langgraph_agent_with_toondb.py
```

---

#### 10. Zep Port (`zep/`)

**Best for**: Users migrating from Zep or needing entity-centric memory.

**Features**:
- Entity extraction and storage
- User profile management
- Conversation thread tracking
- Zep-compatible API patterns

```bash
cd zep
pip install -r requirements.txt
python toondb_simple.py
```

---

## 🔑 Key ToonDB Features Demonstrated

- **TOON Format**: Token-efficient output format (`Database.to_toon()`)
- **Vector Search**: Built-in HNSW index for semantic similarity
- **ACID Transactions**: Group commits with Snapshot Isolation
- **Columnar Storage**: Efficient projection-based reads
- **SQL Support**: Optional SQL interface via IPC mode
- **Embedded Mode**: Zero-config, file-based database

## 📖 Documentation

- [ToonDB Documentation](https://toondb.io)
- [Python SDK (PyPI)](https://pypi.org/project/toondb-client/)
- [API Reference](https://toondb.io/docs/python-sdk)

## ✅ Accuracy Testing

All examples include `accuracy_test.py` scripts with verified results:

| Example | Accuracy | Test Cases |
|---------|----------|------------|
| eCommerce | 100% | 4/4 |
| Azure OpenAI | 100% | 4/4 |
| Wizard of Oz | 100% | 3/3 |
| Podcast | 100% | 4/4 |

## 🤝 Contributing

We welcome contributions! Please submit Pull Requests with:
- New example implementations
- Improvements to existing examples  
- Documentation enhancements
- Bug fixes

## 📄 License

Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

## 🔗 Related Repositories

- [toondb/toondb](https://github.com/toondb/toondb) - Main ToonDB repository
- [toondb/toondb-go](https://github.com/toondb/toondb-go) - Go SDK
- [toondb/toondb-golang-examples](https://github.com/toondb/toondb-golang-examples) - Go examples
- [toondb/toondb-examples](https://github.com/toondb/toondb-examples) - Multi-language examples
