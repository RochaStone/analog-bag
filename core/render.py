"""Turn an HTML file into a PDF or PNG with headless Chrome. If no Chrome is found,
the HTML is still there: open it in any browser and Print > Save as PDF."""
from __future__ import annotations

import os
import platform
import shutil
import subprocess
import tempfile
from pathlib import Path

MAC_PATHS = (
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Chromium.app/Contents/MacOS/Chromium",
    "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
    "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser",
)
WIN_PATHS = (
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
)
NAMES = ("google-chrome", "google-chrome-stable", "chromium", "chromium-browser",
         "chrome", "microsoft-edge", "msedge")


def find_chrome() -> str | None:
    env = os.environ.get("ANALOG_BAG_CHROME") or os.environ.get("CHROME_PATH")
    if env == "none":  # lets you test the no-browser path
        return None
    if env and Path(env).exists():
        return env
    for p in MAC_PATHS + WIN_PATHS:
        if Path(p).exists():
            return p
    for n in NAMES:
        found = shutil.which(n)
        if found:
            return found
    home = Path.home() / ".cache" / "ms-playwright"
    if home.exists():
        hits = sorted(home.glob("chromium-*/chrome-*/chrome")) + sorted(
            home.glob("chromium-*/chrome-mac*/Chromium.app/Contents/MacOS/Chromium"))
        if hits:
            return str(hits[-1])
    return None


def _run(args: list[str]) -> tuple[bool, str]:
    chrome = find_chrome()
    if not chrome:
        return False, "no Chrome or Chromium found"
    with tempfile.TemporaryDirectory(prefix="analog-bag-chrome-") as profile:
        cmd = [chrome, "--headless=new", "--disable-gpu", "--hide-scrollbars",
               "--no-first-run", "--no-default-browser-check",
               f"--user-data-dir={profile}", "--virtual-time-budget=4000"]
        if platform.system() == "Linux" and hasattr(os, "geteuid") and os.geteuid() == 0:
            cmd.append("--no-sandbox")
        try:
            res = subprocess.run(cmd + args, capture_output=True, text=True, timeout=120)
        except (OSError, subprocess.TimeoutExpired) as exc:
            return False, f"Chrome failed to run: {exc}"
    if res.returncode != 0:
        return False, (res.stderr or res.stdout).strip()[-400:]
    return True, ""


def html_to_pdf(html: Path, pdf: Path) -> tuple[bool, str]:
    pdf.unlink(missing_ok=True)
    ok, err = _run(["--no-pdf-header-footer", "--print-to-pdf-no-header",
                    f"--print-to-pdf={pdf.resolve()}", html.resolve().as_uri()])
    if ok and not pdf.exists():
        return False, "Chrome ran but wrote no PDF"
    return ok, err


def html_to_png(html: Path, png: Path, width: int, height: int, scale: float = 2) -> tuple[bool, str]:
    png.unlink(missing_ok=True)
    ok, err = _run([f"--screenshot={png.resolve()}", f"--window-size={width},{height}",
                    f"--force-device-scale-factor={scale}", html.resolve().as_uri()])
    if ok and not png.exists():
        return False, "Chrome ran but wrote no PNG"
    return ok, err


def fallback_note(html: Path) -> str:
    return (f"No browser to render with, so the printable is HTML: {html}\n"
            "Open it in Chrome, Safari or Edge, then Print > Save as PDF "
            "(margins: none, background graphics: on).")


def dump_dom(html: Path, width: int, height: int) -> tuple[bool, str]:
    """Load a page at a window size and return the DOM after scripts ran (used by tests)."""
    chrome = find_chrome()
    if not chrome:
        return False, "no Chrome or Chromium found"
    with tempfile.TemporaryDirectory(prefix="analog-bag-chrome-") as profile:
        cmd = [chrome, "--headless=new", "--disable-gpu", "--no-first-run", f"--user-data-dir={profile}",
               f"--window-size={width},{height}", "--virtual-time-budget=4000",
               "--allow-file-access-from-files", "--dump-dom",
               html.resolve().as_uri()]
        if platform.system() == "Linux" and hasattr(os, "geteuid") and os.geteuid() == 0:
            cmd.insert(1, "--no-sandbox")
        try:
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        except (OSError, subprocess.TimeoutExpired) as exc:
            return False, f"Chrome failed to run: {exc}"
    return res.returncode == 0, res.stdout
