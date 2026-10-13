"""
Heuristic AI instruction scheduler with transparent feature scores.

Architecture (extensible for future modes):
    AIScheduler
    ├── heuristic mode  (current)
    ├── ML mode         (future)
    └── RL mode         (future)
"""

from __future__ import annotations


class AIScheduler:
    """
    Local AI-assisted scheduler for instruction-level parallelism.

    At each step the scheduler:
    1. Finds currently legal (ready) instructions.
    2. Extracts features for each ready instruction.
    3. Scores them with a deterministic heuristic model.
    4. Selects the highest-scoring instruction.
    5. Updates dependency state and repeats.

    Mode is reserved so a trained ML / RL model can be plugged in later
    without rewriting the pipeline integration.
    """

    OPERATION_COST = {
        "LOAD": 1,
        "STORE": 1,
        "ADD": 1,
        "SUB": 1,
        "MUL": 2,
        "DIV": 3,
    }

    def __init__(self, instructions, dependencies, mode="heuristic"):
        self.instructions = instructions
        self.dependencies = dependencies
        self.mode = mode

        self.deps = {i.number: [] for i in instructions}
        self.children = {i.number: [] for i in instructions}
        self.instruction_map = {i.number: i for i in instructions}

        for producer, consumer, _register in dependencies:
            self.deps[consumer].append(producer)
            self.children[producer].append(consumer)

    def critical_path(self, number, memo=None):
        if memo is None:
            memo = {}

        if number in memo:
            return memo[number]

        children = self.children.get(number, [])
        own_cost = self.OPERATION_COST.get(
            self.instruction_map[number].operation,
            1,
        )

        if not children:
            memo[number] = own_cost
            return own_cost

        value = own_cost + max(
            self.critical_path(child, memo) for child in children
        )
        memo[number] = value
        return value

    def unlock_count(self, number, completed):
        """How many waiting consumers become ready if this issues now."""
        provisional = set(completed)
        provisional.add(number)
        count = 0

        for child in self.children.get(number, []):
            required = self.deps.get(child, [])
            if all(dep in provisional for dep in required):
                count += 1

        return count

    def extract_features(self, number, completed):
        instruction = self.instruction_map[number]
        cost = self.OPERATION_COST.get(instruction.operation, 1)
        independent = not self.deps.get(number)

        return {
            "criticality": self.critical_path(number),
            "dependents": len(self.children.get(number, [])),
            "unlocks": self.unlock_count(number, completed),
            "independent": independent,
            "operation_cost": cost,
            "original_position": number,
        }

    def score_features(self, features):
        independent_bonus = 8 if features["independent"] else 0

        return (
            features["criticality"] * 6
            + features["unlocks"] * 15
            + features["dependents"] * 5
            + independent_bonus
            - features["operation_cost"] * 0.5
        )

    def explain(self, features, selected=False):
        reasons = []

        if features["independent"]:
            reasons.append(
                "independent of the current blocked chain"
            )
        if features["unlocks"] > 0:
            reasons.append(
                f"unlocks {features['unlocks']} waiting instruction(s)"
            )
        if features["dependents"] > 0:
            reasons.append(
                f"has {features['dependents']} direct dependent(s)"
            )
        if features["criticality"] >= 4:
            reasons.append(
                "lies on a long critical path"
            )
        if features["operation_cost"] <= 1:
            reasons.append("low estimated operation cost")
        if features["operation_cost"] >= 2:
            reasons.append(
                f"higher latency op (cost {features['operation_cost']})"
            )

        if not reasons:
            reasons.append("best available ready candidate")

        if selected:
            return "; ".join(reasons)
        return "; ".join(reasons)

    def score(self, number, completed):
        features = self.extract_features(number, completed)
        return self.score_features(features)

    def _select_heuristic(self, ready, completed):
        scored = []

        for number in ready:
            features = self.extract_features(number, completed)
            total = self.score_features(features)
            scored.append((number, total, features))

        scored.sort(
            key=lambda item: (
                -item[1],
                item[2]["original_position"],
            )
        )
        return scored

    def schedule(self):
        if self.mode != "heuristic":
            raise NotImplementedError(
                f"AI mode '{self.mode}' is reserved for a future extension. "
                "Use mode='heuristic'."
            )

        remaining = {
            instruction.number for instruction in self.instructions
        }
        completed = set()
        order = []
        decisions = []

        while remaining:
            ready = [
                number
                for number in remaining
                if all(
                    dep in completed
                    for dep in self.deps.get(number, [])
                )
            ]

            if not ready:
                raise RuntimeError(
                    "The dependency graph contains a cycle."
                )

            scored = self._select_heuristic(ready, completed)
            selected, selected_score, selected_features = scored[0]

            order.append(self.instruction_map[selected])
            completed.add(selected)
            remaining.remove(selected)

            candidate_rows = []
            for number, total, features in scored:
                candidate_rows.append(
                    {
                        "instruction": number,
                        "score": total,
                        "features": features,
                        "reason": self.explain(features),
                    }
                )

            decisions.append(
                {
                    "instruction": selected,
                    "score": selected_score,
                    "features": selected_features,
                    "reason": self.explain(
                        selected_features,
                        selected=True,
                    ),
                    "ready_options": [
                        number for number, _, _ in scored
                    ],
                    "candidates": candidate_rows,
                }
            )

        return order, decisions


if __name__ == "__main__":
    print("AI scheduler loaded successfully.")
