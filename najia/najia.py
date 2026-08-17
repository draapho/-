from __future__ import annotations

import json
import logging
import os
import unicodedata
from pathlib import Path

import arrow
from jinja2 import Template

from .const import GANS
from .const import GUA5
from .const import GUA64
from .const import NUMCIR
from .const import GUAS
from .const import SYMBOL
from .const import XING5
from .const import YAOS
from .const import ZHI5
from .const import ZHIS
from .utils import get_god6
from .utils import get_najia
from .utils import get_qin6
from .utils import get_zhi5
from .utils import get_type
from .utils import get_xing5_relationship
from .utils import get_chonghe_relation
from .utils import get_xunkong
from .utils import get_muku
from .utils import get_xing3
from .utils import get_he3
from .utils import get_mark3
from .utils import GZ5X
from .utils import palace
from .guaci_text import build_guaci_dual_payload
from .guaci_text import format_guaci_dual
from .utils import set_shi_yao

logging.basicConfig(level="INFO")
logger = logging.getLogger(__name__)


def _char_disp_width(ch: str) -> int:
    """单字符在「中文等宽 / 终端」下的占位宽度（块状符 Unicode 常标 Na，但实际占一格）。"""
    o = ord(ch)
    e = unicodedata.east_asian_width(ch)
    if e in ("F", "W"):
        return 2
    # 框线、八分块、几何图形：与 NSimSun / 控制台卦符显示一致按全角格计
    if 0x2500 <= o <= 0x257F:
        return 2
    if 0x2580 <= o <= 0x259F:
        return 2
    if 0x25A0 <= o <= 0x25FF:
        return 2
    # 动爻与箭头：在 CJK 等宽 UI 里通常接近一格宽
    if ch in "\u00d7\u25cb\u25cf\u25ef":
        return 2
    if ch in "\u2190\u2191\u2192\u2193\u2194":
        return 2
    return 1


def _cell_display_width(s: str) -> int:
    if not s:
        return 0
    return sum(_char_disp_width(ch) for ch in s)


def _pad_cell(s: str, width: int) -> str:
    """按显示宽度右补全角/半角空格，使该列上下同宽。"""
    s = "" if s is None else str(s)
    d = _cell_display_width(s)
    if d >= width:
        return s
    n = width - d
    out = [s]
    while n > 0:
        if n >= 2:
            out.append("　")
            n -= 2
        else:
            out.append("　")
            n -= 1
    return "".join(out)


def _pad_column(vals: list, width: int) -> list:
    return [_pad_cell(vals[i], width) for i in range(len(vals))]


def _column_width(vals: list) -> int:
    return max(_cell_display_width(vals[i]) for i in range(len(vals)))


def _mark_column_min_width() -> int:
    """本卦/变卦爻画最小列宽（阴、阳、动阴、动阳）。"""
    return max(_cell_display_width(SYMBOL[i]) for i in range(len(SYMBOL)))


def _align_hexagram_table(rows: dict) -> None:
    """各列按显示宽度对齐；卦画列不低于当前爻符最大宽度。"""
    # w = _column_width(rows["god6"])
    # rows["god6"] = _pad_column(rows["god6"], w)

    # w = _column_width(rows["hide"]["qin6"])
    # rows["hide"]["qin6"] = _pad_column(rows["hide"]["qin6"], w)

    # w = _column_width(rows["qin6"])
    # rows["qin6"] = _pad_column(rows["qin6"], w)

    # w = _column_width(rows["qinx"])
    # rows["qinx"] = _pad_column(rows["qinx"], w)

    FIXED_QINX_WIDTH = 8
    rows["yaom"] = _pad_column(rows["yaom"], FIXED_QINX_WIDTH)
    rows["yaod"] = _pad_column(rows["yaod"], FIXED_QINX_WIDTH)
    rows["hide"]["yaom"] = _pad_column(rows["hide"]["yaom"], FIXED_QINX_WIDTH)
    rows["hide"]["yaod"] = _pad_column(rows["hide"]["yaod"], FIXED_QINX_WIDTH)

    mark_floor = _mark_column_min_width()
    w = max(_column_width(rows["main"]["mark"]), mark_floor)
    rows["main"]["mark"] = _pad_column(rows["main"]["mark"], w)

    w = _column_width(rows["shiy"])
    rows["shiy"] = _pad_column(rows["shiy"], w)

    w = _column_width(rows["chohe"])
    rows["chohe"] = _pad_column(rows["chohe"], w)

    w = _column_width(rows["dyao"])
    rows["dyao"] = _pad_column(rows["dyao"], w)

    if rows.get("bian"):
        w = max(_column_width(rows["bian"]["mark"]), mark_floor) + 1
        rows["bian"]["mark"] = _pad_column(rows["bian"]["mark"], w)
        # w = _column_width(rows["bian"]["qin6"])
        # rows["bian"]["qin6"] = _pad_column(rows["bian"]["qin6"], w)

        rows["bian"]["yaom"] = _pad_column(rows["bian"]["yaom"], FIXED_QINX_WIDTH)
        rows["bian"]["yaod"] = _pad_column(rows["bian"]["yaod"], FIXED_QINX_WIDTH)
        rows["bian"]["dong"] = _pad_column(rows["bian"]["dong"], 6)

    # 互/错/综爻宽在 _prepare_aux_layout 中按「本卦—变卦」横向宽度再分配


