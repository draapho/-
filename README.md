纳甲六爻排盘项目
================

[![image](https://img.shields.io/pypi/v/najia.svg)](https://pypi.python.org/pypi/najia)
[![image](https://img.shields.io/travis/bopo/najia.svg)](https://travis-ci.org/bopo/najia)
[![Documentation Status](https://readthedocs.org/projects/najia/badge/?version=latest)](https://najia.readthedocs.io/en/latest/?badge=latest)
[![Updates](https://pyup.io/repos/github/bopo/najia/shield.svg)](https://pyup.io/repos/github/bopo/najia/)

Python Boilerplate contains all the boilerplate you need to create a
Python package.

-   Free software: MIT license
-   Documentation: <https://najia.readthedocs.io>.


> # []: 该软件对六爻纳甲的判断条件说明
>
> 关系: 日月表示日辰月建的地支五行. 各爻动爻静爻表示这些爻的地支五行. 六爻纳甲就是基于地支五行的相互关系进行分析的.
>
> 五行: 日月对各爻, 以"相旺休囚死"标注. 变爻对动爻,
> 以化"生(回头生)克(回头克)泄(化生)耗(化克)退进伏"标注.
> 动爻之间, 动爻对静爻, 未作标注, 需以五行自行判断.
>
> 暗动: 静爻日冲, 标记"△", 提示为可能的暗动, 需人工自行判断静爻气机是否得日月相旺或动爻生伏.
>
> 冲合: 日月对各爻, 动爻之间, 动爻对静爻, 会论冲合.
>
> 三合: 动爻变爻暗动, 得一加日月可成合, 得二则至少成半合, 可与静爻伏神成三合. 需人工综合判断效用.
>
> 三刑: 动爻变爻暗动, 得一加日月可成刑, 得二加之静爻, 则提示为三刑. 需人工综合判断效用.
>
> 自刑: 同爻动变之间论自刑. 其它情况皆不论自刑. 测试下来, 只有乾为天变震为雷, 有辰辰自刑.
>
> 旬空和库墓: 相关的爻位会以"空", "墓"提醒.


输入
---------
0为少阴(静), 1为少阳(静), 2为老阴(动), 3为老阳(动)
卦爻输入顺序为 [初, 二, 三, 四, 五, 上]
显示1适配md格式. 显示2适配终端.

2026年4月3日. UI初版. 运行指令
```python
python -m najia.gui
```
也可运行 `run_gui.py` 进行调试. 或通过脚本 `_najia.bat` 运行.


依赖
----------
```powershell
python --version
# >Python 3.9 且 <4.0
pip install arrow
pip install lunar_python
```



修改

--------

20260403: 感谢网友杨博完成了初版UI.
20260816: 完善了提示功能, 优化了GUI.



Features
--------

-   全部安易卦爻
-   函数独立编写
-   测试各个函数
-   重新命名函数

阳历，阴历（干支，旬空）

-   卦符: mark (001000)，自下而上
-   卦名: name
-   变爻: bian
-   卦宫: gong
-   六亲: qin6
-   六神: god6
-   世爻: shiy, ying
-   纳甲: naja
-   纳甲五行: dzwx
-   卦宫五行: gowx

修复问题
--------

-   解决: 六神不对
-   解决: 世应也有点小BUG , 地天泰卦的世爻为3, 应爻为6
-   解决: 归魂卦世爻为3 此处返回4, 需要修改
-   解决: 归魂卦的六亲是不对的,原因是utils.py里
    判断六爻卦的卦宫名时,优先判读了if index in (1, 2, 3, 6)
    而归魂卦的世爻也在3爻,被这个条件带走了. 解决: elif hun==\'归魂\'
    这个条件调到前面即可 \* 解决: 还有一个不知是否算是错误的地方,就是bian
    变卦中的六亲,
    程序中是按变卦所在的本宫卦来定的,而不是按初始卦所属的本宫卦来定的六亲.

Credits
-------

This package was created with
[Cookiecutter](https://github.com/audreyr/cookiecutter) and the
[audreyr/cookiecutter-pypackage](https://github.com/audreyr/cookiecutter-pypackage)
project template.
