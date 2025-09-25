# ALS Accelerator WIKI Tree-Building Algorithm (Simplified)

## Goal
Use multi-year logbook entries to propose a compact tree structure (~300–700 pages) for the ALS Accelerator WIKI. Focus on identifying **durable, reusable knowledge** (concepts, procedures, stable components) and avoid operational noise.


## Source
- input file: /home/als3/acct/thellert/projects/alpha_berkeley/src/applications/als_assistant/database/logbook/logbook_250525.jsonl
- take newest entries and go back 3 years in time to asure relevancy for current machine

---

## Pipeline

### Step A — Extract candidate topics
- Input: logbook entries (subject + details + category).
- LLM task: Propose up to 3 durable topics from each entry.
- Ignore operational/ephemeral content (shift changes, tours, daily statuses).
- Return JSON with: title, bucket, summary, page_type, durability, aliases.

### Step B — Canonicalize and deduplicate
- Keep only `durable` topics.
- Merge near-duplicates and enforce canonical phrasing.
- Ensure each topic is assigned **exactly one bucket** from a fixed list.

### Step C — Build small tree
- Buckets: Injector, Booster, BTS, Storage Ring, RF, Magnets, Power Supplies, Insertion Devices, Diagnostics, Vacuum, Timing, Controls, Safety, Operations (stable), Procedures, Playbooks.
- Build a **2–3 level hierarchy**:
  - Max 7 children per node; overflow goes into "FAQ & Misc".
  - Prefer merging small/related topics into a parent page as **sections**.

### Step D — Prioritize and prune
- Assign priorities: must | should | could.
- If leaf count exceeds target (e.g., 500), remove low-value "could" leaves by merging into parents as sections.

### Execution plan (typed LLM + Pydantic)
- Stream newest→oldest entries until 3 years back in micro-batches (e.g., 20–50).
- Step A per batch: extract topics with a typed chat completion that validates against `TopicExtractionResult` and discard non-durable.
- Step B incremental per candidate: present a shortlist of possible matches and get a `CanonicalizeDecision` (merge vs new). Maintain a canonical index (normalized titles, aliases, embeddings) and update it as you go.
- Step B global finalize: after streaming completes, run one global canonicalization pass to resolve borderline duplicates and freeze titles, buckets, and aliases.
- Step C: build the compact tree from the finalized canonical topics.
- Step D: assign priorities and prune to target leaf count; merge lowest-value "could" into parent sections.

---

## Data Structures

**TopicRecord**
```json
{
  "title": "Ion gauge cabling: orientation & verification",
  "bucket": "Vacuum",
  "summary": "How to orient and verify IG pigtail/filament wiring; signs of miswire; typical readings.",
  "durability": "durable",
  "page_type": "procedure",
  "why_static": "Remains valid beyond incident.",
  "example_refs": ["170006"],
  "aliases": ["ion gauge cable orientation","IG pigtail wiring"]
}
```

**TreeNode**
```json
{
  "id": "Vacuum/IonGauges/Cabling",
  "title": "Ion Gauges — Cabling & Orientation",
  "children": [],
  "page_type": "procedure",
  "topic_refs": ["TopicRecord ids"]
}
```

## Typed Schemas (Pydantic)

