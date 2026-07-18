# BioDC Web — a newcomer-friendly front-end (proof of concept)

A clean, **accessible** web page that runs the **real** BioDC calculation underneath —
showing what a newcomer could see instead of the command-line tool.

## Setup for a newcomer (two commands)

**Prerequisites:** `git`, Python 3.10–3.13, and an internet connection.

```bash
git clone <this-repo-url>
cd BioDC/webapp
./setup.sh      # creates the environment and installs everything (one time)
./run.sh        # starts the app
```

Then open **http://localhost:8000** in your browser. That's it — no manual `pip`,
no `PYTHONPATH`, no hunting for dependencies. Structures are downloaded from the
Protein Data Bank automatically as you use them.

## What it shows a newcomer
- No terminal prompts — a form + a 3D viewer.
- Pick any structure by PDB ID (e.g. `6NEF`, `7LQ5`, `1M1P`), see it in 3D.
- **🔍 Find** auto-detects the hemes (no need to know residue numbers).
- The real result (electron diffusion coefficient) in plain language.
- Viewer controls: zoom, reset, spin, save PNG, fullscreen.
- Accessible-first: labelled fields, live-region status, keyboard usable —
  works for sighted newcomers **and** for a blind user.

## Architecture (the pattern we'd bring to ProPrep)

```
BioDC science (unchanged)  ->  core.py (thin wrapper: returns data, no prompts)
                                   |
                                   v
                               main.py (FastAPI: exposes it over HTTP)
                                   |
                                   v
                            index.html (accessible web UI + NGL 3D viewer)
```

## Files
- `core.py`         — decoupled wrapper around BioDC (science → data, works on any PDB ID).
- `main.py`         — FastAPI app (the thin API layer). No science inside.
- `index.html`      — the accessible front-end + NGL 3D viewer.
- `requirements.txt`— all Python dependencies.
- `setup.sh`        — one-command environment setup.
- `run.sh`          — start the app.

## Notes
- This wraps BioDC's pure-Python calculator, so it needs no AMBER/VMD.
- The calculation is meaningful for **multi-heme cytochrome wires** (6NEF, 6EF8,
  7LQ5, 7TFS, 8D9M, 8E5F, 1M1P). Other structures still display and detect, but the
  "wire" number only applies to heme chains.
