# Current Workflows

## Monitoring
```text
Load server
 -> validate monitor_enabled/profile
 -> load enabled commands
 -> SSH connection
 -> execute by execution_order
 -> build report
 -> save report
 -> enqueue analysis
 -> update server status
```
SSH/OS/timeout errors تنتج failure report. فشل enqueue لا يلغي التقرير.

## Analysis
```text
Report
 -> normalize + command_set_hash + fingerprint
 -> exact completed fingerprint?
      yes -> REUSE, llm_called=false
      no  -> Hybrid Retrieval (unless force)
               -> accepted context? -> ASSISTED
               -> none?             -> FULL
 -> LLM for ASSISTED/FULL
 -> save metadata/sources
 -> index retrieval document
 -> save performance metrics
```

`force=true` يتجاوز reuse وhistorical retrieval ويؤدي إلى FULL.

## Hybrid Retrieval
```text
normalized report
  +-> embedding -> pgvector candidates
  +-> FTS query -> lexical candidates
  -> RRF rank fusion
  -> minimum vector similarity gate
  -> structured compatibility
  -> Top K accepted contexts
```

قاعدة حاسمة: `vector_score` هو semantic similarity. `rrf_score` ترتيب فقط.

## Decisions
- REUSE: exact fingerprint فقط.
- ASSISTED: historical contexts مقبولة + assisted enabled.
- FULL: لا سياق مقبول، assisted disabled، أو force.
