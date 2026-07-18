"""
main.py — the thin FastAPI layer. No science inside; it just calls core.py.

Every endpoint is driven by a PDB ID, so nothing is hardcoded to 6NEF.

Run with:
    cd ~/developer/BioDC/webapp
    source ../.venv/bin/activate
    uvicorn main:app --reload --port 8000
Then open http://localhost:8000
"""
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from pydantic import BaseModel

import core

app = FastAPI(title="BioDC Web — newcomer demo")
BASE = Path(__file__).resolve().parent


class ComputeRequest(BaseModel):
    pdbid: str = "6NEF"
    seq: str = "STSTST"
    seqids: str = "501,502,503,504,505,506"
    num_sets: int = 2000


@app.get("/", response_class=HTMLResponse)
def index():
    return (BASE / "index.html").read_text()


@app.post("/api/compute")
def compute(req: ComputeRequest):
    try:
        return JSONResponse(core.compute_diffusion(
            pdbid=req.pdbid, seq=req.seq, seqids=req.seqids, num_sets=req.num_sets,
        ))
    except Exception as e:
        return JSONResponse({"ok": False, "error": str(e)})


@app.get("/api/hemes")
def hemes(pdbid: str = "6NEF"):
    try:
        data = core.find_hemes(pdbid)
    except Exception:
        return JSONResponse({"ok": False, "error": f"Could not fetch '{pdbid}'."})
    data["ok"] = data["count"] > 0
    data["seqids"] = ",".join(str(r) for r in data["resids"])
    data["pdbid"] = pdbid.upper()
    return JSONResponse(data)


@app.get("/api/structure")
def structure(pdbid: str = "6NEF"):
    """Serve the chosen structure so the 3D viewer can load it."""
    try:
        path = core.structure_path(pdbid)
    except Exception:
        return JSONResponse({"ok": False, "error": f"Could not fetch '{pdbid}'."}, status_code=404)
    return FileResponse(str(path), media_type="chemical/x-pdb", filename=f"{pdbid.upper()}.pdb")
