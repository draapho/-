from __future__ import annotations

import os
import sys

# 1. 获取当前脚本所在目录
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

# 2. 清理可能导致冲突的子路径，只保留根目录
if PROJECT_ROOT in sys.path:
    sys.path.remove(PROJECT_ROOT)
sys.path.insert(0, PROJECT_ROOT)

import najia.gui

if __name__ == "__main__":
    najia.gui.main()