```python
from typing import List, Literal, Optional
from pydantic import BaseModel, Field

BUCKETS = Literal[
    "Injector","Booster","BTS","Storage Ring","RF","Magnets","Power Supplies",
    "Insertion Devices","Diagnostics","Vacuum","Timing","Controls","Safety",
    "Operations","Procedures","Playbooks"
]
PAGE_TYPE = Literal["overview","concept","procedure","playbook","faq"]
PRIORITY = Literal["must","should","could"]

class TopicCandidate(BaseModel):
    title: str = Field(..., max_length=60)
    bucket: BUCKETS
    summary: str
    page_type: PAGE_TYPE
    durability: Literal["durable","ephemeral"]
    why_static: Optional[str] = None
    example_refs: List[str] = []
    aliases: List[str] = []

class TopicExtractionResult(BaseModel):
    topics: List[TopicCandidate]

class CanonicalTopic(BaseModel):
    id: str
    title: str = Field(..., max_length=60)
    bucket: BUCKETS
    summary: str
    page_type: PAGE_TYPE
    aliases: List[str] = []
    example_refs: List[str] = []

class CanonicalizeDecision(BaseModel):
    action: Literal["merge","new"]
    target_id: Optional[str] = None
    canonical_title: Optional[str] = None
    bucket: Optional[BUCKETS] = None
    aliases_to_add: List[str] = []

class TreeNode(BaseModel):
    id: str
    title: str
    page_type: Optional[PAGE_TYPE] = None
    children: List["TreeNode"] = []
    topic_refs: List[str] = []

TreeNode.model_rebuild()

class TreeBuildResult(BaseModel):
    tree: List[TreeNode]
    merges: List[str] = []

class PrioritizeDecision(BaseModel):
    node_id: str
    priority: PRIORITY

class PruneResult(BaseModel):
    tree: List[TreeNode]
    priorities: List[PrioritizeDecision]
```

---

## Prompts

**Prompt A (Extract topics, typed)**
```
From the batch of logbook texts, propose up to THREE durable topics per entry for the ALS WIKI.
Ignore ephemeral operational content (shift changes, tours, daily statuses).
Return a JSON object that validates against TopicExtractionResult. Titles <60 chars.
```

**Prompt B1 (Canonicalize — incremental, typed)**
```
Given ONE TopicCandidate and a shortlist of possible targets (id, title, bucket, aliases), decide whether to MERGE into one target or create a NEW canonical topic.
Return a JSON object that validates against CanonicalizeDecision. Ensure exactly one bucket.
Prefer concise canonical phrasing; avoid dates or shift IDs.
```

**Prompt B2 (Canonicalize — global finalize, typed)**
```
Given the current list of CanonicalTopic objects, propose safe merges to remove near-duplicates and finalize titles, buckets, and aliases.
Return the final list of CanonicalTopic with unique ids and exactly one bucket each. Preserve example_refs unions.
```

**Prompt C (Tree induction)**
```
Build a compact 2–3 level hierarchy from canonical topics. 
Constraints: max 7 children per node; group overflow into "FAQ & Misc". 
Prefer merging thin topics into parent as sections. 
Return a JSON object that validates against TreeBuildResult.
```

**Prompt D (Prune)**
```
Assign each leaf page a priority: must | should | could. 
Criteria: usefulness for operators 6–12 months later, reusability, safety relevance. 
If total leaves > TARGET, merge lowest-value 'could' leaves into nearest parent sections.
Return a JSON object that validates against PruneResult.
```

---

## Example Run (sample logbook entries)

Input entries:
- ToR switches converted to VSX pair (durable).
- Facilities tour (ephemeral → ignore).
- Operator shift change (ephemeral → ignore).
- Ion Gauge cable orientation (durable).

Output canonical topics:
```json
[
  {
    "title": "Controls network: ToR switch pairing & LAG design",
    "bucket": "Controls",
    "summary": "When/why to convert ToR to VSX pairs; LAG considerations.",
    "page_type": "overview",
    "aliases": ["ToR VSX pairing","multi-chassis LAG"]
  },
  {
    "title": "Ion gauges: pigtail/filament orientation & verification",
    "bucket": "Vacuum",
    "summary": "Cabling orientation checks; symptoms of miswire; expected readings.",
    "page_type": "procedure",
    "aliases": ["IG pigtail wiring","ion gauge cable orientation"]
  }
]
```

Output tree:
```json
{
  "tree": [
    {
      "bucket": "Controls",
      "children": [
        { "title": "Network Architecture", "children": [
            { "title": "ToR VSX Pairing & LAG (Controls)", "children": [] }
        ]}
      ]
    },
    {
      "bucket": "Vacuum",
      "children": [
        { "title": "Ion Gauges", "children": [
            { "title": "Cabling & Orientation (Procedure)", "children": [] }
        ]}
      ]
    }
  ],
  "merges": []
}
```

---

## Minimal Pseudocode (typed streaming)

