import logging
import math
import re
from pathlib import Path
from typing import List, Dict, Any, Set

from . import const

logging.basicConfig(level='INFO')
logger = logging.getLogger(__name__)


def GZ5X(gz=''):
    """
    干支五行
    :param gz:
    :return:
    """
    _, z = [i for i in gz]
    zm = const.ZHIS.index(z)

    return gz + const.XING5[const.ZHI5[zm]]


def mark(symbol=None):
    """
    单拆重交 转 二进制卦码
    :param symbol:
    :return:
    """

    res = [str(int(x) % 2) for x in symbol]
    logger.debug(res)

    return res


def xkong(gz='甲子'):
    """
    计算旬空

    :param gz: 甲子 or 3,11
    :return:
    """

    gm, zm = [i for i in gz]

    if type(gz) == str:
        gm = const.GANS.index(gm)
        zm = const.ZHIS.index(zm)

    if gm == zm or zm < gm:
        zm += 12

    xk = int((zm - gm) / 2) - 1

    return const.KONG[xk]


def get_god6(gz=None):
    """
    # 六神, 根据日干五行配对六神五行

    :param gz: 日干支
    :return:
    """

    gm, _ = [i for i in gz]

    if type(gm) is str:
        gm = const.GANS.index(gm)

    num = math.ceil((gm + 1) / 2) - 7

    if gm == 4:
        num = -4

    if gm == 5:
        num = -3

    if gm > 5:
        num += 1

    return const.SHEN6[num:] + const.SHEN6[:num]


'''
寻世诀：
天同二世天变五，地同四世地变初。
本宫六世三世异，人同游魂人变归。

1. 天同人地不同世在二，天不同人地同在五
2. 三才不同世在三
3. 人同其他不同世在四，人不同其他同在三'''


# 世爻初爻是1，二爻是2
# 寻世诀： 天同二世天变五  地同四世地变初  本宫六世三世异  人同游魂人变归
# int('111', 2) => 7
# 世爻 >= 3, 应爻 = 世爻 - 3， index = 5 - 世爻 + 1
# 世爻 <= 3, 应爻 = 世爻 + 3，
# life oneself
def set_shi_yao(symbol=None):
    """
    获取世爻

    :param symbol: 卦的二进制码
    :return: 世爻，应爻，所在卦宫位置
    """
    wai = symbol[3:]  # 外卦
    nei = symbol[:3]  # 内卦

    def shiy(shi, index=None):
        ying = shi - 3 if shi > 3 else shi + 3
        index = shi if index is None else index
        return shi, ying, index

    # 天同二世天变五
    if wai[2] == nei[2]:
        if wai[1] != nei[1] and wai[0] != nei[0]:
            return shiy(2)
    else:
        if wai[1] == nei[1] and wai[0] == nei[0]:
            return shiy(5)

    # 人同游魂人变归
    if wai[1] == nei[1]:
        if wai[0] != nei[0] and wai[2] != nei[2]:
            return shiy(4, 6)  # , Hun
    else:
        # fix 归魂问题
        if wai[0] == nei[0] and wai[2] == nei[2]:
            return shiy(3, 6)  # , Hun

    # 地同四世地变初
    if wai[0] == nei[0]:
        if wai[1] != nei[1] and wai[2] != nei[2]:
            return shiy(4)
    else:
        if wai[1] == nei[1] and wai[2] == nei[2]:
            return shiy(1)

    # 本宫六世
    if wai == nei:
        return shiy(6)

    # 三世异
    return shiy(3)


def get_type(symbol=None):
    if res := soul(symbol):
        return res

    name = const.GUA64[symbol]
    if any(x in name for x in const.CHONG):
        return '六冲'

    if any(x in name for x in const.LIUHE):
        return "六合"

    return ''

def soul(symbol=None):
    wai = symbol[3:]  # 外卦
    nei = symbol[:3]  # 内卦
    hun = ''

    if wai[1] == nei[1]:
        if wai[0] != nei[0] and wai[2] != nei[2]:
            hun = '游魂'
    else:
        if wai[0] == nei[0] and wai[2] == nei[2]:
            hun = '归魂'

    return hun


