# 🚀 AI-Accelerated Instruction Scheduling

A practical **Computer Organization and Architecture (COA)** project that demonstrates how heuristic AI-based instruction scheduling can improve CPU pipeline efficiency by reducing avoidable stalls.

The project compares traditional in-order instruction scheduling with a dependency-aware heuristic scheduler using a five-stage CPU pipeline simulator and an interactive Streamlit dashboard.

## 📌 Table of Contents

- [Overview](#-overview)
- [Problem Statement](#-problem-statement)
- [Objectives](#-objectives)
- [System Architecture](#-system-architecture)
- [How the Scheduler Works](#-how-the-scheduler-works)
- [CPU Pipeline Model](#-cpu-pipeline-model)
- [Supported Instructions](#-supported-instructions)
- [Key Features](#-key-features)
- [Project Structure](#-project-structure)
- [Installation](#-installation)
- [Running the Project](#-running-the-project)
- [Example Workload](#-example-workload)
- [Performance Metrics](#-performance-metrics)
- [Limitations and Future Improvements](#-limitations-and-future-improvements)
- [Project Demonstration](#-project-demonstration)
- [Viva Questions](#-viva-questions)

## 🎯 Overview

Modern processors use instruction pipelining to execute multiple instructions in overlapping stages. However, data dependencies can prevent an instruction from proceeding until an earlier instruction produces the required result.

This project analyzes instruction dependencies and compares two scheduling approaches:

- **Traditional Scheduling:** Executes instructions in their original program order.
- **Heuristic AI Scheduling:** Selects eligible instructions using a scoring strategy designed to prioritize useful work and reduce pipeline waiting.

Both schedules are simulated using the same simplified five-stage pipeline model. The application calculates performance metrics to help visualize and understand the impact of instruction scheduling.

## ❗ Problem Statement

Traditional in-order instruction execution may introduce unnecessary waiting when an instruction depends on an earlier result, even though other independent instructions are available.

The project explores how dependency-aware instruction reordering can improve pipeline utilization and reduce execution cycles while respecting the dependencies enforced by the scheduler.

## 🎯 Objectives

- Analyze RAW, WAR, and WAW data hazards.
- Build and validate instruction dependencies.
- Implement heuristic-based instruction scheduling.
- Simulate a five-stage CPU pipeline.
- Compare traditional and optimized instruction schedules.
- Calculate execution cycles, stalls, utilization, and speedup.
- Provide an interactive dashboard for visualization and demonstration.

## 🏗️ System Architecture

```text
              Instruction Input
                      |
                      v
             +------------------+
             | Parse & Validate |
             |     main.py      |
             +--------+---------+
                      |
                      v
             +------------------+
             | Dependency       |
             | Analysis         |
             | dependency_      |
             | analyzer.py      |
             +--------+---------+
                      |
             +--------+--------+
             |                 |
             v                 v
      +-------------+   +--------------+
      | Traditional |   | Heuristic AI  |
      | Instruction|   | Scheduler     |
      | Order       |   | ai_scheduler  |
      +------+------+   +------+-------+
             |                 |
             v                 v
      +-------------+   +--------------+
      | Pipeline    |   | Pipeline     |
      | Simulator   |   | Simulator    |
      +------+------+   +------+-------+
             |                 |
             +--------+--------+
                      |
                      v
             +------------------+
             | Performance       |
             | Comparison        |
             | performance.py    |
             +--------+---------+
                      |
             +--------+--------+
             |                 |
             v                 v
       Command Line       Streamlit UI
         main.py             app.py
```

### Module Description

| Module | Responsibility |
|---|---|
| `main.py` | Parses input, validates instructions, and provides the CLI workflow |
| `dependency_analyzer.py` | Identifies register dependencies and data hazards |
| `ai_scheduler.py` | Scores eligible instructions and generates a reordered schedule |
| `pipeline_simulator.py` | Simulates instruction execution through five pipeline stages |
| `performance.py` | Calculates and compares performance metrics |
| `examples.py` | Provides predefined workloads for testing |
| `app.py` | Provides the interactive Streamlit dashboard |

## 🧠 How the Scheduler Works

The scheduler uses a **rule-based heuristic scoring algorithm** to choose which eligible instruction should be scheduled next.

It is an AI-inspired scheduling approach, not a trained machine-learning model.

### Step-by-Step Process

1. **Dependency Analysis:** Identify which registers each instruction reads and writes.
2. **Ready Instruction Selection:** Find instructions whose required dependencies have been satisfied.
3. **Candidate Scoring:** Assign scores using factors such as:
   - **Dependency Criticality:** Prioritizes instructions on longer dependent chains.
   - **Unlock Potential:** Considers how many waiting instructions may become eligible.
   - **Fan-out:** Considers the number of direct dependent instructions.
   - **Independence Bonus:** Favors useful instructions that can be scheduled independently.
   - **Operation Cost:** Applies a penalty to heavier operations such as multiplication and division.
4. **Instruction Selection:** Choose a high-scoring eligible instruction.
5. **Dependency Update:** Recalculate which instructions can be scheduled next.
6. **Pipeline Simulation:** Simulate the original and reordered instruction sequences.
7. **Performance Comparison:** Compare the calculated results.

The actual scheduling quality depends on the heuristic and the dependencies enforced by the implementation.

## ⚙️ CPU Pipeline Model

The simulator uses a five-stage instruction pipeline:

```text
IF  →  ID  →  EX  →  MEM  →  WB
```

| Stage | Description |
|---|---|
| IF | Instruction Fetch |
| ID | Instruction Decode |
| EX | Execute or address calculation |
| MEM | Memory Access |
| WB | Write Back |

### What Is a Pipeline Stall?

A **pipeline stall** occurs when an instruction must wait because a required dependency has not been resolved under the simulator's rules.

The project represents waiting cycles using `ST` in its pipeline timeline.

The documented model uses one issue slot per cycle and makes dependent instructions wait until their producers reach the WB stage.

## 💻 Supported Instructions

| Instruction | Example | Description |
|---|---|---|
| `LOAD` | `LOAD R1, 10` | Loads a value into a destination register |
| `STORE` | `STORE R5, 100` | Stores a register value to memory |
| `ADD` | `ADD R3, R1, R2` | Adds two source registers |
| `SUB` | `SUB R4, R3, R1` | Subtracts two register values |
| `MUL` | `MUL R5, R3, R4` | Multiplies two register values |
| `DIV` | `DIV R6, R5, R2` | Divides register values |

**Important:** Enter instructions in the syntax supported by the parser. Instruction IDs are assigned automatically, so do not add labels such as `I1:` or `I2:` unless the parser supports them.

## ✨ Key Features

- RAW, WAR, and WAW hazard analysis
- Dependency-aware instruction scheduling
- Heuristic candidate scoring
- Five-stage CPU pipeline simulation
- Traditional versus optimized pipeline timelines
- Performance metric calculations
- Predefined example workloads
- Custom instruction input, where supported
- Interactive Streamlit dashboard
- Command-line execution

## 📂 Project Structure

```text
AI_Instruction_Scheduler/
│
├── app.py                  # Streamlit dashboard
├── main.py                 # Main program and CLI
├── ai_scheduler.py         # Heuristic scheduling algorithm
├── pipeline_simulator.py   # Pipeline simulation
├── dependency_analyzer.py  # Dependency and hazard analysis
├── performance.py          # Performance calculations
├── examples.py             # Example workloads
├── requirements.txt        # Python dependencies
└── README.md               # Project documentation
```

## 🛠️ Installation

### Prerequisites

- Python installed on your system
- Git, if cloning the repository
- Required Python packages listed in `requirements.txt`

### Step 1: Clone the Repository

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
```

Replace `YOUR_GITHUB_REPOSITORY_URL` with your actual repository URL.

### Step 2: Enter the Project Directory

```bash
cd AI_Instruction_Scheduler
```

### Step 3: Create a Virtual Environment

```bash
python -m venv .venv
```

### Step 4: Activate the Environment

**Windows:**

```powershell
.venv\Scripts\activate
```

**Linux or macOS:**

```bash
source .venv/bin/activate
```

### Step 5: Install Dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## ▶️ Running the Project

### Option 1: Streamlit Dashboard

Run:

```bash
streamlit run app.py
```

Open the local URL displayed in the terminal to access the dashboard.

### Option 2: Command-Line Interface

Run:

```bash
python main.py
```

Follow the program prompts to select a predefined workload or enter instructions, depending on the supported input workflow.

## 🧪 Example Workload

Use the following instructions to demonstrate independent and dependent instruction chains:

```text
LOAD R1, 10
LOAD R2, 20
ADD R3, R1, R2
LOAD R6, 50
LOAD R7, 60
SUB R8, R6, R7
MUL R9, R3, R8
STORE R9, 200
```

### Understanding the Example

- `LOAD R1, 10` and `LOAD R2, 20` provide inputs to the `ADD` instruction.
- `LOAD R6, 50` and `LOAD R7, 60` provide inputs to the `SUB` instruction.
- The `MUL` instruction combines the results of `ADD` and `SUB`.
- The `STORE` instruction uses the result produced by `MUL`.

The separate dependency chains provide an opportunity to demonstrate how scheduling independent work may reduce waiting.

Actual performance improvements depend on the simulator's scheduling and timing rules.

## 📊 Performance Metrics

The application compares the schedules using calculated performance metrics.

| Metric | Meaning |
|---|---|
| Total Cycles | Number of cycles reported to complete the workload |
| Scheduling Stalls | Waiting cycles attributed to dependencies under the model |
| Pipeline Utilization | Proportion of available pipeline stage-slots used for useful work |
| Cycle Improvement | Percentage reduction in cycles relative to the traditional schedule |
| Stall Reduction | Percentage reduction in stalls relative to the traditional schedule |
| Speedup | Traditional cycle count divided by the heuristic schedule's cycle count |

### Speedup Formula

\[
\text{Speedup} =
\frac{\text{Traditional Cycles}}
{\text{Heuristic Schedule Cycles}}
\]

- **Speedup greater than 1:** The heuristic schedule takes fewer simulated cycles.
- **Speedup equal to 1:** Both schedules take the same number of cycles.
- **Speedup less than 1:** The heuristic schedule takes more simulated cycles.

The project calculates its results from the workload. No fixed speedup or stall reduction is guaranteed.

## ⚠️ Limitations and Future Improvements

### Current Limitations

- The project is an educational simulator, not a cycle-accurate modern CPU model.
- It uses a simplified five-stage pipeline with one issue slot per cycle.
- The scheduler uses rule-based heuristics rather than a trained machine-learning model.
- Realistic cache misses, branch prediction, forwarding, and detailed functional-unit latencies are not represented unless separately implemented.
- Scheduling results vary depending on the instruction workload.
- Correct instruction reordering must preserve all dependencies necessary for program correctness.

**Important correctness note:** RAW (Read After Write), WAR (Write After Read), and WAW (Write After Write) hazards can all affect instruction reordering. The documented implementation analyzes WAR and WAW but does not use them as hard scheduling constraints. Therefore, respecting RAW dependencies alone does not guarantee correct behavior for every possible instruction sequence.

### Future Improvements

- Enforce all required dependencies during scheduling.
- Add more realistic pipeline latency and forwarding models.
- Support additional instruction types.
- Introduce workload-based scheduler evaluation.
- Improve pipeline visualization and scheduling explanations.
- Explore learning-based scheduling techniques as an extension.

## 🎤 Project Demonstration

For a classroom presentation or viva:

1. Launch the Streamlit dashboard.
2. Select a predefined workload or enter a custom instruction sequence.
3. Display the original instruction order.
4. Explain the dependency table and identify RAW hazards.
5. Show the traditional pipeline timeline and its stalls.
6. Display the heuristic scheduler's decisions and reordered sequence.
7. Compare cycle counts, stalls, utilization, and speedup.
8. Explain the model assumptions and correctness limitations.

Use the actual results generated by the application when presenting performance improvements.

## ❓ Viva Questions

**1. What is instruction scheduling?**

Instruction scheduling is the process of arranging instructions to improve execution efficiency while preserving program behavior.

**2. What is a pipeline stall?**

A pipeline stall is a delay that occurs when an instruction cannot proceed because a required condition or dependency has not been satisfied.

**3. What is a RAW hazard?**

A Read After Write hazard occurs when an instruction reads a register that an earlier instruction must write first.

**4. What is the role of the heuristic scheduler?**

It selects eligible instructions using scoring factors intended to reduce unnecessary waiting.

**5. Is the scheduler based on trained machine learning?**

No. It uses a rule-based heuristic to make dependency-aware scheduling decisions.

**6. What is speedup?**

Speedup is the ratio of the traditional schedule's cycle count to the heuristic schedule's cycle count.

**7. Why can independent instructions improve pipeline performance?**

Independent instructions may be scheduled while another instruction chain is waiting, helping reduce avoidable delays.

**8. What is the main limitation of this project?**

The pipeline is simplified, and the scheduler must enforce all relevant dependencies to preserve program correctness for general instruction sequences.

## 📜 License

This project is intended for educational and academic use. Add a formal open-source license if you plan to distribute it under specific licensing terms.

---

**Developed as an educational Computer Organization and Architecture project.**
