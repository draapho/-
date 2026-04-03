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
from .const import GUAS
from .const import SYMBOL
from .const import XING5
from .const import YAOS
from .const import ZHI5
from .const import ZHIS
from .utils import get_god6
from .utils import get_najia
from .utils import get_qin6
from .utils import get_type
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
            out.append("\u3000")
            n -= 2
        else:
            out.append(" ")
            n -= 1
    return "".join(out)


def _pad_column(vals: list, width: int) -> list:
    return [_pad_cell(vals[i], width) for i in range(6)]


def _column_width(vals: list) -> int:
    return max(_cell_display_width(vals[i]) for i in range(6))


def _mark_column_min_width() -> int:
    """本卦/变卦爻画最小列宽（阴、阳、动阴、动阳）。"""
    return max(_cell_display_width(SYMBOL[i]) for i in range(4))


def _align_hexagram_table(rows: dict) -> None:
    """各列按显示宽度对齐；卦画列不低于当前爻符最大宽度。"""
    w = _column_width(rows["god6"])
    rows["god6"] = _pad_column(rows["god6"], w)

    w = _column_width(rows["hide"]["qin6"])
    rows["hide"]["qin6"] = _pad_column(rows["hide"]["qin6"], w)

    w = _column_width(rows["qin6"])
    rows["qin6"] = _pad_column(rows["qin6"], w)

    w = _column_width(rows["qinx"])
    rows["qinx"] = _pad_column(rows["qinx"], w)

    mark_floor = _mark_column_min_width()
    w = max(_column_width(rows["main"]["mark"]), mark_floor)
    rows["main"]["mark"] = _pad_column(rows["main"]["mark"], w)

    w = _column_width(rows["shiy"])
    rows["shiy"] = _pad_column(rows["shiy"], w)

    w = _column_width(rows["dyao"])
    rows["dyao"] = _pad_column(rows["dyao"], w)

    w = _column_width(rows["bian"]["qin6"])
    rows["bian"]["qin6"] = _pad_column(rows["bian"]["qin6"], w)

    w = max(_column_width(rows["bian"]["mark"]), mark_floor)
    rows["bian"]["mark"] = _pad_column(rows["bian"]["mark"], w)

    w = max(_column_width(rows["hu"]["mark"]), mark_floor)
    rows["hu"]["mark"] = _pad_column(rows["hu"]["mark"], w)

    w = max(_column_width(rows["cuo"]["mark"]), mark_floor)
    rows["cuo"]["mark"] = _pad_column(rows["cuo"]["mark"], w)

    w = max(_column_width(rows["zong"]["mark"]), mark_floor)
    rows["zong"]["mark"] = _pad_column(rows["zong"]["mark"], w)


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


# 与 standard.tpl 中变卦爻画与互/错/综爻画之间的全角间距一致
_MARK_COL_GAP = "　　　"


def _prefix_before_hu_mark_row(rows: dict, i: int) -> str:
    """与模板中到互卦首根爻画前的字符串一致（含变卦后与互卦之间的空距）。"""
    return (
        rows["god6"][i]
        + rows["hide"]["qin6"][i]
        + rows["qin6"][i]
        + rows["qinx"][i]
        + " "
        + rows["main"]["mark"][i]
        + " "
        + rows["shiy"][i]
        + rows["dyao"][i]
        + " "
        + rows["bian"]["qin6"][i]
        + " "
        + rows["bian"]["mark"][i]
        + _MARK_COL_GAP
    )


