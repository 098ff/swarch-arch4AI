"""Generate the synthetic CampusEats review dataset (train.csv, test.csv).

The reviews are template-based and deterministic (fixed seed), so every student
gets the same data. Negations ("not bad at all"), contrasts ("... but ..."),
some sarcasm and about 4% label noise are included on purpose: a small
bag-of-words model gets many of them wrong, a larger model that sees word
pairs gets most of them right. That gap is what makes the cascade in Task 2
interesting.

Run:  python data/make_data.py
"""
import csv
import random
from pathlib import Path

SEED = 521
HERE = Path(__file__).parent

DISHES = ["pad thai", "green curry", "fried rice", "noodle soup", "som tam", "khao man gai",
          "basil pork", "mango sticky rice", "burger", "pizza", "bubble tea", "salad",
          "omelette rice", "tom yum", "dumplings", "fried chicken"]
POS = ["delicious", "tasty", "great", "excellent", "amazing", "fresh", "perfect", "lovely", "good"]
NEG = ["bland", "awful", "terrible", "cold", "soggy", "disgusting", "stale", "bad", "greasy"]
POS_DELIVERY = ["arrived early", "came fast", "was on time", "was quick"]
NEG_DELIVERY = ["arrived late", "took forever", "was an hour late", "never showed up on time"]
POS_SERVICE = ["the rider was polite", "the staff were friendly", "packaging was neat"]
NEG_SERVICE = ["the rider was rude", "the staff ignored us", "the sauce leaked everywhere"]

# Short reviews that many users write word for word. They make caching useful.
FREQUENT = [("Delicious!", "positive"), ("Too salty", "negative"), ("Late again", "negative"),
            ("Will order again", "positive"), ("Not worth the price", "negative"),
            ("Best in the canteen", "positive"), ("Cold food", "negative"), ("Yummy", "positive")]


def easy(r):
    label = r.choice(["positive", "negative"])
    adj = r.choice(POS if label == "positive" else NEG)
    dish = r.choice(DISHES)
    extra = r.choice(POS_DELIVERY + POS_SERVICE if label == "positive" else NEG_DELIVERY + NEG_SERVICE)
    forms = [f"The {dish} was {adj}.", f"{adj.capitalize()} {dish}, {extra}.",
             f"Really {adj} {dish}. {extra.capitalize()}."]
    return r.choice(forms), label


def negation(r):
    # "not <positive word>" is negative; "not <negative word>" is positive
    label = r.choice(["positive", "negative"])
    adj = r.choice(NEG if label == "positive" else POS)
    dish = r.choice(DISHES)
    forms = [f"The {dish} was not {adj} at all.", f"Honestly the {dish} is not {adj}.",
             f"Not {adj}, the {dish} I mean."]
    return r.choice(forms), label


def contrast(r):
    # the clause after "but" decides the label
    label = r.choice(["positive", "negative"])
    first = r.choice(NEG if label == "positive" else POS)
    second = r.choice(POS if label == "positive" else NEG)
    dish = r.choice(DISHES)
    return f"The {dish} looked {first} but it tasted {second}.", label


def sarcasm(r):
    # positive words, negative meaning: hard for every model
    dish = r.choice(DISHES)
    forms = [f"Great, the {dish} was {r.choice(NEG)} again.", f"Wow, {r.choice(NEG_DELIVERY)}. Amazing service.",
             f"Just perfect, {r.choice(NEG_SERVICE)}."]
    return r.choice(forms), "negative"


def review(r):
    kind = r.random()
    if kind < 0.55:
        text, label = easy(r)
    elif kind < 0.77:
        text, label = negation(r)
    elif kind < 0.93:
        text, label = contrast(r)
    else:
        text, label = sarcasm(r)
    # about 4% of human labels disagree with the text, as in real annotated data
    if r.random() < 0.04:
        label = "positive" if label == "negative" else "negative"
    return text, label


def write(path, rows):
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["text", "label"])
        w.writerows(rows)


def main():
    r = random.Random(SEED)
    train = [review(r) for _ in range(3000)] + FREQUENT * 5
    test = [review(r) for _ in range(500)]
    write(HERE / "train.csv", train)
    write(HERE / "test.csv", test)
    print(f"train.csv: {len(train)} rows, test.csv: {len(test)} rows")


if __name__ == "__main__":
    main()
