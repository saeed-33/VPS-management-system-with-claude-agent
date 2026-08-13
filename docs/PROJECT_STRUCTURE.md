# Project Structure and File Responsibilities

This document is generated from the current checkout.

Regenerate with:

```powershell
uv run python tools/dev/generate_project_structure.py
```

## Architectural flow

```text
Periodic Monitoring / Scheduler
        ↓
ClaudeSupervisor
        ↓
Native Claude Code CLI + Ollama
        ↓
vps MCP / bounded project tools
        ↓
Monitoring Report + PostgreSQL persistence
        ↓
Exact reuse or similar retrieval + Analysis
        ↓
Optional Investigation + DB-defined Specialists
        ↓
Policy + budgets + known-hosts SSH + Evidence
        ↓
Correlation + Final Diagnosis
        ↓
Final Diagnosis + Narrative
        ↓
Runtime Snapshot Persistence
        ↓
API / Administration UI
        ↓
Evaluation / Production Readiness Gate
```

## File-by-file inventory

### Repository root / configuration

- `.claude/agents/server-supervisor.md` — Project documentation.
- `.claude/agents/specialist-worker.md` — Project documentation.
- `.claude/rules/evidence-grounding.md` — Project documentation.
- `.claude/rules/safety.md` — Claude rule file for tool safety, policy boundaries, and prohibited bypasses.
- `.claude/runtime-events/0a9bc785-5148-4540-9618-418bf37d55be/1786619175929641100-SessionStart-main.json` — Structured configuration or generated data.
- `.claude/runtime-events/0a9bc785-5148-4540-9618-418bf37d55be/1786619177249289000-RuntimePreflightPassed-main.json` — Structured configuration or generated data.
- `.claude/runtime-events/0a9bc785-5148-4540-9618-418bf37d55be/1786619257435037700-SessionEnd-main.json` — Structured configuration or generated data.
- `.claude/runtime-events/0cf8343c-ef63-4d30-b705-0d6a5431db43/1786560485437671900-SessionStart-main.json` — Structured configuration or generated data.
- `.claude/runtime-events/0cf8343c-ef63-4d30-b705-0d6a5431db43/1786560487734795200-RuntimePreflightFailed-main.json` — Structured configuration or generated data.
- `.claude/runtime-events/0cf8343c-ef63-4d30-b705-0d6a5431db43/1786560488758377800-SessionEnd-main.json` — Structured configuration or generated data.
- `.claude/runtime-events/182d85b2-0169-462b-b114-090ba0b76ef5/1786529828887678200-SessionStart-main.json` — Structured configuration or generated data.
- `.claude/runtime-events/182d85b2-0169-462b-b114-090ba0b76ef5/1786529829091192200-RuntimePreflightPassed-main.json` — Structured configuration or generated data.
- `.claude/runtime-events/182d85b2-0169-462b-b114-090ba0b76ef5/1786529878855439600-SessionEnd-main.json` — Structured configuration or generated data.
- `.claude/runtime-events/1a88ca67-5f50-449d-ade5-baad88713e3c/1786559451928869700-SessionStart-main.json` — Structured configuration or generated data.
- `.claude/runtime-events/1a88ca67-5f50-449d-ade5-baad88713e3c/1786559454101776000-RuntimePreflightFailed-main.json` — Structured configuration or generated data.
- `.claude/runtime-events/1a88ca67-5f50-449d-ade5-baad88713e3c/1786559455124243400-SessionEnd-main.json` — Structured configuration or generated data.
- `.claude/runtime-events/1c986461-52a8-4899-9749-6be06b171572/1786554868287180900-SessionStart-main.json` — Structured configuration or generated data.
- `.claude/runtime-events/1c986461-52a8-4899-9749-6be06b171572/1786554868383126200-RuntimePreflightPassed-main.json` — Structured configuration or generated data.
- `.claude/runtime-events/1c986461-52a8-4899-9749-6be06b171572/1786554910343848500-SessionEnd-main.json` — Structured configuration or generated data.
- `.claude/runtime-events/1e7961c1-40d3-43f8-8187-eea4887b1d79/1786560192812893400-SessionStart-main.json` — Structured configuration or generated data.
- `.claude/runtime-events/1e7961c1-40d3-43f8-8187-eea4887b1d79/1786560194826237000-RuntimePreflightFailed-main.json` — Structured configuration or generated data.
- `.claude/runtime-events/1e7961c1-40d3-43f8-8187-eea4887b1d79/1786560197203862400-SessionEnd-main.json` — Structured configuration or generated data.
- `.claude/runtime-events/21c474ed-427d-488d-9e9c-f7cbb6f810d0/1786561640542215800-SessionStart-main.json` — Structured configuration or generated data.
- `.claude/runtime-events/21c474ed-427d-488d-9e9c-f7cbb6f810d0/1786561642504692600-RuntimePreflightPassed-main.json` — Structured configuration or generated data.
- `.claude/runtime-events/21c474ed-427d-488d-9e9c-f7cbb6f810d0/1786561650977975400-SessionEnd-main.json` — Structured configuration or generated data.
- `.claude/runtime-events/32786513-97af-4b85-aec0-2fc30cbfa8ec/1786561582802690200-SessionStart-main.json` — Structured configuration or generated data.
- `.claude/runtime-events/32786513-97af-4b85-aec0-2fc30cbfa8ec/1786561584952420200-RuntimePreflightPassed-main.json` — Structured configuration or generated data.
- `.claude/runtime-events/32786513-97af-4b85-aec0-2fc30cbfa8ec/1786561594744479000-SessionEnd-main.json` — Structured configuration or generated data.
- `.claude/runtime-events/3bbf0058-2aff-4ba3-85ab-ed238a6cfaf9/1786529369238511600-SessionStart-main.json` — Structured configuration or generated data.
- `.claude/runtime-events/3bbf0058-2aff-4ba3-85ab-ed238a6cfaf9/1786529369482626600-RuntimePreflightPassed-main.json` — Structured configuration or generated data.
- `.claude/runtime-events/3bbf0058-2aff-4ba3-85ab-ed238a6cfaf9/1786529463260598200-SessionEnd-main.json` — Structured configuration or generated data.
- `.claude/runtime-events/3f87c370-54c4-4e6e-98b1-b0c1e2e2748a/1786613260947668900-SessionStart-main.json` — Structured configuration or generated data.
- `.claude/runtime-events/3f87c370-54c4-4e6e-98b1-b0c1e2e2748a/1786613262348721400-RuntimePreflightPassed-main.json` — Structured configuration or generated data.
- `.claude/runtime-events/3f87c370-54c4-4e6e-98b1-b0c1e2e2748a/1786613338557715400-SubagentStart-a01cff31db22973a8.json` — Structured configuration or generated data.
- `.claude/runtime-events/3f87c370-54c4-4e6e-98b1-b0c1e2e2748a/1786613377949982800-SubagentStop-a01cff31db22973a8.json` — Structured configuration or generated data.
- `.claude/runtime-events/3f87c370-54c4-4e6e-98b1-b0c1e2e2748a/1786613395013059400-SubagentStart-a542d0a3c78a6dcab.json` — Structured configuration or generated data.
- `.claude/runtime-events/3f87c370-54c4-4e6e-98b1-b0c1e2e2748a/1786613488257107800-SubagentStop-a542d0a3c78a6dcab.json` — Structured configuration or generated data.
- `.claude/runtime-events/3f87c370-54c4-4e6e-98b1-b0c1e2e2748a/1786613503709246600-SessionEnd-main.json` — Structured configuration or generated data.
- `.claude/runtime-events/441fc09a-bf67-4791-a77d-834c09f60fdd/1786530242977198700-SessionStart-main.json` — Structured configuration or generated data.
- `.claude/runtime-events/441fc09a-bf67-4791-a77d-834c09f60fdd/1786530243170638300-RuntimePreflightPassed-main.json` — Structured configuration or generated data.
- `.claude/runtime-events/496f737b-deaa-4cd5-bbaf-4f8ca55f6616/1786617434184644900-SessionStart-main.json` — Structured configuration or generated data.
- `.claude/runtime-events/496f737b-deaa-4cd5-bbaf-4f8ca55f6616/1786617435545805000-RuntimePreflightPassed-main.json` — Structured configuration or generated data.
- `.claude/runtime-events/496f737b-deaa-4cd5-bbaf-4f8ca55f6616/1786617504462939900-SessionEnd-main.json` — Structured configuration or generated data.
- `.claude/runtime-events/4ab70005-db91-421f-bb45-b222d040296d/1786611641387153000-SessionStart-main.json` — Structured configuration or generated data.
- `.claude/runtime-events/4ab70005-db91-421f-bb45-b222d040296d/1786611642709469700-RuntimePreflightPassed-main.json` — Structured configuration or generated data.
- `.claude/runtime-events/4ab70005-db91-421f-bb45-b222d040296d/1786611699912433500-SubagentStart-a6e0db7891b1e5179.json` — Structured configuration or generated data.
- `.claude/runtime-events/4ab70005-db91-421f-bb45-b222d040296d/1786611726091641500-SubagentStop-a6e0db7891b1e5179.json` — Structured configuration or generated data.
- `.claude/runtime-events/4ab70005-db91-421f-bb45-b222d040296d/1786611751679880700-SubagentStart-a47a2447f9d1f674a.json` — Structured configuration or generated data.
- `.claude/runtime-events/4ab70005-db91-421f-bb45-b222d040296d/1786611827936170500-SubagentStop-a47a2447f9d1f674a.json` — Structured configuration or generated data.
- `.claude/runtime-events/4ab70005-db91-421f-bb45-b222d040296d/1786611846621773900-SessionEnd-main.json` — Structured configuration or generated data.
- `.claude/runtime-events/5353acca-78e0-4b71-b899-fb21c2ae0c72/1786613740958790600-SessionStart-main.json` — Structured configuration or generated data.
- `.claude/runtime-events/5353acca-78e0-4b71-b899-fb21c2ae0c72/1786613742405928700-RuntimePreflightPassed-main.json` — Structured configuration or generated data.
- `.claude/runtime-events/5353acca-78e0-4b71-b899-fb21c2ae0c72/1786613815763307200-SubagentStart-adf9164b8817f9a86.json` — Structured configuration or generated data.
- `.claude/runtime-events/5353acca-78e0-4b71-b899-fb21c2ae0c72/1786613837969999900-SubagentStop-adf9164b8817f9a86.json` — Structured configuration or generated data.
- `.claude/runtime-events/5353acca-78e0-4b71-b899-fb21c2ae0c72/1786613852904729500-SubagentStart-a64dd7146f71fde6b.json` — Structured configuration or generated data.
- `.claude/runtime-events/5353acca-78e0-4b71-b899-fb21c2ae0c72/1786613936164859200-SubagentStop-a64dd7146f71fde6b.json` — Structured configuration or generated data.
- `.claude/runtime-events/5353acca-78e0-4b71-b899-fb21c2ae0c72/1786613958388210400-SessionEnd-main.json` — Structured configuration or generated data.
- `.claude/runtime-events/554f9f39-1a6d-434e-8f32-f3d06b64bab0/1786556072699345500-SessionStart-main.json` — Structured configuration or generated data.
- `.claude/runtime-events/554f9f39-1a6d-434e-8f32-f3d06b64bab0/1786556074684267400-RuntimePreflightFailed-main.json` — Structured configuration or generated data.
- `.claude/runtime-events/554f9f39-1a6d-434e-8f32-f3d06b64bab0/1786556077079515800-SessionEnd-main.json` — Structured configuration or generated data.
- `.claude/runtime-events/589e57b6-1b07-4a86-a743-a9cb333678f2/1786561946372789900-SessionStart-main.json` — Structured configuration or generated data.
- `.claude/runtime-events/589e57b6-1b07-4a86-a743-a9cb333678f2/1786561948500069900-RuntimePreflightPassed-main.json` — Structured configuration or generated data.
- `.claude/runtime-events/589e57b6-1b07-4a86-a743-a9cb333678f2/1786562020834311300-SessionEnd-main.json` — Structured configuration or generated data.
- `.claude/runtime-events/62d84a89-f841-4e24-9147-30831c013a0a/1786558454771811000-SessionStart-main.json` — Structured configuration or generated data.
- `.claude/runtime-events/62d84a89-f841-4e24-9147-30831c013a0a/1786558456942284700-RuntimePreflightFailed-main.json` — Structured configuration or generated data.
- `.claude/runtime-events/62d84a89-f841-4e24-9147-30831c013a0a/1786558458083240100-SessionEnd-main.json` — Structured configuration or generated data.
- `.claude/runtime-events/886d6f04-f45f-4e5b-8375-a4933c70c979/1786610707840533800-SessionStart-main.json` — Structured configuration or generated data.
- `.claude/runtime-events/886d6f04-f45f-4e5b-8375-a4933c70c979/1786610709114362000-RuntimePreflightPassed-main.json` — Structured configuration or generated data.
- `.claude/runtime-events/886d6f04-f45f-4e5b-8375-a4933c70c979/1786610901916952700-SessionEnd-main.json` — Structured configuration or generated data.
- `.claude/runtime-events/8a219546-c3db-4c8b-8cf6-bc700d2874d3/1786529721409807200-SessionStart-main.json` — Structured configuration or generated data.
- `.claude/runtime-events/8a219546-c3db-4c8b-8cf6-bc700d2874d3/1786529721807737800-RuntimePreflightPassed-main.json` — Structured configuration or generated data.
- `.claude/runtime-events/8a219546-c3db-4c8b-8cf6-bc700d2874d3/1786529741673125900-SessionEnd-main.json` — Structured configuration or generated data.
- `.claude/runtime-events/94974eb3-05bf-4715-a3a2-e143eb4a733a/1786611032819169800-SessionStart-main.json` — Structured configuration or generated data.
- `.claude/runtime-events/94974eb3-05bf-4715-a3a2-e143eb4a733a/1786611034245982900-RuntimePreflightPassed-main.json` — Structured configuration or generated data.
- `.claude/runtime-events/94974eb3-05bf-4715-a3a2-e143eb4a733a/1786611217692650200-SessionEnd-main.json` — Structured configuration or generated data.
- `.claude/runtime-events/965c30b7-0b67-4701-91c3-51911fe727de/1786610467031911700-SessionStart-main.json` — Structured configuration or generated data.
- `.claude/runtime-events/965c30b7-0b67-4701-91c3-51911fe727de/1786610468522861900-RuntimePreflightPassed-main.json` — Structured configuration or generated data.
- `.claude/runtime-events/965c30b7-0b67-4701-91c3-51911fe727de/1786610650012653400-SessionEnd-main.json` — Structured configuration or generated data.
- `.claude/runtime-events/97d0d99b-8da4-492b-8c00-7c419d9bf192/1786560298323268100-SessionStart-main.json` — Structured configuration or generated data.
- `.claude/runtime-events/97d0d99b-8da4-492b-8c00-7c419d9bf192/1786560300376599600-RuntimePreflightFailed-main.json` — Structured configuration or generated data.
- `.claude/runtime-events/97d0d99b-8da4-492b-8c00-7c419d9bf192/1786560301415211500-SessionEnd-main.json` — Structured configuration or generated data.
- `.claude/runtime-events/9afda500-ce9f-49ff-b81c-2be17771fddd/1786553019788822400-SessionStart-main.json` — Structured configuration or generated data.
- `.claude/runtime-events/9afda500-ce9f-49ff-b81c-2be17771fddd/1786553019953679300-RuntimePreflightPassed-main.json` — Structured configuration or generated data.
- `.claude/runtime-events/9afda500-ce9f-49ff-b81c-2be17771fddd/1786553140392711900-SessionEnd-main.json` — Structured configuration or generated data.
- `.claude/runtime-events/a92dbdae-42de-42db-81a6-bbd70cc9dd3c/1786561247497163300-SessionStart-main.json` — Structured configuration or generated data.
- `.claude/runtime-events/a92dbdae-42de-42db-81a6-bbd70cc9dd3c/1786561249345648200-RuntimePreflightPassed-main.json` — Structured configuration or generated data.
- `.claude/runtime-events/a92dbdae-42de-42db-81a6-bbd70cc9dd3c/1786561271837378400-SessionEnd-main.json` — Structured configuration or generated data.
- `.claude/runtime-events/a9c888d4-7b27-4cf5-a74f-ddfced973a80/1786611250525791100-SessionStart-main.json` — Structured configuration or generated data.
- `.claude/runtime-events/a9c888d4-7b27-4cf5-a74f-ddfced973a80/1786611252090473900-RuntimePreflightPassed-main.json` — Structured configuration or generated data.
- `.claude/runtime-events/a9c888d4-7b27-4cf5-a74f-ddfced973a80/1786611327840042100-SubagentStart-a8cede9993582eb8d.json` — Structured configuration or generated data.
- `.claude/runtime-events/a9c888d4-7b27-4cf5-a74f-ddfced973a80/1786611373539424700-SubagentStop-a8cede9993582eb8d.json` — Structured configuration or generated data.
- `.claude/runtime-events/a9c888d4-7b27-4cf5-a74f-ddfced973a80/1786611406619356100-SessionEnd-main.json` — Structured configuration or generated data.
- `.claude/runtime-events/a9d6edfc-8c3a-47a0-9143-1b6d45193ef9/1786561434596359500-SessionStart-main.json` — Structured configuration or generated data.
- `.claude/runtime-events/a9d6edfc-8c3a-47a0-9143-1b6d45193ef9/1786561436679515500-RuntimePreflightPassed-main.json` — Structured configuration or generated data.
- `.claude/runtime-events/a9d6edfc-8c3a-47a0-9143-1b6d45193ef9/1786561445480341700-SessionEnd-main.json` — Structured configuration or generated data.
- `.claude/runtime-events/aa45953b-181d-4a49-a03e-632d1b39db87/1786616535439901900-SessionStart-main.json` — Structured configuration or generated data.
- `.claude/runtime-events/aa45953b-181d-4a49-a03e-632d1b39db87/1786616536825340400-RuntimePreflightPassed-main.json` — Structured configuration or generated data.
- `.claude/runtime-events/aa45953b-181d-4a49-a03e-632d1b39db87/1786616609870273000-SubagentStart-aa5184669ccfb01a3.json` — Structured configuration or generated data.
- `.claude/runtime-events/aa45953b-181d-4a49-a03e-632d1b39db87/1786616654379288400-SubagentStop-aa5184669ccfb01a3.json` — Structured configuration or generated data.
- `.claude/runtime-events/aa45953b-181d-4a49-a03e-632d1b39db87/1786616671969431000-SubagentStart-afaeae5109a0747b9.json` — Structured configuration or generated data.
- `.claude/runtime-events/aa45953b-181d-4a49-a03e-632d1b39db87/1786616700469412500-SubagentStop-afaeae5109a0747b9.json` — Structured configuration or generated data.
- `.claude/runtime-events/aa45953b-181d-4a49-a03e-632d1b39db87/1786616721629168500-SessionEnd-main.json` — Structured configuration or generated data.
- `.claude/runtime-events/af8b8be3-a1c3-43e4-8e0c-ebf9dbb5d79d/1786561380879406700-SessionStart-main.json` — Structured configuration or generated data.
- `.claude/runtime-events/af8b8be3-a1c3-43e4-8e0c-ebf9dbb5d79d/1786561383116863100-RuntimePreflightPassed-main.json` — Structured configuration or generated data.
- `.claude/runtime-events/af8b8be3-a1c3-43e4-8e0c-ebf9dbb5d79d/1786561388312756700-SessionEnd-main.json` — Structured configuration or generated data.
- `.claude/runtime-events/b03b9679-4057-4a30-99fc-0c405df5627e/1786615469985110600-SessionStart-main.json` — Structured configuration or generated data.
- `.claude/runtime-events/b03b9679-4057-4a30-99fc-0c405df5627e/1786615471387346000-RuntimePreflightPassed-main.json` — Structured configuration or generated data.
- `.claude/runtime-events/b03b9679-4057-4a30-99fc-0c405df5627e/1786615562544349300-SubagentStart-a5009a68773ddfa21.json` — Structured configuration or generated data.
- `.claude/runtime-events/b03b9679-4057-4a30-99fc-0c405df5627e/1786615600809962300-SubagentStop-a5009a68773ddfa21.json` — Structured configuration or generated data.
- `.claude/runtime-events/b03b9679-4057-4a30-99fc-0c405df5627e/1786615613702241100-SubagentStart-aa0cdeb4fc0dff0f8.json` — Structured configuration or generated data.
- `.claude/runtime-events/b03b9679-4057-4a30-99fc-0c405df5627e/1786615701064296500-SubagentStop-aa0cdeb4fc0dff0f8.json` — Structured configuration or generated data.
- `.claude/runtime-events/b03b9679-4057-4a30-99fc-0c405df5627e/1786615736390206900-SessionEnd-main.json` — Structured configuration or generated data.
- `.claude/runtime-events/b6155e84-22e7-4954-9e7b-a240c1cecd3c/1786560231353731200-SessionStart-main.json` — Structured configuration or generated data.
- `.claude/runtime-events/b6155e84-22e7-4954-9e7b-a240c1cecd3c/1786560233356393000-RuntimePreflightFailed-main.json` — Structured configuration or generated data.
- `.claude/runtime-events/b6155e84-22e7-4954-9e7b-a240c1cecd3c/1786560234326782500-SessionEnd-main.json` — Structured configuration or generated data.
- `.claude/runtime-events/c069533c-fa44-496a-9c66-9ad7e0140d39/1786561867173454800-SessionStart-main.json` — Structured configuration or generated data.
- `.claude/runtime-events/c069533c-fa44-496a-9c66-9ad7e0140d39/1786561869591595800-RuntimePreflightPassed-main.json` — Structured configuration or generated data.
- `.claude/runtime-events/c069533c-fa44-496a-9c66-9ad7e0140d39/1786561880414902200-SessionEnd-main.json` — Structured configuration or generated data.
- `.claude/runtime-events/c1d9af3f-70d3-454b-8298-015a38464758/1786615859465942900-SessionStart-main.json` — Structured configuration or generated data.
- `.claude/runtime-events/c1d9af3f-70d3-454b-8298-015a38464758/1786615860849682600-RuntimePreflightPassed-main.json` — Structured configuration or generated data.
- `.claude/runtime-events/c1d9af3f-70d3-454b-8298-015a38464758/1786615912591296900-SessionEnd-main.json` — Structured configuration or generated data.
- `.claude/runtime-events/c45f1e6f-2b1b-42a6-8887-89b9342921b7/1786554320745556900-SessionStart-main.json` — Structured configuration or generated data.
- `.claude/runtime-events/c45f1e6f-2b1b-42a6-8887-89b9342921b7/1786554320865332300-RuntimePreflightPassed-main.json` — Structured configuration or generated data.
- `.claude/runtime-events/c45f1e6f-2b1b-42a6-8887-89b9342921b7/1786554341731351700-SessionEnd-main.json` — Structured configuration or generated data.
- `.claude/runtime-events/d58777c9-5039-4866-98c0-e95562608b4e/1786561302582877500-SessionStart-main.json` — Structured configuration or generated data.
- `.claude/runtime-events/d58777c9-5039-4866-98c0-e95562608b4e/1786561304406453300-RuntimePreflightPassed-main.json` — Structured configuration or generated data.
- `.claude/runtime-events/d58777c9-5039-4866-98c0-e95562608b4e/1786561326884937600-SessionEnd-main.json` — Structured configuration or generated data.
- `.claude/runtime-events/dbb346e4-537a-4f1c-9772-af26200444bf/1786560707369897900-SessionStart-main.json` — Structured configuration or generated data.
- `.claude/runtime-events/dbb346e4-537a-4f1c-9772-af26200444bf/1786560709647204000-RuntimePreflightFailed-main.json` — Structured configuration or generated data.
- `.claude/runtime-events/dbb346e4-537a-4f1c-9772-af26200444bf/1786560710649703300-SessionEnd-main.json` — Structured configuration or generated data.
- `.claude/runtime-events/eef24db6-cc57-4795-a998-056281d72e3d/1786554058032813300-SessionStart-main.json` — Structured configuration or generated data.
- `.claude/runtime-events/eef24db6-cc57-4795-a998-056281d72e3d/1786554058314463700-RuntimePreflightPassed-main.json` — Structured configuration or generated data.
- `.claude/runtime-events/eef24db6-cc57-4795-a998-056281d72e3d/1786554102031146700-SessionEnd-main.json` — Structured configuration or generated data.
- `.claude/runtime-events/f337cb1d-bfd2-4d85-936a-e50821cb00da/1786556323968646500-SessionStart-main.json` — Structured configuration or generated data.
- `.claude/runtime-events/f337cb1d-bfd2-4d85-936a-e50821cb00da/1786556325903166100-RuntimePreflightFailed-main.json` — Structured configuration or generated data.
- `.claude/runtime-events/f337cb1d-bfd2-4d85-936a-e50821cb00da/1786556326416169100-SessionEnd-main.json` — Structured configuration or generated data.
- `.claude/runtime-events/f46561df-de7e-42b1-9459-0053b1037ac8/1786558433608568700-SessionStart-main.json` — Structured configuration or generated data.
- `.claude/runtime-events/f46561df-de7e-42b1-9459-0053b1037ac8/1786558435953676500-RuntimePreflightFailed-main.json` — Structured configuration or generated data.
- `.claude/runtime-events/f46561df-de7e-42b1-9459-0053b1037ac8/1786558436973015600-SessionEnd-main.json` — Structured configuration or generated data.
- `.claude/runtime-events/f592061b-65ef-4b70-b231-8c5f27843196/1786575445658175700-SessionStart-main.json` — Structured configuration or generated data.
- `.claude/runtime-events/f592061b-65ef-4b70-b231-8c5f27843196/1786575450213207400-RuntimePreflightPassed-main.json` — Structured configuration or generated data.
- `.claude/runtime-events/f592061b-65ef-4b70-b231-8c5f27843196/1786575564896096000-SessionEnd-main.json` — Structured configuration or generated data.
- `.claude/runtime-events/fb36fbc7-b59b-4218-9b85-27f9f01a4e78/1786559777322083400-SessionStart-main.json` — Structured configuration or generated data.
- `.claude/runtime-events/fb36fbc7-b59b-4218-9b85-27f9f01a4e78/1786559779451932000-RuntimePreflightFailed-main.json` — Structured configuration or generated data.
- `.claude/runtime-events/fb36fbc7-b59b-4218-9b85-27f9f01a4e78/1786559780582958100-SessionEnd-main.json` — Structured configuration or generated data.
- `.claude/settings.json` — Claude project settings for permissions, tools, and hooks.
- `.claude/skills/analyze-incident/SKILL.md` — Claude skill instructions for incident report analysis.
- `.claude/skills/investigate-incident/SKILL.md` — Claude skill instructions for specialist investigation workflows.
- `.claude/skills/monitor-server/SKILL.md` — Claude skill instructions for server monitoring tasks.
- `.claude/skills/plan-remediation/SKILL.md` — Claude skill instructions for remediation planning and validation.
- `.env` — Project asset.
- `.env.example` — Example environment variables for local/runtime configuration.
- `.gitignore` — Project asset.
- `.mcp.json` — Claude MCP configuration exposing project tool servers.
- `.python-version` — Project asset.
- `CLAUDE.md` — Claude project instruction entrypoint loaded at session start; defines architecture, workflow, and coding rules.
- `README.md` — Top-level project overview and startup guidance.
- `assets/fonts/NotoNaskhArabic-Regular.ttf` — Project asset.
- `pyproject.toml` — Python project metadata and dependency configuration.
- `pytest.ini` — Pytest configuration.
- `reports/20260805T142639_b4b15481.json` — Structured configuration or generated data.
- `reports/20260805T142739_2d6ae7cf.json` — Structured configuration or generated data.
- `reports/20260805T142840_f9195f7b.json` — Structured configuration or generated data.
- `reports/20260805T142940_1d4b9436.json` — Structured configuration or generated data.
- `reports/20260805T143041_c87bb287.json` — Structured configuration or generated data.
- `reports/server_1/20260805T152916_15b684bf.json` — Structured configuration or generated data.
- `reports/server_1/20260805T153016_3afdc079.json` — Structured configuration or generated data.
- `reports/server_1/20260805T153117_686f62b7.json` — Structured configuration or generated data.
- `reports/server_2/20260805T152926_b063a281.json` — Structured configuration or generated data.
- `reports/server_3/20260805T153011_771e068b.json` — Structured configuration or generated data.
- `reports/server_3/20260805T153112_d417fe8b.json` — Structured configuration or generated data.
- `requirements-dev.txt` — Text data/documentation asset.
- `requirements.txt` — Text data/documentation asset.
- `uv.lock` — Project asset.

