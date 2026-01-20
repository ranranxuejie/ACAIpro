# AI 助手 Pro 主包

# 导出主要模块
from .config import CONFIG, load_config
from .core import AIClient
from .ui import render_ui
from .utils import process_ai_content, ensure_current_model

__version__ = "1.0.0"
__author__ = "AI Assistant Pro Team"
