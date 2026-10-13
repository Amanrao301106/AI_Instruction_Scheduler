"""
Streamlit frontend for the AI-Accelerated Instruction Scheduler.

Run:
    streamlit run app.py
"""

from __future__ import annotations

import pandas as pd
import streamlit as st

from dependency_analyzer import build_dependency_graph, format_hazard_table
from examples import DEFAULT_EXAMPLE, example_text, list_examples
from main import build_instructions, run_simulation
from performance import chart_dataframe, comparison_rows, summary_message


st.set_page_config(
    page_title="AI-Accelerated Instruction Scheduling",
    page_icon="⚙️",
    layout="wide",
)

STAGE_COLORS = {
    "IF": "#4C78A8",
    "ID": "#72B7B2",
    "EX": "#54A24B",
    "MEM": "#EECA3B",
    "WB": "#F58518",
    "ST": "#E45756",
}

st.markdown(
    """
    <style>
    .block-container {
        padding-top: 1.6rem;
        padding-bottom: 3rem;
    }
    .hero {
        padding: 1.35rem 1.55rem;
        border-radius: 18px;
        border: 1px solid rgba(120,120,120,.22);
        background: linear-gradient(
            135deg,
            rgba(76,120,168,.10),
            rgba(84,162,75,.08)
        );
        margin-bottom: 1.1rem;
    }
    .hero h1 { margin-bottom: .25rem; }
    .subtitle { opacity: .78; font-size: 1.02rem; }
    .order-ai {
        padding: .65rem .85rem;
        border-radius: 10px;
        border: 1px solid rgba(84,162,75,.45);
        background: rgba(84,162,75,.08);
        font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
    }
    .order-trad {
        padding: .65rem .85rem;
        border-radius: 10px;
        border: 1px solid rgba(120,120,120,.28);
        font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def pipeline_dataframe(simulator):
    simulator.simulate()

    if not simulator.order:
        return pd.DataFrame()

    max_cycle = simulator.total_cycles
    columns = ["Instruction"] + [
        f"C{cycle}" for cycle in range(1, max_cycle + 1)
    ]
    rows = []

    for instruction in simulator.order:
        cycle_map = simulator.timeline[instruction.number]
        id_cycle = next(
            cycle for cycle, stage in cycle_map.items() if stage == "ID"
        )
        if_cycle = next(
            cycle for cycle, stage in cycle_map.items() if stage == "IF"
        )

        row = [f"I{instruction.number} {instruction.operation}"]
        for cycle in range(1, max_cycle + 1):
            stage = cycle_map.get(cycle, "")
            if not stage and if_cycle < cycle < id_cycle:
                stage = "ST"
            row.append(stage)
        rows.append(row)

    return pd.DataFrame(rows, columns=columns)


def style_pipeline(df):
    def color_cell(value):
        if value in STAGE_COLORS:
            color = STAGE_COLORS[value]
            return (
                f"background-color: {color}; color: white; "
                f"font-weight: 600; text-align: center;"
            )
        return "text-align: center;"

    if df.empty:
        return df
    return df.style.map(
        color_cell,
        subset=[c for c in df.columns if c != "Instruction"],
    )


def instruction_table(instructions):
    return pd.DataFrame(
        [
            {
                "Instruction": f"I{i.number}",
                "Operation": i.operation,
                "Destination": i.destination or "-",
                "Sources": ", ".join(i.sources) or "-",
                "Immediate / Addr": i.immediate or i.memory_address or "-",
            }
            for i in instructions
        ]
    )


def order_text(order):
    return " → ".join(f"I{i.number}" for i in order)


def draw_dependency_graph(instructions, dependencies):
    _parents, children = build_dependency_graph(instructions, dependencies)

    st.markdown("#### Dependency Graph (RAW)")

    if not dependencies:
        st.info("No RAW dependencies. All instructions are independent.")
        return

    lines = []
    for instruction in instructions:
        dependent_nodes = children.get(instruction.number, [])
        if dependent_nodes:
            targets = "  ".join(f"→ I{target}" for target in dependent_nodes)
            lines.append(
                f"I{instruction.number} {instruction.operation:<6} {targets}"
            )
        else:
            lines.append(f"I{instruction.number} {instruction.operation}")

    # ASCII fan-in style for a quick viva-friendly view
    ascii_edges = []
    for producer, consumer, register in dependencies:
        ascii_edges.append(
            f"I{producer} ──({register})──> I{consumer}"
        )

    left, right = st.columns(2)
    with left:
        st.code("\n".join(lines), language="text")
    with right:
        st.code("\n".join(ascii_edges), language="text")


def draw_pipeline_legend():
    cols = st.columns(6)
    labels = [
        ("IF", "Instruction Fetch"),
        ("ID", "Instruction Decode"),
        ("EX", "Execute"),
        ("MEM", "Memory Access"),
        ("WB", "Write Back"),
        ("ST", "Stall"),
    ]
    for col, (short, long) in zip(cols, labels):
        with col:
            color = STAGE_COLORS[short]
            st.markdown(
                f"<div style='background:{color};color:white;padding:.45rem;"
                f"border-radius:8px;text-align:center;font-weight:600;'>"
                f"{short}</div><div style='text-align:center;opacity:.75;"
                f"font-size:.85rem;margin-top:.25rem;'>{long}</div>",
                unsafe_allow_html=True,
            )


# -----------------------------
# Header
# -----------------------------
st.markdown(
    """
    <div class="hero">
        <h1>AI-Accelerated Instruction Scheduling</h1>
        <div class="subtitle">
            Dependency-aware CPU instruction scheduling and pipeline optimization
        </div>
        <div class="subtitle" style="margin-top:.35rem;">
            5-stage pipeline simulation · AI optimization · performance comparison
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)