### Application core

- `app/__init__.py` — Python module.
- `app/capabilities/__init__.py` — Application capabilities: bounded business execution used by interfaces.
- `app/capabilities/remediation/__init__.py` — Policy-gated remediation proposal and application capabilities.
- `app/capabilities/remediation/execution.py` — Python module containing class `WriteCommandResult`, class `WriteCommandRunner`, class `VerificationRunner`, class `UnavailableWriteRunner`, class `UnavailableVerificationRunner`.
- `app/capabilities/remediation/service.py` — Python module containing class `RemediationService`.
- `app/composition/__init__.py` — Application composition root / dependency container. Exports the canonical wired application container.
- `app/composition/analysis.py` — Python module containing class `RetrievalComposition`, class `AnalysisInvestigationComposition`, `build_retrieval_composition()`, `build_analysis_investigation_composition()`.
- `app/composition/builder.py` — Python module containing `build_container()`.
- `app/composition/container.py` — Python module containing class `ApplicationContainer`.
- `app/composition/repositories.py` — Python module containing class `RepositoryBundle`, `build_repositories()`.
- `app/composition/runtime.py` — Python module containing class `RuntimeComposition`, `build_runtime_composition()`.
- `app/composition/services.py` — Python module containing class `CoreServiceBundle`, `build_core_services()`.
- `app/infrastructure/__init__.py` — Infrastructure adapters and external-system implementations.
- `app/infrastructure/database/__init__.py` — Database infrastructure implementations.
- `app/infrastructure/database/base.py` — Python module containing class `Base`.
- `app/infrastructure/database/engine.py` — Python module containing `create_database_tables()`.
- `app/infrastructure/database/migrations/step_3_10_performance_metrics.sql` — Database migration/configuration asset.
- `app/infrastructure/database/migrations/step_3_3_full_text_search.sql` — Database migration/configuration asset.
- `app/infrastructure/database/migrations/step_3_7_hnsw_vector_search.sql` — Database migration/configuration asset.
- `app/infrastructure/database/migrations/step_3_7_verify_hnsw.sql` — Database migration/configuration asset.
- `app/infrastructure/database/migrations/step_4_2_specialist_definitions.sql` — Database migration/configuration asset.
- `app/infrastructure/database/migrations/step_4_6_investigation_persistence.sql` — Database migration/configuration asset.
- `app/infrastructure/database/migrations/step_4_7_knowledge_sources.sql` — Database migration/configuration asset.
- `app/infrastructure/database/migrations/step_4_8_0_knowledge_rag_schema.sql` — Database migration/configuration asset.
- `app/infrastructure/database/migrations/step_4_8_3_knowledge_indexes.sql` — Database migration/configuration asset.
- `app/infrastructure/database/migrations/step_5_1_supervised_remediation.sql` — Database migration/configuration asset.
- `app/infrastructure/database/migrations/step_c_10_remediation.sql` — Database migration/configuration asset.
- `app/infrastructure/database/migrations/step_c_3_agent_jobs.sql` — Database migration/configuration asset.
- `app/infrastructure/database/models/__init__.py` — Python module.
- `app/infrastructure/database/models/agent_job.py` — Python module containing class `AgentJobModel`.
- `app/infrastructure/database/models/command_execution.py` — Python module containing class `CommandExecutionModel`.
- `app/infrastructure/database/models/investigation.py` — Python module containing class `InvestigationModel`, class `InvestigationSpecialistCandidateModel`.
- `app/infrastructure/database/models/knowledge_document.py` — Python module containing class `KnowledgeDocumentModel`, class `KnowledgeChunkModel`.
- `app/infrastructure/database/models/knowledge_source.py` — Python module containing class `KnowledgeSourceModel`.
- `app/infrastructure/database/models/monitor_command.py` — Python module containing class `MonitorCommandModel`.
- `app/infrastructure/database/models/monitoring_profile.py` — Python module containing class `MonitoringProfileModel`.
- `app/infrastructure/database/models/monitoring_report.py` — Python module containing class `MonitoringReportModel`.
- `app/infrastructure/database/models/profile_command.py` — Python module containing class `MonitoringProfileCommandModel`.
- `app/infrastructure/database/models/remediation.py` — Python module containing class `RemediationPlanModel`, class `RemediationSandboxResultModel`, class `RemediationApprovalModel`, class `RemediationExecutionModel`, class `RemediationVerificationModel`.
- `app/infrastructure/database/models/report_analysis.py` — Python module containing class `AnalysisJobStatus`, class `ReportAnalysisModel`.
- `app/infrastructure/database/models/report_analysis_source.py` — Python module containing class `ReportAnalysisSourceModel`.
- `app/infrastructure/database/models/report_retrieval_document.py` — Python module containing class `ReportRetrievalDocumentModel`.
- `app/infrastructure/database/models/server.py` — Python module containing class `ServerStatus`, class `ServerModel`.
- `app/infrastructure/database/models/specialist_definition.py` — Python module containing class `SpecialistDefinitionModel`.
- `app/infrastructure/database/repositories/__init__.py` — Persistence repository module.
- `app/infrastructure/database/repositories/agent_job_repository.py` — Persistence repository module containing class `AgentJobRepository`.
- `app/infrastructure/database/repositories/analysis_repository.py` — Persistence repository module containing class `AnalysisRepository`.
- `app/infrastructure/database/repositories/analysis_source_repository.py` — Persistence repository module containing class `AnalysisSourceRepository`.
- `app/infrastructure/database/repositories/command_repository.py` — Persistence repository module containing class `CommandRepository`.
- `app/infrastructure/database/repositories/investigation_repository.py` — Persistence repository module containing class `InvestigationRepository`.
- `app/infrastructure/database/repositories/knowledge_document_repository.py` — Persistence repository module containing class `KnowledgeDocumentRepository`.
- `app/infrastructure/database/repositories/knowledge_retrieval_repository.py` — Persistence repository module containing class `KnowledgeSearchRow`, class `KnowledgeRetrievalRepository`.
- `app/infrastructure/database/repositories/knowledge_source_repository.py` — Persistence repository module containing class `KnowledgeSourceRepository`.
- `app/infrastructure/database/repositories/profile_repository.py` — Persistence repository module containing class `MonitoringProfileRepository`.
- `app/infrastructure/database/repositories/remediation_repository.py` — Persistence repository module containing class `RemediationRepository`.
- `app/infrastructure/database/repositories/report_repository.py` — Persistence repository module containing class `ReportRepository`.
- `app/infrastructure/database/repositories/retrieval_repository.py` — Persistence repository module containing class `RetrievalRepository`.
- `app/infrastructure/database/repositories/server_repository.py` — Persistence repository module containing class `ServerRepository`.
- `app/infrastructure/database/repositories/specialist_definition_repository.py` — Persistence repository module containing class `SpecialistDefinitionRepository`.
- `app/infrastructure/database/session.py` — Python module containing `get_database_session()`.
- `app/infrastructure/llm/__init__.py` — LLM infrastructure adapters.
- `app/infrastructure/llm/ollama/__init__.py` — Ollama infrastructure implementations.
- `app/infrastructure/llm/ollama/analysis_client.py` — Python module containing class `OllamaAnalysisClient`.
- `app/infrastructure/llm/ollama/embedding_client.py` — Python module containing class `OllamaEmbeddingClient`.
- `app/infrastructure/llm/ollama/final_diagnosis_client.py` — Python module containing class `OllamaFinalDiagnosisNarrativeClient`.
- `app/infrastructure/llm/ollama/specialist_reasoning_client.py` — Python module containing class `OllamaSpecialistReasoningClient`.
- `app/interfaces/__init__.py` — External adapters for HTTP administration and MCP.
- `app/interfaces/mcp/__init__.py` — Python module.
- `app/interfaces/mcp/catalog.py` — Categorizes project tools into monitoring, reports, retrieval, investigation, specialists, and remediation groups.
- `app/interfaces/mcp/handlers/__init__.py` — Python module.
- `app/interfaces/mcp/handlers/analysis.py` — Python module containing class `AnalysisToolsMixin`.
- `app/interfaces/mcp/handlers/common.py` — Python module containing class `BoundaryCommonMixin`.
- `app/interfaces/mcp/handlers/definitions.py` — Python module containing class `BoundaryDefinitionsMixin`.
- `app/interfaces/mcp/handlers/investigation.py` — Python module containing class `InvestigationToolsMixin`.
- `app/interfaces/mcp/handlers/monitoring.py` — Python module containing class `MonitoringToolsMixin`.
- `app/interfaces/mcp/handlers/remediation.py` — Python module containing class `RemediationToolsMixin`.
- `app/interfaces/mcp/registry.py` — Project tool execution boundary used by Claude through MCP; validates calls, invokes deterministic services, and returns structured results.
- `app/interfaces/mcp/schemas.py` — Stable MCP request and response contracts exposed to Claude Code.
- `app/interfaces/mcp/serializers.py` — Python module containing `serialize_value()`, `serialize_server()`, `serialize_profile()`, `serialize_monitoring_report_data()`, `serialize_report_details()`.
- `app/interfaces/mcp/server.py` — Project-scoped MCP protocol server exposing project tools to Claude Code.
- `app/main.py` — FastAPI application entry point; registers API/web routers and startup/shutdown behavior.
- `app/runtime/__init__.py` — Runtime adapters and supervisors.

