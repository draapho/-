"""一次性修复 data/guaci.pkl：拆分误粘卦文、清理杂质、修补乱码。由仓库维护者按需运行。"""
from __future__ import annotations

import pickle
import re
import sys
from pathlib import Path

# 包内导入需在 najia 根上运行：python -m najia.tools.repair_guaci_pkl
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT.parent))

from najia.const import GUA64  # noqa: E402
from najia.guaci_text import split_guaci_sections  # noqa: E402


def clean(s: str) -> str:
    s = s.replace("sm.aa963.com", "")
    s = s.replace("[/COLOR]", "")
    s = re.sub(r"(?i)\[color=?[^\]]*\]", "", s)
    return s.strip()


def main() -> None:
    path = ROOT / "data" / "guaci.pkl"
    d: dict[str, str] = pickle.loads(path.read_bytes())

    z = d.get("震为雷", "")
    i = z.find("《易经》第五十二卦")
    if i != -1:
        d["震为雷"] = clean(z[:i])
        d["艮为山"] = clean(z[i:])

    x = d.get("泽山咸", "")
    i = x.find("《易经》第三十二卦")
    if i != -1:
        d["泽山咸"] = clean(x[:i])
        d["雷风恒"] = clean(x[i:])

    if "坎为水" in d:
        t = d["坎为水"]
        t = t.replace("。九二：", "九二：").replace("。六三：", "六三：")
        t = re.sub(
            r"[\u3000 ]*上六：[^\n]+\n象曰：上六失道，凶三岁也。",
            "上六：系用徽纆，寘于丛棘，三岁不得，凶。\n象曰：上六失道，凶三岁也。",
            t,
        )
        d["坎为水"] = clean(t)

    if "泽雷随" in d:
        t = d["泽雷随"]
        t = re.sub(
            r"象曰：泽中有雷，随；君子以[^\n]+",
            "象曰：泽中有雷，随；君子以向晦入宴息。",
            t,
            count=1,
        )
        d["泽雷随"] = clean(t)

    for k in list(d.keys()):
        d[k] = clean(d[k])

    names = set(GUA64.values())
    missing = sorted(names - set(d.keys()))
    extra = sorted(set(d.keys()) - names)
    if missing:
        raise SystemExit(f"still missing: {missing}")
    if extra:
        raise SystemExit(f"extra keys: {extra}")

    issues: list[tuple[str, str]] = []
    for name in sorted(names):
        sec = split_guaci_sections(d[name])
        if not sec["preamble"].strip():
            issues.append((name, "empty preamble"))
        for yi, y in enumerate(sec["yaos"]):
            if not (y or "").strip():
                issues.append((name, f"empty yao {yi}"))

    if issues:
        for it in issues:
            print("ISSUE", it)
        raise SystemExit(1)

    path.write_bytes(pickle.dumps(d, protocol=pickle.HIGHEST_PROTOCOL))
    print("OK", path, "64 gua, issues=0")


if __name__ == "__main__":
    main()