def _derive_hu_cuo_zong(mark: str) -> tuple[str, str, str]:
    """互卦：二、三、四爻为下卦，三、四、五爻为上卦（爻位自下而上）。"""
    if len(mark) != 6:
        raise ValueError("mark must be 6 binary chars")
    hu = mark[1] + mark[2] + mark[3] + mark[2] + mark[3] + mark[4]
    cuo = "".join("1" if c == "0" else "0" for c in mark)
    zong = mark[::-1]
    return hu, cuo, zong


def _aux_gong_name_type(mark: str) -> dict:
    """卦的八宫名、卦名、卦题（六冲/游魂等，无则为空串）。"""
    shiy = set_shi_yao(mark)
    gi = palace(mark, shiy[0])
    typ = get_type(mark) or ""
    return {"name": GUA64[mark], "gong": GUAS[gi], "type": typ}

# def _prepare_main_bian_titles_line(rows: dict) -> None:
#     """本卦、变卦卦名与各自爻画列左缘对齐（按显示宽度，与六神爻行一致）。"""
#     i = 0
#     prefix = "".join(
#         [
#             rows["god6"][i],
#             rows["hide"]["qin6"][i],
#             rows["qin6"][i],
#             rows["qinx"][i],
#         ]
#     )
#     s_main = _cell_display_width(prefix) - 1
#     W_main = _cell_display_width(rows["main"]["mark"][i])
#     gap_b = (
#         rows["shiy"][i] + rows["dyao"][i] + "　"
#     )
#     s_bian = s_main + W_main + _cell_display_width(gap_b)

#     mt = rows["main"].get("type") or "　　"
#     mt += f"　{rows['main']['gong']}宫　{rows['main']['name']}"

#     bt = ""
#     raw_bian = rows.get("bian")
#     if raw_bian and raw_bian.get("name"):
#         bt = f"{raw_bian['name']}　{raw_bian['gong']}宫　"
#         bt += raw_bian.get("type") or ""

#     parts: list[str] = []
#     pos = 0
#     s_main = s_main - 10
#     if pos < s_main:
#         parts.append(_pad_cell("", s_main - pos))
#         pos = s_main
#     parts.append(mt)
#     pos += _cell_display_width(mt)
#     if bt:
#         if pos < s_bian:
#             parts.append(_pad_cell("", s_bian - pos))
#             pos = s_bian
#         parts.append(bt)
#     rows["main_bian_titles_line"] = "".join(parts)


# def _prepare_aux_layout(rows: dict) -> None:
#     """互贴行首；错在互与综之间居中；综与主表变卦爻同列同宽；右缘不超过变卦。"""
#     i = 0
#     prefix = "".join(
#         [
#             rows["god6"][i],
#             rows["hide"]["qin6"][i],
#             rows["qin6"][i],
#             rows["qinx"][i],
#         ]
#     )
#     w_prefix = _cell_display_width(prefix)

#     W_main = _cell_display_width(rows["main"]["mark"][i])
#     W_bian = _cell_display_width(rows["bian"]["mark"][i])
#     gap_mid = (
#         "　" + rows["shiy"][i] + rows["dyao"][i] + "　" + rows["bian"]["qin6"][i] + "　"
#     )
#     gap_mid_w = _cell_display_width(gap_mid)
#     # 与主表「变卦爻」左缘对齐的显示宽度（行首为 0，与六神列对齐）
#     zong_col_start = w_prefix + 1 + W_main + gap_mid_w

