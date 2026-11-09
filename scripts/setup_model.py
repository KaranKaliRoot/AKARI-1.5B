#!/usr/bin/env python3
"""
AKARI model setup script.
Downloads Qwen2.5-1.5B-Instruct GGUF and llama.cpp server binary.
"""
import os
import sys
import platform
import urllib.request
import urllib.error
import zipfile
import tarfile
from pathlib import Path


ROOT = Path(__file__).parent.parent
MODELS_DIR = ROOT / "models"
BIN_DIR = ROOT / "bin"

GGUF_URL = "https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct-GGUF/resolve/main/qwen2.5-1.5b-instruct-q4_k_m.gguf"
GGUF_DEST = MODELS_DIR / "akari.gguf"

LLAMA_VERSION = "b12182"
LLAMA_WIN_URL = f"https://github.com/ggml-org/llama.cpp/releases/download/{LLAMA_VERSION}/llama-{LLAMA_VERSION}-bin-win-cpu-x64.zip"
LLAMA_LINUX_URL = f"https://github.com/ggml-org/llama.cpp/releases/download/{LLAMA_VERSION}/llama-{LLAMA_VERSION}-bin-ubuntu-x64.tar.gz"


def progress_bar(done: int, total: int, prefix: str = "") -> None:
    """Print a live percentage progress bar."""
    if total <= 0:
        return
    pct = done * 100 // total
    bar = "#" * (pct // 2) + "-" * (50 - pct // 2)
    sys.stdout.write(f"\r{prefix}[{bar}] {pct}% ({done}/{total} bytes)")
    sys.stdout.flush()


def check_url(url: str) -> tuple[bool, str, int]:
    """Check URL accessibility without downloading. Returns (ok, message, content_length)."""
    req = urllib.request.Request(url, headers={"User-Agent": "AKARI-setup/1.0"}, method="HEAD")
    try:
        with urllib.request.urlopen(req) as resp:
            cl = resp.headers.get("Content-Length")
            return True, f"OK (HTTP {resp.status})", int(cl) if cl else 0
    except urllib.error.HTTPError as e:
        return False, f"HTTP {e.code}: {e.reason}", 0
    except urllib.error.URLError as e:
        return False, f"URL error: {e.reason}", 0


def download_with_progress(url: str, dest: Path, desc: str = "") -> None:
    """Download a file with a live progress bar."""
    dest.parent.mkdir(parents=True, exist_ok=True)
    req = urllib.request.Request(url, headers={"User-Agent": "AKARI-setup/1.0"})
    try:
        with urllib.request.urlopen(req) as resp:
            total = int(resp.headers.get("Content-Length", 0))
            done = 0
            chunk = 8192
            with open(dest, "wb") as f:
                while True:
                    data = resp.read(chunk)
                    if not data:
                        break
                    f.write(data)
                    done += len(data)
                    progress_bar(done, total, desc)
        print()
    except urllib.error.HTTPError as e:
        dest.unlink(missing_ok=True)
        raise RuntimeError(f"Download failed: HTTP {e.code} {e.reason}")
    except urllib.error.URLError as e:
        dest.unlink(missing_ok=True)
        raise RuntimeError(f"Download failed: {e.reason}")


def extract_windows(zip_path: Path, dest_dir: Path) -> None:
    """Extract llama-server.exe from Windows zip."""
    try:
        with zipfile.ZipFile(zip_path, "r") as zf:
            for name in zf.namelist():
                if name.endswith("llama-server.exe"):
                    zf.extract(name, dest_dir)
                    extracted = dest_dir / name
                    final = dest_dir / "llama-server.exe"
                    if extracted != final:
                        if final.exists():
                            final.unlink()
                        extracted.rename(final)
                    print(f"Extracted: {final}")
                    return
        raise FileNotFoundError("llama-server.exe not found in zip")
    except zipfile.BadZipFile as e:
        raise RuntimeError(f"Corrupt zip archive: {e}")


def extract_linux(tar_path: Path, dest_dir: Path) -> None:
    """Extract llama-server from Linux tar.gz."""
    try:
        with tarfile.open(tar_path, "r:gz") as tf:
            for member in tf.getmembers():
                if member.name.endswith("llama-server"):
                    tf.extract(member, dest_dir)
                    extracted = dest_dir / member.name
                    final = dest_dir / "llama-server"
                    if extracted != final:
                        if final.exists():
                            final.unlink()
                        extracted.rename(final)
                    final.chmod(0o755)
                    print(f"Extracted: {final}")
                    return
        raise FileNotFoundError("llama-server not found in tar.gz")
    except tarfile.TarError as e:
        raise RuntimeError(f"Corrupt tar.gz archive: {e}")


def detect_platform() -> tuple[str, str, bool]:
    """
    Detect platform and architecture.
    Returns (system, arch, compatible) where compatible means a prebuilt binary exists.
    """
    system = platform.system().lower()
    machine = platform.machine().lower()

    if system == "windows":
        if machine in ("amd64", "x86_64"):
            # AVX2 check requires external lib; assume compatible (Windows x64 binaries are AVX2)
            return "windows", "x64", True
        return "windows", machine, False

    elif system == "linux":
        if machine in ("x86_64", "amd64"):
            return "linux", "x64", True
        if machine in ("aarch64", "arm64"):
            return "linux", "arm64", False  # No ARM64 prebuilt in this release
        return "linux", machine, False

    elif system == "darwin":
        if machine in ("x86_64",):
            return "darwin", "x64", False  # Not in this release
        if machine in ("arm64",):
            return "darwin", "arm64", False  # Not in this release
        return "darwin", machine, False

    return system, machine, False


def get_llama_url(system: str, arch: str) -> str | None:
    """Get the appropriate llama.cpp binary URL for the platform."""
    if system == "windows" and arch == "x64":
        return LLAMA_WIN_URL
    if system == "linux" and arch == "x64":
        return LLAMA_LINUX_URL
    return None


def check_mode() -> int:
    """Run environment and compatibility checks. Returns exit code."""
    print("=== AKARI Setup Check ===")
    print()

    # Python version
    py_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    print(f"Python: {py_version} ({platform.python_implementation()})")

    # Platform detection
    system, arch, compatible = detect_platform()
    print(f"Platform: {system} ({arch})")
    if compatible:
        print("  Prebuilt binary: AVAILABLE")
    else:
        print("  Prebuilt binary: NOT AVAILABLE for this platform/arch")

    # Directory structure
    print()
    print("Directories:")
    for d in ("bin", "models", "backend", "frontend", "data", "scripts", "notebooks"):
        path = ROOT / d
        status = "EXISTS" if path.exists() else "MISSING"
        print(f"  {d}/ : {status}")

    # Existing files
    print()
    print("Existing files:")
    if GGUF_DEST.exists():
        size = GGUF_DEST.stat().st_size
        print(f"  models/akari.gguf: {size:,} bytes")
    else:
        print("  models/akari.gguf: NOT FOUND")

    llama_exe = BIN_DIR / "llama-server.exe"
    llama_bin = BIN_DIR / "llama-server"
    if llama_exe.exists():
        print(f"  bin/llama-server.exe: {llama_exe.stat().st_size:,} bytes")
    elif llama_bin.exists():
        print(f"  bin/llama-server: {llama_bin.stat().st_size:,} bytes")
    else:
        print("  bin/llama-server: NOT FOUND")

    # URL checks
    print()
    print("URL accessibility:")
    ok, msg, cl = check_url(GGUF_URL)
    status = "OK" if ok else "FAIL"
    print(f"  GGUF: {status} - {msg}" + (f" ({cl:,} bytes)" if cl else ""))

    llama_url = get_llama_url(system, arch)
    if llama_url:
        ok, msg, cl = check_url(llama_url)
        status = "OK" if ok else "FAIL"
        print(f"  llama.cpp: {status} - {msg}" + (f" ({cl:,} bytes)" if cl else ""))
    else:
        print("  llama.cpp: SKIP (no compatible binary)")

    print()
    if compatible and llama_url:
        print("RESULT: Ready for installation")
        return 0
    else:
        print("RESULT: Cannot install - incompatible platform or missing binary")
        return 1


def main():
    if "--check" in sys.argv:
        sys.exit(check_mode())

    # Verify platform compatibility before proceeding
    system, arch, compatible = detect_platform()
    llama_url = get_llama_url(system, arch)

    if not compatible or not llama_url:
        print(f"ERROR: No compatible llama.cpp binary for {system} ({arch})")
        print("Supported: Windows x64 (AVX2), Linux x64")
        sys.exit(1)

    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    BIN_DIR.mkdir(parents=True, exist_ok=True)

    # 1. Download GGUF
    if not GGUF_DEST.exists():
        print("Downloading GGUF model...")
        download_with_progress(GGUF_URL, GGUF_DEST, "GGUF: ")
    else:
        print(f"Model already exists: {GGUF_DEST}")

    # 2. Download & extract llama-server
    print(f"Downloading {system} llama-server...")
    if system == "windows":
        llama_archive = BIN_DIR / "llama-win.zip"
        download_with_progress(llama_url, llama_archive, "llama: ")
        extract_windows(llama_archive, BIN_DIR)
        llama_archive.unlink(missing_ok=True)
    else:
        llama_archive = BIN_DIR / "llama-linux.tar.gz"
        download_with_progress(llama_url, llama_archive, "llama: ")
        extract_linux(llama_archive, BIN_DIR)
        llama_archive.unlink(missing_ok=True)

    print("Setup complete.")
    print(f"  Model: {GGUF_DEST}")
    final_exe = BIN_DIR / ("llama-server.exe" if system == "windows" else "llama-server")
    print(f"  Server: {final_exe}")


if __name__ == "__main__":
    main()