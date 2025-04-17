# Chat Summarization System Design

## 1. Differences from Grammarly System Design

| Area                | Grammarly System Design                                 | Chat Summarization System                                              |
|---------------------|---------------------------------------------------------|------------------------------------------------------------------------|
| Input               | Real-time, short-form user text (per keystroke)         | Full chat history (possibly long-form)                                 |
| Output              | Grammar or style suggestions                            | One-shot summary of the entire conversation                            |
| Latency Constraints | Ultra low latency (<100ms), operates inline with typing | Precomputed summaries; latency is acceptable if pre-generated          |
| Model Type          | Lightweight, possibly hybrid rule-based + ML            | Large-scale transformer (e.g., Google's custom model)                  |
| Architecture Focus  | Client-focused (edge or in-memory)                      | Server-centric with cloud inference (e.g., on TPUs or GPUs)            |
| Persistence Needs   | Minimal or none                                         | Requires persistent storage of chat and generated summaries            |
| Feedback Mechanism  | May offer real-time corrections                         | Requires structured feedback (e.g., thumbs up/down on summary quality) |

## 2. System Design Document


### a. Assumptions
- Chat data is accessible from Google Chat's backend via an internal service
- Summarization model is already trained and accessible via API (hosted on Vertex AI or any internal infra)
- Chat summaries are stored once generated
- Regeneration is only needed on content change
- Summaries must be quickly accessible via API
- Privacy and access control policies are enforced externally (handled by infra team)
- Product team will use summaries in Google Chat UI and via internal API

### b. Objectives
- Provide a system to generate and serve summaries of chat conversations
- Expose a lightweight API:
  ```
  GET /summary/{chat_id} → returns JSON { "chat_id": ..., "summary": ... }
  ```
- Ensure low response time at API layer (<300ms, assuming summaries are cached)
- Maintain flexibility to update summaries if chat content changes

### c. Framing
- Problem Type: Text summarization
- System Mode: Offline/nearline generation; online serving
- ML Role: Model generates natural language summary from full chat context
- API Role: Serve summaries on request, possibly trigger generation if missing

### d. Constraints
- Latency target at API response: <300ms
- Chat content must be encrypted at rest and in transit
- Offloaded to batch/async pipeline
- No storage limitations
- Summary must remain under a specific token or character limit (e.g., 3 sentences)

## 3. Pipelines

### a. Summarization Pipeline (Offline/Batch)
**Trigger:** Every new or updated chat thread
**Steps:**
1. Fetch chat from Chat Store
2. Preprocess (remove emojis, noise, fix formatting)
3. Run through summarization model (e.g., Pegasus)
4. Store output in Summary Storage with metadata

### b. Online Serving API
- Fetches from Summary Storage 
- If not found, returns fallback ("Summary not available") or triggers async job

### c. Database Schemas

**`chats` Table**
| Field | Type | 
|-------|------|
| chat_id | STRING (PK) |
| participants | ARRAY |
| timestamp | DATETIME |
| messages | JSON |

**`chat_summaries` Table**
| Field | Type |
|-------|------|
| chat_id | STRING (PK) |
| summary | TEXT |
| model_version | STRING |
| generated_at | TIMESTAMP |
| feedback | JSON |

**`summary_feedback` Table**
| Field | Type |
|-------|------|
| chat_id | STRING |
| user_id | STRING |
| feedback | ENUM |
| timestamp | DATETIME |

### d. Evaluation
**Annotation Collection:**
- Human-generated summaries from product testers or labelers
- "Was this summary helpful?" feedback from users

**Evaluation Metrics:**
- Models for comparing summaries
- User rating %
- Latency and cache hit rate

### e. Risks / Edge Cases

| Risk | Mitigation |
|------|------------|
| Model hallucinates content | Use factual consistency metrics, human evals |
| Chat changes after summary | Auto-trigger regeneration if chat is edited |
| Summary too long | Enforce token limit (e.g., 100 words) during generation |
| Privacy breach | Encrypt data, role-based access control |
| Multiple languages | Ensure model is multilingual or route per language |

## 4. System Architecture Diagrams

### a. High-Level System Flow
```
+-------------------+       +----------------+        +------------------------+
|   Chat Store DB   +-----> | Preprocessing  +----->  | Summarization Model    |
| (chat_id, text)   |       +----------------+        | (Google Research API)  |
+-------------------+                                 +------------------------+
         |                                                       |
         v                                                       v
+-------------------+                                  +-------------------+
| Summary Storage   |              +------------------ | API Endpoint      |
| (chat_id, text)   | <-----------+                   | (Cloud Function)  |
+-------------------+                                  +-------------------+
         ^                                                       ^
         |                                                       |
+-------------------+                                  +-------------------+
| Chat UI/Frontend  | <--------------------------------| GET /summary     |
| (Summary Box)     |                                  | request          |
+-------------------+                                  +-------------------+
```

**Notes on High-Level Flow:**
1. **Data Ingestion**: Chat Store DB contains the raw conversation data
2. **Processing Stage**: 
   - Preprocessing removes noise, formats text, and prepares for summarization
   - Summarization Model generates concise summaries using Google's Research API
3. **Storage & Serving**:
   - Summaries are stored in dedicated storage for quick retrieval
   - API Endpoint serves as the interface for frontend requests
4. **Frontend Access**:
   - Chat UI requests summaries via GET /summary endpoint
   - Summaries are displayed in a dedicated Summary Box in the UI

### b. Data Processing Pipeline
```
+---------------+     +------------------+     +-------------------+
|  Chat Store   | --> | Preprocessing    | --> | Summary Model     |
+---------------+     +------------------+     +-------------------+
        |                                              |
        v                                              v
+---------------+                            +-------------------+
| Change        |                            | Summary Storage   |
| Detection     |                            +-------------------+
+---------------+                                     |
        |                                            v
        v                                    +-------------------+
+---------------+                            | Cache Layer       |
| Regeneration  |                            +-------------------+
| Trigger       |                                     |
+---------------+                                     v
                                            +-------------------+
                                            | API Gateway       |
                                            +-------------------+
                                                     |
                                                     v
                                            +-------------------+
                                            | Chat UI          |
                                            +-------------------+
```

**Notes on Data Processing Pipeline:**
1. **Batch Processing Flow**:
   - Change Detection monitors for updates in chat content
   - Regeneration Trigger initiates new summary creation when needed
   - Preprocessing prepares data for model consumption

2. **Serving Path**:
   - Cache Layer provides fast access to frequently requested summaries
   - API Gateway handles all external requests
   - Summary Storage maintains persistent storage of generated summaries

3. **Key Features**:
   - Asynchronous processing for better scalability
   - Caching for improved response times
   - Change detection for keeping summaries up-to-date

4. **Performance Considerations**:
   - Cache hit rate affects overall system latency
   - Batch processing reduces load on summarization model
   - API Gateway provides rate limiting and request management
