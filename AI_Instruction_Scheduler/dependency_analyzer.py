"""
Dependency analysis for instruction-level scheduling.

Detects classic data hazards:
  RAW  – Read After Write  (true dependence)
  WAR  – Write After Read  (anti-dependence)
  WAW  – Write After Write (output dependence)

RAW hazards constrain the AI scheduler. WAR/WAW are reported for
analysis and viva explanation.
"""


def detect_raw(instructions):
    """Return list of (producer, consumer, register) RAW hazards."""
    hazards = []

    for i, producer in enumerate(instructions):
        if producer.destination is None:
            continue

        for consumer in instructions[i + 1:]:
            for source in consumer.sources:
                if source == producer.destination:
                    hazards.append(
                        (producer.number, consumer.number, source)
                    )
                    break

    return hazards


def detect_war(instructions):
    """Return list of (reader, writer, register) WAR hazards."""
    hazards = []

    for i, reader in enumerate(instructions):
        for source in reader.sources:
            for writer in instructions[i + 1:]:
                if writer.destination == source:
                    hazards.append(
                        (reader.number, writer.number, source)
                    )
                    break

    return hazards


def detect_waw(instructions):
    """Return list of (first_writer, second_writer, register) WAW hazards."""
    hazards = []

    for i, first in enumerate(instructions):
        if first.destination is None:
            continue

        for second in instructions[i + 1:]:
            if second.destination == first.destination:
                hazards.append(
                    (first.number, second.number, first.destination)
                )
                break

    return hazards


def analyze_all(instructions):
    """Run full hazard analysis and return a structured report."""
    return {
        "raw": detect_raw(instructions),
        "war": detect_war(instructions),
        "waw": detect_waw(instructions),
    }


def build_dependency_graph(instructions, raw_dependencies=None):
    """
    Build adjacency lists from RAW dependencies.

    Returns:
        parents  – consumer -> [producers]
        children – producer -> [consumers]
    """
    if raw_dependencies is None:
        raw_dependencies = detect_raw(instructions)

    parents = {i.number: [] for i in instructions}
    children = {i.number: [] for i in instructions}

    for producer, consumer, _register in raw_dependencies:
        parents.setdefault(consumer, []).append(producer)
        children.setdefault(producer, []).append(consumer)

    return parents, children


def validate_dependencies(instructions, raw_dependencies=None):
    """
    Validate that the RAW dependency graph is acyclic and
    every referenced instruction number exists.
    """
    if raw_dependencies is None:
        raw_dependencies = detect_raw(instructions)

    known = {i.number for i in instructions}
    parents, _children = build_dependency_graph(
        instructions,
        raw_dependencies,
    )

    for producer, consumer, register in raw_dependencies:
        if producer not in known or consumer not in known:
            return False, (
                f"Dependency I{producer} -> I{consumer} "
                f"({register}) references an unknown instruction."
            )

    # Cycle detection via DFS coloring: 0=white, 1=gray, 2=black
    color = {number: 0 for number in known}

    def visit(node):
        color[node] = 1

        for parent in parents.get(node, []):
            if color[parent] == 1:
                return True
            if color[parent] == 0 and visit(parent):
                return True

        color[node] = 2
        return False

    for number in known:
        if color[number] == 0 and visit(number):
            return False, "The RAW dependency graph contains a cycle."

    return True, "Dependency graph is valid."


def find_dependencies(instructions):
    """
    Primary dependency API used by the scheduler and simulator.

    Returns RAW hazards only, because those are true ordering
    constraints for correctness-preserving reordering.
    """
    return detect_raw(instructions)


def format_hazard_table(hazards, kind="RAW"):
    """Return a list of dict rows suitable for display/DataFrames."""
    rows = []

    for first, second, register in hazards:
        if kind == "RAW":
            label = "Producer → Consumer"
            left, right = "Producer", "Consumer"
        elif kind == "WAR":
            label = "Reader → Writer"
            left, right = "Reader", "Writer"
        else:
            label = "First → Second"
            left, right = "First Writer", "Second Writer"

        rows.append({
            "Type": kind,
            left: f"I{first}",
            right: f"I{second}",
            "Register": register,
            "Edge": f"I{first} → I{second}",
            "Relation": label,
        })

    return rows


if __name__ == "__main__":
    print("Dependency analyzer loaded successfully.")
