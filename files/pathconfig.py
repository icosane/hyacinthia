import sys,os
from ctranslate2 import get_cuda_device_count

base_dir, res_dir = (os.path.dirname(sys.executable), sys.prefix) if getattr(sys, 'frozen', False) else (os.path.dirname(os.path.abspath(__file__)), os.path.dirname(os.path.abspath(__file__)))

voices_dir = os.path.join(base_dir, "voices")

def get_lib_paths():
    if getattr(sys, 'frozen', False):  # Running inside PyInstaller
        base_dir = os.path.join(sys.prefix)
    else:  # Running inside a virtual environment
        base_dir = os.path.join(sys.prefix, "Lib", "site-packages")

    nvidia_base_libs = os.path.join(base_dir, "nvidia")

    if sys.platform == "win32":
        cuda_runtime = os.path.join(nvidia_base_libs, "cuda_runtime", "bin")
        cublas = os.path.join(nvidia_base_libs, "cublas", "bin")
        cudnn = os.path.join(nvidia_base_libs, "cudnn", "bin")
    else:
        cuda_runtime = os.path.join(nvidia_base_libs, "cuda_runtime", "lib")
        cublas = os.path.join(nvidia_base_libs, "cublas", "lib")
        cudnn = os.path.join(nvidia_base_libs, "cudnn", "lib")

    return [cuda_runtime, cublas, cudnn]

def initialize():
    if get_cuda_device_count() != 0:
        for dll_path in get_lib_paths():
            if os.path.exists(dll_path):
                os.environ["PATH"] = dll_path + os.pathsep + os.environ["PATH"]
