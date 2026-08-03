"""Deterministic token and endpoint cost guards for evaluation runs."""

from __future__ import annotations

from dataclasses import dataclass


class BudgetExceededError(RuntimeError):
    """Raised before starting a batch that could exceed the hard budget."""


@dataclass(frozen=True)
class TokenPricing:
    input_usd_per_million: float
    output_usd_per_million: float

    def estimate(self, input_tokens: int, output_tokens: int) -> float:
        if input_tokens < 0 or output_tokens < 0:
            raise ValueError("token counts must be non-negative")
        return (
            input_tokens / 1_000_000 * self.input_usd_per_million
            + output_tokens / 1_000_000 * self.output_usd_per_million
        )


@dataclass(frozen=True)
class BudgetPolicy:
    hard_budget_usd: float = 250.0
    reserve_usd: float = 25.0

    def assert_next_batch_allowed(
        self, *, actual_spend_usd: float, next_batch_upper_bound_usd: float
    ) -> None:
        projected = actual_spend_usd + next_batch_upper_bound_usd + self.reserve_usd
        if projected > self.hard_budget_usd + 1e-9:
            raise BudgetExceededError(
                f"projected spend ${projected:.2f} exceeds hard budget "
                f"${self.hard_budget_usd:.2f} including reserve"
            )


def estimate_self_deployed_cost(
    *, endpoint_hours: float, hourly_price_usd: float,
    storage_network_usd: float = 0.0,
) -> float:
    if min(endpoint_hours, hourly_price_usd, storage_network_usd) < 0:
        raise ValueError("self-deployed cost inputs must be non-negative")
    return endpoint_hours * hourly_price_usd + storage_network_usd
