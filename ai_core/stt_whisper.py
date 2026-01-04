import whisper
import numpy as np

model = whisper.load_model("base")

def transcribe_audio(audio_path: str):
    result = model.transcribe(audio_path, word_timestamps=True)

    text = result["text"]

    words = []
    for seg in result["segments"]:
        for w in seg.get("words", []):
            words.append(w)

    # ---- Measurements ----
    duration = words[-1]["end"] - words[0]["start"] if words else 1
    words_per_second = len(words) / max(duration, 1)

    pauses = []
    for i in range(1, len(words)):
        gap = words[i]["start"] - words[i-1]["end"]
        pauses.append(gap)

    average_pause_ms = int(np.mean(pauses) * 1000) if pauses else 0

    return {
        "text": text,
        "words_per_second": words_per_second,
        "average_pause_ms": average_pause_ms,
    }
