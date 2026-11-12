from pathlib import Path
from tempfile import TemporaryDirectory
import shutil
import subprocess
import uuid

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse, HTMLResponse
from starlette.background import BackgroundTask
from fastapi.middleware.cors import CORSMiddleware
import music21

BASE_DIR = Path(__file__).resolve().parent
MAX_UPLOAD_BYTES = 15 * 1024 * 1024

app = FastAPI(title="Transcriptor Musical OMR", version="3.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restringir al dominio de la app antes de uso público.
    allow_methods=["GET", "POST"],
    allow_headers=["*"]
)

# Semitonos de instrumento escrito respecto al sonido real.
INSTRUMENTS = {
    "oboe": 0, "flute": 0, "trombone": 0, "piano": 0,
    "trumpet": -2, "clarinet": -2, "soprano": -2,
    "tenor": -14, "alto": -9,
}

@app.get("/", response_class=HTMLResponse)
def home():
    page = BASE_DIR / "app.html"
    if not page.exists():
        raise HTTPException(404, "No se encontró la interfaz app.html")
    return page.read_text(encoding="utf-8")

@app.get("/api/health")
def health():
    return {"ok": True, "audiveris": shutil.which("audiveris") is not None}

@app.post("/api/transpose")
async def transpose_score(
    file: UploadFile = File(...),
    source: str = Form(...),
    target: str = Form(...)
):
    if source not in INSTRUMENTS or target not in INSTRUMENTS:
        raise HTTPException(400, "Instrumento no reconocido.")

    suffix = Path(file.filename or "").suffix.lower()
    if suffix not in {".pdf", ".png", ".jpg", ".jpeg"}:
        raise HTTPException(400, "Usa un archivo PDF, PNG o JPG.")

    if not shutil.which("audiveris"):
        raise HTTPException(503, "El motor Audiveris no está disponible en el servidor.")

    try:
        content = await file.read(MAX_UPLOAD_BYTES + 1)
        if len(content) > MAX_UPLOAD_BYTES:
            raise HTTPException(413, "El archivo supera el límite de 15 MB.")

        with TemporaryDirectory(prefix="transcriptor-") as tmp:
            tmpdir = Path(tmp)
            input_path = tmpdir / ("entrada" + suffix)
            input_path.write_bytes(content)
            output_dir = tmpdir / "omr"
            output_dir.mkdir()

            cmd = [
                "audiveris", "-batch", "-export", "-output", str(output_dir),
                "--", str(input_path)
            ]
            proc = subprocess.run(
                cmd, capture_output=True, text=True, timeout=240
            )
            candidates = (
                list(output_dir.rglob("*.mxl"))
                + list(output_dir.rglob("*.musicxml"))
                + list(output_dir.rglob("*.xml"))
            )
            if proc.returncode != 0 or not candidates:
                detail = (proc.stderr or proc.stdout or "Audiveris no produjo MusicXML.")[-1500:]
                raise HTTPException(422, "No se pudo reconocer la partitura: " + detail)

            score = music21.converter.parse(str(candidates[0]))
            semitones = INSTRUMENTS[source] - INSTRUMENTS[target]
            if semitones:
                score = score.transpose(semitones)

            result_path = tmpdir / "partitura_convertida.musicxml"
            score.write("musicxml", fp=str(result_path))

            # Copia temporal fuera del contexto que se limpia al salir de TemporaryDirectory.
            persistent_dir = Path("/tmp/transcriptor-musical")
            persistent_dir.mkdir(parents=True, exist_ok=True)
            final_path = persistent_dir / f"resultado_{uuid.uuid4().hex}.musicxml"
            shutil.copy2(result_path, final_path)

        return FileResponse(
            final_path,
            filename="partitura_convertida.musicxml",
            media_type="application/vnd.recordare.musicxml+xml",
            background=BackgroundTask(lambda: final_path.unlink(missing_ok=True)),
        )
    except HTTPException:
        raise
    except subprocess.TimeoutExpired:
        raise HTTPException(408, "El reconocimiento tardó demasiado. Prueba con menos páginas.")
    except Exception as exc:
        raise HTTPException(500, f"Error al convertir la partitura: {exc}")
