# Tutorial 6 worksheet: serving patterns

**Group:**
**Members (name, student ID):**

Copy result rows from `results/runs.csv` (or the load test's output) into the tables. Keep answers short: one to three sentences each.

## How did you write the code?

| Task | By hand / AI agent (which one?) | What did you have to check or fix? |
|---|---|---|
| 1 Fallback | | |
| 2 Cascade | | |
| 3 Cache | | |

## Task 0: Baseline

| Run | p50 ms | p95 ms | accuracy | large calls |
|---|---|---|---|---|
| t0-large | | | | |
| t0-small | | | | |

**Q0.** What does the large model buy, and what does it cost?

>

## Task 1: Fallback prediction

| Run | run time (s) | p50 ms | p95 ms | errors | pending | accuracy |
|---|---|---|---|---|---|---|
| t1-before | | | | | | |
| t1-after | | | | | | |

**Q1.1** In `t1-before`, p50 can look *better* than the baseline. Why is p50 misleading here? Which column tells the real story?

>

**Q1.2** The hang affects only 10% of large-model calls. Why is it worse for the system than 10% of reviews being slow? Think about what a waiting request holds on to in the review service and the gateway.

>

**Q1.3** Pending reviews have no label. Suggest what should happen to them, and name the topology from the lecture that does it.

>

**Q1.4** We chose a 1-second timeout. What goes wrong if it is 0.1 s? And if it is 10 s?

>

## Task 2: Cascade

| Run | threshold | p50 ms | p95 ms | accuracy | large calls |
|---|---|---|---|---|---|
| t2-0.6 | 0.6 | | | | |
| t2-0.7 | 0.7 | | | | |
| t2-0.8 | 0.8 | | | | |
| t2-0.9 | 0.9 | | | | |

**Q2.1** Which threshold would you deploy for CampusEats, and why? Name the quality you give up.

>

**Q2.2** Look at p50 and p95 for your threshold. Why does the cascade help p50 much more than p95?

>

**Q2.3** The cascade trusts the small model's confidence. Give one situation where that trust is misplaced, and its effect on users.

>

## Task 3: Cached predictions

| Run | p50 ms | p95 ms | accuracy | large calls | cache hits |
|---|---|---|---|---|---|
| t3-cache | | | | | |

**Q3.1** Which reviews benefit from the cache, and which never will?

>

**Q3.2** Next week you deploy a better large model. What must happen to the cache, and how would you design for it?

>

## Debrief

**Q4.** Name one thing these measurements told you that you could not have known from the lecture alone.

>
