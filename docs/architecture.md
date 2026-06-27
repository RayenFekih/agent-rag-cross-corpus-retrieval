# Architecture: Agentic RAG Cross-Corpus Retrieval

Detailed reference for the iterative cross-corpus retrieval workflow — agent responsibilities, inter-agent data schemas, the sufficient-context evaluation loop, and a concrete end-to-end example.

---

## Table of contents

- [How the workflow fits together](#how-the-workflow-fits-together)
- [Agent responsibilities](#agent-responsibilities)
- [Data passed between agents](#data-passed-between-agents)
- [Sufficient context evaluation loop](#sufficient-context-evaluation-loop)
- [Example end-to-end flow](#example-end-to-end-flow)
- [Planned improvements](#planned-improvements)

---

## How the workflow fits together

A user query enters as plain text. It may contain:

- a single simple request,
- multiple independent requests, or
- a complex request that needs to be broken down into multiple retrieval tasks.

The system decomposes it, retrieves evidence from the relevant corpora, evaluates whether that evidence is sufficient, and only generates a final answer once sufficiency is confirmed (or a retry limit is reached).

---

## Agent responsibilities

### Query Rewriter / Search Planning Agent

Receives the original user query — and on retries, the gap analysis from the Evaluation Agent — and is responsible for:

- Analyzing the user query and understanding what information is needed.
- Breaking it down into multiple focused retrieval queries when appropriate.
- Improving or reformulating each query to make it more retrieval-friendly.
- Reading the descriptions of available corpora to decide which corpus should be searched for each query.
- Selecting one or multiple corpora per query depending on the request.
- On retries: incorporating the Evaluation Agent's feedback to generate targeted follow-up queries for missing or weak areas only.

### Retrieval Engine

Sits between the Search Planning Agent and the corpora. Responsible for:

- Receiving the structured search plan from the Search Planning Agent.
- Executing each improved query against the selected corpus using Agent Search (Google Cloud Discovery Engine).
- Collecting retrieved documents and snippets for every query.
- Passing each query, its `looking_for` description, and retrieved documents to the Evaluation Agent.

The retrieval layer is implemented in [`src/retrieval.py`](../src/retrieval.py) via `search_agent_search()`, and the Discovery Engine client setup is in [`src/utils.py`](../src/utils.py).

### Evaluation Agent

Reviews retrieval results in context and is responsible for:

- Comparing retrieved documents against the `looking_for` description for each query task.
- Deciding whether the retrieved context is sufficient for each task.
- Detecting when a corpus is irrelevant (retrieved results do not match the intended information need).
- Generating a structured missing-pieces analysis (finding, gap, feedback) when context is insufficient.

The Evaluation Agent does **not** only return "sufficient" or "insufficient" — when context is insufficient it produces specific reasoning that the Search Planning Agent can act on directly.

### LLM Generator

Receives only the verified, sufficient contexts and is responsible for:

- Synthesizing them into a grounded final answer.
- Avoiding claims not supported by the retrieved evidence.

---

## Data passed between agents

### Search plan (Search Planning Agent → Retrieval Engine)

**Single query per corpus:**

```json
{
  "corpus_id_1": {
    "improved_query": "...",
    "looking_for": "Description of the exact information needed from this corpus"
  },
  "corpus_id_2": {
    "improved_query": "...",
    "looking_for": "Description of the exact information needed from this corpus"
  }
}
```

**Multiple queries targeting the same corpus:**

```json
{
  "corpus_id_1": [
    {
      "improved_query": "...",
      "looking_for": "..."
    },
    {
      "improved_query": "...",
      "looking_for": "..."
    }
  ]
}
```

### Evaluation output (Evaluation Agent → Search Planning Agent, on retry)

```
Finding:  "What was found in the retrieved documents."
Gap:      "What is explicitly missing."
Feedback: "Specific search terms or angles to use in the follow-up query."
```

---

## Sufficient context evaluation loop

```
1. Search Planning Agent produces a structured search plan.
2. Retrieval Engine executes each query against the selected corpora.
3. Evaluation Agent reviews all results.
   ├── All tasks sufficient → pass contexts to LLM Generator → final answer.
   └── One or more tasks insufficient →
         return missing-pieces analysis to Search Planning Agent →
         generate targeted follow-up queries for missing/weak areas only →
         go to step 2 (only missing areas are re-queried).
4. Repeat until sufficient or retry limit is reached.
```

Key properties:

- **Partial sufficiency**: satisfied tasks are not re-queried on retry runs.
- **Corpus irrelevance detection**: corpora determined to be irrelevant are dropped from the retry plan.
- **Retry limit**: a configurable `max_retries` guard prevents infinite iteration.
- **Late generation**: the LLM Generator is only invoked after the Evaluation Agent clears all tasks (or the retry limit is hit), preventing unsupported answers.

---

## Example end-to-end flow

**User query:**

> "Summarize the patient discharge instructions and mention whether the patient had any allergic reactions during the stay."

---

**Round 1 — search plan:**

```json
{
  "clinical_notes_corpus": [
    {
      "improved_query": "patient discharge instructions medication diet follow-up",
      "looking_for": "Discharge instructions including medications, diet, and follow-up guidance"
    },
    {
      "improved_query": "patient allergic reaction rash adverse event during stay",
      "looking_for": "Evidence of allergic reactions, rashes, or adverse events during the hospital stay"
    }
  ]
}
```

**Round 1 — evaluation result:**

- **Finding:** Retrieved documents include medication instructions and low-sodium diet guidance.
- **Gap:** No retrieved document mentions allergic reactions, rashes, or adverse events.
- **Feedback:** Run a follow-up search focused on allergy notes, adverse events, rashes, and medication reactions.

---

**Round 2 — targeted follow-up (gap only):**

```json
{
  "clinical_notes_corpus": [
    {
      "improved_query": "allergy notes adverse events rash medication reaction hospital stay",
      "looking_for": "Evidence of allergic reactions, rashes, or adverse events during the hospital stay"
    }
  ]
}
```

**Round 2 — evaluation result:**

Either the allergy/adverse-event information is found and confirmed sufficient, or the system explicitly determines that no such evidence exists in the available corpora and notes this in the final answer.

---

**Final generation:**

The LLM Generator receives only the verified, sufficient contexts (discharge instructions + allergy query resolution) and synthesizes a grounded answer. No claims are made beyond what the evidence supports.

---

## Planned improvements

- **Agent `generate()` methods**: wire each agent to the Google ADK LLM runtime.
- **Prompts**: fill in `src/prompts.py` with production-quality system and user prompts.
- **Structured output schemas**: validate search plan and evaluation output with Pydantic.
- **LLM Generator agent**: implement the final synthesis step.
- **Orchestration pipeline**: wire all agents together in `main.py`.
- **Retry loop with limit**: implement the sufficient-context loop with `max_retries`.
- **Partial retry**: only re-issue queries for tasks flagged as insufficient.
- **Corpus irrelevance pruning**: drop irrelevant corpora from retry plans.
- **Citations**: surface document IDs and source references in the final answer.
- **Observability**: structured logging of each loop iteration, retrieval latency, and evaluation decisions.
- **Tests**: unit tests for agent logic, retrieval parsing, and the evaluation loop.
