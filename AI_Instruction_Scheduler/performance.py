"""
Performance comparison helpers for traditional vs AI scheduling.

All metrics are derived from pipeline simulation results; nothing
is hard-coded.
"""

from __future__ import annotations


def calculate_speedup(traditional_cycles, ai_cycles):
    if not ai_cycles:
        return 1.0
    return traditional_cycles / ai_cycles


def calculate_cycle_improvement(traditional_cycles, ai_cycles):
    if not traditional_cycles:
        return 0.0
    return (
        (traditional_cycles - ai_cycles) / traditional_cycles
    ) * 100.0


def calculate_stall_reduction(traditional_stalls, ai_stalls):
    if not traditional_stalls:
        return 0.0
    return (
        (traditional_stalls - ai_stalls) / traditional_stalls
    ) * 100.0


def calculate_utilization(instruction_count, total_cycles, stages=5):
    if not total_cycles:
        return 0.0
    useful = instruction_count * stages
    available = total_cycles * stages
    return (useful / available) * 100.0


def compare_results(traditional_result, ai_result):
    """
    Compare two pipeline simulation result dictionaries.

    Expected keys in each result:
        cycles, stalls, utilization
    """
    old_cycles = traditional_result["cycles"]
    new_cycles = ai_result["cycles"]
    old_stalls = traditional_result["stalls"]
    new_stalls = ai_result["stalls"]

    return {
        "traditional_cycles": old_cycles,
        "ai_cycles": new_cycles,
        "traditional_stalls": old_stalls,
        "ai_stalls": new_stalls,
        "traditional_utilization": traditional_result.get(
            "utilization",
            0.0,
        ),
        "ai_utilization": ai_result.get("utilization", 0.0),
        "cycle_improvement": calculate_cycle_improvement(
            old_cycles,
            new_cycles,
        ),
        "stall_reduction": calculate_stall_reduction(
            old_stalls,
            new_stalls,
        ),
        "speedup": calculate_speedup(old_cycles, new_cycles),
        "cycles_saved": old_cycles - new_cycles,
        "stalls_saved": old_stalls - new_stalls,
    }


def comparison_rows(metrics):
    """Return table rows for UI / CLI display."""
    return [
        {
            "Metric": "Total Cycles",
            "Traditional": metrics["traditional_cycles"],
            "AI": metrics["ai_cycles"],
        },
        {
            "Metric": "Scheduling Stalls",
            "Traditional": metrics["traditional_stalls"],
            "AI": metrics["ai_stalls"],
        },
        {
            "Metric": "Pipeline Utilization",
            "Traditional": (
                f"{metrics['traditional_utilization']:.2f}%"
            ),
            "AI": f"{metrics['ai_utilization']:.2f}%",
        },
        {
            "Metric": "Cycle Improvement",
            "Traditional": "-",
            "AI": f"{metrics['cycle_improvement']:.2f}%",
        },
        {
            "Metric": "Stall Reduction",
            "Traditional": "-",
            "AI": f"{metrics['stall_reduction']:.2f}%",
        },
        {
            "Metric": "Speedup",
            "Traditional": "1.00x",
            "AI": f"{metrics['speedup']:.2f}x",
        },
    ]


def chart_dataframe(metrics):
    """Rows suitable for a Streamlit / Pandas comparison chart."""
    return [
        {
            "Schedule": "Traditional",
            "Cycles": metrics["traditional_cycles"],
            "Stalls": metrics["traditional_stalls"],
            "Utilization": metrics["traditional_utilization"],
        },
        {
            "Schedule": "AI",
            "Cycles": metrics["ai_cycles"],
            "Stalls": metrics["ai_stalls"],
            "Utilization": metrics["ai_utilization"],
        },
    ]


def summary_message(metrics):
    """Dynamic natural-language summary from actual metrics."""
    old_c = metrics["traditional_cycles"]
    new_c = metrics["ai_cycles"]
    improvement = metrics["cycle_improvement"]
    speedup = metrics["speedup"]

    if improvement > 0:
        return (
            f"AI scheduling reduced the execution time from {old_c} cycles "
            f"to {new_c} cycles, giving a {improvement:.2f}% improvement "
            f"and {speedup:.2f}x speedup."
        )

    if improvement == 0:
        return (
            f"No cycle improvement for this workload. "
            f"Both schedules finish in {old_c} cycles."
        )

    return (
        f"The AI heuristic used {new_c} cycles versus {old_c} traditional "
        f"cycles for this workload. Try Mixed Workload or Independent "
        f"Instructions to see a clearer scheduling opportunity."
    )


def print_comparison(metrics):
    print("\n" + "=" * 72)
    print("FINAL COMPARISON")
    print("=" * 72)
    print(f"{'Metric':<28}{'Traditional':>16}{'AI':>16}")
    print("-" * 60)

    for row in comparison_rows(metrics)[:3]:
        print(
            f"{row['Metric']:<28}"
            f"{str(row['Traditional']):>16}"
            f"{str(row['AI']):>16}"
        )

    print("-" * 60)
    print(f"Cycle Improvement : {metrics['cycle_improvement']:.2f}%")
    print(f"Stall Reduction   : {metrics['stall_reduction']:.2f}%")
    print(f"Speedup           : {metrics['speedup']:.2f}x")
    print("=" * 72)
    print(summary_message(metrics))


if __name__ == "__main__":
    print("Performance module loaded successfully.")
