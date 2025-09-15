from pathlib import Path


def read_high_score(path: str) -> int:
    p = Path(path)
    try:
        if not p.exists():
            return 0
        txt = p.read_text(encoding="utf-8", errors="ignore").strip()
        return int(txt) if txt.isdigit() else 0
    except Exception:
        return 0


def write_high_score(path: str, score: int) -> None:
    try:
        Path(path).write_text(str(int(score)), encoding="utf-8")
    except Exception:
        # Silently ignore write failures
        pass
