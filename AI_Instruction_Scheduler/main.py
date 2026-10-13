"""
AI-Accelerated Instruction Scheduler — core engine + CLI entry point.

Run:
    python main.py
"""

from ai_scheduler import AIScheduler
from dependency_analyzer import (
    analyze_all,
    find_dependencies,
    validate_dependencies,
)
from examples import DEFAULT_EXAMPLE, EXAMPLES, example_text, list_examples
from performance import compare_results, print_comparison
from pipeline_simulator import PipelineSimulator


class Instruction:
    def __init__(
        self,
        number,
        operation,
        destination=None,
        sources=None,
        immediate=None,
        memory_address=None,
    ):
        self.number = number
        self.operation = operation
        self.destination = destination
        self.sources = sources or []
        self.immediate = immediate
        self.memory_address = memory_address

    def __str__(self):
        if self.operation == "LOAD":
            addr = self.memory_address or self.immediate or "?"
            return (
                f"I{self.number}: {self.operation} "
                f"{self.destination}, {addr}"
            )
        if self.operation == "STORE":
            addr = self.memory_address or self.immediate or "?"
            return (
                f"I{self.number}: {self.operation} "
                f"{self.sources[0]}, {addr}"
            )
        if self.destination:
            if self.sources:
                return (
                    f"I{self.number}: {self.operation} "
                    f"{self.destination}, {', '.join(self.sources)}"
                )
            return f"I{self.number}: {self.operation} {self.destination}"
        return f"I{self.number}: {self.operation}"


def _looks_like_register(token):
    return (
        len(token) >= 2
        and token[0].upper() == "R"
        and token[1:].isdigit()
    )


def parse_instruction(number, line):
    parts = line.replace(",", " ").split()

    if not parts:
        raise ValueError("Empty instruction.")

    operation = parts[0].upper()

    if operation == "LOAD":
        if len(parts) < 2:
            raise ValueError("LOAD requires a destination register.")
        if not _looks_like_register(parts[1]):
            raise ValueError(
                f"LOAD destination must be a register like R1, got '{parts[1]}'."
            )
        address = parts[2] if len(parts) >= 3 else None
        return Instruction(
            number,
            operation,
            destination=parts[1].upper(),
            sources=[],
            immediate=address,
            memory_address=address,
        )

    if operation == "STORE":
        if len(parts) < 2:
            raise ValueError("STORE requires a source register.")
        if not _looks_like_register(parts[1]):
            raise ValueError(
                f"STORE source must be a register like R1, got '{parts[1]}'."
            )
        address = parts[2] if len(parts) >= 3 else None
        return Instruction(
            number,
            operation,
            destination=None,
            sources=[parts[1].upper()],
            immediate=address,
            memory_address=address,
        )

    if operation in ("ADD", "SUB", "MUL", "DIV"):
        if len(parts) < 4:
            raise ValueError(
                f"{operation} requires a destination and two source registers."
            )
        for token in parts[1:4]:
            if not _looks_like_register(token):
                raise ValueError(
                    f"{operation} expects register operands, got '{token}'."
                )
        return Instruction(
            number,
            operation,
            destination=parts[1].upper(),
            sources=[parts[2].upper(), parts[3].upper()],
        )

    raise ValueError(f"Unsupported instruction: {operation}")


def build_instructions(text_or_lines):
    """Parse multiline text or a list of lines into Instruction objects."""
    if isinstance(text_or_lines, str):
        lines = text_or_lines.splitlines()
    else:
        lines = text_or_lines

    instructions = []
    errors = []

    cleaned = [line.strip() for line in lines if line.strip()]

    for number, line in enumerate(cleaned, start=1):
        try:
            instructions.append(parse_instruction(number, line))
        except ValueError as error:
            errors.append(f"Line {number}: {error}")

    return instructions, errors


def print_dependencies(dependencies, title="RAW DEPENDENCIES"):
    print("\n" + "=" * 72)
    print(title)
    print("=" * 72)

    if not dependencies:
        print("None detected.")
        return

    for first, second, register in dependencies:
        print(f"I{first} -> I{second}    Register: {register}")


def print_order(title, instructions):
    print("\n" + "=" * 72)
    print(title)
    print("=" * 72)
    print(
        " -> ".join(f"I{instruction.number}" for instruction in instructions)
    )


