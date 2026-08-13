# C.14.11A.4.3b — Investigation Ollama Infrastructure

Moved Ollama-specific investigation adapters into
`app/infrastructure/llm/ollama/`:

- `OllamaSpecialistReasoningClient`
- `OllamaFinalDiagnosisNarrativeClient`

Provider-neutral contracts and factories remain in their historical
investigation modules for now.

Factories import the Infrastructure adapters lazily when called, avoiding an
import-time circular dependency. Historical class names remain available via
module-level `__getattr__` compatibility shims until A.4.6.