# -----------------------------
# Sidebar
# -----------------------------
with st.sidebar:
    st.header("Project Controls")

    example_name = st.selectbox(
        "Instruction workload",
        ["Custom"] + list_examples(),
    )

    if example_name == "Custom":
        default_text = example_text(DEFAULT_EXAMPLE)
    else:
        default_text = example_text(example_name)

    load_clicked = st.button("Load Example", use_container_width=True)
    clear_clicked = st.button("Clear", use_container_width=True)
    reset_clicked = st.button("Reset", use_container_width=True)

    if load_clicked:
        st.session_state["instruction_text"] = default_text
        st.session_state.pop("simulation", None)

    if clear_clicked:
        st.session_state["instruction_text"] = ""
        st.session_state.pop("simulation", None)

    if reset_clicked:
        st.session_state["instruction_text"] = example_text(DEFAULT_EXAMPLE)
        st.session_state.pop("simulation", None)

    st.divider()
    st.markdown("### CPU model")
    st.write("5-stage pipeline")
    st.code("IF → ID → EX → MEM → WB", language="text")

    st.markdown("### AI features")
    st.write(
        "• dependency criticality\n"
        "• unlock potential\n"
        "• independent-instruction priority\n"
        "• operation cost\n"
        "• transparent decision reasons"
    )

    st.markdown("### Viva demo tip")
    st.caption(
        "Load Mixed Workload → Run → compare orders, "
        "pipelines, stalls, and speedup."
    )


if "instruction_text" not in st.session_state:
    st.session_state["instruction_text"] = default_text


# -----------------------------
# Input
# -----------------------------
st.subheader("1. Instruction Input")

st.session_state["instruction_text"] = st.text_area(
    "Enter one instruction per line",
    value=st.session_state["instruction_text"],
    height=220,
    help=(
        "Do not type I1:, I2:, etc. "
        "Supported: LOAD, STORE, ADD, SUB, MUL, DIV"
    ),
)

run_button = st.button(
    "▶ Run AI Scheduling Simulation",
    type="primary",
    use_container_width=True,
)

if run_button:
    st.session_state.pop("simulation", None)

    instructions, errors = build_instructions(
        st.session_state["instruction_text"]
    )

    if errors:
        st.error("Please fix the following instruction errors.")
        for error in errors:
            st.write(error)
    elif not instructions:
        st.warning("Please enter at least one instruction.")
    else:
        try:
            st.session_state["simulation"] = run_simulation(instructions)
        except RuntimeError as error:
            st.error(str(error))


if "simulation" not in st.session_state:
    st.info(
        "Enter instructions and click **Run AI Scheduling Simulation**."
    )
