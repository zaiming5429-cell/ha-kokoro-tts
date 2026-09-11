import io, os, threading, uuid
from pathlib import Path
from typing import Optional
from fastapi import FastAPI, HTTPException
from fastapi.responses import Response, JSONResponse
from pydantic import BaseModel, Field

app = FastAPI(title='Personal Kokoro TTS API', version='0.1.0')
OUT_DIR = Path(os.getenv('TTS_OUTPUT_DIR', '/data/audio'))
OUT_DIR.mkdir(parents=True, exist_ok=True)
_lock = threading.Lock()
_pipeline = None

PERSONAS = {
    'assistant': {'voice': os.getenv('TTS_DEFAULT_VOICE', 'af_heart'), 'speed': 1.0},
    'announcer': {'voice': 'am_adam', 'speed': 0.92},
    'friendly': {'voice': 'af_bella', 'speed': 1.04},
}

class TTSRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=4000)
    persona: str = 'assistant'
    voice: Optional[str] = None
    speed: Optional[float] = Field(None, ge=0.5, le=2.0)
    save: bool = True


def get_pipeline():
    global _pipeline
    if _pipeline is None:
        try:
            from kokoro import KPipeline
            _pipeline = KPipeline(lang_code=os.getenv('KOKORO_LANG', 'a'))
        except Exception as exc:
            raise RuntimeError(f'Kokoro is not installed or failed to load: {exc}') from exc
    return _pipeline

@app.get('/health')
def health():
    return {'status': 'ok', 'model_loaded': _pipeline is not None, 'personas': list(PERSONAS)}

@app.get('/personas')
def personas():
    return PERSONAS

@app.post('/tts')
def tts(req: TTSRequest):
    if req.persona not in PERSONAS:
        raise HTTPException(400, f'unknown persona: {req.persona}')
    cfg = PERSONAS[req.persona]
    voice = req.voice or cfg['voice']
    speed = req.speed if req.speed is not None else cfg['speed']
    try:
        import soundfile as sf
        import numpy as np
        pipe = get_pipeline()
        chunks = []
        with _lock:
            for _, _, audio in pipe(req.text, voice=voice, speed=speed):
                chunks.append(np.asarray(audio))
        if not chunks:
            raise RuntimeError('Kokoro returned no audio')
        audio = np.concatenate(chunks)
        buf = io.BytesIO()
        sf.write(buf, audio, 24000, format='WAV', subtype='PCM_16')
        wav = buf.getvalue()
        result = {'id': str(uuid.uuid4()), 'persona': req.persona, 'voice': voice, 'sample_rate': 24000, 'bytes': len(wav)}
        if req.save:
            # A bind-mounted output directory can disappear while the container
            # is running. Recreate it before every persisted result.
            OUT_DIR.mkdir(parents=True, exist_ok=True)
            name = result['id'] + '.wav'
            (OUT_DIR / name).write_bytes(wav)
            result['file'] = f'/audio/{name}'
        return Response(content=wav, media_type='audio/wav', headers={'X-TTS-Metadata': JSONResponse(result).body.decode()})
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(503, str(exc))

from fastapi.staticfiles import StaticFiles
app.mount('/audio', StaticFiles(directory=OUT_DIR), name='audio')
