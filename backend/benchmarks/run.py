"""Benchmarks de latencia de la API (mock por defecto, --live con Claude real)."""

from __future__ import annotations

import argparse
import asyncio
import logging
import os
import statistics
import sys
import time
from collections.abc import AsyncIterator, Awaitable, Callable
from dataclasses import dataclass
from typing import Any
from unittest.mock import patch

from httpx import ASGITransport, AsyncClient

from fastapi import HTTPException

os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///:memory:")
os.environ.setdefault("JWT_SECRET", "benchmark-secret-key-for-jwt-signing")
os.environ.setdefault("RATE_LIMIT", "100000/minute")
os.environ.setdefault("API_KEY", "")
os.environ.setdefault("DEBUG", "false")

from app.config import get_settings  # noqa: E402
from app.database import Base, engine  # noqa: E402
from app.main import create_app  # noqa: E402
from app.services.claude import ClaudeService  # noqa: E402


MOCK_LLM_MS = 50
MOCK_CHUNK_MS = 15
MOCK_CHUNKS = 8
LIVE_MAX_ITERATIONS = 10
LIVE_REFACTOR_PAYLOAD = {
    "module": "refactor",
    "files": [
        {
            "path": "bench.py",
            "content": "def add(a, b):\n    return a+b\n",
        }
    ],
    "context": {"language": "python", "project_root": "/bench"},
}
DIRECT_PROMPT = (
    "You are running a latency benchmark. Reply with exactly one word: BENCH_OK"
)


@dataclass
class BenchResult:
    name: str
    samples: int
    mean_ms: float
    p50_ms: float
    p95_ms: float
    min_ms: float
    max_ms: float
    extra: str = ""


def _percentile(values: list[float], pct: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    index = max(0, min(len(ordered) - 1, int(len(ordered) * pct) - 1))
    return ordered[index]


def _summarize(name: str, timings: list[float], extra: str = "") -> BenchResult:
    ms = [t * 1000 for t in timings]
    return BenchResult(
        name=name,
        samples=len(ms),
        mean_ms=statistics.mean(ms),
        p50_ms=statistics.median(ms),
        p95_ms=_percentile(ms, 0.95),
        min_ms=min(ms),
        max_ms=max(ms),
        extra=extra,
    )


def _quiet_logs() -> None:
    logging.getLogger().setLevel(logging.WARNING)
    for name in ("unicornio", "sqlalchemy.engine.Engine"):
        logging.getLogger(name).setLevel(logging.WARNING)


async def _reset_db() -> None:
    get_settings.cache_clear()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


async def _register_and_auth(client: AsyncClient) -> dict[str, str]:
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "bench@example.com",
            "name": "Bench User",
            "password": "benchpass123",
        },
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


async def _bench(
    name: str,
    iterations: int,
    fn: Callable[[], Awaitable[Any]],
    *,
    pause_s: float = 0.0,
) -> BenchResult:
    timings: list[float] = []
    for index in range(iterations):
        if index and pause_s:
            await asyncio.sleep(pause_s)
        start = time.perf_counter()
        await fn()
        timings.append(time.perf_counter() - start)
    return _summarize(name, timings)


async def _bench_stream(
    name: str,
    iterations: int,
    fn: Callable[[], Awaitable[tuple[float, float]]],
    *,
    pause_s: float = 0.0,
) -> BenchResult:
    ttfb_samples: list[float] = []
    total_samples: list[float] = []
    for index in range(iterations):
        if index and pause_s:
            await asyncio.sleep(pause_s)
        ttfb, total = await fn()
        ttfb_samples.append(ttfb)
        total_samples.append(total)
    total = _summarize(name, total_samples)
    ttfb = _summarize(f"{name} (TTFB)", ttfb_samples)
    total.extra = f"TTFB p50={ttfb.p50_ms:.1f}ms"
    return total


