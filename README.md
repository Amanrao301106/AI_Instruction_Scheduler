# AI-Accelerated Instruction Scheduling
Academic Computer Organization & Architecture (COA) project that shows how a heuristic AI scheduler can reorder CPU instructions to reduce pipeline stalls compared with traditional in-order issue.
System architecture
Instruction Input
       │
       ▼
┌──────────────────┐
│ parse + validate │  main.py
└────────┬─────────┘
         ▼
┌──────────────────┐
│ dependency       │  dependency_analyzer.py
│ RAW / WAR / WAW  │
└────────┬─────────┘
         ▼
┌──────────────────┐     ┌──────────────────┐
│ traditional      │     │ AI scheduler     │  ai_scheduler.py
│ program order    │     │ score + pick     │
└────────┬─────────┘     └────────┬─────────┘
         ▼                        ▼
┌──────────────────┐     ┌──────────────────┐
│ 5-stage pipeline │     │ 5-stage pipeline │  pipeline_simulator.py
└────────┬─────────┘     └────────┬─────────┘
         └──────────┬─────────────┘
                    ▼
           performance.py
           (cycles, stalls, speedup)
                    │
        ┌───────────┴───────────┐
        ▼                       ▼
   CLI (main.py)         UI (app.py / Streamlit)
How AI scheduling works
1. Build the RAW dependency graph (true data dependences).
2. Find currently ready instructions (all producers already scheduled).
3. Score each ready instruction using:
   - Dependency criticality – length of the longest dependent chain
   - Unlock potential – how many waiting instructions become ready
   - Fan-out – number of direct dependents
   - Independence bonus – prefer work that can fill idle slots
   - Operation cost – slight penalty for heavier ops (MUL/DIV)
4. Issue the highest-scoring instruction.
5. Repeat until the schedule is complete.
6. Simulate both traditional and AI orders on the same 5-stage pipeline.
The scheduler never violates RAW constraints, so the reordered program remains correct.
CPU pipeline model
Five stages, one issue slot per cycle:
IF → ID → EX → MEM → WB
- Instructions issue in the given schedule order.
- A dependent instruction cannot issue until every producer has reached WB.
- Waiting cycles between IF and ID are shown as ST (stall).
This model is intentionally transparent for viva explanation.
Supported instructions
Op	Form	Notes
LOAD	LOAD R1, 10	Writes destination register
STORE	STORE R5, 100	Reads source register
ADD	ADD R3, R1, R2	Dest + two sources
SUB	SUB R4, R3, R1	Dest + two sources
MUL	MUL R5, R3, R4	Higher operation cost
DIV	DIV R6, R5, R2	Highest operation cost


Do not prefix lines with I1:, I2:, etc. Numbers are assigned automatically.
Features
- RAW / WAR / WAW hazard detection
- Dependency graph construction and validation
- Heuristic AI instruction scheduling
- Side-by-side traditional vs AI pipeline timelines
- Dynamic performance metrics (no hard-coded results)
- Predefined workloads in examples.py
- Streamlit dashboard + command-line runner
Folder structure
AI_Instruction_Scheduler/
├── app.py                  # Streamlit UI
├── main.py                 # Core models + CLI
├── ai_scheduler.py         # Heuristic AI scheduler
├── pipeline_simulator.py   # 5-stage CPU pipeline
├── dependency_analyzer.py  # RAW / WAR / WAW analysis
├── performance.py          # Comparison metrics
├── examples.py             # Demo workloads
├── requirements.txt
└── README.md
Installation
cd AI_Instruction_Scheduler
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate

pip install -r requirements.txt
Running
Streamlit UI
streamlit run app.py
Command line
python main.py
Choose a predefined workload or enter custom instructions interactively.
Example input
LOAD R1, 10
LOAD R2, 20
ADD R3, R1, R2
LOAD R6, 50
LOAD R7, 60
SUB R8, R6, R7
MUL R9, R3, R8
STORE R9, 200
Expected output
You should see:
1. Original instruction order
2. RAW / WAR / WAW dependency tables
3. Traditional in-order pipeline timeline + cycle count
4. AI scheduler step-by-step decisions (ready set + score)
5. AI-optimized order and pipeline timeline
6. Final comparison: cycles, stalls, utilization, speedup
Workloads with independent chains (for example Mixed Workload or Independent Instructions) usually show the largest AI improvement, because the scheduler can fill stall slots with unrelated work.
Performance metrics
Metric	Meaning
Total Cycles	Last WB cycle of the schedule
Scheduling Stalls	Extra issue delays caused by RAW waits
Pipeline Utilization	Useful stage-slots / available stage-slots
Cycle Improvement	Percent fewer cycles vs traditional
Stall Reduction	Percent fewer stalls vs traditional
Speedup	Traditional cycles ÷ AI cycles


All values are computed from the simulation for the entered workload.
How to explain this in a viva
1. Problem: In-order pipelines often stall on RAW hazards even when other independent instructions are available.
2. Idea: Use a dependency-aware heuristic (lightweight “AI”) to pick which ready instruction to issue next.
3. Correctness: Only RAW edges constrain reordering; WAR/WAW are analyzed but not used as hard scheduler edges in this model.
4. Evidence: Show the two pipeline charts and the computed speedup for the same input.
5. Limitation: This is a teaching model (single issue, simplified stalls), not a full out-of-order CPU with register renaming.
License
Educational / academic use.