def palace(symbol=None, index=None):  # inStr -> '111000'  # intNum -> 世爻
    """
    六爻卦的卦宫名

    认宫诀：
    一二三六外卦宫，四五游魂内变更。
    若问归魂何所取，归魂内卦是本宫。

    :param symbol: 卦的二进制码
    :param index: 世爻
    :return:
    """

    wai = symbol[3:]  # 外卦
    nei = symbol[:3]  # 内卦
    hun = ''

    if wai[1] == nei[1]:
        if wai[0] != nei[0] and wai[2] != nei[2]:
            hun = '游魂'
    else:
        if wai[0] == nei[0] and wai[2] == nei[2]:
            hun = '归魂'

    # 归魂内卦是本宫
    if hun == '归魂':
        return const.YAOS.index(nei)

    # 一二三六外卦宫
    if index in (1, 2, 3, 6):
        return const.YAOS.index(wai)

    # 四五游魂内变更
    if index in (4, 5) or hun == '游魂':
        symbol = ''.join([str(int(c) ^ 1) for c in nei])
        return const.YAOS.index(symbol)

# 纳甲配干支
def get_najia(symbol=None):
    """
    纳甲配干支

    :param symbol:
    :return:
    """

    wai = symbol[3:]  # 外卦
    nei = symbol[:3]  # 内卦

    wai, nei = const.YAOS.index(wai), const.YAOS.index(nei)

    gan = const.NAJIA[nei][0][0]
    ngz = [f'{gan}{zhi}' for zhi in const.NAJIA[nei][0][1:]]  # 排干支

    gan = const.NAJIA[wai][1][0]
    wgz = [f'{gan}{zhi}' for zhi in const.NAJIA[wai][1][1:]]  # 排干支

    return ngz + wgz


def get_qin6(w1, w2):
    """
    两个五行判断六亲
    水1 # 木2 # 金3 # 火4 # 土5

    :param w1:
    :param w2:
    :return:
    """
    w1 = const.XING5.index(w1) if type(w1) is str else w1
    w2 = const.XING5.index(w2) if type(w2) is str else w2

    ws = w1 - w2
    ws = ws + 5 if ws < 0 else ws
    q6 = const.QING6[ws]

    logger.debug(ws)
    logger.debug(q6)

    return q6


def get_zhi5(text: str) -> str:
    """传入干支(如 '甲子')或纯地支(如 '子'), 返回对应地支五行(如 '水')."""
    if not text:
        return ""

    zhi = text[-1]
    if zhi in const.ZHIS:
        return const.XING5[const.ZHI5[const.ZHIS.index(zhi)]]
    return ""

def _extract_xing5(s: str) -> str:
    """
    从固定格式的干支字符串中提取五行

    Args:
        s: 固定格式的干支/纳音字符串
    Returns:
        地支字符; 长度异常时返回空字符串
    """
    return s[-1] if s else ""

def _extract_zhi(s: str) -> str:
    """
    从固定格式的干支字符串中提取地支

    支持格式:
        - 1字: "子"       → s[0]
        - 2字: "甲子"     → s[1]
        - 3字: "甲子水"   → s[1]

    Args:
        s: 固定格式的干支/纳音字符串
    Returns:
        地支字符; 长度异常时返回空字符串
    """
    length = len(s)
    if length == 1:
        return s[0]
    if length in (2, 3):
        return s[1]
    return ""

