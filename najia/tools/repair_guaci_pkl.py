"""一次性修复 data/guaci.pkl：拆分误粘卦文、清理杂质、修补乱码。由仓库维护者按需运行。"""
from __future__ import annotations

import pickle
import re
import sys
import json
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

def export_pkl_to_json(
    pkl_path: str | Path, json_path: str | Path | None = None
) -> Path:
    """1. 将 pkl 数据转存为可直接阅读和编辑的 JSON 文件

    :param pkl_path: 输入的 .pkl 文件路径
    :param json_path: 输出的 .json 文件路径（默认同目录下同名 .json）
    :return: 生成的 json 文件 Path 对象
    """
    p_pkl = Path(pkl_path)
    p_json = Path(json_path) if json_path else p_pkl.with_suffix(".json")

    # 反序列化读取 pkl
    with open(p_pkl, "rb") as f:
        data = pickle.load(f)

    # 格式化导出为 json (indent=2 确保格式排版整齐，ensure_ascii=False 确保中文正常显示)
    with open(p_json, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"✅ 转换完成: {p_pkl.name} -> {p_json.name}")
    return p_json


def import_json_to_pkl(
    json_path: str | Path, pkl_path: str | Path | None = None
) -> Path:
    """2. 将修改好的 JSON 文件重新打包打包回 .pkl 文件

    :param json_path: 输入的 .json 文件路径
    :param pkl_path: 输出的 .pkl 文件路径（默认同目录下同名 .pkl）
    :return: 生成的 pkl 文件 Path 对象
    """
    p_json = Path(json_path)
    p_pkl = Path(pkl_path) if pkl_path else p_json.with_suffix(".pkl")

    # 读取修改后的 json
    with open(p_json, "r", encoding="utf-8") as f:
        data = json.load(f)

    # 重新序列化保存为 pkl (使用最高协议)
    with open(p_pkl, "wb") as f:
        pickle.dump(data, f, protocol=pickle.HIGHEST_PROTOCOL)

    print(f"✅ 打包完成: {p_json.name} -> {p_pkl.name}")
    return p_pkl

if __name__ == "__main__":
    # export_pkl_to_json("../data/guaci.pkl", "./guaci.json")
    # import_json_to_pkl("./guaci.json", "../data/guaci.pkl")