### Claude Runtime

- `app/runtime/claude/__init__.py` — Claude runtime module.
- `app/runtime/claude/command.py` — Validated native Claude CLI process command contract.
- `app/runtime/claude/exceptions.py` — Claude runtime module containing class `ClaudeRuntimeError`, class `ClaudeStructuredOutputError`, class `ClaudeToolAccessError`, class `ClaudeProcessExecutionError`, class `ClaudeProcessOutputError`.
- `app/runtime/claude/job_service.py` — Claude runtime module containing class `ClaudeAgentJobService`.
- `app/runtime/claude/models.py` — Claude runtime module containing class `ClaudeJobStatus`, class `ClaudeRuntimeRequest`, class `ClaudeRawResult`, class `ClaudeStructuredOutput`, class `ClaudeRuntimeResult`.
- `app/runtime/claude/native_monitoring.py` — Claude runtime module containing class `ClaudeNativeMonitoringRunner`.
- `app/runtime/claude/observability.py` — Claude runtime module containing class `ClaudeAgentObservabilityService`.
- `app/runtime/claude/ollama_runtime.py` — Claude runtime module containing class `OllamaClaudeCommandBuilder`.
- `app/runtime/claude/result_parser.py` — Claude runtime module containing class `ClaudeStructuredResultParser`.
- `app/runtime/claude/runtime.py` — Claude runtime module containing class `ClaudeSessionRunner`, class `ClaudeRuntimeAdapter`.
- `app/runtime/claude/session_runner.py` — Claude runtime module containing class `SubprocessClaudeSessionRunner`.
- `app/runtime/claude/stream_decoder.py` — Claude runtime module containing class `ClaudeCliJsonDecoder`.
- `app/runtime/claude/supervisor.py` — Claude runtime module containing class `MonitoringRunner`, class `ClaudeSupervisor`.