#     mark_floor = _mark_column_min_width()
#     M_inner = zong_col_start
#     g_min = 1
#     W_pair = max(mark_floor, (M_inner - 2 * g_min) // 2)
#     if 2 * W_pair > M_inner:
#         W_pair = max(1, M_inner // 2)
#     leftover = M_inner - 2 * W_pair
#     if leftover < 0:
#         W_pair = max(1, M_inner // 2)
#         leftover = M_inner - 2 * W_pair
#     g1 = (leftover + 1) // 2
#     g2 = leftover // 2

#     rows["gap_hu_cuo"] = _pad_cell("", g1)
#     rows["gap_cuo_zong"] = _pad_cell("", g2)

#     for j in range(6):
#         rows["hu"]["mark"][j] = _pad_cell(rows["hu"]["mark"][j], W_pair)
#         rows["cuo"]["mark"][j] = _pad_cell(rows["cuo"]["mark"][j], W_pair)
#         rows["zong"]["mark"][j] = _pad_cell(rows["zong"]["mark"][j], W_bian)

#     def one(label: str, h: dict) -> str:
#         t = f"({h['type']})" if h.get("type") else ""
#         return f"{label}{h['gong']}宫:{h['name']}{t}"

#     titles = [one("互卦", rows["hu"]), one("错卦", rows["cuo"]), one("综卦", rows["zong"])]
#     s0, s1, s2 = 0, W_pair + g1, zong_col_start
#     parts: list[str] = []
#     pos = 0
#     for t, s in zip(titles, [s0, s1, s2]):
#         if pos < s:
#             parts.append(_pad_cell("", s - pos))
#             pos = s
#         parts.append(t)
#         pos += _cell_display_width(t)
#     rows["aux_titles_line"] = "".join(parts)


