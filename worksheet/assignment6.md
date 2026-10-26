# Assignment 6: Deployment topologies and trade-offs

**Group / กลุ่ม:**

**Members (name, student ID) / สมาชิก (ชื่อ, รหัสนิสิต):**

**Scenario (A, B or C) / Scenario ที่เลือก:**

Choose **one** scenario below. Groups with an odd number take A or B, groups with an even number take B or C. Use your measurements from Tutorial 6 as evidence: cite run names from `results/runs.csv`. Answer in Thai or English.

เลือก scenario **หนึ่ง** ข้อด้านล่าง กลุ่มเลขคี่เลือก A หรือ B กลุ่มเลขคู่เลือก B หรือ C ใช้ผลการวัดจาก Tutorial 6 เป็นหลักฐาน โดยอ้างชื่อ run จาก `results/runs.csv` จะตอบเป็นภาษาไทยหรือภาษาอังกฤษก็ได้

Facts that hold in every scenario / ข้อเท็จจริงที่ใช้กับทุก scenario:

- The large model serves at most **20 calls per second** (4 calls at once × about 200 ms each), and every call costs money.

  *large model รับได้สูงสุด **20 calls ต่อวินาที** (พร้อมกัน 4 calls × ประมาณ 200 ms ต่อ call) และทุก call มีค่าใช้จ่าย*
- The small model is fast and cheap enough to run anywhere, including inside the review service or on a kiosk, but it is much less accurate on its own.

  *small model เร็วและถูกพอที่จะรันที่ไหนก็ได้ รวมถึงภายใน review service หรือบน kiosk แต่ถ้าใช้ตัวเดียวจะแม่นน้อยกว่ามาก*

## Scenarios

**A. Owner alerts.** When a customer posts a negative review, the restaurant owner gets a push notification within **2 seconds**. At the lunch peak, CampusEats receives **40 reviews per second**. A missed alert is acceptable; a wrong alert ("your customer is unhappy" when they are not) makes owners ignore alerts.

*เมื่อลูกค้าโพสต์รีวิวเชิงลบ เจ้าของร้านต้องได้รับ push notification ภายใน **2 วินาที** ช่วงพีคตอนเที่ยง CampusEats ได้รับรีวิว **40 รายการต่อวินาที** การพลาด alert ไปบ้างยอมรับได้ แต่ alert ที่ผิด ("ลูกค้าไม่พอใจ" ทั้งที่จริงๆ ไม่ใช่) จะทำให้เจ้าของร้านเลิกสนใจ alert*

**B. Canteen kiosk.** A tablet in each canteen lets students leave a review on the spot. Canteen Wi-Fi drops several times a day for minutes at a time. Every review must be accepted, even offline. The food committee needs the labels **by the end of the day**.

*มี tablet ในแต่ละโรงอาหารให้นิสิตรีวิวได้ทันที Wi-Fi ในโรงอาหารหลุดวันละหลายครั้ง ครั้งละหลายนาที ต้องรับรีวิวได้ทุกรายการแม้ขณะ offline และคณะกรรมการอาหารต้องการ label **ภายในสิ้นวัน***

**C. Weekly report.** The university food committee wants a weekly sentiment report per restaurant. Nothing is real-time. **Accuracy matters most** and **cost must be minimal**.

*คณะกรรมการอาหารของมหาวิทยาลัยต้องการรายงาน sentiment รายสัปดาห์ของแต่ละร้าน ไม่มีอะไรต้อง real-time **accuracy สำคัญที่สุด** และ **ค่าใช้จ่ายต้องน้อยที่สุด***

## Topologies and patterns to choose from / Topology และ pattern ที่เลือกใช้ได้

| | Topology | Where the model runs / โมเดลรันที่ไหน |
|---|---|---|
| T1 | Model as a service, synchronous | Inference service, called for each review (today's baseline)<br>*inference service ถูกเรียกทุกรีวิว (baseline ของวันนี้)* |
| T2 | Model as a library | Inside the review service, or on the device<br>*ภายใน review service หรือบนอุปกรณ์* |
| T3 | Hybrid | Small model locally, large model as a remote service<br>*small model รันในเครื่อง large model เป็น remote service* |
| T4 | Asynchronous / batch | Reviews are queued (broker, W10) or stored, and scored later in bulk<br>*รีวิวถูกเข้าคิว (broker, W10) หรือเก็บไว้ แล้วติด label ทีหลังเป็นชุด* |

Combine one topology with any of the patterns from Tutorial 6: **fallback**, **cascade** and **cache**.

*เลือก topology หนึ่งแบบ แล้วผสมกับ pattern จาก Tutorial 6 ได้ตามต้องการ: **fallback**, **cascade** และ **cache***

## 1. Quality requirements

The three most important quality requirements for your scenario, each with a number where possible.

*quality requirements ที่สำคัญที่สุด 3 ข้อของ scenario ที่เลือก ระบุตัวเลขเมื่อทำได้*

| # | Quality | Requirement |
|---|---|---|
| 1 | | |
| 2 | | |
| 3 | | |

## 2. Design / การออกแบบ

Your topology, the patterns you add, and a container-level diagram (C4 level 2). Mermaid is fine, as in W12.

*topology ที่เลือก pattern ที่เพิ่ม และ diagram ระดับ container (C4 level 2) ใช้ Mermaid ได้เหมือนใน W12*

```mermaid
flowchart LR
    %% your containers and arrows here
```

## 3. Evidence / หลักฐาน

Which runs support your choice? Show the numbers and, for scenario A, the capacity arithmetic: how many large-model calls per second does your design need at the peak?

*run ไหนสนับสนุนการตัดสินใจ แสดงตัวเลข และสำหรับ scenario A ให้แสดงการคำนวณ capacity ด้วย: ในช่วงพีค design ของคุณต้องใช้ large model กี่ calls ต่อวินาที*

| Run | What it shows / แสดงอะไร |
|---|---|
| | |
| | |

## 4. ADR

Use the ADR format from W5.

*ใช้รูปแบบ ADR จาก W5*

**Title:**

**Status:** Proposed

**Context:**

**Decision:**

**Consequences:**
- Positive:
- Negative:

**Alternatives considered:** at least one topology you rejected, and why.

*อย่างน้อยหนึ่ง topology ที่ไม่เลือก และเหตุผล*

## 5. Risk / ความเสี่ยง

One way your design could fail silently in production, and the number you would monitor to notice it.

*หนึ่งวิธีที่ design ของคุณอาจล้มเหลวแบบเงียบๆ ใน production และตัวเลขที่จะ monitor เพื่อให้รู้ตัว*

>
