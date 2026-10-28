# Tutorial 6 worksheet: serving patterns

**Name / ชื่อ:** Chanatda Konchom

**Student ID / รหัสนิสิต:** 6631305321

This is **individual work**: each student completes and submits their own copy, in their own fork.

*งานนี้เป็น**งานเดี่ยว** นิสิตแต่ละคนทำและส่งงานของตัวเอง โดยใช้ forked repository ของตัวเอง*

Copy result rows from `results/runs.csv` (or the load test's output) into the tables. Keep answers short: one to three sentences each. Answer in Thai or English.

ตอนที่ตอบ ให้นิสิตคัดลอกผลจาก `results/runs.csv` (หรือจาก output ของ load test) ลงในตาราง ตอบสั้นๆ ข้อละ 1–3 ประโยค จะตอบเป็นภาษาไทยหรือภาษาอังกฤษก็ได้

## Task 0: Baseline (copy the baseline results from `results/runs.csv` here / copy ผลลัพธ์ของ baseline จาก `results/runs.csv` มาวางที่นี่)

| Run | p50 ms | p95 ms | accuracy | large calls |
|---|---|---|---|---|
| t0-large | 490 | 587 | 93.5% | 100% |
| t0-small | 9 | 21 | 72.5% | 0% |

**Q0.** What does the large model buy, and what does it cost?

*large model ให้อะไรเพิ่ม และต้องแลกด้วยอะไร*

> The large model buys an accuracy gain of +21.0% (93.5% vs 72.5% for small) by understanding word combinations and negations. However, it costs significantly higher latency (p50 of 490 ms vs 9 ms) and requires 100% large model calls, consuming expensive compute and limited concurrency slots.

## Task 1: Fallback prediction (copy the Task 1 results from `results/runs.csv` here / copy ผลลัพธ์ของ Task 1 จาก `results/runs.csv` มาวางที่นี่)

| Run | run time (s) | p50 ms | p95 ms | errors | pending | accuracy |
|---|---|---|---|---|---|---|
| t1-before | 30.3 | 244 | 407 | 21 | 0 | 92.7% |
| t1-after | 9.7 | 388 | 1011 | 0 | 28 | 93.0% |

**Q1.1** In `t1-before`, p50 can look *better* than the baseline. Why is p50 misleading here? Which column tells the real story?

*ใน `t1-before` ค่า p50 อาจดู "ดีกว่า" baseline ทำไม p50 จึงทำให้เข้าใจผิดในกรณีนี้ และ column ไหนบอกความจริง*

> In `t1-before`, p50 looks misleadingly fast (244 ms vs 490 ms baseline) because `loadtest.py` calculates percentiles only across successful requests. The 21 requests that hung for >10 s were dropped into `errors` and excluded from latency calculations. The `errors` column (21 failures) and total run time (30.3 s vs 9.7 s) tell the real story of severe degradation.

**Q1.2** The hang affects only 10% of large-model calls. Why is it worse for the system than 10% of reviews being slow? Think about what a waiting request holds on to in the review service and the gateway.

*การค้างเกิดกับ calls ไปยัง large model แค่ 10% ทำไมจึงส่งผลต่อระบบแย่กว่าการที่รีวิว 10% ช้าลงเฉยๆ ลองคิดว่า request ที่รออยู่ถือทรัพยากรอะไรไว้ใน review service และ gateway*

> Because the large model allows only 4 concurrent calls (`LARGE_CAPACITY = 4`), a few hung calls quickly consume all concurrency slots for 20 seconds. Each waiting request ties up an open HTTP socket, memory, and async worker thread in the gateway and review service. This creates head-of-line blocking that queues up healthy requests until they also time out as errors.

**Q1.3** Pending reviews have no label. Suggest what should happen to them, and name the topology from the lecture that does it.

*รีวิวที่ pending ยังไม่มี label ควรจัดการกับรีวิวเหล่านี้อย่างไร และ topology ใดจาก lecture ที่ทำแบบนั้น*

> Pending reviews should be safely saved in the database and scored later by an offline batch job or background worker once inference capacity recovers. This corresponds to Topology T4 (Asynchronous / Batch processing) using a message broker or scheduled job.

**Q1.4** We chose a 1-second timeout. What goes wrong if it is 0.1 s? And if it is 10 s?

*เราเลือก timeout 1 วินาที จะเกิดปัญหาอะไรถ้าตั้งเป็น 0.1 วินาที และถ้าตั้งเป็น 10 วินาที*

> A 0.1 s timeout causes false timeouts because the large model normally takes ~200 ms, unnecessarily dropping almost all reviews to pending. A 10 s timeout lets hung requests hold concurrency slots for too long, blowing tail latency to 10 s. With 1.0 s, `t1-after` keeps p95 at 1011 ms (bordering QR1's 1-second limit) while trading 28 reviews (14%) to `pending` to guarantee 0 errors and preserve availability (QR2).

## Task 2: Cascade (copy the Task 2 results from `results/runs.csv` here / copy ผลลัพธ์ของ Task 2 จาก `results/runs.csv` มาวางที่นี่)

| Run | threshold | p50 ms | p95 ms | accuracy | large calls |
|---|---|---|---|---|---|
| t2-0.6 | 0.6 | 7 | 541 | 91.5% | 38% |
| t2-0.7 | 0.7 | 369 | 570 | 93.0% | 53% |
| t2-0.8 | 0.8 | 444 | 599 | 93.5% | 64% |
| t2-0.9 | 0.9 | 478 | 596 | 93.5% | 77% |

**Q2.1** Which threshold would you deploy for CampusEats, and why? Name the quality you give up.

*จะเลือก threshold ใดสำหรับ deploy ใน CampusEats เพราะอะไร และต้องยอมเสีย quality ใดไป*

> I would deploy threshold 0.7 for CampusEats. It achieves 93.0% accuracy (surpassing QR3's >= 90% target and close to the large model's 93.5%) while reducing large model calls to 53%, comfortably meeting QR5's capacity constraint (< 20 calls/s). The quality given up is a small amount of cost and latency compared to threshold 0.6 in exchange for higher label accuracy.

**Q2.2** Look at p50 and p95 for your threshold. Why does the cascade help p50 much more than p95?

*ดูค่า p50 และ p95 ของ threshold ที่เลือก ทำไม cascade จึงช่วย p50 ได้มากกว่า p95 มาก*

> At threshold 0.7, 47% of requests are answered immediately by the small model (<10 ms), pulling median latency (p50) down from 490 ms to 369 ms. In contrast, 53% of requests still escalate to the large model; because 53% is far greater than 5%, the 95th percentile request is always one that incurred both the small model check and the large model wait, leaving p95 virtually unchanged at 570 ms.

**Q2.3** The cascade trusts the small model's confidence. Give one situation where that trust is misplaced, and its effect on users.

*cascade เชื่อ confidence ของ small model ยกตัวอย่างหนึ่งสถานการณ์ที่ไม่ควรเชื่อ และผลที่เกิดกับผู้ใช้*

> Trust is misplaced on sentences with negations or contrast (e.g., "The soup was not good" or "great ambience but awful food"). The bag-of-words small model spots words like "good" or "great" and outputs high confidence for positive, ignoring "not". This misclassifies a dissatisfied customer's review as positive, preventing restaurant owners from receiving critical complaint alerts.

## Task 3: Cached predictions (copy the Task 3 results from `results/runs.csv` here / copy ผลลัพธ์ของ Task 3 จาก `results/runs.csv` มาวางที่นี่)

| Run | p50 ms | p95 ms | accuracy | large calls | cache hits |
|---|---|---|---|---|---|
| t3-cache | 5 | 535 | 93.0% | 38% | 35% |

**Q3.1** Which reviews benefit from the cache, and which never will?

*รีวิวแบบไหนได้ประโยชน์จาก cache และแบบไหนไม่มีวันได้ประโยชน์*

> Short, common, and repetitive reviews (e.g., "อร่อย", "Too salty") and reviews with varying spaces or casing benefit because `key()` normalizes them to identical entries. Long, unique narrative reviews submitted once, initial cold misses, or reviews evicted due to the `max_size` limit will never benefit.

**Q3.2** Next week you deploy a better large model. What must happen to the cache, and how would you design for it?

*สัปดาห์หน้าจะ deploy large model ตัวใหม่ที่ดีกว่าเดิม ต้องทำอะไรกับ cache และจะออกแบบรองรับเรื่องนี้อย่างไร*

> The cache holds stale predictions from the old model and must be invalidated. To design for this, the cache key should include the model version namespace (e.g., `f"{model_id}:{normalized_text}"`) so new model deployments automatically bypass old entries, combined with an administrative cache flush endpoint on startup.

## Debrief

**Q4.** Name one thing you learned from these measurements that the lecture did not cover.

*ยกตัวอย่างหนึ่งสิ่งที่ได้เรียนรู้จากการวัดผลครั้งนี้ ที่ไม่มีพูดถึงใน lecture*

> While the lecture presents cascade as reducing latency and cost, our measurements showed that cascade drastically slashes median latency (p50 dropped from 490 ms to 369 ms at threshold 0.7, and 7 ms at 0.6) but has almost no effect on tail latency (p95 remained around 541–570 ms vs 587 ms baseline). In addition, `t1-before` revealed how partial failure can paradoxically deflate p50 (from 490 ms to 244 ms) because the 21 failed requests were excluded from the latency calculation.
