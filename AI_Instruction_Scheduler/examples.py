"""
Predefined instruction workloads for demos, CLI, and the Streamlit UI.
"""

EXAMPLES = {
    "Basic Dependency": [
        "LOAD R1, 10",
        "LOAD R2, 20",
        "ADD R3, R1, R2",
        "LOAD R4, 5",
        "MUL R5, R3, R4",
        "STORE R5, 100",
    ],
    "Mixed Workload": [
        "LOAD R1, 10",
        "LOAD R2, 20",
        "ADD R3, R1, R2",
        "LOAD R6, 50",
        "LOAD R7, 60",
        "SUB R8, R6, R7",
        "MUL R9, R3, R8",
        "STORE R9, 200",
    ],
    "Independent Instructions": [
        "LOAD R1, 10",
        "LOAD R2, 20",
        "ADD R3, R1, R2",
        "LOAD R6, 50",
        "LOAD R7, 60",
        "SUB R8, R6, R7",
        "LOAD R10, 100",
        "ADD R11, R10, R1",
        "MUL R12, R3, R8",
        "STORE R12, 200",
    ],
    "Long Dependency Chain": [
        "LOAD R1, 10",
        "LOAD R2, 20",
        "ADD R3, R1, R2",
        "SUB R4, R3, R1",
        "MUL R5, R4, R2",
        "ADD R6, R5, R3",
        "STORE R6, 100",
    ],
    "WAR / WAW Hazards": [
        "LOAD R1, 10",
        "ADD R2, R1, R1",
        "LOAD R1, 30",
        "SUB R3, R2, R1",
        "ADD R2, R3, R1",
        "STORE R2, 50",
    ],
}


DEFAULT_EXAMPLE = "Basic Dependency"


def list_examples():
    return list(EXAMPLES.keys())


def get_example(name):
    if name not in EXAMPLES:
        raise KeyError(f"Unknown example workload: {name}")
    return EXAMPLES[name][:]


def example_text(name):
    return "\n".join(get_example(name))


if __name__ == "__main__":
    for title, lines in EXAMPLES.items():
        print(f"\n{title}")
        print("-" * len(title))
        for line in lines:
            print(f"  {line}")