async def _mock_complete(_self: object, _prompt: str) -> str:
    await asyncio.sleep(MOCK_LLM_MS / 1000)
    return "benchmark result"


async def _mock_stream(_self: object, _prompt: str) -> AsyncIterator[str]:
    for _ in range(MOCK_CHUNKS):
        await asyncio.sleep(MOCK_CHUNK_MS / 1000)
        yield "chunk "


def _ensure_live_configured() -> None:
    settings = get_settings()
    key = settings.CLAUDE_API_KEY.strip()
    if not key or key in {"your-anthropic-key-here", "sk-ant-placeholder"}:
        print(
            "Error: CLAUDE_API_KEY no configurada o es un placeholder.\n"
            "Define una clave válida en backend/.env antes de usar --live.",
            file=sys.stderr,
        )
        raise SystemExit(1)


def _format_live_error(exc: BaseException) -> str:
    if isinstance(exc, HTTPException):
        return f"HTTP {exc.status_code}: {exc.detail}"
    return str(exc)


async def _bench_live(
    name: str,
    iterations: int,
    fn: Callable[[], Awaitable[Any]],
    *,
    pause_s: float = 0.0,
) -> BenchResult:
    timings: list[float] = []
    for index in range(iterations):
        if index and pause_s:
            await asyncio.sleep(pause_s)
        start = time.perf_counter()
        try:
            await fn()
        except (HTTPException, RuntimeError) as exc:
            print(
                f"\nError en {name}: {_format_live_error(exc)}",
                file=sys.stderr,
            )
            raise SystemExit(1) from exc
        timings.append(time.perf_counter() - start)
    return _summarize(name, timings)


async def _bench_stream_live(
    name: str,
    iterations: int,
    fn: Callable[[], Awaitable[tuple[float, float]]],
    *,
    pause_s: float = 0.0,
) -> BenchResult:
    ttfb_samples: list[float] = []
    total_samples: list[float] = []
    for index in range(iterations):
        if index and pause_s:
            await asyncio.sleep(pause_s)
        try:
            ttfb, total = await fn()
        except (HTTPException, RuntimeError) as exc:
            print(
                f"\nError en {name}: {_format_live_error(exc)}",
                file=sys.stderr,
            )
            raise SystemExit(1) from exc
        ttfb_samples.append(ttfb)
        total_samples.append(total)
    total = _summarize(name, total_samples)
    ttfb = _summarize(f"{name} (TTFB)", ttfb_samples)
    total.extra = f"TTFB p50={ttfb.p50_ms:.1f}ms"
    return total


async def _make_client() -> tuple[AsyncClient, dict[str, str]]:
    await _reset_db()
    app = create_app()
    transport = ASGITransport(app=app)
    client = AsyncClient(transport=transport, base_url="http://bench")
    headers = await _register_and_auth(client)
    return client, headers


