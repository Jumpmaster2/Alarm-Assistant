"""Build frontend/labels.js (field names and help texts of the panel) from the translations.

python scripts/build_labels.py          write the file
python scripts/build_labels.py --check  fail if the file is not up to date
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

INTEGRATION = Path(__file__).resolve().parent.parent / "custom_components" / "alarm_assistant"
TARGET = INTEGRATION / "frontend" / "labels.js"
LANGUAGES = ("de", "en")
HEADER = "// Generated from the translation source, do not edit by hand.\n"
HEADER += "// Run python scripts/build_labels.py after changing the translations.\n"


def _forms(translations: dict[str, Any]) -> list[dict[str, Any]]:
    """All form blocks (with 'data') in a stable order."""
    steps = [
        *translations.get("config", {}).get("step", {}).values(),
        *translations.get("options", {}).get("step", {}).values(),
    ]
    for sub in translations.get("config_subentries", {}).values():
        steps += sub.get("step", {}).values()
    forms = []
    for step in steps:
        forms.append(step)
        forms += step.get("sections", {}).values()
    return [form for form in forms if form.get("data")]


def labels(translations: dict[str, Any]) -> dict[str, list[str]]:
    """Field key -> [name, help]; the first name and the first help text win."""
    result: dict[str, list[str]] = {}
    for form in _forms(translations):
        help_texts = form.get("data_description", {})
        for key, name in form["data"].items():
            entry = result.setdefault(key, [name, ""])
            if not entry[1] and help_texts.get(key):
                entry[1] = help_texts[key]
    return result


def render() -> str:
    data = {
        lang: labels(json.loads((INTEGRATION / "translations" / f"{lang}.json").read_text("utf-8")))
        for lang in LANGUAGES
    }
    return f"{HEADER}export const LABELS = {json.dumps(data, ensure_ascii=False, indent=1)};\n"


def main() -> int:
    content = render()
    if "--check" in sys.argv:
        if TARGET.read_text("utf-8") != content:
            print(f"{TARGET} is not up to date, run python scripts/build_labels.py")
            return 1
        return 0
    TARGET.write_text(content, "utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