def _prepare_aux_layout(rows: dict) -> None:
    """互/错/综标题与下方三列爻画：列宽与行间空白一致，避免标题远在爻画右侧。"""
    pw = _cell_display_width(_prefix_before_hu_mark_row(rows, 5))

    def one(label: str, h: dict) -> str:
        t = f"({h['type']})" if h.get("type") else ""
        return f"{label}{h['gong']}宫:{h['name']}{t}"

    w_mu = _cell_display_width(rows["hu"]["mark"][5])
    w_cuo = _cell_display_width(rows["cuo"]["mark"][5])
    g = _cell_display_width(_MARK_COL_GAP)

    t_hu = one("互卦", rows["hu"])
    t_cuo = one("错卦", rows["cuo"])
    t_zong = one("综卦", rows["zong"])
    wt_hu = _cell_display_width(t_hu)
    wt_cuo = _cell_display_width(t_cuo)

    # 卦名常比爻画列更宽：动态加宽互–错、错–综空白，与标题行用同一 g1/g2
    g1 = g + max(0, wt_hu - w_mu)
    g2 = g + max(0, wt_cuo - w_cuo)
    rows["gap_hu_cuo"] = _pad_cell("", g1)
    rows["gap_cuo_zong"] = _pad_cell("", g2)

    lead = _pad_cell("", pw)
    pad1 = _pad_cell("", w_mu + g1 - wt_hu)
    pad2 = _pad_cell("", w_cuo + g2 - wt_cuo)
    rows["aux_titles_line"] = lead + t_hu + pad1 + t_cuo + pad2 + t_zong


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
        if gong is None:
            raise Exception("")

        if qins is None:
            raise Exception("")

        if len(set(qins)) < 5:
            mark = YAOS[gong] * 2

            logger.debug(mark)

            # 六亲
            qin6 = [
                (get_qin6(XING5[int(GUA5[gong])], ZHI5[ZHIS.index(x[1])]))
                for x in get_najia(mark)
            ]

            # 干支五行
            qinx = [GZ5X(x) for x in get_najia(mark)]
            seat = [qin6.index(x) for x in list(set(qin6).difference(set(qins)))]

            return {
                "name": GUA64.get(mark),
                "mark": mark,
                "qin6": qin6,
                "qinx": qinx,
                "seat": seat,
            }

        return None

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

        # gender = '男' if gender == 1 else '女'
        gender = ("", gender)[bool(gender)]

        # 卦码
        mark = "".join([str(int(p) % 2) for p in params])

        shiy = set_shi_yao(mark)  # 世应爻

        # 卦宫
        gong = palace(mark, shiy[0])  # 卦宫

        # 卦名
        name = GUA64[mark]

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

        # 动爻位置
        dong = [i for i, x in enumerate(params) if x > 1]
        # logger.debug(dong)

        # 伏神
        hide = self._hidden(gong, qin6)

        # 变卦
        bian = self._transform(params=params, gong=gong)

        self.data = {
            "params": params,
            "gender": gender,
            "title": title,
            "guaci": guaci,
            "solar": solar,
            "lunar": lunar,
            "god6": god6,
            "dong": dong,
            "name": name,
            "mark": mark,
            "gong": GUAS[gong],
            "shiy": shiy,
            "qin6": qin6,
            "qinx": qinx,
            "bian": bian,
            "hide": hide,
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

        empty = "\u3000" * 6
        rows = self.data

        symbal = SYMBOL
        rows["dyao"] = [symbal[x] if x in (2, 3) else "" for x in self.data["params"]]

        rows["main"] = {}
        rows["main"]["mark"] = [symbal[int(x)] for x in self.data["mark"]]
        rows["main"]["type"] = get_type(self.data["mark"])

        rows["main"]["gong"] = rows["gong"]
        rows["main"]["name"] = rows["name"]
        rows["main"]["indent"] = "\u3000" * 2

        if rows.get("hide"):
            rows["hide"]["qin6"] = [
                (
                    " %s%s " % (rows["hide"]["qin6"][x], rows["hide"]["qinx"][x])
                    if x in rows["hide"]["seat"]
                    else empty
                )
                for x in range(0, 6)
            ]
            rows["main"]["indent"] += empty
        else:
            rows["main"]["indent"] += "\u3000" * 1
            rows["hide"] = {"qin6": [empty for _ in range(0, 6)]}

        rows["main"]["display"] = "{indent}{name} ({gong}-{type})".format(
            **rows["main"]
        )

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
            hide = (12, 23)[bool(rows.get("hide"))]
            rows["bian"]["type"] = get_type(rows["bian"]["mark"])
            rows["bian"]["indent"] = (hide - len(rows["main"]["display"])) * "\u3000"

            if rows["bian"]["qin6"]:
                # 变卦六亲问题
                rows["bian"]["qin6"] = [
                    (
                        f'{rows["bian"]["qin6"][x]}{rows["bian"]["qinx"][x]}'
                        if x in self.data["dong"]
                        else f'  {rows["bian"]["qin6"][x]}{rows["bian"]["qinx"][x]}'
                    )
                    for x in range(0, 6)
                ]

            if rows["bian"]["mark"]:
                rows["bian"]["mark"] = [x for x in rows["bian"]["mark"]]
                rows["bian"]["mark"] = [
                    symbal[int(rows["bian"]["mark"][x])] for x in range(0, 6)
                ]
        else:
            rows["bian"] = {
                "qin6": ["\u3000" for _ in range(0, 6)],
                "mark": ["\u3000" for _ in range(0, 6)],
            }

        shiy = []

        # 显示世应字
        for x in range(0, 6):
            if x == self.data["shiy"][0] - 1:
                shiy.append("世")
            elif x == self.data["shiy"][1] - 1:
                shiy.append("应")
            else:
                shiy.append("\u3000")

        rows["shiy"] = shiy

        _align_hexagram_table(rows)

        _prepare_aux_layout(rows)

        # 注意：rows 即 self.data，勿把「是否显示卦辞」布尔量 guaci 改成字符串，否则 GUI 的 guaci_dual_payload 会失灵。
        rows["guaci_text"] = ""
        if self.data["guaci"]:
            bian_name = None
            raw_bian = self.data.get("bian")
            if raw_bian and isinstance(raw_bian, dict) and raw_bian.get("name"):
                bian_name = raw_bian["name"]
            if embed_guaci_plain:
                rows["guaci_text"] = format_guaci_dual(rows["name"], bian_name)

        template = Template(tpl)
        return template.render(**rows)

    def export(self):
        solar, params = self.data
        return solar, params

    def predict(self):
        return