### Monitoring Capability

- `app/capabilities/monitoring/__init__.py` — Server monitoring execution and report construction capabilities.
- `app/capabilities/monitoring/command_service.py` — Python module containing class `CommandService`.
- `app/capabilities/monitoring/profile_service.py` — Python module containing class `MonitoringProfileService`.
- `app/capabilities/monitoring/report_query_service.py` — Python module containing class `ReportQueryService`.
- `app/capabilities/monitoring/report_service.py` — Python module containing class `ReportService`.
- `app/capabilities/monitoring/scheduler.py` — Python module containing class `SchedulableServerRecord`, class `MonitoringRunnerProtocol`, class `SchedulerServerRepositoryProtocol`, class `MonitoringScheduler`.
- `app/capabilities/monitoring/server_service.py` — Python module containing class `ServerService`.
- `app/capabilities/monitoring/service.py` — Python module containing class `ServerRecord`, class `MonitoringCommandRecord`, class `ServerRepositoryProtocol`, class `MonitoringProfileRepositoryProtocol`, class `ReportRepositoryProtocol`.

### SSH Infrastructure

- `app/infrastructure/ssh/__init__.py` — Low-level, policy-neutral SSH transport and command execution.
- `app/infrastructure/ssh/client.py` — Known-hosts-verified SSH transport with validated private keys.
- `app/infrastructure/ssh/command_executor.py` — Bounded SSH command execution and result contract.

### Analysis Domain

- `app/capabilities/analysis/__init__.py` — Analysis capability package with lazy public exports.
- `app/capabilities/analysis/analysis_orchestrator.py` — Analysis domain module containing class `AnalysisOrchestrator`.
- `app/capabilities/analysis/client_factory.py` — Analysis domain module containing `create_llm_analysis_client()`.
- `app/capabilities/analysis/llm_client.py` — Analysis domain module containing class `LLMAnalysisClient`.
- `app/capabilities/analysis/prompts.py` — Analysis domain module containing `build_analysis_prompt()`.
- `app/capabilities/analysis/report_analyzer.py` — Analysis domain module containing class `ReportAnalyzer`.
- `app/capabilities/analysis/report_serializer.py` — Analysis domain module containing class `ReportSerializer`.
- `app/capabilities/analysis/retrieval/__init__.py` — Historical analysis retrieval components.
- `app/capabilities/analysis/retrieval/context_builder.py` — Analysis domain module containing class `RagContextBuilder`.
- `app/capabilities/analysis/retrieval/embedding_client.py` — Analysis domain module containing class `EmbeddingClient`.
- `app/capabilities/analysis/retrieval/embedding_factory.py` — Analysis domain module containing `create_embedding_client()`.
- `app/capabilities/analysis/retrieval/full_text_retriever.py` — Analysis domain module containing class `FullTextCandidate`, class `FullTextQueryBuilder`, class `FullTextRetriever`.
- `app/capabilities/analysis/retrieval/hybrid_retriever.py` — Analysis domain module containing class `_FusionCandidate`, class `HybridRetriever`.
- `app/capabilities/analysis/retrieval/performance_profiler.py` — Analysis domain module containing class `PerformanceProfile`, `start_profile()`, `record_timing()`, `set_counter()`, `snapshot()`.
- `app/capabilities/analysis/retrieval/rag_context.py` — Analysis domain module containing class `RetrievedAnalysisContext`.
- `app/capabilities/analysis/retrieval/rag_retriever.py` — Analysis domain module containing class `RagRetriever`.
- `app/capabilities/analysis/retrieval/report_fingerprint.py` — Analysis domain module containing class `ReportFingerprintService`.
- `app/capabilities/analysis/retrieval/report_normalizer.py` — Analysis domain module containing class `ReportNormalizer`.
- `app/capabilities/analysis/retrieval/retrieval_indexer.py` — Analysis domain module containing class `RetrievalIndexer`.
- `app/capabilities/analysis/retrieval/reuse_policy.py` — Analysis domain module containing class `AnalysisDecision`, class `AnalysisDecisionResult`, class `AnalysisReusePolicy`.
- `app/capabilities/analysis/retrieval/structured_compatibility.py` — Analysis domain module containing class `CompatibilityConflict`, class `CompatibilityResult`, class `StructuredCompatibilityChecker`.

### Investigation Domain

- `app/capabilities/investigation/__init__.py` — Investigation capability package with lazy public exports.
- `app/capabilities/investigation/correlation.py` — Investigation domain module containing class `DiagnosisCertainty`, class `DiagnosisConflict`, class `CorrelatedDiagnosisClaim`, class `FinalDiagnosis`, class `CrossSpecialistCorrelator`.
- `app/capabilities/investigation/evidence_collection.py` — Investigation domain module containing class `DiagnosticExecutionOutcome`, class `DiagnosticCommandRunner`, class `ServerRecord`, class `ServerRepositoryProtocol`, class `EvidenceCollectionRequest`.
- `app/capabilities/investigation/execution_contracts.py` — Investigation domain module containing class `InvestigationSpecialistRun`, class `InvestigationExecutionResult`.
- `app/capabilities/investigation/final_diagnosis_synthesizer.py` — Investigation domain module containing class `FinalDiagnosisSynthesizer`, `create_final_diagnosis_narrative_client()`.
- `app/capabilities/investigation/investigation_router.py` — Investigation domain module containing class `RoutingReason`, class `SpecialistRoutingMatch`, class `InvestigationRoutingDecision`, class `_IssueSignal`, class `_Candidate`.
- `app/capabilities/investigation/persistence_service.py` — Investigation domain module containing class `InvestigationPersistenceService`.
- `app/capabilities/investigation/read_service.py` — Investigation domain module containing class `InvestigationReadService`.
- `app/capabilities/investigation/runtime_snapshot_service.py` — Investigation domain module containing class `InvestigationRuntimeSnapshotService`.
- `app/capabilities/investigation/specialist_context.py` — Investigation domain module containing class `SpecialistContextBudget`, class `SpecialistContextSnapshot`, class `SpecialistKnowledgeQueryBuilder`, class `SpecialistContextBuilder`.
- `app/capabilities/investigation/specialist_investigation_loop.py` — Investigation domain module containing class `SpecialistLoopStopReason`, class `SpecialistLoopToolDecision`, class `SpecialistLoopRoundTrace`, class `SpecialistInvestigationLoopResult`, class `SpecialistInvestigationLoop`.
- `app/capabilities/investigation/specialist_reasoning_agent.py` — Investigation domain module containing class `SpecialistDiagnosticToolRequest`, class `SpecialistReasoningExecution`, class `SpecialistReasoningAgent`.
- `app/capabilities/investigation/specialist_reasoning_client.py` — Investigation domain module containing `create_specialist_reasoning_client()`.
- `app/capabilities/investigation/specialist_registry.py` — Investigation domain module containing class `SpecialistRegistryValidationError`, class `SpecialistRuntimeDefinition`, class `SpecialistDomainMatch`, class `SpecialistRegistrySnapshot`, class `SpecialistRegistry`.
- `app/capabilities/investigation/specialist_service.py` — Investigation domain module containing class `SpecialistDefinitionService`.

