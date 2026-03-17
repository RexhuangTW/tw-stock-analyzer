"""初始化模組導入路徑"""
import sys
from pathlib import Path

# 將專案根目錄加入 Python path
project_root = Path(__file__).parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
