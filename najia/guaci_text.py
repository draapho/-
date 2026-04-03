"""卦辞、爻辞自 guaci.pkl 文本解析，并排版为左本卦 / 右变卦对照。"""

from __future__ import annotations

import re
import unicodedata
from typing import Optional

from .utils import get_guaci

_YAO_FIRST_LINE = re.compile(
    r"^(初[九六]|九二|六二|九三|六三|九四|六四|九五|六五|上[九六]|用九|用六)\s*[：:]"
)

_YAO_IDX_RULES: list[tuple[re.Pattern[str], int]] = [
    (re.compile(r"^初[九六]"), 0),
    (re.compile(r"^(九二|六二)"), 1),
    (re.compile(r"^(九三|六三)"), 2),
    (re.compile(r"^(九四|六四)"), 3),
    (re.compile(r"^(九五|六五)"), 4),
    (re.compile(r"^上[九六]"), 5),
]


def _ea_w(ch: str) -> int:
    return 2 if unicodedata.east_asian_width(ch) in ("F", "W") else 1


def _line_display_width(s: str) -> int:
    return sum(_ea_w(c) for c in s)


def _wrap_line_to_width(s: str, width: int) -> list[str]:
    """按显示宽度断行（全角算 2）。"""
    s = s.strip()
    if not s:
        return [""]
    lines: list[str] = []
    buf: list[str] = []
    w = 0
    for ch in s:
        cw = _ea_w(ch)
        if w + cw > width and buf:
            lines.append("".join(buf))
            buf = [ch]
            w = cw
        else:
            buf.append(ch)
            w += cw
    if buf:
        lines.append("".join(buf))
    return lines


def _wrap_paragraph(text: str, width: int) -> list[str]:
    out: list[str] = []
    for para in text.split("\n"):
        para = para.strip()
        if not para:
            continue
        out.extend(_wrap_line_to_width(para, width))
    return out or [""]


def _yao_index_from_chunk(chunk: str) -> Optional[int]:
    first = chunk.strip().split("\n", 1)[0].strip()
    for rx, idx in _YAO_IDX_RULES:
        if rx.match(first):
            return idx
    if first.startswith("用九") or first.startswith("用六"):
        return None
    return None


def split_guaci_sections(text: str) -> dict:
    """拆成卦前段（题头+卦辞+彖+大象等）与六根爻辞块（初→上）。"""
    if not text or not text.strip():
        return {"preamble": "", "yaos": [""] * 6}
    lines = text.strip().split("\n")
    y_starts: list[int] = []
    for i, line in enumerate(lines):
        if _YAO_FIRST_LINE.match(line.strip()):
            y_starts.append(i)
    if not y_starts:
        return {"preamble": text.strip(), "yaos": [""] * 6}
    preamble = "\n".join(lines[: y_starts[0]]).strip()
    chunks: list[str] = []
    for k, st in enumerate(y_starts):
        ed = y_starts[k + 1] if k + 1 < len(y_starts) else len(lines)
        chunks.append("\n".join(lines[st:ed]).strip())
    yaos = [""] * 6
    extras: list[str] = []
    for ch in chunks:
        idx = _yao_index_from_chunk(ch)
        if idx is not None:
            yaos[idx] = ch
        else:
            extras.append(ch)
    if extras:
        preamble = (preamble + "\n\n" + "\n\n".join(extras)).strip()
    return {"preamble": preamble, "yaos": yaos}


def _dual_column(left_lines: list[str], right_lines: list[str], gutter: str) -> str:
    n = max(len(left_lines), len(right_lines))
    ll = left_lines + [""] * (n - len(left_lines))
    rr = right_lines + [""] * (n - len(right_lines))
    gw = _line_display_width(gutter)
    # 不对右侧再截断，由 col_width 在 wrap 时已控制
    return "\n".join(a + gutter + b for a, b in zip(ll, rr))


def format_guaci_dual(main_name: str, bian_name: Optional[str], col_width: int = 30) -> str:
    """
    本卦在左、变卦在右：先卦前并列块，再六根爻逐条并列。
    无变卦名时只输出本卦全文（与原行为一致）。
    """
    main_raw = get_guaci(main_name) or ""
    if not main_raw.strip():
        return ""

    if not bian_name:
        return main_raw.strip()

    bian_raw = get_guaci(bian_name) or ""
    sm = split_guaci_sections(main_raw)
    sb = split_guaci_sections(bian_raw)
    gutter = "  │  "
    YAO_LABS = ("初爻", "二爻", "三爻", "四爻", "五爻", "上爻")

    parts: list[str] = []
    parts.append("")
    parts.append("【卦辞 · 彖传 · 象传】（左：本卦「" + main_name + "」　右：变卦「" + bian_name + "」）")
    parts.append("")
    pl = _wrap_paragraph(sm["preamble"], col_width)
    pr = _wrap_paragraph(sb["preamble"], col_width)
    parts.append(_dual_column(pl, pr, gutter))

    parts.append("")
    parts.append("【爻辞】（自下而上：初→上）")
    parts.append("")
    for i in range(6):
        lab = YAO_LABS[i]
        a = sm["yaos"][i].strip() or "（无）"
        b = sb["yaos"][i].strip() or "（无）"
        head = f"── {lab} ──"
        parts.append(head)
        parts.append(
            _dual_column(
                _wrap_paragraph(a, col_width),
                _wrap_paragraph(b, col_width),
                gutter,
            )
        )
        parts.append("")

    return "\n".join(parts).rstrip() + "\n"


def build_guaci_dual_payload(main_name: str, bian_name: Optional[str]) -> Optional[dict]:
    """
    供 GUI 左右分栏：返回本卦 / 变卦原文片段。无卦辞数据或未勾选等情况下返回 None。
    仅本卦、无变卦名时 mode 为 single，只有 text_left。
    """
    main_raw = get_guaci(main_name) or ""
    if not main_raw.strip():
        return None

    if not bian_name:
        return {
            "mode": "single",
            "main_name": main_name,
            "bian_name": None,
            "text_left": main_raw.strip(),
            "text_right": "",
        }

    bian_raw = get_guaci(bian_name) or ""
    sm = split_guaci_sections(main_raw)
    sb = split_guaci_sections(bian_raw)
    YAO_LABS = ("初爻", "二爻", "三爻", "四爻", "五爻", "上爻")
    yaos: list[dict] = []
    for i in range(6):
        yaos.append(
            {
                "label": YAO_LABS[i],
                "left": sm["yaos"][i].strip() or "（无）",
                "right": sb["yaos"][i].strip() or "（无）",
            }
        )
    return {
        "mode": "dual",
        "main_name": main_name,
        "bian_name": bian_name,
        "preamble_left": sm["preamble"].strip(),
        "preamble_right": sb["preamble"].strip(),
        "yaos": yaos,
    }
