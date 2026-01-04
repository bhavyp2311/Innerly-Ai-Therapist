import numpy as np
import soundfile as sf

def extract_audio_volume(audio_path: str):
    audio, sr = sf.read(audio_path)

    # RMS volume (convert to dB)
    rms = np.sqrt(np.mean(audio ** 2))
    avg_volume_db = 20 * np.log10(rms + 1e-6)

    return avg_volume_db
