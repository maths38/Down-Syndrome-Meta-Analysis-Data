import re
from collections import defaultdict

# --------------------------------------------------
# Read one probability file
# --------------------------------------------------

def read_probabilities(filename):
    probs = {}

    with open(filename, "r") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue

            m = re.match(r"P\((.*)\)\s*=\s*([0-9.eE+-]+)", line)
            if not m:
                continue

            expr = m.group(1).strip()
            value = float(m.group(2))

            atoms = [x.strip() for x in expr.split("&")]
            key = " & ".join(sorted(atoms))

            probs[key] = value

    return probs


# --------------------------------------------------
# Helper functions
# --------------------------------------------------

def canon(*events):
    return " & ".join(sorted(events))


def P(probs, *events):
    return probs[canon(*events)]


def cond(probs, A_events, B_events):
    num = P(probs, *(list(A_events) + list(B_events)))
    den = P(probs, *B_events)
    return num / den


def sensitivity(p_x, p_down_given_x, p_down_given_not_x):
    num = p_x * p_down_given_x
    den = num + (1 - p_x) * p_down_given_not_x
    return num / den


def specificity(p_x, p_down_given_x, p_down_given_not_x):
    num = (1 - p_x) * (1 - p_down_given_not_x)
    den = num + p_x * (1 - p_down_given_x)
    return num / den


def fmt(x):
    return f"{100*x:.4f}"


# --------------------------------------------------
# Settings
# --------------------------------------------------

tests = ["NIPT", "COMB", "FTSS"]

conditions = [
    (),
    ("AGE",),
    ("TWIN",),
    ("AGE", "TWIN")
]

# --------------------------------------------------
# Collect results from all files
# --------------------------------------------------

results = defaultdict(list)

for i in range(25):

    filename = f"Reliability/probabilities{i}.txt"
    probs = read_probabilities(filename)

    for X in tests:

        for conds in conditions:

            cond_label = "None" if not conds else " & ".join(conds)

            px = cond(probs, (X,), conds) if conds else P(probs, X)

            pdx = cond(probs, ("DOWN",), (X,) + conds)

            pdnx = cond(probs, ("DOWN",), (f"NOT {X}",) + conds)

            sens = sensitivity(px, pdx, pdnx)
            spec = specificity(px, pdx, pdnx)

            key = (X, cond_label)

            results[(key, "P(X|C)")].append(px)
            results[(key, "P(NOT X|C)")].append(1 - px)
            results[(key, "P(DOWN|X,C)")].append(pdx)
            results[(key, "P(NOT DOWN|X,C)")].append(1 - pdx)
            results[(key, "P(DOWN|NOT X,C)")].append(pdnx)
            results[(key, "P(NOT DOWN|NOT X,C)")].append(1 - pdnx)
            results[(key, "Sensitivity")].append(sens)
            results[(key, "Specificity")].append(spec)

# --------------------------------------------------
# Print ranges
# --------------------------------------------------

for X in tests:

    print("\n" + "=" * 20)
    print(X)
    print("=" * 20)

    for conds in conditions:

        cond_label = "None" if not conds else " & ".join(conds)
        key = (X, cond_label)

        print(f"\nConditions: {cond_label}")

        for quantity in [
            "P(X|C)",
            "P(NOT X|C)",
            "P(DOWN|X,C)",
            "P(NOT DOWN|X,C)",
            "P(DOWN|NOT X,C)",
            "P(NOT DOWN|NOT X,C)",
            "Sensitivity",
            "Specificity",
        ]:

            values = results[(key, quantity)]

            print(
                f"{quantity:24s}: "
                f"[{fmt(min(values))}, {fmt(max(values))}]"
            )