def get_xing5_relationship(a: str, b: str, format="b") -> str:
    """
    五行关系判断 (纯中文接口)
    Args:
        a: 主体五行, 限 "木火土金水"
        b: 客体五行, 限 "木火土金水"
        d: 动化关系, 需要地支和五行
    Returns:
        中文关系字符串: "比和"/"生"/"克"/"被生"/"被克"
    Raises:
        ValueError: 输入非合法五行字符时抛出
    """
    _XING5_STANDARD = ("木", "火", "土", "金", "水")
    _INDEX_MAP = {name: idx for idx, name in enumerate(_XING5_STANDARD)}
    _RELATION_MAP_A_SHENKE = {0: "比", 1: "生", 2: "克", 3: "耗", 4: "泄"}      # 对应于{A同B, A生B, A克B, A耗B(B克A), A泄B(B生A)}
    _RELATION_MAP_B_WANGSHUAI = {0: "旺", 1: "相", 2: "死", 3: "囚", 4: "休"}   # 对应于{A同B, A生B, A克B, A耗B(B克A), A泄B(B生A)}
    _RELATION_MAP_D_DONGHUA = {0: "比和", 1: "化泄", 2: "化耗", 3: "化克", 4: "化生"}

    xing1 = _extract_xing5(a);
    xing2 = _extract_xing5(b);
    if xing1 not in _INDEX_MAP or xing2 not in _INDEX_MAP:
        return ""

    diff = (_INDEX_MAP[xing2] - _INDEX_MAP[xing1]) % 5

    if 'a' == format.lower():
        return _RELATION_MAP_A_SHENKE[diff]
    elif 'b' == format.lower():
        return _RELATION_MAP_B_WANGSHUAI[diff]
    elif 'd' == format.lower():
        if diff != 0:
            return _RELATION_MAP_D_DONGHUA[diff]
        _JIN_MAP = { # 化进表
            "寅": "卯", "巳": "午", "申": "酉", "亥": "子",
            "丑": "辰", "辰": "未", "未": "戌", "戌": "丑"
        }
        _TUI_MAP = { # 化退表
            "卯": "寅", "午": "巳", "酉": "申", "子": "亥",
            "辰": "丑", "未": "辰", "戌": "未", "丑": "戌"
        }
        zhi1 = _extract_zhi(a);
        zhi2 = _extract_zhi(b);
        if zhi1 == zhi2:
            return "吟伏"    # 应为吟伏, 为了末字取"伏"字.
        elif _JIN_MAP.get(zhi1) == zhi2:
            return "化进"
        elif _TUI_MAP.get(zhi1) == zhi2:
            return "化退"
    return ""

def get_chonghe_relation(d1: str, d2: str) -> str:
    """
    判断两个地支的六冲/六合关系
    Args:
        d1: 第一个地支
        d2: 第二个地支
    Returns:
        "六冲" / "六合" / None
    """

    zhi1 = _extract_zhi(d1)
    zhi2 = _extract_zhi(d2)
    if not zhi1 or not zhi2:
        return ""

    key = frozenset((zhi1, zhi2))
    return (
        const.CHONG6.get(key)
        or const.HE6.get(key)
        or ""
    )

def get_xinghai_relation(d1: str, d2: str, format = "all") -> str:
    """
    判断两个地支的六冲/六合关系
    Args:
        d1: 第一个地支
        d2: 第二个地支
        format: "all" 全部, "nozi" 去掉自刑
    Returns:
        "六害" / "无礼刑" / "自刑" / None
    """

    zhi1 = _extract_zhi(d1)
    zhi2 = _extract_zhi(d2)
    if not zhi1 or not zhi2:
        return ""

    if zhi1 == zhi2 and format.lower() != "nozi":
        if zhi1 in const.XING3["one"]:
            return "自刑"
        return ""

    key = frozenset((zhi1, zhi2))
    return (
        const.XING3["two"].get(key)
        # or const.HAI6.get(key)        # [] 取消害的判断
        or ""
    )

def get_xunkong(kong: str, d1: str) -> str:
    zhi1 = _extract_zhi(d1)
    if zhi1 in kong:
        return "旬空"
    else:
        return ""

def get_muku(d1: str, muku: str) -> str:
    """
    判断第一个地支是否为墓库, 以及第二个地支是否能入该墓库.

    :param d1: 第一个地支 (待判断是否入墓库)
    :param muku: 第二个地支 (待判断是否为墓库)
    """

    dstzhi = _extract_zhi(d1)
    mukuzhi = _extract_zhi(muku)
    if not mukuzhi or not dstzhi:
        return ""

    # 定义墓库与其对应的可入墓地支集合
    # 辰为水墓(亥/子), 戌为火墓(巳/午), 丑为金墓(申/酉), 未为木墓(寅/卯)
    TOMB_MAP = {
        "辰": {"branches": {"亥", "子", "辰", "戌", "丑", "未"}, "name": "水墓"},
        "戌": {"branches": {"巳", "午"}, "name": "火墓"},
        "丑": {"branches": {"申", "酉"}, "name": "金墓"},
        "未": {"branches": {"寅", "卯"}, "name": "木墓"}
    }

    if mukuzhi not in TOMB_MAP:
        return ""

    if dstzhi in TOMB_MAP[mukuzhi]["branches"]:
        return TOMB_MAP[mukuzhi]["name"]

    return ""

