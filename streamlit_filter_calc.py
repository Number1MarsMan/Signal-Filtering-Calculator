# app.py - Streamlit version of the RL/RC Filter Calculator
import math
import streamlit as st

TAU = 2 * math.pi

E12_BASE = [1.0, 1.2, 1.5, 1.8, 2.2, 2.7, 3.3, 3.9, 4.7, 5.6, 6.8, 8.2]

def e12_values(min_val, max_val):
    vals = []
    for decade in range(-12, 13):
        mult = 10 ** decade
        for b in E12_BASE:
            v = b * mult
            if min_val <= v <= max_val:
                vals.append(v)
    return vals

def top_n(arr, n, key):
    return sorted(arr, key=key)[:n]

# --- RL ---
def solve_rl(R=None, L=None, f=None):
    if sum(x is not None for x in [R, L, f]) < 2:
        return None, "Need 2 values"
    try:
        if R is None:
            return {"R": f * TAU * L}, None
        if L is None:
            return {"L": R / (TAU * f)}, None
        if f is None:
            return {"f": R / (TAU * L)}, None
    except:
        return None, "Calc error"
    return None, "Invalid combo"

# --- RC ---
def solve_rc(R=None, C=None, f=None):
    if sum(x is not None for x in [R, C, f]) < 2:
        return None, "Need 2 values"
    try:
        if R is None:
            return {"R": 1 / (TAU * C * f)}, None
        if C is None:
            return {"C": 1 / (TAU * R * f)}, None
        if f is None:
            return {"f": 1 / (TAU * R * C)}, None
    except:
        return None, "Calc error"
    return None, "Invalid combo"

# --- Suggestions ---
def suggest_rl(f_target):
    Rvals = e12_values(10, 1e6)
    Lvals = e12_values(1e-6, 0.1)
    combos = []
    for R in Rvals:
        for L in Lvals:
            fc = R / (TAU * L)
            err = abs(fc - f_target) / f_target
            combos.append({"R": R, "L": L, "fc": fc, "err": err})
    return top_n(combos, 5, key=lambda c: c["err"])

def suggest_rc(f_target):
    Rvals = e12_values(10, 1e6)
    Cvals = e12_values(1e-12, 1e-4)
    combos = []
    for R in Rvals:
        for C in Cvals:
            fc = 1 / (TAU * R * C)
            err = abs(fc - f_target) / f_target
            combos.append({"R": R, "C": C, "fc": fc, "err": err})
    return top_n(combos, 5, key=lambda c: c["err"])

# --- UI ---
st.title("RL / RC Filter Cutoff Calculator")
mode = st.radio("Select circuit type", ["RL", "RC"])

if mode == "RL":
    st.header("RL Calculator")
    R = st.number_input("Resistance R (Ω)", value=0.0)
    L = st.number_input("Inductance L (H)", value=0.0)
    f = st.number_input("Cutoff Frequency f (Hz)", value=0.0)
    R = None if R == 0 else R
    L = None if L == 0 else L
    f = None if f == 0 else f
    result, err = solve_rl(R, L, f)
    st.write(result if result else err)

    st.subheader("RL suggestions from target f_c")
    f_target = st.number_input("Target f_c (Hz)", value=1000.0)
    if f_target > 0:
        st.table(suggest_rl(f_target))

else:
    st.header("RC Calculator")
    R = st.number_input("Resistance R (Ω)", value=0.0)
    C = st.number_input("Capacitance C (F)", value=0.0)
    f = st.number_input("Cutoff Frequency f (Hz)", value=0.0)
    R = None if R == 0 else R
    C = None if C == 0 else C
    f = None if f == 0 else f
    result, err = solve_rc(R, C, f)
    st.write(result if result else err)

    st.subheader("RC suggestions from target f_c")
    f_target = st.number_input("Target f_c (Hz)", value=1000.0)
    if f_target > 0:
        st.table(suggest_rc(f_target))