class Najia(object):

    def __init__(self, verbose=None):
        # 仅一种卦线样式；保留参数以兼容旧代码，不再使用
        self.bian = None  # 变卦
        self.hide = None  # 伏神
        self.data = None

    @staticmethod
    def _gz(cal):
        """
        获取干支
        :param cal:
        :return:
        """
        return GANS[cal.tg] + ZHIS[cal.dz]

    @staticmethod
    def _cn(cal):
        """
        转换中文干支
        :param cal:
        :return:
        """
        return GANS[cal.tg] + ZHIS[cal.dz]

    @staticmethod
    def _daily(date=None):
        """
        计算日期
        :param date:
        :return:
        """
        # lunar = sxtwl.Lunar()
        # daily = lunar.getDayBySolar(date.year, date.month, date.day)
        # hour = lunar.getShiGz(daily.Lday2.tg, date.hour)

        from lunar_python import Solar

        solar = Solar.fromYmdHms(date.year, date.month, date.day, date.hour, 0, 0)
        lunar = solar.getLunar()

        ganzi = lunar.getBaZi()

        result = {
            # 'xkong': xkong(''.join([GANS[daily.Lday2.tg], ZHIS[daily.Lday2.dz]])),
            "xkong": lunar.getDayXunKong(),
            # 'month': daily.Lmonth2,
            # 'year' : daily.Lyear2,
            # 'day'  : daily.Lday2,
            # 'hour' : hour,
            # 'cn'   : {
            #     'month': self._gz(daily.Lmonth2),
            #     'year' : self._gz(daily.Lyear2),
            #     'day'  : self._gz(daily.Lday2),
            #     'hour' : self._gz(hour),
            # },
            "gz": {
                "month": ganzi[1],
                "year": ganzi[0],
                "day": ganzi[2],
                "hour": ganzi[3],
            },
        }
        # pprint(result)
        return result

    @staticmethod
    def _hidden(gong=None, qins=None):
        """
        计算伏神卦

        :param gong:
        :param qins:
        :return:
        """
        if gong is None or qins is None:
            raise ValueError("gong 与 qins 参数不可为 None")

        qinx = [""] * 6       # 伏神干支五行
        qin6 = [""] * 6       # 伏神六亲
        numc = [""] * 6       # 特殊符号

        if len(set(qins)) < 5:
            mark = YAOS[gong] * 2
            logger.debug(mark)

            # 六亲
            najia = get_najia(mark)
            qin6_hide = [
                (get_qin6(XING5[int(GUA5[gong])], ZHI5[ZHIS.index(x[1])]))
                for x in najia
            ]
            # 干支五行
            qinx_hide = [GZ5X(x) for x in najia]
            qin_missing = [qin6_hide.index(x) for x in list(set(qin6_hide).difference(set(qins)))]

            for idx in qin_missing:
                qinx[idx] = qinx_hide[idx]
                qin6[idx] = qin6_hide[idx]
                numc[idx] = NUMCIR[idx]

        return {
            "name": GUA64.get(mark) if len(set(qins)) < 5 else None,
            "mark": mark if len(set(qins)) < 5 else None,
            "qinx": qinx,
            "qin6": qin6,
            "numc": numc,
        }

    @staticmethod
    def _transform(params=None, gong=None):
        """
        计算变卦

        :param params:
        :return:
        """

        if params is None:
            raise Exception("")

        if type(params) == str:
            params = [x for x in params]

        if len(params) < 6:
            raise Exception("")

        # 与 compile 中动爻判定一致：x>1 即动（2 老阴、3 老阳）
        if any(v > 1 for v in params):
            mark = "".join(["1" if v in [1, 2] else "0" for v in params])
            qin6 = [
                (get_qin6(XING5[int(GUA5[gong])], ZHI5[ZHIS.index(x[1])]))
                for x in get_najia(mark)
            ]
            qinx = [GZ5X(x) for x in get_najia(mark)]

            return {
                "name": GUA64.get(mark),
                "mark": mark,
                "qin6": qin6,
                "qinx": qinx,
                "gong": GUAS[palace(mark, set_shi_yao(mark)[0])],
                "extra": get_type(mark) or "　　",
            }

        return None

    def compile(
        self, params=None, gender=None, date=None, title=None, guaci=False, **kwargs
    ):
        """
        根据参数编译卦
        :param guaci:
        :param title:
        :param gender:
        :param params:
        :param date:
        :return:
        """

        title = (title, "")[not title]

        solar = arrow.now() if date is None else arrow.get(date)
        lunar = self._daily(solar)
        gz = lunar["gz"]
        lunar["gz5"] = {
            "year": f"{gz['year']}{get_zhi5(gz['year'])}",
            "month": f"{gz['month']}{get_zhi5(gz['month'])}",
            "day": f"{gz['day']}{get_zhi5(gz['day'])}",
            "hour": f"{gz['hour']}{get_zhi5(gz['hour'])}",
        }

        # gender = '男' if gender == 1 else '女'
        gender = ("", gender)[bool(gender)]

        # 卦码
        mark = "".join([str(int(p) % 2) for p in params])

        shiy = set_shi_yao(mark)  # 世应爻

        # 卦宫
        gong = palace(mark, shiy[0])  # 卦宫

        # 卦名
        name = GUA64[mark]

        # 其它信息
        extra = get_type(mark) or "　　"

        # 六亲
        qin6 = [
            (get_qin6(XING5[int(GUA5[gong])], ZHI5[ZHIS.index(x[1])]))
            for x in get_najia(mark)
        ]
        qinx = [GZ5X(x) for x in get_najia(mark)]

        # logger.debug(qin6)

        # 六神
        # god6 = God6(''.join([GANS[lunar['day'].tg], ZHIS[lunar['day'].dz]]))
        god6 = get_god6(lunar["gz"]["day"])

        # 伏神
        hide = self._hidden(gong, qin6)

        # 变卦
        bian = self._transform(params=params, gong=gong)

        # 五行, 相旺休囚死
        gz5_m = lunar["gz5"]["month"]
        gz5_d = lunar["gz5"]["day"]

        yao_month = [[get_xing5_relationship(gz5_m, qinx[i])] for i in range(6)]
        yao_day = [[get_xing5_relationship(gz5_d, qinx[i])] for i in range(6)]
        hide["yaom"] = [[get_xing5_relationship(gz5_m, hide["qinx"][i] if hide["qinx"][i] else "")] for i in range(6)]
        hide["yaod"] = [[get_xing5_relationship(gz5_d, hide["qinx"][i] if hide["qinx"][i] else "")] for i in range(6)]
        hide["fei"] = [[get_xing5_relationship(qinx[i], hide["qinx"][i])] for i in range(6)]   # 飞神 -> 伏神

        if bian:
            bian["yaom"] = [[get_xing5_relationship(gz5_m, bian["qinx"][i])] for i in range(6)]
            bian["yaod"] = [[get_xing5_relationship(gz5_d, bian["qinx"][i])] for i in range(6)]
            bian["dong"] = [[get_xing5_relationship(qinx[i], bian["qinx"][i], format= 'd')] for i in range(6)]  # 动爻 -> 变爻. 比和会进一步判断地支进, 退, 伏

        # 冲合分析
        for i in range(6):
            yao_month[i].append(get_chonghe_relation(gz5_m, qinx[i]))
            yao_day[i].append(get_chonghe_relation(gz5_d, qinx[i]))
            hide["yaom"][i].append(get_chonghe_relation(gz5_m, hide["qinx"][i]))
            hide["yaod"][i].append(get_chonghe_relation(gz5_d, hide["qinx"][i]))
            hide["fei"][i].append(get_chonghe_relation(qinx[i], hide["qinx"][i]))   # 飞神 -> 伏神

            if bian:
                bian["yaom"][i].append(get_chonghe_relation(gz5_m, bian["qinx"][i]))
                bian["yaod"][i].append(get_chonghe_relation(gz5_d, bian["qinx"][i]))
                bian["dong"][i].append(get_chonghe_relation(qinx[i], bian["qinx"][i]))

        # 提取干支, 动爻位置, 暗动位置等
        dong = [i for i, x in enumerate(params) if x > 1]       # 动爻位置
        dong_yao = [qinx[i] for i in dong]                      # 动爻干支
        andong = [i for i in range(6) if i not in dong and "六冲" in yao_day[i]]    # 暗动位置, 静爻+日冲, 不判断相旺生伏情况.
        an_dongy = [qinx[i] for i in andong]                    # 暗动干支
        jing_yao = [qinx[i] for i in range(6) if i not in dong + andong]            # 静爻干支
        bian_yao = [bian["qinx"][i] for i in dong]              # 变爻干支
        hide_yao = [x for x in hide["qinx"] if x]               # 伏神干支

        # 本卦中, 动爻(不含暗动)对各爻的冲合状态, 不包括变爻和伏神.
        yao_chohe = [set() for _ in range(6)]
        for d in dong:
            for i in range(6):
                if d != i:  # 排除自身
                    ch = get_chonghe_relation(qinx[d], qinx[i])
                    if ch:
                        yao_chohe[d].add(ch)
                        yao_chohe[i].add(ch)
        # yao_chohe = [list(s) for s in yao_chohe]

        # 旬空. 仅日辰考虑.
        for i in range(6):
            yao_day[i].append(get_xunkong(lunar["xkong"], qinx[i]))
            hide["yaod"][i].append(get_xunkong(lunar["xkong"], hide["qinx"][i]))
            if bian:
                bian["yaod"][i].append(get_xunkong(lunar["xkong"], bian["qinx"][i]))

        # 墓库
        for i in range(6):
            yao_month[i].append(get_muku(gz5_m, qinx[i]))
            yao_day[i].append(get_muku(gz5_d, qinx[i]))
            hide["yaom"][i].append(get_muku(gz5_m, hide["qinx"][i]))
            hide["yaod"][i].append(get_muku(gz5_d, hide["qinx"][i]))

            if bian:
                bian["yaom"][i].append(get_muku(bian["qinx"][i], gz5_m))
                bian["yaod"][i].append(get_muku(bian["qinx"][i], gz5_d))
                bian["dong"][i].append(get_muku(qinx[i], bian["qinx"][i])) # 动爻入变爻墓库.

        # 三合, 三刑
        # 判断三和, 三刑的特殊结构. [["动", "变"], ["暗动", ""]]
        biando_pairs = [[d, b] for d, b in zip(dong_yao, bian_yao) if d]
        andong_pairs = [[a, ''] for a in an_dongy if a]
        yao_force = biando_pairs + andong_pairs
        yao_option = jing_yao                                           # [] + hide_yao 伏神不参与三合, 三刑.
        desche3 = get_he3(yao_force, yao_option, [gz5_m, gz5_d])        # [] 三合, 目前允许一动+日月成三合.
        descxing3 = get_xing3(yao_force, yao_option, [gz5_m, gz5_d])     # [] 三刑, 目前允许一动+日月成三合.

        # 增加三刑, 三合相关爻的提示.
        for i in range(6):
            yao_exclude = dong_yao + an_dongy + bian_yao + [gz5_m, gz5_d]
            yao_month[i].append(get_mark3(qinx[i], desche3, descxing3, yao_exclude, i not in dong and i not in andong)) # 标记静爻
            # hide["yaom"][i].append(get_mark3(hide["qinx"][i], desche3, descxing3, yao_exclude, True))   # 标记伏神
            if bian:
                yao_exclude = dong_yao + an_dongy
                bian["yaom"][i].append(get_mark3(bian["qinx"][i], desche3, descxing3, yao_exclude, True))     # 标记变爻
        lunar["gz5"]["year"] += "年"
        lunar["gz5"]["month"] += "月" + (get_mark3(gz5_m, desche3, descxing3)[-1:] or "　")
        lunar["gz5"]["day"] += "日" + (get_mark3(gz5_d, desche3, descxing3)[-1:] or "　")
        lunar["gz5"]["hour"] += "时"

        self.data = {           # [] 整理后的参数集
            "params": params,
            "gender": gender,
            "title": title,
            "guaci": guaci,
            "solar": solar,     # 阳历
            "lunar": lunar,     # 阴历
            "god6": god6,       # 六神
            "andong": andong,   # 可能的暗动.
            "name": name,       # 卦名
            "extra": extra,     # 其它信息, 游魂, 归魂, 六冲, 六合.
            "mark": mark,       # 阴阳
            "gong": GUAS[gong], # 宫名
            "shiy": shiy,       # 世应
            "qin6": qin6,       # 六亲
            "qinx": qinx,       # 天干地支五行
            "bian": bian,       # 变爻
            "hide": hide,       # 伏爻
            "yaom": yao_month,  # 各爻基于月的分析
            "yaod": yao_day,    # 各爻基于日的分析
            "yaochohe": yao_chohe,  # 各爻基于动爻的分析
            "desche3": desche3,     # 三合描述
            "descxing3": descxing3, # 三刑描述
        }

        # logger.debug(self.data)

        return self

    def gua_type(self, i):
        return

    def guaci_dual_payload(self):
        """勾选卦辞时供 GUI 分栏展示；无数据或未启用卦辞则为 None。"""
        if not self.data or not self.data.get("guaci"):
            return None
        bian_name = None
        raw_bian = self.data.get("bian")
        if raw_bian and isinstance(raw_bian, dict) and raw_bian.get("name"):
            bian_name = raw_bian["name"]
        return build_guaci_dual_payload(self.data["name"], bian_name)

    def render(self, embed_guaci_plain: bool = True):
        """
        :param embed_guaci_plain: False 时不把对照卦辞写入模板（供 GUI 单独分栏显示）。
        :return:
        """
        tpl = Path(__file__).parent / "data" / "standard.tpl"
        tpl = tpl.read_text(encoding="utf-8")

        rows = self.data

        symbal = SYMBOL
        # rows["dyao"] = [symbal[x] if x in (2, 3) else "" for x in self.data["params"]]
        rows["dyao"] = [
            symbal[x] if x in (2, 3)
            else '△' if i in rows["andong"]       # 加上可能的暗动的提示.
            else ""
            for i, x in enumerate(self.data["params"])
        ]

        rows["main"] = {}
        rows["main"]["mark"] = [symbal[int(x)] for x in self.data["mark"]]

        mark_bin = self.data["mark"]
        hu_m, cuo_m, zong_m = _derive_hu_cuo_zong(mark_bin)
        rows["hu"] = {
            **_aux_gong_name_type(hu_m),
            "mark": [symbal[int(c)] for c in hu_m],
        }
        rows["cuo"] = {
            **_aux_gong_name_type(cuo_m),
            "mark": [symbal[int(c)] for c in cuo_m],
        }
        rows["zong"] = {
            **_aux_gong_name_type(zong_m),
            "mark": [symbal[int(c)] for c in zong_m],
        }

        if rows.get("bian"):
            rows["bian"]["type"] = get_type(rows["bian"]["mark"])
            if rows["bian"]["mark"]:
                rows["bian"]["mark"] = list(rows["bian"]["mark"])
                rows["bian"]["mark"] = [
                    symbal[int(rows["bian"]["mark"][x])] for x in range(0, 6)
                ]

        # 显示世应字
        shiy = []
        for x in range(0, 6):
            if x == self.data["shiy"][0] - 1:
                shiy.append("世")
            elif x == self.data["shiy"][1] - 1:
                shiy.append("应")
            else:
                shiy.append("　")
        rows["shiy"] = shiy

        # 动爻对本卦各爻的冲合关系
        rows["chohe"] = []
        for s in rows["yaochohe"]:  # s 为单个爻的 set 集合，如 {"子午冲", "卯戌合"}
            has_chong = any("冲" in item for item in s)
            has_he = any("合" in item for item in s)
            if has_chong and has_he:
                rows["chohe"].append("六")
            elif has_chong:
                rows["chohe"].append("冲")
            elif has_he:
                rows["chohe"].append("合")
            else:
                rows["chohe"].append("　")

        # all_chohe_set = set().union(*[set(x) for x in rows["yaochohe"]])
        # rows["descchohe"] = "　".join([i for i in sorted(all_chohe_set) if i and i.strip()])  # 冲合提示.

        # 字符串简化处理,
        for i in range(6):
            rows["yaom"][i] = "".join(item.strip()[-1] for item in rows["yaom"][i] if item and item.strip())
            if ('㊂' in rows["yaom"][i]) and len(rows["yaom"][i]) < 4:  # 三合, 三刑的注释判断
                rows["yaom"][i] = rows["yaom"][i].replace('㊂', '㊀㊁') 
            rows["yaod"][i] = "".join(item.strip()[-1] for item in rows["yaod"][i] if item and item.strip())
            rows["hide"]["yaom"][i] = "".join(item.strip()[-1] for item in rows["hide"]["yaom"][i] if item and item.strip())
            rows["hide"]["yaod"][i] = "".join(item.strip()[-1] for item in rows["hide"]["yaod"][i] if item and item.strip())
            rows["hide"]["fei"][i] = "".join(item.strip()[-1] for item in rows["hide"]["fei"][i] if item and item.strip())

        if rows.get("bian"):
            for i in range(6):
                rows["bian"]["yaom"][i] = "".join(item.strip()[-1] for item in rows["bian"]["yaom"][i] if item and item.strip())
                if ('㊂' in rows["bian"]["yaom"][i]) and len(rows["bian"]["yaom"][i]) < 4:  # 三合, 三刑的注释判断
                    rows["bian"]["yaom"][i] = rows["bian"]["yaom"][i].replace('㊂', '㊀㊁')
                rows["bian"]["yaod"][i] = "".join(item.strip()[-1] for item in rows["bian"]["yaod"][i] if item and item.strip())
                rows["bian"]["dong"][i] = "".join(item.strip()[-1] for item in rows["bian"]["dong"][i] if item and item.strip())
                rows["bian"]["dong"][i] = "".join(item.strip()[-1] for item in rows["bian"]["dong"][i] if item and item.strip()) if rows["dyao"][i] in ("ｏ", "ｘ") else ""

        rows["desche3"] = "　".join([i for i in rows["desche3"] if i and i.strip()])        # 三合提示.
        rows["descxing3"] = "　".join([i for i in rows["descxing3"] if i and i.strip()])    # 三刑提示.

        _align_hexagram_table(rows)     # 统一字符串长度.
        # _prepare_main_bian_titles_line(rows)
        # _prepare_aux_layout(rows)

        # 注意：rows 即 self.data，勿把「是否显示卦辞」布尔量 guaci 改成字符串，否则 GUI 的 guaci_dual_payload 会失灵。
        rows["guaci_text"] = ""
        if self.data["guaci"]:
            bian_name = None
            raw_bian = self.data.get("bian")
            if raw_bian and isinstance(raw_bian, dict) and raw_bian.get("name"):
                bian_name = raw_bian["name"]
            if embed_guaci_plain:
                rows["guaci_text"] = format_guaci_dual(rows["name"], bian_name)

        # [] tpl 格式模板, 导入.
        template = Template(tpl)
        return template.render(**rows)

    def export(self):
        solar, params = self.data
        return solar, params

    def predict(self):
        return
