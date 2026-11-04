# Team plan (3 people)

| Member | Assigned tasks | Points | Dependency |
|---|---|---:|---|
| Person 1 | Pandas 1.1 single-threaded, 1.2 partitioning, 1.3 multi-threaded; Pandas report section | 30 | Independent start |
| Person 2 | Spark 2.1 preprocessing, 2.2 partitioning; support 2.3; Spark report notes | 25 (+ support) | Independent start; coordinate partition interface with Person 3 |
| Person 3 | Spark 2.3 join-based processing; 3.1 runtime, 3.2 scalability; comparison/report integration | 45 | Spark processing depends partly on Person 2; evaluation depends on all implementations |

These point values are **not** contribution percentages. Record actual work by task for the final contribution table.

## Person 1 checklist
- [ ] Inspect official `getData()` and `checkCollision()`; leave them unchanged.
- [ ] Implement `processSingleThreaded()` and check required vessel-pair output.
- [ ] Implement `partitionData()` preserving all possible collision pairs across time/space boundaries.
- [ ] Implement `processMultiThreaded()` and combine results correctly.
- [ ] Verify single vs multi outputs match; document attempted optimizations.

## Person 2 checklist
- [ ] Implement Spark `preprocess()` to match Pandas preprocessing, with `pyspark.pandas.DataFrame` input/output.
- [ ] Implement Spark `partitionData()` with correctness-preserving partitioning.
- [ ] Agree on columns, partition representation and join keys with Person 3.
- [ ] Support integration of `process()`; document optimizations.

## Person 3 checklist
- [ ] Agree on interface with Person 2 before coding.
- [ ] Implement Spark `process()` using PySpark joins; ensure correct pair filtering and output.
- [ ] Compare Spark results with Pandas on the same small input.
- [ ] Benchmark Pandas single, Pandas multi, and Spark under comparable conditions.
- [ ] Analyze scaling, overhead and expected limits; compile report with all members.

## Suggested internal milestones (not official deadlines)
- **Nov 6:** Commit official templates, agree roles and interface.
- **Nov 13:** First Pandas single-threaded and Spark preprocessing versions.
- **Nov 27:** Pandas parallel and Spark partition/join versions.
- **Dec 11:** Integrate and validate matching results.
- **Jan 8:** Run benchmarks and improve performance.
- **Jan 20:** Review 3-page report and contribution percentages.
- **Jan 27:** Final ZIP checked before **Jan 28, 2027, 23:59** deadline.

## Git collaboration
Branches: `feature/pandas`, `feature/spark-preprocess`, `feature/spark-process-benchmarks`. Open merge requests and request peer review. Person 2 edits only `preprocess()` and `partitionData()` in the Spark template; Person 3 edits only `process()`; coordinate merges because both share the same file. Never change non-designated framework code or add dependencies.