```python
entries = load_jsonl_stream(path, since=now_minus_3y, newest_first=True)

canon_index = CanonIndex()  # normalized_title_map, alias_map, ANN for embeddings
for batch in batched(entries, 50):
    extraction = llm_typed_call_A(batch, output_model=TopicExtractionResult)
    for cand in extraction.topics:
        if cand.durability != "durable":
            continue
        shortlist = propose_merge_targets(cand, canon_index, k=5)
        decision = llm_typed_call_B_incremental(cand, shortlist, output_model=CanonicalizeDecision)
        apply_decision(decision, cand, canon_index)

canon = canon_index.materialize()  # List[CanonicalTopic]
canon = llm_typed_call_B_global(canon)  # finalize merges and buckets

tree = llm_typed_call_C(canon, max_children=7)  # TreeBuildResult
final = llm_typed_call_D(tree, target_leaves=500)  # PruneResult

render_review_ui(final)
```

---

## Code structure (under `ALS_wiki/`)

Clean separation of concerns across 3 files.

```text
ALS_wiki/
  wiki_guidelines.md
  __init__.py
  schemas.py        # All Pydantic models
  prompts.py        # Prompt builders for Steps A, B1, B2, C, D
  pipeline.py       # Constants, IO, CanonIndex, typed LLM calls, run_pipeline()
  artifacts/
    canonical_topics.json
    tree.json
    pruned_tree.json
```

### File responsibilities
- `schemas.py`: Pydantic models
  - **includes**: `BUCKETS`, `PAGE_TYPE`, `PRIORITY`, `TopicCandidate`, `TopicExtractionResult`, `CanonicalTopic`, `CanonicalizeDecision`, `TreeNode`, `TreeBuildResult`, `PrioritizeDecision`, `PruneResult`.

- `prompts.py`: prompt builders (schema-bound)
  - **functions**: `build_prompt_A(batch)`, `build_prompt_B_incremental(candidate, shortlist)`, `build_prompt_B_global(canon)`, `build_prompt_C(canon, max_children)`, `build_prompt_D(tree, target_leaves)`.

- `pipeline.py`: orchestration and core logic
  - Constants and thresholds (e.g., `MAX_CHILDREN=7`, `TARGET_LEAVES=500`, `TITLE_JACCARD=0.80`, `BIGRAM_OVERLAP=0.60`, `EMBED_COSINE=0.86`).
  - IO helpers: `load_jsonl_stream`, `save_json`, `load_json`.
  - `CanonIndex` class: normalized-title map, alias map, optional ANN/embedding index; methods `normalize_title`, `add_new`, `merge`, `find_match`, `propose_merge_targets`, `materialize`.
  - Typed LLM wrappers: `llm_typed_call_A`, `llm_typed_call_B_incremental`, `llm_typed_call_B_global`, `llm_typed_call_C`, `llm_typed_call_D`.
  - Orchestrator: `run_pipeline(logbook_path, since, output_dir)` that wires A→B1→B2→C→D and writes artifacts.

### Minimal orchestrator usage
```python
from .pipeline import run_pipeline

run_pipeline(
    logbook_path="/path/to/logbook_250525.jsonl",
    since=now_minus_3y,
    output_dir="ALS_wiki/artifacts",
)
```

---

## Key Design Principles
- **Ignore frequency**; presence ≠ importance.
- **Durability filter** first, to cut noise.
- **Caps** (max 7 children, FAQ & Misc) prevent sprawl.
- **Sections, not pages** for minor topics.
- **One-time human review** for merges and labels.

---

## Outcome
This pipeline yields:
- A compact, human-reviewable WIKI tree.
- Topics focused on durable, reusable knowledge.
- Control knobs: children cap, target leaf count, pruning priorities.

-------------------------------

## Example logbook entires from /home/als3/acct/thellert/projects/alpha_berkeley/src/applications/als_assistant/database/logbook/logbook_250525.jsonl