else:
    data = st.session_state["simulation"]
    metrics = data["metrics"]
    analysis = data["analysis"]
    dependencies = data["dependencies"]
    traditional_result = data["traditional_result"]
    ai_result = data["ai_result"]

    # -------------------------
    # Performance cards
    # -------------------------
    st.divider()
    st.subheader("2. Performance Comparison")

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Traditional Cycles", traditional_result["cycles"])
    c2.metric(
        "AI Cycles",
        ai_result["cycles"],
        delta=f"{metrics['cycle_improvement']:.2f}%",
    )
    c3.metric(
        "Cycle Improvement",
        f"{metrics['cycle_improvement']:.2f}%",
    )
    c4.metric(
        "Stall Reduction",
        f"{metrics['stall_reduction']:.2f}%",
    )
    c5.metric("Speedup", f"{metrics['speedup']:.2f}x")

    message = summary_message(metrics)
    if metrics["cycle_improvement"] > 0:
        st.success(message)
    elif metrics["cycle_improvement"] == 0:
        st.info(message)
    else:
        st.warning(message)

    left, right = st.columns(2)
    with left:
        st.markdown("#### Traditional Order")
        st.markdown(
            f"<div class='order-trad'>{order_text(data['traditional_order'])}</div>",
            unsafe_allow_html=True,
        )
    with right:
        st.markdown("#### AI-Optimized Order")
        st.markdown(
            f"<div class='order-ai'>{order_text(data['ai_order'])}</div>",
            unsafe_allow_html=True,
        )

    # -------------------------
    # Tabs
    # -------------------------
    st.divider()
    tabs = st.tabs(
        [
            "Instructions",
            "Dependencies",
            "Hazards (WAR/WAW)",
            "AI Decisions",
            "Performance Chart",
        ]
    )

    with tabs[0]:
        st.dataframe(
            instruction_table(data["traditional_order"]),
            use_container_width=True,
            hide_index=True,
        )

    with tabs[1]:
        draw_dependency_graph(data["traditional_order"], dependencies)
        raw_rows = format_hazard_table(analysis["raw"], "RAW")
        if raw_rows:
            st.dataframe(
                pd.DataFrame(raw_rows)[
                    ["Type", "Producer", "Consumer", "Register"]
                ],
                use_container_width=True,
                hide_index=True,
            )
        else:
            st.caption("No RAW hazards.")
        st.caption(
            "RAW dependencies are the ordering constraints used by "
            "the AI scheduler."
        )

    with tabs[2]:
        war_rows = format_hazard_table(analysis["war"], "WAR")
        waw_rows = format_hazard_table(analysis["waw"], "WAW")

        st.markdown("#### WAR (Write After Read)")
        if war_rows:
            st.dataframe(
                pd.DataFrame(war_rows)[
                    ["Type", "Reader", "Writer", "Register"]
                ],
                use_container_width=True,
                hide_index=True,
            )
        else:
            st.info("No WAR hazards detected.")

        st.markdown("#### WAW (Write After Write)")
        if waw_rows:
            st.dataframe(
                pd.DataFrame(waw_rows)[
                    ["Type", "First Writer", "Second Writer", "Register"]
                ],
                use_container_width=True,
                hide_index=True,
            )
        else:
            st.info("No WAW hazards detected.")

    with tabs[3]:
        decision_rows = []
        for step, decision in enumerate(data["decisions"], start=1):
            decision_rows.append(
                {
                    "Step": step,
                    "Ready": ", ".join(
                        f"I{i}" for i in decision["ready_options"]
                    ),
                    "Selected": f"I{decision['instruction']}",
                    "Score": round(decision["score"], 2),
                    "Reason": decision["reason"],
                }
            )

        st.dataframe(
            pd.DataFrame(decision_rows),
            use_container_width=True,
            hide_index=True,
        )

        with st.expander("Per-step candidate scores"):
            for step, decision in enumerate(data["decisions"], start=1):
                st.markdown(
                    f"**Step {step} — selected I{decision['instruction']}**"
                )
                cand = pd.DataFrame(
                    [
                        {
                            "Instruction": f"I{c['instruction']}",
                            "Score": round(c["score"], 2),
                            "Criticality": c["features"]["criticality"],
                            "Unlocks": c["features"]["unlocks"],
                            "Dependents": c["features"]["dependents"],
                            "Independent": c["features"]["independent"],
                            "Op Cost": c["features"]["operation_cost"],
                            "Reason": c["reason"],
                        }
                        for c in decision["candidates"]
                    ]
                )
                st.dataframe(
                    cand,
                    use_container_width=True,
                    hide_index=True,
                )

    with tabs[4]:
        chart_df = pd.DataFrame(chart_dataframe(metrics))
        st.markdown("#### Cycles & Stalls")
        st.bar_chart(
            chart_df.set_index("Schedule")[["Cycles", "Stalls"]]
        )
        st.markdown("#### Pipeline Utilization (%)")
        st.bar_chart(
            chart_df.set_index("Schedule")[["Utilization"]]
        )
        st.metric("Speedup", f"{metrics['speedup']:.2f}x")

    # -------------------------
    # Pipeline visualization
    # -------------------------
    st.divider()
    st.subheader("3. CPU Pipeline Visualization")
    draw_pipeline_legend()

    st.markdown("#### Traditional Pipeline")
    trad_df = pipeline_dataframe(data["traditional_sim"])
    st.dataframe(
        style_pipeline(trad_df),
        use_container_width=True,
        hide_index=True,
    )

    st.markdown("#### AI-Optimized Pipeline")
    ai_df = pipeline_dataframe(data["ai_sim"])
    st.dataframe(
        style_pipeline(ai_df),
        use_container_width=True,
        hide_index=True,
    )

    # -------------------------
    # Detailed results
    # -------------------------
    st.divider()
    st.subheader("4. Detailed Results")
    st.dataframe(
        pd.DataFrame(comparison_rows(metrics)),
        use_container_width=True,
        hide_index=True,
    )
    st.caption(
        "All results are calculated dynamically from the entered "
        "instruction workload; no performance values are hard-coded."
    )