### Knowledge Domain

- `app/capabilities/knowledge/__init__.py` — Knowledge capability package with lazy public exports.
- `app/capabilities/knowledge/chunker.py` — Knowledge domain module containing class `KnowledgeChunkerConfig`, class `_Block`, class `StructureAwareKnowledgeChunker`.
- `app/capabilities/knowledge/chunking_service.py` — Knowledge domain module containing class `KnowledgeChunkingService`.
- `app/capabilities/knowledge/indexer.py` — Knowledge domain module containing class `KnowledgeIndexingResult`, class `KnowledgeIndexer`.
- `app/capabilities/knowledge/ingestion_contracts.py` — Knowledge domain module containing class `KnowledgeDocumentStatus`, class `ParsedKnowledgeDocument`, class `KnowledgeChunkDraft`.
- `app/capabilities/knowledge/ingestion_service.py` — Knowledge domain module containing class `KnowledgeIngestionService`.
- `app/capabilities/knowledge/parsers.py` — Knowledge domain module containing `normalize_text()`, class `_HTMLTextExtractor`, class `KnowledgeContentParser`.
- `app/capabilities/knowledge/retrieval.py` — Knowledge domain module containing class `KnowledgeRetrievalContext`, class `_FusionCandidate`, class `KnowledgeHybridRetriever`.
- `app/capabilities/knowledge/source_loader.py` — Knowledge domain module containing class `LoadedKnowledgeContent`, class `KnowledgeSourceLoader`.
- `app/capabilities/knowledge/source_registry.py` — Knowledge domain module containing class `KnowledgeSourceRuntimeDefinition`, class `KnowledgeSourceRegistrySnapshot`, class `KnowledgeSourceRegistry`.
- `app/capabilities/knowledge/source_service.py` — Knowledge domain module containing class `KnowledgeSourceService`.

### Evaluation and Production Readiness

- `tools/acceptance/evaluation/__init__.py` — Operator/developer tool.
- `tools/acceptance/evaluation/aggregate_readiness.py` — Operator/developer tool exposing class `AggregateEvaluationResult`, class `AggregateReadinessEvaluator`.
- `tools/acceptance/evaluation/cases.py` — Operator/developer tool exposing class `EvaluationCase`, `default_evaluation_cases()`.
- `tools/acceptance/evaluation/contracts.py` — Operator/developer tool exposing class `EvaluationMetric`, class `ReadinessStatus`, class `EvaluationObservation`, class `MetricThreshold`.
- `tools/acceptance/evaluation/persisted_runtime.py` — Operator/developer tool exposing class `PersistedRuntimeEvaluation`, class `PersistedRuntimeEvaluator`.
- `tools/acceptance/evaluation/phase5_readiness.py` — Operator/developer tool exposing class `Phase5Metric`, class `Phase5Observation`, class `Phase5MetricResult`, class `Phase5ReadinessResult`.
- `tools/acceptance/evaluation/readiness_gate.py` — Operator/developer tool exposing class `ProductionReadinessGate`.
- `tools/acceptance/evaluation/runner.py` — Operator/developer tool exposing class `EvaluationCaseResult`, class `EvaluationRunResult`, class `DeterministicEvaluationRunner`, `expected_behavior_executor()`.
- `tools/acceptance/evaluation/runtime_readiness.py` — Operator/developer tool exposing class `RuntimeReadinessMetric`, class `RuntimeReadinessResult`, class `RuntimeReadinessGate`.
- `tools/acceptance/evaluation/safety_runtime.py` — Operator/developer tool exposing class `_StaticRegistry`, `evaluate_routing_cases()`, `evaluate_policy_cases()`, `evaluate_provider_cases()`.

### Administration API and Web UI

- `app/interfaces/admin/__init__.py` — Administration interface package.
- `app/interfaces/admin/api/__init__.py` — FastAPI API router/module.
- `app/interfaces/admin/api/agent_observability.py` — FastAPI API router/module exposing `list_agent_job_traces()`, `get_agent_job_trace()`, `get_agent_observability_summary()`.
- `app/interfaces/admin/api/commands.py` — FastAPI API router/module exposing `list_commands()`, `get_command()`, `create_command()`, `update_command()`.
- `app/interfaces/admin/api/diagnostic_tools.py` — FastAPI API router/module exposing `list_diagnostic_tools()`.
- `app/interfaces/admin/api/investigations.py` — FastAPI API router/module exposing `list_investigations()`, `get_investigation()`, `list_report_investigations()`.
- `app/interfaces/admin/api/knowledge_sources.py` — FastAPI API router/module exposing `list_knowledge_sources()`, `get_knowledge_source()`, `create_knowledge_source()`, `update_knowledge_source()`.
- `app/interfaces/admin/api/profiles.py` — FastAPI API router/module exposing `list_profiles()`, `get_profile()`, `create_profile()`, `update_profile()`.
- `app/interfaces/admin/api/remediation.py` — FastAPI API router/module exposing `list_remediation_plans()`, `get_remediation_plan()`, `get_remediation_audit()`, `request_remediation_approval()`.
- `app/interfaces/admin/api/reports.py` — FastAPI API router/module exposing `list_reports()`, `get_report()`, `get_report_analysis()`, `get_report_analysis_sources()`.
- `app/interfaces/admin/api/servers.py` — FastAPI API router/module exposing `list_servers()`, `get_server()`, `create_server()`, `update_server()`.
- `app/interfaces/admin/api/specialists.py` — FastAPI API router/module exposing `list_specialists()`, `get_specialist()`, `create_specialist()`, `update_specialist()`.
- `app/interfaces/admin/api/system.py` — FastAPI API router/module exposing `get_runtime_overview()`.
- `app/interfaces/admin/dependencies.py` — Python module containing `get_monitoring_profile_service()`, `get_server_service()`, `get_command_service()`, `get_report_query_service()`, `get_ssh_test_service()`.
- `app/interfaces/admin/schemas/__init__.py` — API/schema models.
- `app/interfaces/admin/schemas/commands.py` — API/schema models including class `CommandCreateRequest`, class `CommandUpdateRequest`, class `CommandResponse`, class `AssignCommandRequest`, class `UpdateCommandAssignmentRequest`.
- `app/interfaces/admin/schemas/investigations.py` — API/schema models including class `InvestigationCandidateResponse`, class `InvestigationSummaryResponse`, class `InvestigationRuntimeResponse`, class `InvestigationDetailResponse`.
- `app/interfaces/admin/schemas/knowledge_sources.py` — API/schema models including class `KnowledgeSourceCreateRequest`, class `KnowledgeSourceUpdateRequest`, class `KnowledgeSourceEnabledRequest`, class `KnowledgeSourceResponse`.
- `app/interfaces/admin/schemas/profiles.py` — API/schema models including class `MonitoringProfileCreateRequest`, class `MonitoringProfileUpdateRequest`, class `MonitoringProfileResponse`, class `AssignProfileCommandRequest`, class `UpdateProfileCommandRequest`.
- `app/interfaces/admin/schemas/remediation.py` — API/schema models including class `ApprovalRequest`, class `ApprovalDecisionRequest`, class `ExecuteRemediationRequest`, class `RollbackRemediationRequest`.
- `app/interfaces/admin/schemas/reports.py` — API/schema models including class `ReportListItemResponse`, class `PaginatedReportsResponse`, class `CommandExecutionResponse`, class `ReportDetailsResponse`, class `ReportAnalysisResponse`.
- `app/interfaces/admin/schemas/servers.py` — API/schema models including class `ServerCreateRequest`, class `ServerUpdateRequest`, class `ServerResponse`, class `SSHTestResponse`.
- `app/interfaces/admin/schemas/specialists.py` — API/schema models including class `SpecialistCreateRequest`, class `SpecialistUpdateRequest`, class `SpecialistEnabledRequest`, class `SpecialistResponse`.
- `app/interfaces/admin/services/__init__.py` — Service-layer module.
- `app/interfaces/admin/services/report_pdf_service.py` — Service-layer module containing class `ReportPdfService`.
- `app/interfaces/admin/services/ssh_test_service.py` — Service-layer module containing class `SSHTestResult`, class `SSHTestService`.
- `app/interfaces/admin/web/__init__.py` — Python module.
- `app/interfaces/admin/web/routes.py` — Python module containing `dashboard_page()`, `servers_page()`, `commands_page()`, `investigations_page()`, `reports_page()`.
- `app/interfaces/admin/web/static/css/app.css` — Administration UI stylesheet.
- `app/interfaces/admin/web/static/js/app.js` — Administration UI browser-side JavaScript.
- `app/interfaces/admin/web/static/js/commands.js` — Administration UI browser-side JavaScript.
- `app/interfaces/admin/web/static/js/monitoring_profiles.js` — Administration UI browser-side JavaScript.
- `app/interfaces/admin/web/static/js/report_details.js` — Administration UI browser-side JavaScript.
- `app/interfaces/admin/web/static/js/servers.js` — Administration UI browser-side JavaScript.
- `app/interfaces/admin/web/templates/agent_runs.html` — Jinja/HTML administration UI template.
- `app/interfaces/admin/web/templates/base.html` — Jinja/HTML administration UI template.
- `app/interfaces/admin/web/templates/commands.html` — Jinja/HTML administration UI template.
- `app/interfaces/admin/web/templates/dashboard.html` — Jinja/HTML administration UI template.
- `app/interfaces/admin/web/templates/investigation_details.html` — Jinja/HTML administration UI template.
- `app/interfaces/admin/web/templates/investigations.html` — Jinja/HTML administration UI template.
- `app/interfaces/admin/web/templates/knowledge_sources.html` — Jinja/HTML administration UI template.
- `app/interfaces/admin/web/templates/monitoring_profiles.html` — Jinja/HTML administration UI template.
- `app/interfaces/admin/web/templates/remediation.html` — Jinja/HTML administration UI template.
- `app/interfaces/admin/web/templates/report_details.html` — Jinja/HTML administration UI template.
- `app/interfaces/admin/web/templates/reports.html` — Jinja/HTML administration UI template.
- `app/interfaces/admin/web/templates/runtime_policies.html` — Jinja/HTML administration UI template.
- `app/interfaces/admin/web/templates/servers.html` — Jinja/HTML administration UI template.
- `app/interfaces/admin/web/templates/specialists.html` — Jinja/HTML administration UI template.
- `app/interfaces/admin/web/templates/system.html` — Jinja/HTML administration UI template.

### Tools and acceptance scripts

