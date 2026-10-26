# Assignment 6: Deployment topologies and trade-offs

**Group:**
**Members (name, student ID):**
**Scenario (A, B or C):**

Choose **one** scenario below. Groups with an odd number take A or B, groups with an even number take B or C. Use your measurements from Tutorial 6 as evidence: cite run names from `results/runs.csv`.

Facts that hold in every scenario:

- The large model serves at most **20 calls per second** (4 calls at once × about 200 ms each), and every call costs money.
- The small model is fast and cheap enough to run anywhere, including inside the review service or on a kiosk, but it is much less accurate on its own.

## Scenarios

**A. Owner alerts.** When a customer posts a negative review, the restaurant owner gets a push notification within **2 seconds**. At the lunch peak, CampusEats receives **40 reviews per second**. A missed alert is acceptable; a wrong alert ("your customer is unhappy" when they are not) makes owners ignore alerts.

**B. Canteen kiosk.** A tablet in each canteen lets students leave a review on the spot. Canteen Wi-Fi drops several times a day for minutes at a time. Every review must be accepted, even offline. The food committee needs the labels **by the end of the day**.

**C. Weekly report.** The university food committee wants a weekly sentiment report per restaurant. Nothing is real-time. **Accuracy matters most** and **cost must be minimal**.

## Topologies and patterns to choose from

| | Topology | Where the model runs |
|---|---|---|
| T1 | Model as a service, synchronous | Inference service, called for each review (today's baseline) |
| T2 | Model as a library | Inside the review service, or on the device |
| T3 | Hybrid | Small model locally, large model as a remote service |
| T4 | Asynchronous / batch | Reviews are queued (broker, W10) or stored, and scored later in bulk |

Combine one topology with any of the patterns from Tutorial 6: **fallback**, **cascade** and **cache**.

## 1. Quality requirements

The three most important quality requirements for your scenario, each with a number where possible.

| # | Quality | Requirement |
|---|---|---|
| 1 | | |
| 2 | | |
| 3 | | |

## 2. Design

Your topology, the patterns you add, and a container-level diagram (C4 level 2). Mermaid is fine, as in W12.

```mermaid
flowchart LR
    %% your containers and arrows here
```

## 3. Evidence

Which runs support your choice? Show the numbers and, for scenario A, the capacity arithmetic: how many large-model calls per second does your design need at the peak?

| Run | What it shows |
|---|---|
| | |
| | |

## 4. ADR

Use the ADR format from W5.

**Title:**

**Status:** Proposed

**Context:**

**Decision:**

**Consequences:**
- Positive:
- Negative:

**Alternatives considered:** at least one topology you rejected, and why.

## 5. Risk

One way your design could fail silently in production, and the number you would monitor to notice it.

>
