class PipelineSimulator:
    """
    Five-stage CPU pipeline with a single instruction issue slot.

    Stages:
        IF -> ID -> EX -> MEM -> WB

    Scheduling model:
    - The given order determines which instruction is considered next.
    - One instruction may be issued per cycle.
    - A dependent instruction cannot be issued until all of its
      producers have reached WB.
    - This lets an AI scheduler place independent instructions into
      cycles that would otherwise be wasted waiting for dependencies.

    This model is deliberately simple and transparent for a COA
    academic project.
    """

    STAGES = ("IF", "ID", "EX", "MEM", "WB")

    def __init__(self, order, dependencies):
        self.order = list(order)
        self.dependencies = dependencies

        self.deps = {
            instruction.number: []
            for instruction in self.order
        }

        for producer, consumer, register in dependencies:
            self.deps.setdefault(consumer, []).append(producer)

        self.timeline = {}
        self.wb_cycles = {}
        self.total_cycles = 0
        self.stalls = 0

    def simulate(self):
        self.timeline = {}
        self.wb_cycles = {}
        self.stalls = 0

        previous_issue = 0

        for instruction in self.order:
            number = instruction.number

            # Normally the next instruction can be issued one cycle
            # after the previous one.
            issue_cycle = previous_issue + 1

            # RAW dependency constraint:
            # If producer WB is cycle 5, consumer can issue in cycle 5,
            # placing ID in cycle 6 and ensuring the operand is available.
            producer_ready = 0

            for producer in self.deps.get(number, []):
                if producer not in self.wb_cycles:
                    raise RuntimeError(
                        f"I{number} was scheduled before its producer I{producer}."
                    )

                producer_ready = max(
                    producer_ready,
                    self.wb_cycles[producer]
                )

            if producer_ready:
                desired_issue = max(
                    previous_issue + 1,
                    producer_ready
                )

                self.stalls += max(
                    0,
                    desired_issue - (previous_issue + 1)
                )

                issue_cycle = desired_issue

            id_cycle = issue_cycle + 1
            ex_cycle = id_cycle + 1
            mem_cycle = ex_cycle + 1
            wb_cycle = mem_cycle + 1

            self.timeline[number] = {
                issue_cycle: "IF",
                id_cycle: "ID",
                ex_cycle: "EX",
                mem_cycle: "MEM",
                wb_cycle: "WB",
            }

            self.wb_cycles[number] = wb_cycle
            previous_issue = issue_cycle

        self.total_cycles = (
            max(self.wb_cycles.values())
            if self.wb_cycles
            else 0
        )

        return self.get_result()

    def get_result(self):
        if self.total_cycles == 0:
            utilization = 0.0
        else:
            useful = len(self.order) * len(self.STAGES)
            available = self.total_cycles * len(self.STAGES)
            utilization = useful / available * 100

        return {
            "cycles": self.total_cycles,
            "stalls": self.stalls,
            "utilization": utilization,
        }

    def display(self):
        self.simulate()

        print("\n" + "=" * 72)
        print("5-STAGE CPU PIPELINE")
        print("=" * 72)

        if not self.order:
            print("No instructions.")
            return self.get_result()

        cell = 4
        label = 13

        header = f"{'Instruction':<{label}}"

        for cycle in range(1, self.total_cycles + 1):
            header += f"{cycle:<{cell}}"

        print(header)
        print("-" * len(header))

        for instruction in self.order:
            number = instruction.number
            name = instruction.operation
            row = f"I{number} {name:<9}"

            cycle_map = self.timeline[number]

            occupied = set(cycle_map.keys())

            for cycle in range(1, self.total_cycles + 1):
                value = cycle_map.get(cycle, "")

                # Empty cycles before IF are represented by blanks.
                # Waiting cycles after IF and before ID are shown as ST.
                if (
                    not value
                    and cycle > min(occupied)
                    and cycle < max(
                        c for c, stage in cycle_map.items()
                        if stage == "ID"
                    )
                ):
                    value = "ST"

                row += f"{value:<{cell}}"

            print(row)

        result = self.get_result()

        print("\n" + "=" * 72)
        print("PERFORMANCE")
        print("=" * 72)
        print(f"Instructions        : {len(self.order)}")
        print(f"Total Cycles        : {result['cycles']}")
        print(f"Scheduling Stalls   : {result['stalls']}")
        print(f"Pipeline Utilization: {result['utilization']:.2f}%")
        print("=" * 72)

        return result


if __name__ == "__main__":
    print("Pipeline simulator loaded successfully.")
