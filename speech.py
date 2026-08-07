from faster_whisper import WhisperModel


# Load the model only once when this module is used.
model = WhisperModel(
    "base",
    device="cpu",
    compute_type="int8"
)


def transcribe_audio(audio_path: str) -> str:
    """
    Transcribe an audio file using Faster Whisper.
    """

    segments, info = model.transcribe(
        audio_path,
        beam_size=5
    )

    transcription = " ".join(
        segment.text.strip()
        for segment in segments
    ).strip()

    return transcription