def get_he3(force: List[str], option: List[str]) -> List[str]:
    """
    三合局与半合局判定函数, 半合局必须由force构成

    :param force: 必须存在的地支 (日, 月, 变/动)
    :param option: 可以不存在的地支 (静爻)
    :return: 如 ['水合: 申子辰', '水合: 申子辰缺子']
    """

    # 提取并过滤有效地支
    force_set = set(filter(None, [_extract_zhi(b) for b in force]))
    option_set = set(filter(None, [_extract_zhi(b) for b in option]))
    all_set = force_set.union(option_set)

    results = []

    for combo_set, name in const.HE3.items():
        # 第一组必须有地支参与，否则不具备主导作用，直接跳过
        force_present = combo_set.intersection(force_set)
        if not force_present:
            continue

        all_present = combo_set.intersection(all_set)

        # 获取当前三合局的标准顺序字符串 (例如 "申子辰")
        standard_order = const.HE3_ORDER_MAP.get(name, [])
        standard_str = "".join(standard_order)

        # 1. 完整三合局
        if len(all_present) == 3:
            results.append(f"{name}: {standard_str}")

        # 2. 半合局：日月动凑齐 2 个地支, 才比较有价值.
        elif len(force_present) == 2:
            missing_set = combo_set - force_present
            if missing_set:
                missing = list(missing_set)[0]
                results.append(f"{name}: {standard_str}缺{missing}")

    return results

def get_xing3(force: List[str], option: List[str]) -> List[str]:
    """
    三刑与半刑判定函数

    :param force: 必须存在的地支 (日, 月, 动)
    :param option: 可以不存在的地支 (静爻)
    :return: 如 ['无恩: 寅巳申']
    """
    # 严格限定三刑地支的标准顺序
    ORDER_MAP = {
        "无恩": ["寅", "巳", "申"],
        "恃势": ["丑", "戌", "未"],
    }

    # 提取并过滤有效地支
    force_set = set(filter(None, [_extract_zhi(b) for b in force]))
    option_set = set(filter(None, [_extract_zhi(b) for b in option]))
    all_set = force_set.union(option_set)

    results = []

    for name, order_list in ORDER_MAP.items():
        combo_set = set(order_list)
        # 必须有二个强制地支参与，否则不具备主导作用，直接跳过
        force_present = combo_set.intersection(force_set)
        if not force_present: # 日, 月, 动
            continue

        all_present = combo_set.intersection(all_set)

        # 获取当前三刑的标准顺序字符串 (例如 "寅巳申")
        standard_str = "".join(order_list)

        # 1. 完整三刑: 全局凑齐 3 个地支
        if len(all_present) == 3:
            results.append(f"{name}: {standard_str}")

        # 2. 半刑: 基本不论.
        # elif len(force_present) == 2:
        #     missing_set = (combo_set - force_present)
        #     missing = list(missing_set)[0]
        #     results.append(f"{name}: {standard_str}缺{missing}")

    return results

def get_mark3(d1: str, desche3: List[str], descxing3: List[str], yao_exlude = "", is_option = False) -> str:
    """
    通过字符串频次直接判断地支是否存在于合局或刑局中.

    :param target_zhi: 目标地支 (如 '申', '辰')
    :param desche3: 三合列表 (如 ['水合: 申子辰缺辰'])
    :param descxing3: 三刑列表
    :param yao_exlude: 强制地支列表/集合，用于排除重复提示
    :param is_option: 当前输入的 d1 是否属于可选地支 (如静爻/伏神)
    :return: "双㊂", "合㊂", "刑㊂", 或 ""
    """
    target_zhi = _extract_zhi(d1)
    if not target_zhi:
        return ""

    if yao_exlude and is_option:
        exlude_set = set(filter(None, [_extract_zhi(b) for b in yao_exlude]))
        if target_zhi in exlude_set:
            return ""

    # 在描述字符串中，如果地支存在且未缺失，它只会出现 1 次
    # 如果地支缺失 (如 '申子辰缺辰')，它会出现在标准名和缺字后，共出现 2 次
    matched_he = any(desc.count(target_zhi) == 1 for desc in desche3)
    matched_xing = any(desc.count(target_zhi) == 1 for desc in descxing3)

    if matched_he and matched_xing:
        return "双㊂"
    elif matched_he:
        return "合㊂"
    elif matched_xing:
        return "刑㊂"

    return ""

def get_guaci(name=None):
    import pickle

    try:
        raw_name = re.sub(r'[\u4DC0-\u4DFF\s ]', '', name)
        result = Path(__file__).parent / 'data' / 'guaci.pkl'
        result = pickle.loads(result.read_bytes())
        result = result.get(raw_name)

        return result
    except Exception as ex:
        logger.exception(ex)