async def run_mock_benchmarks(iterations: int) -> list[BenchResult]:
    _quiet_logs()
    results: list[BenchResult] = []

    async with AsyncClient(
        transport=ASGITransport(app=create_app()),
        base_url="http://bench",
    ) as client:
        await _reset_db()

        results.append(
            await _bench(
                "GET /api/v1/health",
                iterations,
                lambda: client.get("/api/v1/health"),
            )
        )

        register_timings: list[float] = []
        for index in range(iterations):
            await _reset_db()
            start = time.perf_counter()
            response = await client.post(
                "/api/v1/auth/register",
                json={
                    "email": f"user{index}@example.com",
                    "name": "Bench",
                    "password": "benchpass123",
                },
            )
            assert response.status_code == 201
            register_timings.append(time.perf_counter() - start)
        results.append(_summarize("POST /api/v1/auth/register", register_timings))

        await _reset_db()
        headers = await _register_and_auth(client)

        results.append(
            await _bench(
                "POST /api/v1/auth/login",
                iterations,
                lambda: client.post(
                    "/api/v1/auth/login",
                    json={"email": "bench@example.com", "password": "benchpass123"},
                ),
            )
        )

        with patch("app.services.claude.ClaudeService.complete", _mock_complete):
            results.append(
                await _bench(
                    "POST /api/v2/analyze (mock LLM)",
                    iterations,
                    lambda: client.post(
                        "/api/v2/analyze",
                        headers=headers,
                        json=LIVE_REFACTOR_PAYLOAD,
                    ),
                )
            )

            results.append(
                await _bench(
                    "POST /api/v1/refactor/code (mock LLM)",
                    iterations,
                    lambda: client.post(
                        "/api/v1/refactor/code",
                        headers=headers,
                        json={"code": "def foo():\n    return 1", "language": "python"},
                    ),
                )
            )

        with patch("app.services.claude.ClaudeService.stream_complete", _mock_stream):

            async def stream_once() -> tuple[float, float]:
                start = time.perf_counter()
                ttfb: float | None = None
                async with client.stream(
                    "POST",
                    "/api/v2/analyze/stream",
                    headers=headers,
                    json=LIVE_REFACTOR_PAYLOAD,
                ) as response:
                    async for line in response.aiter_lines():
                        if line.startswith("data:") and ttfb is None:
                            ttfb = time.perf_counter() - start
                total = time.perf_counter() - start
                return ttfb or total, total

            results.append(
                await _bench_stream(
                    "POST /api/v2/analyze/stream (mock LLM)",
                    iterations,
                    stream_once,
                )
            )

        results.append(
            await _bench(
                "GET /api/v1/queries/history",
                iterations,
                lambda: client.get("/api/v1/queries/history?limit=10", headers=headers),
            )
        )

    return results


async def run_live_benchmarks(iterations: int) -> list[BenchResult]:
    _quiet_logs()
    _ensure_live_configured()
    settings = get_settings()
    service = ClaudeService()
    results: list[BenchResult] = []
    pause_s = 0.75

    results.append(
        await _bench_live(
            "ClaudeService.complete (direct)",
            iterations,
            lambda: service.complete(DIRECT_PROMPT),
            pause_s=pause_s,
        )
    )

    async def direct_stream_once() -> tuple[float, float]:
        start = time.perf_counter()
        ttfb: float | None = None
        async for chunk in service.stream_complete(DIRECT_PROMPT):
            if chunk and ttfb is None:
                ttfb = time.perf_counter() - start
        total = time.perf_counter() - start
        return ttfb or total, total

    results.append(
        await _bench_stream_live(
            "ClaudeService.stream_complete (direct)",
            iterations,
            direct_stream_once,
            pause_s=pause_s,
        )
    )

    client, headers = await _make_client()
    try:
        results.append(
            await _bench_live(
                "POST /api/v2/analyze (live)",
                iterations,
                lambda: client.post(
                    "/api/v2/analyze",
                    headers=headers,
                    json=LIVE_REFACTOR_PAYLOAD,
                ),
                pause_s=pause_s,
            )
        )

        async def api_stream_once() -> tuple[float, float]:
            start = time.perf_counter()
            ttfb: float | None = None
            async with client.stream(
                "POST",
                "/api/v2/analyze/stream",
                headers=headers,
                json=LIVE_REFACTOR_PAYLOAD,
            ) as response:
                if response.status_code != 200:
                    body = await response.aread()
                    raise RuntimeError(
                        f"stream failed ({response.status_code}): "
                        f"{body.decode(errors='replace')[:200]}"
                    )
                async for line in response.aiter_lines():
                    if not line.startswith("data:"):
                        continue
                    if ttfb is None and '"text"' in line:
                        ttfb = time.perf_counter() - start
            total = time.perf_counter() - start
            return ttfb or total, total

        results.append(
            await _bench_stream_live(
                "POST /api/v2/analyze/stream (live)",
                iterations,
                api_stream_once,
                pause_s=pause_s,
            )
        )
    finally:
        await client.aclose()

    results.append(
        BenchResult(
            name="config",
            samples=1,
            mean_ms=0,
            p50_ms=0,
            p95_ms=0,
            min_ms=0,
            max_ms=0,
            extra=f"model={settings.CLAUDE_MODEL}",
        )
    )

    return results


