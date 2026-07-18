"""
core.py — a thin, decoupled wrapper around BioDC's real calculation + heme detection.

Works with ANY structure, chosen by PDB ID (not hardcoded to 6NEF). It downloads the
structure from the public Protein Data Bank on demand, detects its hemes, and runs
BioDC's calculation on it. This is the pattern we'd put on ProPrep: the science is
untouched; we just expose it as plain functions that take inputs and return data.
"""
import re
import sys
import subprocess
import urllib.request
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]     # ~/developer/BioDC
V2 = REPO / "V2.2"
MODULES = V2 / "Modules"

# Residue names that identify a heme group in a PDB file
HEME_RESNAMES = {"HEC", "HEM", "HEB", "HEA", "HEO", "DHE", "HDD", "1FH"}


def structure_path(pdbid: str) -> Path:
    """Local path to the structure; downloads it from the PDB the first time."""
    pid = pdbid.strip().upper()
    path = V2 / f"{pid}.pdb"
    if not path.exists():
        url = f"https://files.rcsb.org/download/{pid}.pdb"
        text = urllib.request.urlopen(url, timeout=30).read().decode("utf-8", "ignore")
        path.write_text(text)
    return path


def find_hemes_from_text(pdb_text: str) -> dict:
    """Scan PDB text and return the residue numbers of every heme group."""
    resids, seen, resname = [], set(), None
    for line in pdb_text.splitlines():
        if line.startswith(("ATOM", "HETATM")):
            rn = line[17:20].strip()
            if rn in HEME_RESNAMES:
                try:
                    rid = int(line[22:26])
                except ValueError:
                    continue
                if rid not in seen:
                    seen.add(rid)
                    resids.append(rid)
                    resname = resname or rn
    resids.sort()
    return {"resname": resname, "resids": resids, "count": len(resids)}


def find_hemes(pdbid: str) -> dict:
    """Auto-detect hemes in the given structure (downloads it if needed)."""
    return find_hemes_from_text(structure_path(pdbid).read_text())


def compute_diffusion(
    pdbid: str = "6NEF",
    seq: str = "STSTST",
    seqids: str = "501,502,503,504,505,506",
    num_sets: int = 2000,
    num_processes: int = 2,
    top: int = 10,
) -> dict:
    """Run BioDC's ParameterExploration on the chosen structure and return results."""
    path = structure_path(pdbid)
    seq = seq.strip().upper()
    num_s = seq.count("S")
    num_t = seq.count("T")
    num_tot = num_s + num_t

    cmd = [
        sys.executable, "ParameterExploration.py",
        f"num_tot={num_tot}", f"num_s={num_s}", f"num_t={num_t}", f"seq={seq}",
        f"num_sets={num_sets}", "free_eng_opt=false",
        f"pdbname=../{path.name}", f"seqids={seqids}", f"num_processes={num_processes}",
    ]
    proc = subprocess.run(cmd, cwd=str(MODULES), capture_output=True, text=True, timeout=180)
    out = (proc.stdout or "") + "\n" + (proc.stderr or "")

    spacing = None
    m = re.search(r"Average heme spacing:\s*([\d.]+)", out)
    if m:
        spacing = float(m.group(1))

    results = []
    for line in out.splitlines():
        parts = line.split()
        if len(parts) >= 10 and parts[0].isdigit():
            try:
                results.append({"rank": int(parts[0]), "D": float(parts[-1])})
            except ValueError:
                continue
    results = results[:top]

    ok = proc.returncode == 0 and spacing is not None and bool(results)
    return {
        "ok": ok,
        "pdbid": pdbid.upper(),
        "spacing_angstrom": spacing,
        "num_hemes": num_tot,
        "results": results,
        "best_D": results[0]["D"] if results else None,
        "error": None if ok else "No result — this structure may not be a multi-heme wire, "
                                 "or the heme numbers/pattern length don't match.",
    }


if __name__ == "__main__":
    import json
    print("hemes(6NEF):", json.dumps(find_hemes("6NEF")))
    print(json.dumps(compute_diffusion(num_sets=500), indent=2))
