"""Repeatable in-process performance benchmark for the hot application paths.

The benchmark deliberately uses deterministic fakes instead of live Ollama,
PostgreSQL, or SSH services.  It measures application orchestration overhead,
event-loop behavior, and query-call counts without changing external state.
Use production-like load tests separately when those services are available.
"""
from __future__ import annotations

import argparse
import asyncio
import json
import math
import sys
import time
from pathlib import Path
from types import SimpleNamespace
from typing import Awaitable, Callable

import httpx

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.capabilities.analysis.retrieval.rag_retriever import RagRetriever
from app.capabilities.monitoring.scheduler.monitoring_scheduler import MonitoringScheduler
from app.infrastructure.llm.ollama.embedding_client import OllamaEmbeddingClient


def percentile(samples: list[float], percentile_value: float) -> float:
    """Return a nearest-rank percentile in milliseconds."""
    ordered = sorted(samples)
    if not ordered:
        return 0.0
    rank = max(
        0,
        min(
            len(ordered) - 1,
            math.ceil(percentile_value / 100 * len(ordered)) - 1,
        ),
    )
    return round(ordered[rank], 3)


def summarize(samples: list[float]) -> dict[str, float | int]:
    """Summarize a list of elapsed milliseconds."""
    return {
        "samples": len(samples),
        "p50_ms": percentile(samples, 50),
        "p95_ms": percentile(samples, 95),
        "p99_ms": percentile(samples, 99),
        "max_ms": round(max(samples), 3) if samples else 0.0,
    }


async def benchmark_embedding(iterations: int, warmup: int) -> dict:
    """Measure repeated embedding calls through one reusable HTTP client."""
    calls = 0

    async def handler(request: httpx.Request) -> httpx.Response:
        nonlocal calls
        calls += 1
        return httpx.Response(
            200,
            json={"embeddings": [[0.1, 0.2, 0.3]]},
            request=request,
        )

    client = OllamaEmbeddingClient(
        base_url="http://benchmark-ollama",
        model="benchmark-model",
        dimensions=3,
    )
    await client._client.aclose()
    client._client = httpx.AsyncClient(
        transport=httpx.MockTransport(handler),
        base_url="http://benchmark-ollama",
    )

    for index in range(warmup):
        await client.embed(f"warmup-{index}")

    samples: list[float] = []
    for index in range(iterations):
        started = time.perf_counter()
        await client.embed(f"benchmark-{index}")
        samples.append((time.perf_counter() - started) * 1000)

    await client.close()
    return {
        "summary": summarize(samples),
        "measured_http_calls": calls - warmup,
        "connection_strategy": "one shared AsyncClient",
    }


async def benchmark_rag(
    iterations: int,
    warmup: int,
    database_delay_ms: float,
) -> dict:
    """Measure RAG orchestration and confirm one bulk hydration call."""
    hydration_calls = 0
    vector_calls = 0

    async def embed(_text: str) -> list[float]:
        return [0.1, 0.2, 0.3]

    def find_similar(**_kwargs):
        nonlocal vector_calls
        vector_calls += 1
        if database_delay_ms:
            time.sleep(database_delay_ms / 1000)
        return [
            (SimpleNamespace(analysis_id=1, report_id=101), 0.91),
            (SimpleNamespace(analysis_id=2, report_id=102), 0.84),
            (SimpleNamespace(analysis_id=3, report_id=103), 0.77),
        ]

    def get_by_ids(analysis_ids: list[int]):
        nonlocal hydration_calls
        hydration_calls += 1
        if database_delay_ms:
            time.sleep(database_delay_ms / 1000)
        return {
            analysis_id: SimpleNamespace(
                status="completed",
                health_status="healthy",
                summary=f"analysis-{analysis_id}",
                issues=[],
                positive_findings=[],
                recommended_actions=[],
            )
            for analysis_id in analysis_ids
        }

    retriever = RagRetriever(
        embedding_client=SimpleNamespace(embed=embed),
        retrieval_repository=SimpleNamespace(find_similar=find_similar),
        analysis_repository=SimpleNamespace(get_by_ids=get_by_ids),
        top_k=3,
    )

    async def retrieve_once() -> None:
        await retriever.retrieve(
            normalized_report="benchmark report",
            server_id=1,
            monitoring_profile_id=None,
            command_set_hash=None,
            exclude_report_id=999,
        )

    for _ in range(warmup):
        await retrieve_once()

    samples: list[float] = []
    for _ in range(iterations):
        started = time.perf_counter()
        await retrieve_once()
        samples.append((time.perf_counter() - started) * 1000)

    return {
        "summary": summarize(samples),
        "measured_vector_queries": vector_calls - warmup,
        "measured_bulk_hydration_queries": hydration_calls - warmup,
        "candidates_per_query": 3,
        "database_delay_ms": database_delay_ms,
    }


async def benchmark_scheduler(
    iterations: int,
    warmup: int,
    server_count: int,
    monitoring_delay_ms: float,
) -> dict:
    """Measure bounded scheduler dispatch with deterministic monitoring fakes."""
    completed = 0
    servers = [
        SimpleNamespace(
            id=server_id,
            monitor_enabled=True,
            interval_seconds=0,
        )
        for server_id in range(1, server_count + 1)
    ]

    async def run(_server_id: int) -> None:
        nonlocal completed
        if monitoring_delay_ms:
            await asyncio.to_thread(
                time.sleep,
                monitoring_delay_ms / 1000,
            )
        completed += 1

    scheduler = MonitoringScheduler(
        server_repository=SimpleNamespace(
            list_enabled_servers=lambda: servers,
        ),
        monitoring_service=SimpleNamespace(run=run),
        polling_interval_seconds=5,
        max_concurrent_servers=max(1, min(server_count, 5)),
    )

    for _ in range(warmup):
        await scheduler.run_iteration()

    samples: list[float] = []
    for _ in range(iterations):
        started = time.perf_counter()
        await scheduler.run_iteration()
        samples.append((time.perf_counter() - started) * 1000)

    return {
        "summary": summarize(samples),
        "server_count": server_count,
        "monitoring_delay_ms": monitoring_delay_ms,
        "measured_completed_cycles": completed - (warmup * server_count),
        "max_concurrent_servers": min(server_count, 5),
    }


def run_async(operation: Callable[[], Awaitable[dict]]) -> dict:
    """Run one async benchmark from the command-line process."""
    return asyncio.run(operation())


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--iterations", type=int, default=30)
    parser.add_argument("--warmup", type=int, default=3)
    parser.add_argument("--servers", type=int, default=10)
    parser.add_argument("--database-delay-ms", type=float, default=0.5)
    parser.add_argument("--monitoring-delay-ms", type=float, default=0.5)
    args = parser.parse_args()

    if args.iterations < 1 or args.warmup < 0 or args.servers < 1:
        parser.error("iterations and servers must be positive; warmup cannot be negative")

    results = {
        "benchmark": "synthetic in-process hot-path benchmark",
        "embedding": run_async(
            lambda: benchmark_embedding(args.iterations, args.warmup)
        ),
        "rag": run_async(
            lambda: benchmark_rag(
                args.iterations,
                args.warmup,
                args.database_delay_ms,
            )
        ),
        "scheduler": run_async(
            lambda: benchmark_scheduler(
                args.iterations,
                args.warmup,
                args.servers,
                args.monitoring_delay_ms,
            )
        ),
    }

    print(json.dumps(results, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
