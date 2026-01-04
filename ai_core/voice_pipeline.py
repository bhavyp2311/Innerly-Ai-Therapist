from stt_whisper import transcribe_audio
from audio_features import extract_audio_volume
from voice_extractor import extract_voice_signals
from voice_to_stage import decide_stage_from_voice

def process_voice_input(audio_path: str):
    stt = transcribe_audio(audio_path)
    volume_db = extract_audio_volume(audio_path)

    signals = extract_voice_signals(
        transcript=stt["text"],
        words_per_second=stt["words_per_second"],
        average_pause_ms=stt["average_pause_ms"],
        avg_volume_db=volume_db,
        sigh_count=0,              # optional
        cut_sentence_ratio=0.0     # optional
    )

    stage = decide_stage_from_voice(signals)

    return {
        "transcript": stt["text"],
        "voice_signals": signals,
        "stage": stage
    }
