# How to Run BioDC — a step-by-step guide (that actually produced output)

This is the exact, tested path I used to get a **real scientific result** out of BioDC on your Mac,
written so you can reproduce it yourself. Every step is a copy-paste command.

**What we computed:** the electron "diffusion coefficient" (D) of a real 6-heme *Geobacter*
cytochrome nanowire — i.e. *how well electrons move through the protein wire*. This is the
kind of number BioDC exists to produce, and it needs **no AMBER or VMD** (see the two paths below).

---

## Background: BioDC has two ways to run

1. **The full interactive pipeline** (`BioDCv2.py`) — a text menu that prepares a protein and
   simulates it. **Needs VMD + AMBER installed** (heavy; VMD needs a manual registered download).
   We can start it and see the menu, but it stops when it needs those engines.

2. **The direct physics calculators** (single Python scripts in `Modules/`) — pure Python, **no
   AMBER/VMD needed**. This is the shortcut we used to get a real answer today
   (`ParameterExploration.py`).

---

## One-time setup

### 1. The code is already here
```bash
cd ~/developer/BioDC
```
(If it were missing: `git clone https://github.com/Mag14011/BioDC.git ~/developer/BioDC`)

### 2. Python environment (already created)
The lab's science libraries don't support your system Python 3.14 yet, so we use **Python 3.11**
in an isolated "virtual environment" (venv). It's already built at `~/developer/BioDC/.venv`.

To recreate it from scratch if ever needed:
```bash
cd ~/developer/BioDC
python3.11 -m venv .venv
source .venv/bin/activate
pip install numpy pandas scikit-learn matplotlib networkx tabulate scipy pdb-tools
```

### 3. Get a real protein structure to test with
`pdb_fetch` downloads a structure from the public Protein Data Bank. 6NEF is a *Geobacter*
cytochrome nanowire (Matthew's field):
```bash
cd ~/developer/BioDC/V2.2
source ../.venv/bin/activate
pdb_fetch 6NEF > 6NEF.pdb
```

**Gotcha (a real bug in their code):** `ParameterExploration.py`'s argument parser treats any value
containing the letter **e/E** as a number — and "6N**E**F" has an E, so it crashes on the filename.
Workaround: copy it to a name with no "e":
```bash
cp 6NEF.pdb mhc6.pdb          # 'mhc6' = multi-heme-cytochrome, no 'e'
```
Find the heme groups (needed for the command below): they are residues **501–506**:
```bash
grep ' FE ' mhc6.pdb | awk '{print $4, $6}' | sort -u   # shows HEC 501..506
```

---

## Run it and get the answer

```bash
cd ~/developer/BioDC/V2.2/Modules
source ../../.venv/bin/activate

python ParameterExploration.py \
  num_tot=6 num_s=3 num_t=3 seq=STSTST \
  num_sets=2000 free_eng_opt=false \
  pdbname=../mhc6.pdb seqids=501,502,503,504,505,506 \
  num_processes=2
```

### What each argument means
| Argument | Meaning |
|---|---|
| `num_tot=6` | 6 hemes in the wire |
| `num_s=3 num_t=3` | 3 "S-type" + 3 "T-type" hemes (they use different coupling ranges) |
| `seq=STSTST` | the order of S/T hemes along the wire (must contain 3 S + 3 T) |
| `num_sets=2000` | how many random parameter sets to try (bigger = slower, more thorough) |
| `free_eng_opt=false` | let it also randomize the free-energy term |
| `pdbname=../mhc6.pdb` | the structure file (e-free name!) |
| `seqids=501,...,506` | the residue numbers of the hemes, in order |
| `num_processes=2` | run on 2 CPU cores |

### What you'll see (real output we got)
```
Average heme spacing: 5.14 Å
...
Accepted sets: 2,000
Acceptance rate: 100.00%
  Index  V1(S) ... D
      1  4.978 ... 0.000128
      2 12.026 ... 8.77e-05
```
- **`Average heme spacing: 5.14 Å`** — measured from the real structure.
- The big table: each row is one trial set of physical parameters; the **last column `D`** is the
  **diffusion coefficient** (cm²/s) — higher = electrons flow better = a better "wire".
- Best result today: **D ≈ 1.3 × 10⁻⁴ cm²/s** (rank 1).
- Results are also saved to a file: **`STSTST_<date>.txt`**.

---

## Bonus: the simplest possible real run (one command, no setup args)

`derrida.py` is a self-contained calculator with a built-in demo. It computes drift velocity + a
diffusion constant for a hopping chain:
```bash
cd ~/developer/BioDC/V2.2/Modules
source ../../.venv/bin/activate
python derrida.py
# prints e.g. (V, D) tuples
```

---

## Seeing the interactive pipeline (menu only)

To watch the guided text interface (it will stop at the VMD/AMBER check):
```bash
~/developer/BioDC/run_biodc.sh
# choose 1  -> yes -> 6NEF -> keep answering...
```

To go past that check you'd need to install **AmberTools** (free, via miniforge) and **VMD**
(free, manual registered download). Not required for the calculators above.

---

## Quick reference — trouble I hit and how I fixed it
1. **`ModuleNotFoundError: numpy`** → system Python had no science libs → used the 3.11 venv.
2. **`No module named tabulate` / `scipy`** → `pip install tabulate scipy` in the venv.
3. **`could not convert string to float: '../6NEF.pdb'`** → filename contained "E" → renamed to `mhc6.pdb`.
4. **`EOFError: EOF when reading a line`** (interactive run) → not a bug; it just ran out of piped
   answers. Type answers live in your terminal instead.
</content>
