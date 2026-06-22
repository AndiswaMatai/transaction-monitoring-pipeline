"""
Cost Optimization Calculator — Transaction Monitoring Pipeline

Models the savings from this pipeline's event-driven cost controls:

  1. Azure Functions Consumption plan (pay-per-execution) vs. an always-on
     Premium/Dedicated plan sized for peak throughput
  2. Cosmos DB autoscale RU/s vs. fixed provisioned throughput sized for peak
  3. Event Hubs auto-inflate vs. fixed throughput units sized for peak

The shared theme: every component here scales to zero (or near-zero) when
the transaction stream is quiet, which for most fraud platforms is most of
the day — provisioning for 3am peak-load 24/7 is the naive baseline this
avoids.

Run: python cost_optimization/cost_calculator.py
"""
from dataclasses import dataclass

# Approximate Azure South Africa North pricing (ZAR), illustrative.
FUNCTIONS_CONSUMPTION_PER_MILLION_EXEC = 33.0
FUNCTIONS_CONSUMPTION_GBSECOND = 0.0000349
FUNCTIONS_PREMIUM_EP1_MONTH = 3100  # smallest always-on Premium plan instance
COSMOS_RU_HOUR_PER_100_RU = 0.014
EVENTHUB_TU_HOUR = 4.40


@dataclass
class EventVolumeProfile:
    events_per_month: int
    avg_duration_ms: float
    memory_mb: int


def functions_cost_consumption(profile: EventVolumeProfile) -> float:
    million_execs = profile.events_per_month / 1_000_000
    gb_seconds = profile.events_per_month * (profile.avg_duration_ms / 1000) * (profile.memory_mb / 1024)
    return million_execs * FUNCTIONS_CONSUMPTION_PER_MILLION_EXEC + gb_seconds * FUNCTIONS_CONSUMPTION_GBSECOND


def functions_cost_premium_always_on() -> float:
    return FUNCTIONS_PREMIUM_EP1_MONTH


def cosmos_cost_autoscale(avg_ru_used: float, hours_per_month: int = 720) -> float:
    return (avg_ru_used / 100) * COSMOS_RU_HOUR_PER_100_RU * hours_per_month


def cosmos_cost_fixed_provisioned(peak_ru: float, hours_per_month: int = 720) -> float:
    """Fixed provisioning has to be sized for peak load, billed 24/7 regardless of actual usage."""
    return (peak_ru / 100) * COSMOS_RU_HOUR_PER_100_RU * hours_per_month


def eventhub_cost_auto_inflate(avg_tu_used: float, hours_per_month: int = 720) -> float:
    return avg_tu_used * EVENTHUB_TU_HOUR * hours_per_month


def eventhub_cost_fixed(peak_tu: float, hours_per_month: int = 720) -> float:
    return peak_tu * EVENTHUB_TU_HOUR * hours_per_month


def main():
    print("=" * 60)
    print("COST OPTIMIZATION IMPACT — TRANSACTION MONITORING PIPELINE")
    print("=" * 60)

    profile = EventVolumeProfile(events_per_month=15_000_000, avg_duration_ms=45, memory_mb=256)
    consumption_cost = functions_cost_consumption(profile)
    premium_cost = functions_cost_premium_always_on()
    print(f"\nAzure Functions (~{profile.events_per_month:,} events/month):")
    print(f"  Premium plan (always-on, sized for peak): R{premium_cost:,.2f}/month")
    print(f"  Consumption plan (pay-per-execution):      R{consumption_cost:,.2f}/month")
    print(f"  Monthly savings:                           R{premium_cost - consumption_cost:,.2f} "
          f"({(1 - consumption_cost/premium_cost):.1%})")

    cosmos_auto = cosmos_cost_autoscale(avg_ru_used=180)   # average usage well below peak
    cosmos_fixed = cosmos_cost_fixed_provisioned(peak_ru=1000)  # sized for the worst-case burst
    print(f"\nCosmos DB (autoscale ceiling 1000 RU/s, average usage ~180 RU/s):")
    print(f"  Fixed provisioning at peak (1000 RU/s):  R{cosmos_fixed:,.2f}/month")
    print(f"  Autoscale (10%-100% of ceiling):          R{cosmos_auto:,.2f}/month")
    print(f"  Monthly savings:                          R{cosmos_fixed - cosmos_auto:,.2f} "
          f"({(1 - cosmos_auto/cosmos_fixed):.1%})")

    eh_auto = eventhub_cost_auto_inflate(avg_tu_used=1.4)
    eh_fixed = eventhub_cost_fixed(peak_tu=8)
    print(f"\nEvent Hubs (auto-inflate ceiling 8 TU, average usage ~1.4 TU):")
    print(f"  Fixed at peak throughput (8 TU):  R{eh_fixed:,.2f}/month")
    print(f"  Auto-inflate (scales with load):  R{eh_auto:,.2f}/month")
    print(f"  Monthly savings:                  R{eh_fixed - eh_auto:,.2f} ({(1 - eh_auto/eh_fixed):.1%})")

    total_savings = (premium_cost - consumption_cost) + (cosmos_fixed - cosmos_auto) + (eh_fixed - eh_auto)
    print(f"\n{'TOTAL ESTIMATED MONTHLY SAVINGS:':<28} R{total_savings:,.2f}")
    print(f"{'TOTAL ESTIMATED ANNUAL SAVINGS:':<28} R{total_savings * 12:,.2f}")


if __name__ == "__main__":
    main()