def _print_results(
    results: list[BenchResult],
    *,
    iterations: int,
    mode: str,
) -> None:
    print()
    print(f"Unicornio Dev — API Benchmarks ({mode})")
    print("=" * 72)
    if mode == "mock":
        print(
            f"Iteraciones: {iterations}  |  Mock LLM: {MOCK_LLM_MS}ms  |  "
            f"Mock stream: {MOCK_CHUNKS}x{MOCK_CHUNK_MS}ms"
        )
    else:
        print(
            f"Iteraciones: {iterations}  |  Claude real  |  "
            f"Pausa entre muestras: 750ms"
        )
    print("-" * 72)
    print(f"{'Endpoint':<42} {'p50':>7} {'p95':>7} {'mean':>7} {'min':>7} {'max':>7}")
    print("-" * 72)
    for row in results:
        if row.name == "config":
            print(f"Modelo: {row.extra}")
            continue
        extra = f"  ({row.extra})" if row.extra else ""
        print(
            f"{row.name:<42} "
            f"{row.p50_ms:>6.1f}ms "
            f"{row.p95_ms:>6.1f}ms "
            f"{row.mean_ms:>6.1f}ms "
            f"{row.min_ms:>6.1f}ms "
            f"{row.max_ms:>6.1f}ms"
            f"{extra}"
        )
    print("-" * 72)
    if mode == "mock":
        print("Nota: Claude real suele dominar la latencia (~2-15s). Estos números miden overhead API.")
    else:
        print("Nota: --live consume tokens de Anthropic. Usa pocas iteraciones (p. ej. -n 3).")
    print()


def main() -> None:
    parser = argparse.ArgumentParser(description="Benchmark de latencia de Unicornio Dev API")
    parser.add_argument(
        "-n",
        "--iterations",
        type=int,
        default=None,
        help="Muestras por endpoint (default: 30 mock, 3 live)",
    )
    parser.add_argument(
        "--live",
        action="store_true",
        help="Benchmark con Claude real (requiere CLAUDE_API_KEY)",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Ejecuta mock y live en secuencia",
    )
    args = parser.parse_args()

    if args.all:
        mock_iterations = args.iterations or 30
        live_iterations = min(args.iterations or 3, LIVE_MAX_ITERATIONS)
        mock_results = asyncio.run(run_mock_benchmarks(mock_iterations))
        _print_results(mock_results, iterations=mock_iterations, mode="mock")

        if (args.iterations or 3) > LIVE_MAX_ITERATIONS:
            print(
                f"Aviso: live limitado a {LIVE_MAX_ITERATIONS} iteraciones "
                f"(pediste {args.iterations})."
            )
        live_results = asyncio.run(run_live_benchmarks(live_iterations))
        _print_results(live_results, iterations=live_iterations, mode="live")
        return

    if args.live:
        live_iterations = min(args.iterations or 3, LIVE_MAX_ITERATIONS)
        if (args.iterations or 3) > LIVE_MAX_ITERATIONS:
            print(
                f"Aviso: live limitado a {LIVE_MAX_ITERATIONS} iteraciones "
                f"(pediste {args.iterations})."
            )
        results = asyncio.run(run_live_benchmarks(live_iterations))
        _print_results(results, iterations=live_iterations, mode="live")
        return

    mock_iterations = args.iterations or 30
    results = asyncio.run(run_mock_benchmarks(mock_iterations))
    _print_results(results, iterations=mock_iterations, mode="mock")


if __name__ == "__main__":
    main()
