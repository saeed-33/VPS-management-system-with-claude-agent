# investigate

Purpose: supervise deeper investigation when analysis identifies potential
issues.

Required sequence:

```text
get analysis
start or read investigation
get available DB-defined Specialists
select Specialists inside project rules and budgets
run Specialists through project-owned tools
collect Evidence and Specialist results
aggregate per-server result
persist/read final diagnosis
```

Do not create hard-coded domain Specialists as the authority for runtime
selection.
