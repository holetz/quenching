"""Read a split flow as one text: the index with each step's file inlined where it is linked."""
import re
from pathlib import Path

STEP_LINK = re.compile(r"^Run it from \[step \d+\]\(\.agents/skills/quenching-specs/references/(specs-[a-z]+/step-[^)]+)\), read whole\.\n", re.M)


def flow_text(index: Path) -> str:
    text = Path(index).read_text(encoding="utf-8")

    def inline(match):
        body = (Path(index).parent / match.group(1)).read_text(encoding="utf-8")
        return body.split("\n", 2)[2] if body.startswith("# ") else body

    text, inlined = STEP_LINK.subn(inline, text)
    steps = Path(index).parent / f"specs-{Path(index).stem}"
    if not inlined and steps.is_dir():  # a flow whose index links its step files in prose: append them in order
        text += "\n" + "\n".join(p.read_text(encoding="utf-8") for p in sorted(steps.glob("*.md")))
    return text
