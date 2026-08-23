import time
import threading
from dataclasses import dataclass, field
from typing import Optional
from collections import defaultdict


@dataclass
class RequestMetric:
    path: str
    method: str
    status_code: int
    latency_ms: float
    timestamp: float = field(default_factory=time.time)


@dataclass
class TokenMetric:
    provider: str
    tokens: int
    modo_degradado: bool
    timestamp: float = field(default_factory=time.time)


class MetricsStore:
    # Almacén thread-safe de métricas.

    def __init__(self):
        self._lock = threading.Lock()
        self.requests: list[RequestMetric] = []
        self.tokens: list[TokenMetric] = []

    def record_request(self, path: str, method: str, status_code: int, latency_ms: float):
        with self._lock:
            self.requests.append(
                RequestMetric(path=path, method=method, status_code=status_code, latency_ms=latency_ms)
            )

    def record_tokens(self, provider: str, tokens: int, modo_degradado: bool = False):
        with self._lock:
            self.tokens.append(
                TokenMetric(provider=provider, tokens=tokens, modo_degradado=modo_degradado)
            )

    def resumen(self) -> dict:
        with self._lock:
            if not self.requests and not self.tokens:
                return {
                    "total_requests": 0,
                    "latencia_promedio_ms": 0,
                    "latencia_p95_ms": 0,
                    "total_tokens": 0,
                    "requests_por_path": {},
                    "tokens_por_proveedor": {},
                }

            latencias = sorted([r.latency_ms for r in self.requests])
            p95_index = int(len(latencias) * 0.95) - 1 if latencias else 0
            p95 = latencias[max(0, p95_index)] if latencias else 0

            requests_por_path = defaultdict(int)
            for r in self.requests:
                requests_por_path[f"{r.method} {r.path}"] += 1

            tokens_por_proveedor = defaultdict(int)
            total_tokens = 0
            for t in self.tokens:
                tokens_por_proveedor[t.provider] += t.tokens
                total_tokens += t.tokens

            return {
                "total_requests": len(self.requests),
                "latencia_promedio_ms": round(sum(latencias) / len(latencias), 2) if latencias else 0,
                "latencia_p95_ms": round(p95, 2),
                "total_tokens": total_tokens,
                "requests_por_path": dict(requests_por_path),
                "tokens_por_proveedor": dict(tokens_por_proveedor),
            }


# Instancia global
metrics = MetricsStore()