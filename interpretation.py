import re

# --------------------------------------------------
# Read probability file
# --------------------------------------------------

probs = {}

with open("probabilities.txt", "r") as f:
    for line in f:
        line = line.strip()
        if not line:
            continue

        m = re.match(r"P\((.*)\)\s*=\s*([0-9.eE+-]+)", line)
        if not m:
            continue

        expr = m.group(1).strip()
        value = float(m.group(2))

        # store using canonical ordering
        atoms = [x.strip() for x in expr.split("&")]
        key = " & ".join(sorted(atoms))

        probs[key] = value


# --------------------------------------------------
# Helper functions
# --------------------------------------------------

def canon(*events):
    """
    Build canonical conjunction key.
    """
    return " & ".join(sorted(events))


def P(*events):
    """
    Return probability of conjunction.
    Example:
        P("DOWN")
        P("DOWN", "AGE")
        P("DOWN", "AGE", "TWIN")
    """
    return probs[canon(*events)]


def cond(A_events, B_events):
    """
    P(A | B) = P(A & B)/P(B)

    A_events, B_events are tuples/lists of literals.
    """
    num = P(*(list(A_events) + list(B_events)))
    den = P(*B_events)
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
    return f"{100*x:.6f}"

# --------------------------------------------------
# Requested calculations
# --------------------------------------------------

tests = ["NIPT", "COMB", "FTSS"]

conditions = [
    (),
    ("AGE",),
    ("TWIN",),
    ("AGE", "TWIN")
]

for X in tests:

    print(f"\n{'='*20}")
    print(X)
    print(f"{'='*20}")

    for conds in conditions:

        cond_label = "None" if not conds else " & ".join(conds)

        print(f"\nConditions: {cond_label}")

        # P(X | conditions)
        px = cond((X,), conds) if conds else P(X)

        # P(DOWN | X & conditions)
        pdx = cond(("DOWN",), (X,) + conds)

        # P(DOWN | NOT X & conditions)
        pdnx = cond(("DOWN",), (f"NOT {X}",) + conds)

        sens = sensitivity(px, pdx, pdnx)
        spec = specificity(px, pdx, pdnx)

        print(
            f"P(X|C)={fmt(px)}   "
            f"P(NOT X|C)={fmt(1-px)}"
        )

        print(
            f"P(DOWN|X,C)={fmt(pdx)}   "
            f"P(NOT DOWN|X,C)={fmt(1-pdx)}   "
            f"P(NOT DOWN|NOT X,C)={fmt(1-pdnx)}    "
            f"P(DOWN|NOT X,C)={fmt(pdnx)}"
        )

        print(
            f"Sensitivity={fmt(sens)}   "
            f"Specificity={fmt(spec)}"
        )