- `tools/acceptance/__init__.py` — Acceptance and runtime verification entry points.
- `tools/acceptance/check_knowledge_source_acceptance.py` — Operator/developer tool exposing `main()`.
- `tools/acceptance/run_all_tests.py` — Operator/developer tool exposing `run()`, `tool_exists()`, `main()`.
- `tools/acceptance/run_evaluation_dataset.py` — Operator/developer tool exposing `main()`.
- `tools/acceptance/run_investigation_web_api_acceptance.py` — Operator/developer tool exposing `status()`, `main()`.
- `tools/acceptance/run_persisted_runtime_evaluation.py` — Operator/developer tool exposing `main()`.
- `tools/acceptance/run_phase5_readiness_evaluation.py` — Operator/developer tool exposing `main()`.
- `tools/acceptance/run_production_readiness_evaluation.py` — Operator/developer tool exposing `run()`, `main()`.
- `tools/acceptance/run_safety_runtime_evaluation.py` — Operator/developer tool exposing `run()`, `main()`.
- `tools/acceptance/smoke_ollama_claude_runtime.py` — Operator/developer tool exposing `parse_args()`, `jsonable()`, `prepare_database_schema()`, `main_async()`.
- `tools/bootstrap_database.py` — Operator/developer tool exposing `connection_kwargs()`, `database_exists()`, `create_database_if_missing()`, `ensure_vector_extension()`.
- `tools/claude_hooks/runtime_hooks.py` — Operator/developer tool exposing `dispatch()`, `main()`.
- `tools/dev/__init__.py` — Developer, inspection, seeding, and documentation utilities.
- `tools/dev/audit_documentation.py` — Operator/developer tool exposing `rel()`, `local_markdown_links()`, `main()`.
- `tools/dev/chunk_knowledge_document.py` — Operator/developer tool exposing `main()`.
- `tools/dev/collect_diagnostic_evidence.py` — Operator/developer tool exposing `parse_args()`, `run()`, `main()`.
- `tools/dev/evaluate_rag.py` — Operator/developer tool exposing class `EvaluationSummary`, `ratio()`, `fetch_hnsw_index_present()`, `build_document_map()`.
- `tools/dev/generate_project_structure.py` — Operator/developer tool exposing `should_skip()`, `python_summary()`, `describe()`, `group()`.
- `tools/dev/generate_test_catalog.py` — Operator/developer tool exposing `first_docstring()`, `test_functions()`, `main()`.
- `tools/dev/index_knowledge_document.py` — Operator/developer tool exposing `run()`, `main()`.
- `tools/dev/ingest_knowledge_source.py` — Operator/developer tool exposing `main()`.
- `tools/dev/inspect_diagnostic_policy.py` — Operator/developer tool exposing `main()`.
- `tools/dev/inspect_diagnostic_tools.py` — Operator/developer tool exposing `main()`.
- `tools/dev/inspect_investigation.py` — Operator/developer tool exposing `main()`.
- `tools/dev/inspect_investigation_routing.py` — Operator/developer tool exposing `print_matches()`, `main()`.
- `tools/dev/inspect_knowledge_index.py` — Operator/developer tool exposing `db_indexes()`, `main()`.
- `tools/dev/inspect_knowledge_sources.py` — Operator/developer tool exposing `main()`.
- `tools/dev/inspect_specialist_context.py` — Operator/developer tool exposing `run()`, `main()`.
- `tools/dev/inspect_specialist_registry.py` — Operator/developer tool exposing `main()`.
- `tools/dev/list_routes.py` — Operator/developer tool exposing `collect_routes()`, `main()`.
- `tools/dev/persist_investigation_routing.py` — Operator/developer tool exposing `main()`.
- `tools/dev/production_preflight.py` — Operator/developer tool exposing `check()`, `main()`.
- `tools/dev/reason_specialist_context.py` — Operator/developer tool exposing `run()`, `main()`.
- `tools/dev/report_rag_performance.py` — Operator/developer tool exposing `percentile()`, `stats()`, `main()`.
- `tools/dev/run_specialist_investigation.py` — Operator/developer tool exposing `run()`, `main()`.
- `tools/dev/search_knowledge.py` — Operator/developer tool exposing `run()`, `main()`.
- `tools/dev/seed_knowledge_sources.py` — Operator/developer tool exposing class `SeedKnowledgeSource`, `create_dto()`, `update_dto()`, `main()`.
- `tools/dev/seed_specialists.py` — Operator/developer tool exposing `build_create_dto()`, `build_update_dto()`, `main()`.
- `tools/dev/sync_documentation.py` — Operator/developer tool exposing `rel()`, `classify()`, `title()`, `remove_managed_block()`.
- `tools/linux_scenarios/random_linux_workload.py` — Operator/developer tool exposing `now()`, `busy_worker()`, `cpu_scenario()`, `memory_scenario()`.
- `tools/linux_scenarios/run_linux_scenario_matrix.py` — Operator/developer tool exposing `main()`.
- `tools/run_project_mcp_server.py` — Stdio entrypoint used by .mcp.json to run the project MCP server.

### Tests

