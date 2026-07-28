#!/usr/bin/python3
"""
Write the neighbour-weighted descriptors back to the SQLite database.

    q_qtaim_w                   = Σ exp(-α·d_i)·q_qtaim_i        (sum over the
    condensed_linear_response_w = Σ exp(-β·d_i)·clr_i            molecule's atoms)

where d_i is the distance of atom i to the analysed atom (d_0 = 0, so the
analysed atom contributes its full charge).

Matching .pout entries to database rows
---------------------------------------
The old version matched by (experimental_N, experimental_Sn) only and then
UPDATEd by (smiles, solvent) — which is wrong for the molecules that expose two
analysed atoms under the same (smiles, solvent) and for the (N, Sn) pairs that
collide across different SMILES.  Both atoms ended up with the same value and a
few rows were left NULL.

The robust key (same idea as opt5.py `fetch_eigenchi`) is
(experimental_N, experimental_Sn) **plus the analysed-atom q_qtaim as a
tie-breaker**.  The analysed atom is the first atom in every .pout block
(distance 0.0); its q_qtaim equals the value stored in the table's `q_qtaim`
column, so matching on it uniquely identifies the row — including multi-site
molecules.  Assignment is greedy/unique so two atoms of the same molecule each
claim their own row.

`reactive`  : 244 .pout blocks ↔ 244 rows, matched on (N, Sn, q) — exact.
`no_reactive`: the .pout carries placeholder `0 0` keys and only covers part of
              the table, so rows are matched on analysed-atom q_qtaim alone via
              a global nearest-neighbour (greedy bipartite) assignment.  Nothing
              that reads the DB consumes no_reactive.q_qtaim_w today, so this is
              best-effort completeness; coverage is reported below.
"""
import sqlite3
import numpy as np

DB_PATH = '/Users/vcastor/Documents/PhD_Rouen/plamsfilter/db_nucleo/nucleo_data.db'

ALPHA = 1.0   # decay for q_qtaim_w
BETA  = 1.0   # decay for condensed_linear_response_w

# ---------------------------------------------------------------------------
# .pout readers (block layout identical to opt5.py)
# ---------------------------------------------------------------------------
def read_react(filename):
    data = {"expN": [], "expSn": [], "distances": [], "q_qtaim": [], "clr": []}
    with open(filename) as f:
        lines = f.readlines()
    i = 0
    while i < len(lines):
        i += 1                                                   # natoms
        expN, expSn = map(float, lines[i].split()); i += 1
        data["expN"].append(expN); data["expSn"].append(expSn)
        data["distances"].append(list(map(float, lines[i].split()))); i += 1
        data["q_qtaim"].append(list(map(float, lines[i].split()))); i += 1
        data["clr"].append(list(map(float, lines[i].split()))); i += 1
        i += 2                                                   # esp + extra prop
        i += 1                                                   # electrofuge
    return data


def read_noreact(filename):
    data = {"distances": [], "q_qtaim": [], "clr": []}
    with open(filename) as f:
        lines = f.readlines()
    i = 0
    while i < len(lines):
        i += 2                                                   # natoms, "0 0"
        data["distances"].append(list(map(float, lines[i].split()))); i += 1
        data["q_qtaim"].append(list(map(float, lines[i].split()))); i += 1
        data["clr"].append(list(map(float, lines[i].split()))); i += 1
    return data


# ---------------------------------------------------------------------------
# Weighted descriptors
# ---------------------------------------------------------------------------
def weighted(distances, values, decay):
    d = np.asarray(distances)
    v = np.asarray(values)
    return float(np.sum(np.exp(-decay * d) * v))


def compute(data):
    """Return per-entry (q_w, clr_w, q_analysed)."""
    out = []
    for d, q, clr in zip(data["distances"], data["q_qtaim"], data["clr"]):
        out.append((weighted(d, q, ALPHA), weighted(d, clr, BETA), q[0]))
    return out


# ---------------------------------------------------------------------------
# reactive: robust (N, Sn, q) match, greedy-unique
# ---------------------------------------------------------------------------
def write_reactive(cur):
    data = read_react('reactive.pout')
    feats = compute(data)

    cur.execute("""
        SELECT t.smiles, t.solvent, t.atom_analysed, t.q_qtaim,
               p.experimental_N, p.experimental_Sn
        FROM reactive t
        JOIN parameters p
          ON t.smiles = p.smiles
         AND t.solvent = p.solvent
         AND t.atom_analysed = p.atom_analysed
        WHERE p.table_name = 'reactive'
    """)
    rows = cur.fetchall()   # (smiles, solvent, atom, q_db, eN, eSn)

    claimed = set()
    written = 0
    unmatched = []
    for i, (q_w, clr_w, q_analysed) in enumerate(feats):
        expN, expSn = data["expN"][i], data["expSn"][i]
        candidates = [
            r for j, r in enumerate(rows)
            if j not in claimed
            and abs(r[4] - expN) < 1e-6 and abs(r[5] - expSn) < 1e-6
        ]
        if not candidates:
            unmatched.append((expN, expSn, q_analysed))
            continue
        best = min(candidates, key=lambda r: abs(r[3] - q_analysed))
        claimed.add(rows.index(best))
        cur.execute(
            "UPDATE reactive SET q_qtaim_w = ?, condensed_linear_response_w = ? "
            "WHERE smiles = ? AND solvent = ? AND atom_analysed = ?",
            (q_w, clr_w, best[0], best[1], best[2]),
        )
        written += 1

    print(f"reactive: {written}/{len(feats)} .pout entries written, "
          f"{len(rows)} DB rows joined")
    if unmatched:
        print(f"  unmatched .pout entries ({len(unmatched)}): {unmatched}")


# ---------------------------------------------------------------------------
# no_reactive: nearest-q greedy bipartite (best-effort, placeholder keys)
# ---------------------------------------------------------------------------
def write_no_reactive(cur):
    data = read_noreact('no_reactive.pout')
    feats = compute(data)

    cur.execute("SELECT rowid, q_qtaim FROM no_reactive WHERE q_qtaim IS NOT NULL")
    rows = cur.fetchall()   # (rowid, q_db)

    # all (pout_i, row_j, |Δq|) pairs, assign closest first, one-to-one
    pairs = []
    for i, (_, _, q_analysed) in enumerate(feats):
        for j, (rowid, q_db) in enumerate(rows):
            pairs.append((abs(q_db - q_analysed), i, j, rowid))
    pairs.sort()

    used_pout, used_row = set(), set()
    written, max_dq = 0, 0.0
    for dq, i, j, rowid in pairs:
        if i in used_pout or j in used_row:
            continue
        used_pout.add(i); used_row.add(j)
        q_w, clr_w, _ = feats[i]
        cur.execute(
            "UPDATE no_reactive SET q_qtaim_w = ?, condensed_linear_response_w = ? "
            "WHERE rowid = ?",
            (q_w, clr_w, rowid),
        )
        written += 1
        max_dq = max(max_dq, dq)

    print(f"no_reactive: {written}/{len(feats)} .pout entries matched "
          f"(table has {len(rows)} rows), worst |Δq| = {max_dq:.4f}")


# ---------------------------------------------------------------------------
if __name__ == "__main__":
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    write_reactive(cur)
    write_no_reactive(cur)
    conn.commit()
    conn.close()
    print("done.")
