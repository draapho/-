"""
梅花易数起卦（与常见课式一致）：

- 上卦：(农历年地支序 + 农历月数 + 农历日数) 对 8 取余，余 0 则作 8
- 下卦：(年支 + 月 + 日 + 时辰地支序) 对 8 取余，余 0 则作 8
- 变爻：同上「下卦」之和 对 6 取余，余 0 则作 6

先天八卦序：1乾 2兑 3离 4震 5巽 6坎 7艮 8坤。

下卦为三爻（初、二、三），上卦为三爻（四、五、上）；「变爻」1～6 对应初爻～上爻。
年、时地支序：子1、丑2 … 亥12（与项目内手写示例「巳6、戌11」一致）。
"""

from __future__ import annotations

from typing import Any

from lunar_python import Solar

from .const import GUAS
from .const import YAOS
from .const import ZHIS


def _zhi_ordinal(zhi_char: str) -> int:
    return ZHIS.index(zhi_char) + 1


def _mod8_to_xiantian(n: int) -> int:
    r = n % 8
    return 8 if r == 0 else r


def _mod6_to_yao(n: int) -> int:
    r = n % 6
    return 6 if r == 0 else r


def _xiantian_bits(seq_1_to_8: int) -> str:
    return YAOS[seq_1_to_8 - 1]


def _mark_lower_upper(lower_xiantian: int, upper_xiantian: int) -> str:
    """初爻自下往上：先下卦三爻，再上卦三爻。"""
    return _xiantian_bits(lower_xiantian) + _xiantian_bits(upper_xiantian)


def _params_from_mark_and_moving(mark: str, yao_1_to_6: int) -> list[int]:
    """本卦码 + 变爻位(1～6) -> 六爻参数 0静少 1静阳 2动阴 3动阳。"""
    i = yao_1_to_6 - 1
    params: list[int] = []
    for j, ch in enumerate(mark):
        yang = ch == "1"
        if j == i:
            params.append(3 if yang else 2)
        else:
            params.append(1 if yang else 0)
    return params


def meihua_from_ymdhms(
    year: int,
    month: int,
    day: int,
    hour: int,
    minute: int = 0,
    second: int = 0,
) -> tuple[list[int], dict[str, Any]]:
    """
    公历换算农历后按上式起卦，返回 (Najia.compile 用的 params, 说明用 meta)。

    meta 含：年干支、农历月日、时干支、各序和、上/下卦先天序与卦名、变爻位数、本卦六比特。
    """
    solar = Solar.fromYmdHms(year, month, day, hour, minute, second)
    lunar = solar.getLunar()

    y_gz = lunar.getYearInGanZhi()
    t_gz = lunar.getTimeInGanZhi()
    y = _zhi_ordinal(y_gz[-1])
    h = _zhi_ordinal(t_gz[-1])
    m = lunar.getMonth()
    d = lunar.getDay()

    sum_upper = y + m + d
    sum_lower = y + m + d + h

    upper_n = _mod8_to_xiantian(sum_upper)
    lower_n = _mod8_to_xiantian(sum_lower)
    yao_n = _mod6_to_yao(sum_lower)

    mark = _mark_lower_upper(lower_n, upper_n)
    params = _params_from_mark_and_moving(mark, yao_n)

    meta: dict[str, Any] = {
        "solar": (year, month, day, hour, minute, second),
        "lunar_year_gz": y_gz,
        "lunar_month": m,
        "lunar_day": d,
        "time_gz": t_gz,
        "year_zhi_ordinal": y,
        "hour_zhi_ordinal": h,
        "sum_upper": sum_upper,
        "sum_lower": sum_lower,
        "upper_xiantian": upper_n,
        "lower_xiantian": lower_n,
        "upper_name": GUAS[upper_n - 1],
        "lower_name": GUAS[lower_n - 1],
        "moving_yao_1_to_6": yao_n,
        "mark": mark,
        "params": params,
    }
    return params, meta


def format_meihua_explain(meta: dict[str, Any]) -> str:
    """简短文字，便于在界面或终端核对。"""
    y, m_, d, h_, mi, s = meta["solar"]
    return (
        f"公历 {y}年{m_}月{d}日 {h_:02d}:{mi:02d}\n"
        f"农历 {meta['lunar_year_gz']}年 月{meta['lunar_month']} 日{meta['lunar_day']} "
        f"{meta['time_gz']}时\n"
        f"年支序={meta['year_zhi_ordinal']} 时支序={meta['hour_zhi_ordinal']}\n"
        f"上卦: ({meta['year_zhi_ordinal']}+{meta['lunar_month']}+{meta['lunar_day']}) mod 8"
        f" = {meta['sum_upper']} mod 8 → {meta['upper_xiantian']} {meta['upper_name']}\n"
        f"下卦: ({meta['year_zhi_ordinal']}+{meta['lunar_month']}+{meta['lunar_day']}+{meta['hour_zhi_ordinal']}) mod 8"
        f" = {meta['sum_lower']} mod 8 → {meta['lower_xiantian']} {meta['lower_name']}\n"
        f"变爻: {meta['sum_lower']} mod 6 → {meta['moving_yao_1_to_6']}爻动\n"
        f"本卦爻码(初→上): {meta['mark']}\n"
        f"纳甲六爻参数(初→上): {meta['params']}"
    )