- `tests/conftest.py` — Pytest coverage for the corresponding project behavior.
- `tests/real_runtime/__init__.py` — Pytest coverage for the corresponding project behavior.
- `tests/real_runtime/test_c14_11_claude_ollama_mcp_acceptance.py` — Pytest coverage for `test_c14_11_real_claude_ollama_mcp_cycle_persists_evidence()`.
- `tests/test_admin_system_api.py` — Pytest coverage for class `FakeSupervisor`, class `FakeToolBoundary`, `test_system_runtime_api_exposes_supervisor_and_tools()`.
- `tests/test_admin_system_web.py` — Pytest coverage for `test_system_runtime_page_is_available()`.
- `tests/test_agent_job_persistence.py` — Pytest coverage for `test_agent_job_error_messages_are_bounded_to_schema_contract()`.
- `tests/test_aggregate_readiness.py` — Pytest coverage for `obs()`, `test_aggregate_combines_sources()`, `test_sample_deficits_are_reported()`, `test_one_real_runtime_sample_is_not_ready()`, `test_hard_failure_blocks_when_samples_sufficient()`.
- `tests/test_architecture_dependencies.py` — Pytest coverage for `test_core_has_no_outer_layer_dependencies()`, `test_capabilities_do_not_depend_on_interfaces_composition_or_runtime()`, `test_infrastructure_does_not_depend_on_interface_or_runtime_layers()`, `test_legacy_application_packages_are_absent()`, `test_application_sources_do_not_import_deleted_namespaces()`.
- `tests/test_c14_10_claude_observability.py` — Pytest coverage for class `FakeRepository`, `make_job()`, `test_trace_normalizes_runtime_evidence()`, `test_summary_exposes_failures_tools_and_mcp_health()`, `test_completed_job_missing_required_tools_is_visible()`.
- `tests/test_c14_11_runtime_contract.py` — Pytest coverage for `test_c14_11_runtime_allows_mandatory_operational_tools()`, `test_c14_11_native_prompt_requires_real_mcp_execution()`.
- `tests/test_c14_11a3_ollama_only_contract.py` — Pytest coverage for `test_c14_11a3_removes_legacy_runtime_surfaces()`, `test_c14_11a3_runtime_dependencies_are_ollama_only()`, `test_c14_11a3_no_openai_implementation_surfaces_remain()`, `test_c14_11a3_ollama_implementations_remain()`.
- `tests/test_c14_11a4_1_composition_boundary.py` — Pytest coverage for `test_composition_owns_the_application_container()`, `test_composition_builder_owns_dependency_wiring()`, `test_composition_package_exists_as_explicit_boundary()`.
- `tests/test_c14_11a4_2a_repository_composition.py` — Pytest coverage for `test_repository_construction_lives_in_repository_composition_module()`, `test_repository_composition_module_is_not_eager()`.
- `tests/test_c14_11a4_2b_container_services_composition.py` — Pytest coverage for `test_application_container_is_outside_builder()`, `test_core_service_construction_is_outside_builder()`, `test_analysis_and_runtime_are_outside_builder()`.
- `tests/test_c14_11a4_2c_analysis_investigation_composition.py` — Pytest coverage for `test_analysis_and_investigation_composition_is_outside_builder()`, `test_claude_mcp_and_scheduler_wiring_moves_to_runtime_composition()`.
- `tests/test_c14_11a4_2d_runtime_composition.py` — Pytest coverage for `test_runtime_composition_is_outside_builder()`, `test_runtime_composition_keeps_ollama_claude_contract()`, `test_builder_is_composition_coordinator_after_a4_2d()`.
- `tests/test_c14_11a4_3a_ollama_infrastructure_boundary.py` — Pytest coverage for `test_ollama_provider_implementations_live_in_infrastructure()`, `test_analysis_capability_factories_use_infrastructure_implementations()`, `test_legacy_ollama_modules_are_removed()`.
- `tests/test_c14_11a4_3b_investigation_ollama_infrastructure.py` — Pytest coverage for `test_investigation_ollama_adapters_live_in_infrastructure()`, `test_investigation_capability_keeps_contracts_not_ollama_implementations()`, `test_capability_contracts_resolve_provider_adapters_lazily()`.
- `tests/test_c14_11a4_3c_database_infrastructure_boundary.py` — Pytest coverage for `test_database_core_implementation_lives_in_infrastructure()`, `test_repository_implementations_live_only_in_infrastructure()`, `test_production_composition_uses_infrastructure_repositories()`, `test_shared_database_package_is_removed_after_boundary_closure()`.
- `tests/test_c14_11a4_3d_database_models_migrations_boundary.py` — Pytest coverage for `test_database_models_live_only_in_infrastructure()`, `test_production_uses_infrastructure_model_imports()`, `test_engine_registers_infrastructure_models()`, `test_migrations_have_one_canonical_owner()`.
- `tests/test_c14_12_runtime_readiness.py` — Pytest coverage for `test_c14_12_startup_recovers_interrupted_jobs()`, `test_c14_12_mcp_surface_is_bounded_and_stable()`, `test_c14_12_unknown_and_unregistered_tools_fail_closed()`, `test_c14_12_claude_malformed_output_fails_closed()`, `test_c14_12_controlled_policy_and_provider_failures_are_measured()`.
- `tests/test_c14_7_smoke_schema_init.py` — Pytest coverage for `test_c14_7_smoke_initializes_schema_before_container()`, `test_c14_7_smoke_preserves_direct_project_import_fix()`.
- `tests/test_c14_7_stream_runtime_evidence.py` — Pytest coverage for `test_stream_json_operational_success_is_evidence_based()`, `test_operational_success_rejects_failed_mcp()`, `test_operational_success_rejects_missing_required_tool()`, `test_result_error_subtype_is_not_accepted()`.
- `tests/test_c14_8_project_boundary_decomposition.py` — Pytest coverage for `make_boundary()`, `test_c14_8_public_tool_contract_is_unchanged()`, `test_c14_8_project_boundary_is_thin_public_facade()`, `test_c14_8_bounded_modules_own_tool_implementations()`, `test_c14_8_mcp_package_export_is_lazy_and_cycle_free()`.
- `tests/test_c14_9_claude_native_orchestration.py` — Pytest coverage for `test_c14_9_legacy_python_orchestrators_are_removed()`, `test_c14_9_monitoring_service_is_execution_only()`, `test_c14_9_runtime_exports_only_native_claude_orchestration()`, `test_c14_9_domain_packages_drop_old_orchestration_exports()`, `test_c14_9_supervisor_fails_closed_when_runtime_disabled()`.
- `tests/test_claude_agent_job_persistence.py` — Pytest coverage for `make_repository()`, `make_request()`, `test_job_is_created_from_runtime_request()`, `test_job_completion_preserves_result_observability()`, `test_job_survives_repository_recreation()`.
- `tests/test_claude_bounded_agents.py` — Pytest coverage for `read_text()`, `parse_frontmatter()`, `test_canonical_agent_set_is_two_bounded_roles()`, `test_server_supervisor_is_main_session_coordinator()`, `test_specialist_worker_cannot_delegate_or_remediate()`.
- `tests/test_claude_code_runtime_configuration.py` — Pytest coverage for `read_text()`, `parse_frontmatter()`, `test_project_mcp_server_is_registered_for_claude_code()`, `test_claude_settings_use_enforced_permissions()`, `test_claude_agents_have_frontmatter_and_tools()`.
- `tests/test_claude_least_privilege.py` — Pytest coverage for `read_text()`, `parse_frontmatter()`, `test_settings_allow_only_current_runtime_capabilities()`, `test_raw_remediation_escape_tools_are_explicitly_denied()`, `test_raw_operational_shell_paths_are_denied_for_both_shells()`.
- `tests/test_claude_operational_skills.py` — Pytest coverage for `read_skill()`, `frontmatter()`, `allowed_tools()`, `test_operational_skill_set_is_canonical()`, `test_skills_have_frontmatter_and_exact_intended_tools()`.
- `tests/test_claude_process_session_runner.py` — Pytest coverage for `request()`, class `ScriptCommandBuilder`, `write_script()`, `test_process_runner_decodes_structured_output()`, `test_process_runner_accepts_result_text_envelope()`.
- `tests/test_claude_project_mcp_runtime_config.py` — Pytest coverage for `read_json()`, `test_vps_project_mcp_is_explicitly_approved()`, `test_vps_mcp_launch_is_project_root_stable()`.
- `tests/test_claude_runtime_adapter.py` — Pytest coverage for `request()`, class `Runner`, `test_bounded_claude_invocation_succeeds()`, `test_timeout_is_returned_as_controlled_result()`, `test_runtime_failure_is_returned_as_controlled_result()`.
- `tests/test_claude_runtime_documentation.py` — Pytest coverage for `read_doc()`, `test_project_structure_documents_runtime_files()`, `test_runtime_operations_doc_matches_configured_ollama_defaults()`, `test_runtime_documentation_has_current_verification_commands()`, `test_r5_status_and_test_catalog_are_documented()`.
- `tests/test_claude_runtime_hooks.py` — Pytest coverage for `read_settings()`, `run_hook()`, `runtime_payload()`, `test_settings_register_only_concrete_runtime_hooks()`, `test_hook_handlers_use_cross_platform_exec_form()`.
- `tests/test_claude_supervisor.py` — Pytest coverage for class `Runner`, `test_supervisor_delegates_monitoring_cycle()`, `test_supervisor_reports_runtime_status()`.
- `tests/test_cross_specialist_conflicts.py` — Pytest coverage for `make_state()`, `make_run()`, `wrap()`, `test_explicit_conflicting_states_become_unknown()`, `test_matching_explicit_states_do_not_conflict()`.
- `tests/test_cross_specialist_correlation.py` — Pytest coverage for `make_state()`, `make_run()`, `wrap()`, `test_live_evidence_high_confidence_is_confirmed()`, `test_live_evidence_lower_confidence_is_probable()`.
- `tests/test_diagnostic_policy.py` — Pytest coverage for `specialist()`, `request()`, `engine()`, `test_policy_allows_registered_assigned_safe_tool()`, `test_policy_denies_unknown_tool()`.
- `tests/test_diagnostic_tool_registry.py` — Pytest coverage for `registry()`, `test_default_registry_contains_expected_read_only_tools()`, `test_service_parameter_rejects_shell_injection()`, `test_path_parameter_rejects_shell_injection()`, `test_connect_probe_validates_port()`.
- `tests/test_diagnostic_tools_api.py` — Pytest coverage for `test_diagnostic_tools_api_lists_registry()`.
- `tests/test_domain_boundaries.py` — Pytest coverage for `test_removed_domain_package_has_no_boundary_to_audit()`.
- `tests/test_evaluation_dataset_runner.py` — Pytest coverage for `test_default_dataset_meets_gate_sample_counts()`, `test_case_ids_are_unique()`, `test_expected_behavior_executor_wires_gate()`, `test_runtime_failure_blocks_hard_metric()`, `test_executor_must_return_matching_case_id()`.
- `tests/test_evidence_collection.py` — Pytest coverage for class `Repository`, class `Runner`, `make_outcome()`, `allowed_policy()`, `denied_policy()`.
- `tests/test_final_diagnosis_synthesizer.py` — Pytest coverage for `diagnosis()`, class `Client`, `test_valid_llm_narrative_is_used()`, `test_unknown_claim_id_uses_fallback()`, `test_conflict_must_be_preserved()`.
- `tests/test_hybrid_retriever.py` — Pytest coverage for class `FakeAnalysis`, class `FakeDocument`, class `FakeAnalysisRepository`, class `FakeRetrievalRepository`, class `FakeVectorRetriever`.
- `tests/test_investigation_contracts.py` — Pytest coverage for `make_state()`, `make_task()`, `test_default_investigation_state()`, `test_confidence_must_be_normalized()`, `test_duplicate_evidence_is_rejected()`.
- `tests/test_investigation_persistence_service.py` — Pytest coverage for class `FakeRepository`, `make_match()`, `test_persistence_preserves_candidate_and_selected_ranks()`, `test_healthy_decision_can_be_persisted_for_audit()`.
- `tests/test_investigation_read_service.py` — Pytest coverage for class `Candidate`, class `Model`, class `Repository`, `test_read_model_does_not_invent_runtime()`, `test_runtime_snapshot_is_exposed_when_persisted()`.
- `tests/test_investigation_router.py` — Pytest coverage for `specialist()`, class `FakeRepository`, `make_router()`, `report()`, `analysis()`.
- `tests/test_investigation_runtime_snapshot_service.py` — Pytest coverage for class `Repository`, `make_result()`, `make_diagnosis()`, `test_build_snapshot_serializes_runtime()`, `test_persist_preserves_existing_metadata()`.
- `tests/test_investigations_api.py` — Pytest coverage for `summary()`, `detail()`, class `Service`, `make_client()`, `test_list_investigations()`.
- `tests/test_investigations_web.py` — Pytest coverage for `make_client()`, `test_investigations_page_is_available()`, `test_investigation_detail_page_is_available()`.
- `tests/test_knowledge_chunker.py` — Pytest coverage for `make_chunker()`, `test_markdown_heading_is_preserved_as_section()`, `test_html_heading_metadata_is_used()`, `test_pdf_page_metadata_preserves_page_number()`, `test_large_document_is_split_under_max_chars()`.
- `tests/test_knowledge_chunking_service.py` — Pytest coverage for class `Repository`, `test_chunking_service_persists_chunks()`.
- `tests/test_knowledge_hybrid_retrieval.py` — Pytest coverage for class `EmbeddingClient`, `row()`, class `Repository`, `test_hybrid_retrieval_fuses_both_branches()`, `test_specialist_scope_boosts_direct_source()`.
- `tests/test_knowledge_indexer.py` — Pytest coverage for class `EmbeddingClient`, class `Repository`, `test_indexer_embeds_all_chunks_and_marks_document()`, `test_indexer_skips_current_embedding()`, `test_force_reindexes_current_embedding()`.
- `tests/test_knowledge_ingestion_contracts.py` — Pytest coverage for `test_document_status_lifecycle_is_explicit()`, `test_parsed_document_requires_text()`, `test_parsed_document_accepts_large_document_metadata()`, `test_chunk_draft_preserves_page_and_section()`, `test_chunk_index_is_zero_based()`.
- `tests/test_knowledge_ingestion_service.py` — Pytest coverage for class `SourceRepository`, class `Loader`, class `DocumentRepository`, `test_ingestion_persists_parsed_document()`.
- `tests/test_knowledge_parsers.py` — Pytest coverage for `test_normalize_text_collapses_spacing()`, `test_html_parser_removes_script_and_extracts_title()`, `test_plain_text_parser()`.
- `tests/test_knowledge_retrieval_scope.py` — Pytest coverage for `compile_condition()`, `test_scope_condition_contains_specialist()`, `test_scope_condition_accepts_domains()`, `test_empty_scope_is_true()`.
- `tests/test_knowledge_source_foundation.py` — Pytest coverage for class `FakeRepository`, `source()`, `test_url_source_requires_uri()`, `test_inline_source_requires_content()`, `test_create_dto_normalizes_scope()`.
- `tests/test_knowledge_source_loader.py` — Pytest coverage for `test_inline_loader()`, `test_loader_rejects_unknown_source_type()`.
- `tests/test_knowledge_source_seed.py` — Pytest coverage for `test_seed_slugs_are_unique()`, `test_seed_sources_are_official_https_urls()`, `test_seed_covers_all_baseline_specialists()`, `test_each_seed_has_routing_scope()`.
- `tests/test_ollama_claude_runtime.py` — Pytest coverage for `test_direct_claude_uses_ollama_backend()`, `test_runtime_composition_uses_direct_claude_settings()`.
- `tests/test_ollama_context_window.py` — Pytest coverage for `run_request()`, `test_normal_reasoning_uses_32k_context_and_6144_output()`, `test_final_synthesis_uses_32k_context_and_6144_output()`.
- `tests/test_ollama_final_synthesis_dto.py` — Pytest coverage for `test_final_synthesis_minimal_contract_succeeds()`.
- `tests/test_ollama_final_synthesis_minimal_contract.py` — Pytest coverage for `test_final_synthesis_uses_minimal_json_mode()`, `test_normal_reasoning_keeps_existing_generation_limits()`.
- `tests/test_ollama_specialist_reasoning_client.py` — Pytest coverage for `make_response()`, `test_schema_rejection_is_cached_and_json_fallback_succeeds()`, `test_length_retry_uses_compact_retry_instruction()`, `test_final_synthesis_enables_provider_compact_mode()`.
- `tests/test_persisted_runtime_evaluation.py` — Pytest coverage for `make_detail()`, `by_metric()`, `test_valid_snapshot_emits_five_real_metrics()`, `test_unknown_evidence_fails_grounding()`, `test_budget_overrun_fails()`.
- `tests/test_phase5_readiness.py` — Pytest coverage for `test_phase5_gate_requires_all_metrics_and_real_acceptance()`, `test_phase5_gate_passes_only_with_explicit_real_acceptance()`.
- `tests/test_phase5_supervised_remediation.py` — Pytest coverage for class `FakeWriter`, class `FakeVerifier`, `make_service()`, `make_plan()`, `approve_plan()`.
- `tests/test_production_readiness_gate.py` — Pytest coverage for `observations_for_thresholds()`, `test_gate_requires_minimum_samples()`, `test_all_thresholds_pass_supervised_only()`, `test_hard_safety_failure_blocks()`, `test_policy_failure_blocks()`.
- `tests/test_project_mcp_analysis_tools.py` — Pytest coverage for class `Analysis`, class `AnalysisRepository`, class `AnalysisOrchestrator`, class `IncidentRetriever`, class `KnowledgeRetriever`.
- `tests/test_project_mcp_investigation_tools.py` — Pytest coverage for class `Router`, class `PersistedInvestigation`, class `PersistenceService`, class `ReadService`, class `EmptyAnalysisRepository`.
- `tests/test_project_mcp_protocol_server.py` — Pytest coverage for class `ToolBoundary`, `run_message()`, `test_mcp_initialize_exposes_tool_capability()`, `test_mcp_tools_list_uses_project_tool_definitions()`, `test_mcp_tools_call_returns_structured_project_result()`.
- `tests/test_project_mcp_remediation_tools.py` — Pytest coverage for `make_remediation_service()`, `boundary()`, `run_tool()`, `plan_arguments()`, `test_propose_remediation_requires_diagnosis_and_evidence_links()`.
- `tests/test_project_mcp_specialist_tools.py` — Pytest coverage for `specialist()`, class `SpecialistRegistry`, class `SpecialistLoop`, `boundary()`, `run_tool()`.
- `tests/test_project_mcp_tool_boundary.py` — Pytest coverage for class `Server`, class `Profile`, class `Command`, class `Assignment`, class `ServerService`.
- `tests/test_project_tool_catalog.py` — Pytest coverage for `boundary()`, `test_every_project_tool_belongs_to_one_group()`, `test_boundary_exposes_grouped_tool_definitions()`, `test_tool_group_lookup_rejects_unknown_tools()`.
- `tests/test_rag_evaluation_contract.py` — Pytest coverage for `test_hybrid_does_not_use_rrf_as_vector_similarity()`, `test_orchestrator_persists_vector_similarity_not_rrf()`, `test_vector_repository_filters_before_limit()`.
- `tests/test_reuse_policy.py` — Pytest coverage for `policy()`, `test_exact_fingerprint_reuses_analysis()`, `test_force_always_requires_full_analysis()`, `test_compatible_historical_context_is_assisted()`, `test_context_is_ignored_when_assisted_is_disabled()`.
- `tests/test_route_inventory.py` — Pytest coverage for `test_route_inventory_contains_application_routes()`, `test_web_routes_are_excluded_from_openapi()`, `test_specialists_api_is_in_openapi_inventory()`, `test_health_route_remains_visible()`.
- `tests/test_runtime_readiness_gate.py` — Pytest coverage for `observations()`, `test_runtime_readiness_gate_passes_full_non_regressing_matrix()`, `test_runtime_readiness_gate_blocks_missing_runtime_case()`, `test_runtime_readiness_gate_blocks_critical_regression()`, `test_runtime_readiness_gate_blocks_critical_score_regression()`.
- `tests/test_safety_runtime_evaluation.py` — Pytest coverage for `test_routing_runtime_emits_ten_passes()`, `test_policy_runtime_emits_ten_passes()`, `test_provider_runtime_emits_ten_safe_results()`.
- `tests/test_specialist_context.py` — Pytest coverage for `specialist()`, `task()`, `knowledge()`, class `Retriever`, `test_context_preserves_knowledge_source_ids()`.
- `tests/test_specialist_definition_repository.py` — Pytest coverage for `repository()`, `make_specialist()`, `test_create_and_reload()`, `test_slug_is_normalized()`, `test_duplicate_slug_is_rejected()`.
- `tests/test_specialist_investigation_loop.py` — Pytest coverage for class `ContextBuilder`, class `ReasoningAgent`, class `EvidenceCollector`, `specialist()`, `task()`.
- `tests/test_specialist_reasoning_agent.py` — Pytest coverage for class `Client`, `context()`, `valid_output()`, `test_reasoning_converts_valid_output_to_contract()`, `test_unknown_knowledge_citation_is_rejected()`.
- `tests/test_specialist_reasoning_client_ollama_compat.py` — Pytest coverage for class `FakeResponse`, class `FakeHTTPClient`, `valid_content()`, `make_client()`, `test_schema_http_400_falls_back_to_json_mode()`.
- `tests/test_specialist_reasoning_client_structured_output.py` — Pytest coverage for class `Response`, class `HTTPClient`, `valid_content()`, `make_client()`, `test_ollama_uses_json_schema_as_format()`.
- `tests/test_specialist_reasoning_objective_prompt.py` — Pytest coverage for class `Client`, `context()`, `test_objective_is_prominent_before_and_after_catalog()`.
- `tests/test_specialist_reasoning_provenance_ids.py` — Pytest coverage for class `Client`, `context()`, `test_evidence_namespace_prefix_is_normalized_only_for_real_id()`, `test_unknown_prefixed_reference_remains_rejected()`.
- `tests/test_specialist_reasoning_tool_requests.py` — Pytest coverage for class `Client`, `context()`, `test_reasoning_returns_structured_tool_requests()`.
- `tests/test_specialist_registry.py` — Pytest coverage for `specialist()`, class `FakeRepository`, `test_disabled_specialists_are_excluded()`, `test_snapshot_is_stable_and_uses_one_repository_read()`, `test_registry_order_is_deterministic()`.
- `tests/test_specialists_api.py` — Pytest coverage for `model()`, class `FakeService`, `client()`, `test_list_specialists()`, `test_create_specialist()`.
- `tests/test_structured_compatibility.py` — Pytest coverage for `report()`, `test_identical_structured_state_is_compatible()`, `test_connection_state_conflict_is_rejected()`, `test_command_success_conflict_is_rejected()`, `test_exit_status_class_conflict_is_rejected()`.

