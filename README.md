# DIA — Ship Collision Detection

**Course:** Data Integration and Large-scale Analysis (DIA), TU Berlin · WiSe 2026/27  
**Deadline:** 28 January 2027, 23:59 (Berlin time)  
**Team:** 3 members · **Language:** Python 3.12

## Important: official starter code

The course supplies `collisionDetectionPandas.py`, `collisionDetectionSpark.py`, `requirements.txt`, and/or `pyproject.toml`. **Copy the original files from ISIS into the repository root before coding.** This scaffold deliberately does **not** create replacement Python templates: only edit designated sections of the official files, keep function signatures unchanged, and do not modify framework code. Do not install additional dependencies.

## Repository layout

```text
dia-ship-collision-detection/
├── README.md
├── .gitignore
├── .python-version
├── collisionDetectionPandas.py    # ADD official ISIS template
├── collisionDetectionSpark.py     # ADD official ISIS template
├── requirements.txt               # ADD official ISIS dependency file (if provided)
├── pyproject.toml                 # ADD official ISIS file (if provided)
├── data/
│   ├── raw/                       # local AIS input; ignored by Git
│   └── processed/                 # local derived data; ignored by Git
├── docs/
│   ├── TEAM_PLAN.md
│   ├── REPORT_NOTES.md
│   └── SUBMISSION_CHECKLIST.md
├── tests/                          # optional local tests; not submitted
├── scripts/                        # optional local benchmarks; not submitted
└── results/                        # local timings/plots; not submitted
```

## Quick start

1. Download the **official** course code, dependencies and filtered AIS dataset from ISIS.
2. Put the two original `.py` files and official dependency file(s) in the repository root. Put AIS CSVs in `data/raw/` (or use the paths expected by the official code).
3. Use Python 3.12 and install **only** the provided dependencies:

   ```bash
   python3.12 -m venv .venv
   source .venv/bin/activate             # Windows: .venv\\Scripts\\activate
   python -m pip install -r requirements.txt  # if this is the provided setup
   ```

   If the course provides Poetry as its chosen setup, follow its official instructions instead.
4. Read `docs/TEAM_PLAN.md`; create a feature branch for your assigned work.
5. Run the official framework commands once confirmed from its `__main__`/course instructions. Do not assume these scripts accept CLI arguments.

## Git workflow

- Protect `main` as the stable integration branch (if supported).
- Each person works on their own branch, e.g. `feature/pandas`, `feature/spark-preprocess`, `feature/spark-process-benchmarks`.
- Make small commits, open merge requests, request review from another team member, then merge.
- **Spark file is shared:** Person 2 edits only `preprocess()` and `partitionData()`; Person 3 edits only `process()`. Coordinate merges to avoid conflicts.
- Keep datasets, caches, generated files and local benchmark scripts out of the final ZIP.

## Deliverables

One ZIP named `DIA Exercise <studentID>.zip` (max 5 MB) containing **only**:
- `collisionDetectionPandas.py`
- `collisionDetectionSpark.py`
- PDF report, at most **3 pages, 12 pt**, including task-specific contribution percentages for all three members.

See `docs/SUBMISSION_CHECKLIST.md` for the final checks.
# Ship-Collision-Detection