"id": "169685", "timestamp": "1751467415", "author": "m.ross", "subject": "0743: Toured Facilities", "details": "", "level": "Info", "category": "Operations", "tag": "0", "linkedto": "0", "attachments": []}
{"id": "169686", "timestamp": "1751469702", "author": "mpirkola", "subject": "0800: Operator Shift Change", "details": "ALS is Operational for users.", "level": "Info", "category": "Operations", "tag": "0", "linkedto": "0", "attachments": []}
{"id": "169687", "timestamp": "1751479544", "author": "hunt", "subject": "RE: SR02S:Gamma radiation monitor EPICS not updating", "details": "We have a PV for each monitor for instance \"SR02S:Gamma:samplesPerHour\" which calculates the number of readings sent by the monitor each hour.\u00a0 I will set these PVs to have a low low alarm severity of MAJOR at 0 to detect any monitors that are not updating. These PVs should therefore be added to the alarm handler.", "level": "Info", "category": "Accelerator Controls, Operations, Radiation", "tag": "0", "linkedto": "169684", "attachments": []}
{"id": "169689", "timestamp": "1751491474", "author": "mpirkola", "subject": "1406: Topoff_nux_AM went into minor alarm", "details": "The PV Topoff_nux_AM went into minor alarm for approximately 20 seconds with a value of 16.196, then returned to values in its normal range.\u00a0 No effects on the beam were noticed other than a weak topoff shot.", "level": "Info", "category": "Accelerator Physics, Operations", "tag": "0", "linkedto": "0", "attachments": [{"url": "attach/id/169689/name/temp.png"}]}
{"id": "169690", "timestamp": "1751492233", "author": "ARWilliams", "subject": "BL 8.3.2 IG202 trip point #2 changed", "details": "The 8.3 IP203 is not pumping well so we added a turbo cart to help. 8.3.2 IG202 trip point #2 changed from 5.0 -7 to 1.0 -6 because they are running right next to the trip point on the turbo cart.\u00a0", "level": "Info", "category": "Operations", "tag": "0", "linkedto": "0", "attachments": []}
{"id": "169694", "timestamp": "1751499018", "author": "ejrim", "subject": "1600: Operator Shift Change", "details": "ALS is operational for users", "level": "Info", "category": "Operations", "tag": "0", "linkedto": "0", "attachments": []}
{"id": "169695", "timestamp": "1751500322", "author": "ascc_user", "subject": "ST-25-067 is Closed", "details": "ST-25-067  Checklist has been completed.Please see ASCC for details - ST-25-067", "level": "Info", "category": ", Operations", "tag": "0", "linkedto": "0", "attachments": []}
{"id": "169698", "timestamp": "1751527625", "author": "M.ROSS", "subject": "0000: Operator Shift Change", "details": "ALS is Operational for users with current of 501.16 mA. Single cam 5.05 mA. Topoff lifetime is 5.84 h. SR injection efficiency is 51.4%.", "level": "Info", "category": "Operations", "tag": "0", "linkedto": "0", "attachments": []}
{"id": "169700", "timestamp": "1751556393", "author": "mpirkola", "subject": "0800: Operator Shift Change", "details": "ALS is Operational for users.", "level": "Info", "category": "Operations", "tag": "0", "linkedto": "0", "attachments": []}
{"id": "169701", "timestamp": "1751560418", "author": "ascc_user", "subject": "RSSWA-25-028 is Closed - BL04.2_PSS201", "details": "Please see ASCC for details - RSSWA-25-028", "level": "Info", "category": ", Electronics Maintenance, Operations, Safety Interlocks", "tag": "0", "linkedto": "0", "attachments": []}
{"id": "169706", "timestamp": "1751576701", "author": "sanord", "subject": "LN Mod1 Tripped to HV", "details": "Tank&0x5CDigiFwhmHlim Hlim exceeded 33.206 us. Waited >5min before resetting.", "level": "Info", "category": "Operations, RF", "tag": "0", "linkedto": "0", "attachments": []}
{"id": "169707", "timestamp": "1751581040", "author": "ascc_user", "subject": "ST-25-068 is Closed", "details": "ST-25-068  Checklist has been completed.Please see ASCC for details - ST-25-068", "level": "Info", "category": ", Operations", "tag": "0", "linkedto": "0", "attachments": []}
{"id": "169708", "timestamp": "1751602777", "author": "Santiago", "subject": "Test", "details": "This is just a test entry for training purposes.", "level": "Problem", "category": "Beamline Activities, Operations", "tag": "0", "linkedto": "0", "attachments": []}