### Documentation

- `docs/ADR_README.append.md` — Project documentation.
- `docs/DOCUMENTATION_INVENTORY.md` — Project documentation.
- `docs/DOCUMENTATION_MAINTENANCE.md` — Project documentation.
- `docs/PROJECT_STATUS.md` — Project documentation.
- `docs/README.md` — Project documentation.
- `docs/api/admin-management.md` — Project documentation.
- `docs/api/admin-web-ui.md` — Project documentation.
- `docs/api/http-api.md` — Project documentation.
- `docs/api/investigations.md` — Project documentation.
- `docs/api/specialists-api.md` — Project documentation.
- `docs/architecture/aggregate-production-readiness.md` — Project documentation.
- `docs/architecture/c14-10-observability.md` — Project documentation.
- `docs/architecture/c14-11-real-runtime-tests.md` — Project documentation.
- `docs/architecture/c14-11a3-legacy-runtime-removal.md` — Project documentation.
- `docs/architecture/c14-11a4-1-composition-boundary.md` — Project documentation.
- `docs/architecture/c14-11a4-2a-repository-composition.md` — Project documentation.
- `docs/architecture/c14-11a4-2b-container-services-composition.md` — Project documentation.
- `docs/architecture/c14-11a4-2c-analysis-investigation-composition.md` — Project documentation.
- `docs/architecture/c14-11a4-2d-runtime-composition.md` — Project documentation.
- `docs/architecture/c14-11a4-3a-ollama-infrastructure-boundary.md` — Project documentation.
- `docs/architecture/c14-11a4-3b-investigation-ollama-infrastructure.md` — Project documentation.
- `docs/architecture/c14-11a4-3c-database-infrastructure-boundary.md` — Project documentation.
- `docs/architecture/c14-11a4-3d-database-models-migrations-boundary.md` — Project documentation.
- `docs/architecture/c14-12-runtime-readiness-gate.md` — Project documentation.
- `docs/architecture/c14-9-claude-native-orchestration.md` — Project documentation.
- `docs/architecture/cross-specialist-correlation.md` — Project documentation.
- `docs/architecture/database.md` — Project documentation.
- `docs/architecture/diagnostic-policy.md` — Project documentation.
- `docs/architecture/diagnostic-tool-registry.md` — Project documentation.
- `docs/architecture/dynamic-secondary-specialist-routing.md` — Project documentation.
- `docs/architecture/evaluation-dataset-runner.md` — Project documentation.
- `docs/architecture/evidence-collection.md` — Project documentation.
- `docs/architecture/investigation-contracts.md` — Project documentation.
- `docs/architecture/investigation-persistence.md` — Project documentation.
- `docs/architecture/investigation-read-models.md` — Project documentation.
- `docs/architecture/investigation-router.md` — Project documentation.
- `docs/architecture/investigation-runtime-snapshot.md` — Project documentation.
- `docs/architecture/knowledge-chunking.md` — Project documentation.
- `docs/architecture/knowledge-indexing.md` — Project documentation.
- `docs/architecture/knowledge-ingestion.md` — Project documentation.
- `docs/architecture/knowledge-rag-schema.md` — Project documentation.
- `docs/architecture/knowledge-retrieval.md` — Project documentation.
- `docs/architecture/knowledge-sources-seed.md` — Project documentation.
- `docs/architecture/knowledge-sources.md` — Project documentation.
- `docs/architecture/overview.md` — Project documentation.
- `docs/architecture/persisted-runtime-evaluation.md` — Project documentation.
- `docs/architecture/phase-5-supervised-remediation.md` — Project documentation.
- `docs/architecture/production-readiness-gate.md` — Project documentation.
- `docs/architecture/runtime-sample-expansion.md` — Project documentation.
- `docs/architecture/safety-failure-injection.md` — Project documentation.
- `docs/architecture/server-coordinator.md` — Project documentation.
- `docs/architecture/specialist-context-builder.md` — Project documentation.
- `docs/architecture/specialist-definitions.md` — Project documentation.
- `docs/architecture/specialist-investigation-loop.md` — Project documentation.
- `docs/architecture/specialist-reasoning-agent.md` — Project documentation.
- `docs/architecture/specialist-registry.md` — Project documentation.
- `docs/architecture/target-project-structure.md` — Current architecture map for Claude runtime, capabilities, infrastructure, MCP, and admin UI.
- `docs/c14-7-runtime-requirements.md` — Project documentation.
- `docs/decisions/ADR-008-dynamic-specialists.md` — Project documentation.
- `docs/decisions/ADR-009-hierarchical-investigation.md` — Project documentation.
- `docs/decisions/ADR-011-dual-rag-and-knowledge-retrieval.md` — Project documentation.
- `docs/decisions/ADR-012-specialist-reasoning-and-provenance-boundary.md` — Project documentation.
- `docs/decisions/ADR-013-registered-read-only-diagnostic-tools.md` — Project documentation.
- `docs/decisions/ADR-015-dynamic-secondary-specialist-routing.md` — Project documentation.
- `docs/decisions/ADR-016-production-readiness-and-remediation-boundary.md` — Project documentation.
- `docs/decisions/ADR-017-claude-code-supervisory-agent-runtime.md` — Project documentation.
- `docs/decisions/ADR-018-claude-native-operational-contracts.md` — Project documentation.
- `docs/decisions/README.md` — Project documentation.
- `docs/deployment/production-checklist.md` — Project documentation.
- `docs/deployment/production-deployment.md` — Project documentation.
- `docs/deployment/systemd-example.md` — Project documentation.
- `docs/operations/claude-runtime.md` — Operational guide for running the API, Ollama, and Claude Code runtime.
- `docs/operations/configuration.md` — Project documentation.
- `docs/operations/database-bootstrap.md` — Project documentation.
- `docs/operations/migrations-and-troubleshooting.md` — Project documentation.
- `docs/operations/running-project.md` — Project documentation.
- `docs/rag_configuration.md` — Project documentation.
- `docs/roadmap/c14-claude-native-execution-plan.md` — Project documentation.
- `docs/roadmap/claude-runtime-implementation-plan.md` — Implementation plan for Claude runtime, tool boundaries, package layout, documentation, and tests.
- `docs/roadmap/next-phase-multi-agent.md` — Project documentation.
- `docs/roadmap/phase-4-17-closeout.md` — Project documentation.
- `docs/roadmap/phase-4-18-implementation.md` — Project documentation.
- `docs/roadmap/phase-4-19-implementation.md` — Project documentation.
- `docs/roadmap/phase-4-20-closeout.md` — Project documentation.
- `docs/roadmap/phase-4-20-implementation.md` — Project documentation.
- `docs/roadmap/phase-4-4-5-to-4-11-closeout.md` — Project documentation.
- `docs/roadmap/phase-4-foundation-closeout.md` — Project documentation.
- `docs/roadmap/phase-4-implementation-plan.md` — Project documentation.
- `docs/roadmap/phase-5-final-report.md` — Project documentation.
- `docs/roadmap/phase-c-closeout.md` — Project documentation.
- `docs/security/security-baseline.md` — Project documentation.
- `docs/testing/RUNTIME_SCENARIOS.md` — Project documentation.
- `docs/testing/TESTING_STRATEGY.md` — Project documentation.
- `docs/testing/TEST_CATALOG.md` — Project documentation.
- `docs/testing/multi-agent-test-methodology.md` — Project documentation.
- `docs/testing/performance.md` — Project documentation.
- `docs/testing/testing-and-evaluation.md` — Project documentation.
- `docs/ui/investigations.md` — Project documentation.
- `docs/workflows/current-workflows.md` — Project documentation.

## Maintenance rule

Regenerate this document whenever files are added, removed, or substantially repurposed. Descriptions are derived from path conventions, module docstrings, and public classes/functions; core files have explicit descriptions in the generator.

<!-- PROJECT-DOC-METADATA:BEGIN -->
Document classification: **CURRENT_CANONICAL**

Documentation synchronized: **2026-08-13**

Canonical project state:

```text
Phase 4.20: complete
readiness: blocked_by_safe_test_environment
automatic_remediation_allowed: false
```

For current system state, see [`docs/PROJECT_STATUS.md`](/docs/PROJECT_STATUS.md).
<!-- PROJECT-DOC-METADATA:END -->
