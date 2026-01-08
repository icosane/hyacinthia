import os
import soundfile as sf
from f5_tts.infer.utils_infer import infer_process, load_model, load_vocoder
from faster_whisper import WhisperModel
from f5_tts.model import DiT
from omogre import Accentuator
from .pathconfig import tts_dir, vocoder_dir
from .config import cfg
from ctranslate2 import get_cuda_device_count

accentuator = Accentuator(data_path='./files/models/omogre',
                          download=False,
                          device_name='cuda')

WHISPER_MODEL_SIZE = cfg.get(cfg.whisper_model).value
WHISPER_DEVICE = "cuda" if get_cuda_device_count() != 0 else "cpu"
WHISPER_COMPUTE_TYPE = "float16"      # "int8" works on very low‑VRAM GPUs
DOWNLOAD_ROOT="./files/models/whisper"

whisper = WhisperModel(
    WHISPER_MODEL_SIZE,
    device=WHISPER_DEVICE,
    compute_type=WHISPER_COMPUTE_TYPE,
    download_root=DOWNLOAD_ROOT,
    local_files_only=True
)

vocoder_path= os.path.join(vocoder_dir)
vocoder = load_vocoder(device="cuda", is_local=True, local_path=vocoder_dir)
ckpt_path = os.path.join(tts_dir, "model_last_inference.safetensors")
vocab_path = os.path.join(tts_dir, "vocab.txt")
model_cfg = dict(dim=1024, depth=22, heads=16, ff_mult=2,
                 text_dim=512, conv_layers=4)

model_obj = load_model(DiT, model_cfg, ckpt_path, vocab_file=vocab_path)

def whisper_transcribe(ref_audio: str) -> str:
    segments, info = whisper.transcribe(
        ref_audio,
    )
    full_text = " ".join([seg.text for seg in segments])
    return " ".join(full_text.strip().split())


def process_text(text: str) -> str:
    sentences = text.split('. ')
    accented = accentuator.accentuate(sentences)
    return '. '.join(accented) + "\n ......"


def generate(text: str, ref_file: str, out_format: str, out_path: str) -> str:

    gen_text = process_text(text)

    ref_text = whisper_transcribe(ref_audio=ref_file)

    wav, sr, _ = infer_process(
        ref_file,
        ref_text,
        gen_text,
        model_obj,
        vocoder,
        cross_fade_duration=0.15,
        nfe_step=64,
        speed=1,
        device="cuda"
    )

    sf.write(out_path, wav, sr, format=out_format)

    return out_path