def run_pipeline(title, order, dependencies):
    print("\n" + "#" * 72)
    print(f"# {title}")
    print("#" * 72)

    simulator = PipelineSimulator(
        order=order,
        dependencies=dependencies,
    )
    return simulator.display()


def run_simulation(instructions):
    """
    Full traditional vs AI comparison.

    Returns a dict used by both the CLI and the Streamlit UI.
    """
    analysis = analyze_all(instructions)
    dependencies = analysis["raw"]

    valid, message = validate_dependencies(instructions, dependencies)
    if not valid:
        raise RuntimeError(message)

    traditional_order = instructions[:]
    traditional_sim = PipelineSimulator(
        order=traditional_order,
        dependencies=dependencies,
    )
    traditional_result = traditional_sim.simulate()

    ai_scheduler = AIScheduler(instructions, dependencies)
    ai_order, decisions = ai_scheduler.schedule()

    ai_sim = PipelineSimulator(
        order=ai_order,
        dependencies=dependencies,
    )
    ai_result = ai_sim.simulate()

    metrics = compare_results(traditional_result, ai_result)

    return {
        "instructions": instructions,
        "analysis": analysis,
        "dependencies": dependencies,
        "traditional_order": traditional_order,
        "traditional_sim": traditional_sim,
        "traditional_result": traditional_result,
        "ai_order": ai_order,
        "ai_sim": ai_sim,
        "ai_result": ai_result,
        "decisions": decisions,
        "metrics": metrics,
        "cycle_improvement": metrics["cycle_improvement"],
        "stall_reduction": metrics["stall_reduction"],
        "speedup": metrics["speedup"],
    }


def read_instructions_interactive():
    print("\nEnter instructions WITHOUT I1:, I2:, etc.")
    print("Example: LOAD R1, 10")
    print("Press ENTER on an empty line when finished.\n")

    instructions = []
    number = 1

    while True:
        line = input(f"I{number}: ").strip()

        if not line:
            break

        try:
            instructions.append(parse_instruction(number, line))
            number += 1
        except ValueError as error:
            print(f"Error: {error}")

    return instructions


def choose_workload():
    names = list_examples()

    print("\nChoose a workload:")
    print("  0. Custom (type instructions)")
    for index, name in enumerate(names, start=1):
        print(f"  {index}. {name}")

    choice = input("\nSelection [1]: ").strip() or "1"

    if choice == "0":
        return read_instructions_interactive()

    try:
        selected = names[int(choice) - 1]
    except (ValueError, IndexError):
        selected = DEFAULT_EXAMPLE
        print(f"Invalid choice. Using '{selected}'.")

    print(f"\nLoaded workload: {selected}")
    print(example_text(selected))

    instructions, errors = build_instructions(EXAMPLES[selected])
    if errors:
        for error in errors:
            print(error)
        return []

    return instructions


def main():
    print("=" * 72)
    print("AI-ACCELERATED INSTRUCTION SCHEDULER")
    print("=" * 72)

    instructions = choose_workload()

    if not instructions:
        print("\nNo instructions entered.")
        return

    data = run_simulation(instructions)
    analysis = data["analysis"]
    dependencies = data["dependencies"]

    print_order("ORIGINAL INSTRUCTION ORDER", instructions)
    print_dependencies(analysis["raw"], "RAW DEPENDENCIES")
    print_dependencies(analysis["war"], "WAR DEPENDENCIES")
    print_dependencies(analysis["waw"], "WAW DEPENDENCIES")

    traditional_result = run_pipeline(
        "TRADITIONAL IN-ORDER SCHEDULING",
        data["traditional_order"],
        dependencies,
    )

    print("\n" + "=" * 72)
    print("AI SCHEDULER DECISIONS")
    print("=" * 72)

    for step, decision in enumerate(data["decisions"], 1):
        ready = ", ".join(
            f"I{number}" for number in decision["ready_options"]
        )
        print(
            f"Step {step}: "
            f"Select I{decision['instruction']} | "
            f"Score {decision['score']:.2f} | "
            f"Ready: {ready}"
        )
        print(f"         Reason: {decision['reason']}")


    print_order("AI-OPTIMIZED INSTRUCTION ORDER", data["ai_order"])

    ai_result = run_pipeline(
        "AI-OPTIMIZED SCHEDULING",
        data["ai_order"],
        dependencies,
    )

    metrics = compare_results(traditional_result, ai_result)
    print_comparison(metrics)


if __name__ == "__main__":
    main()
