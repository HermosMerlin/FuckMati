"""
core.py — 状态机、托盘图标、配置加载
"""
from __future__ import annotations

import json
import logging
import threading
from dataclasses import dataclass
from enum import Enum, auto
from pathlib import Path
from typing import Callable

from PIL import Image, ImageDraw

log = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# 配置
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class Config:
    api_key: str
    base_url: str
    model: str
    typing_delay_ms: int
    typing_jitter: bool
    typing_jitter_range_ms: int
    long_pause_enabled: bool
    long_pause_chance: float
    long_pause_min_ms: int
    long_pause_max_ms: int
    system_prompt: str

    @classmethod
    def load(cls, path: Path | str = "config.json") -> "Config":
        p = Path(path)
        if not p.exists():
            raise FileNotFoundError(f"配置文件不存在: {p.absolute()}")
        with p.open("r", encoding="utf-8") as f:
            data = json.load(f)
        return cls(
            api_key=data.get("api_key", ""),
            base_url=data.get("base_url", "https://api.openai.com/v1"),
            model=data.get("model", "gpt-4o-mini"),
            typing_delay_ms=data.get("typing_delay_ms", 80),
            typing_jitter=data.get("typing_jitter", True),
            typing_jitter_range_ms=data.get("typing_jitter_range_ms", 20),
            long_pause_enabled=data.get("long_pause_enabled", True),
            long_pause_chance=data.get("long_pause_chance", 0.3),
            long_pause_min_ms=data.get("long_pause_min_ms", 3000),
            long_pause_max_ms=data.get("long_pause_max_ms", 12000),
            system_prompt=data.get(
                "system_prompt",
                "你是一位C语言编程专家。用户会粘贴一道C语言题目，请直接给出完整、可编译的C语言代码作为答案。注意：代码中不要包含任何注释，不要包含解释说明，只输出纯代码。",
            ),
        )


# ---------------------------------------------------------------------------
# 状态机
# ---------------------------------------------------------------------------
class State(Enum):
    IDLE = auto()       # 空闲（灰色）
    REQUESTING = auto() # 请求中（黄色）
    READY = auto()      # 已就绪（绿色）
    TYPING = auto()     # 输出中（蓝色）
    ERROR = auto()      # 错误（红色）


class StateMachine:
    """
    线程安全的状态机（v3）。

    状态语义：
      IDLE(灰)    = 正在检测 API（启动或重试）
      REQUESTING(黄)= 正在向 AI 请求答案（业务请求）
      READY(绿)   = 系统就绪 / 答案已缓存
      TYPING(蓝)  = 正在输出答案
      ERROR(红)   = API 检测失败 / 请求失败

    流转规则：
      IDLE --(检测成功)--> READY
      IDLE --(检测失败)--> ERROR --(重试)--> IDLE
      READY --(热键)--> REQUESTING --(成功)--> READY
      READY --(热键,有缓存)--> TYPING --(完成)--> READY
      REQUESTING --(失败)--> ERROR --(重试)--> IDLE
      任意状态 --(强制重置)--> IDLE
    """

    _TRANSITIONS: dict[State, tuple[State, ...]] = {
        State.IDLE: (State.READY, State.ERROR),
        State.REQUESTING: (State.READY, State.ERROR),
        State.READY: (State.REQUESTING, State.TYPING),
        State.TYPING: (State.READY,),
        State.ERROR: (State.IDLE,),
    }

    def __init__(self, on_change: Callable[[State], None] | None = None):
        self._state = State.IDLE
        self._lock = threading.Lock()
        self._on_change = on_change

    @property
    def state(self) -> State:
        with self._lock:
            return self._state

    def transition(self, target: State) -> bool:
        """尝试状态转换，成功返回 True。"""
        with self._lock:
            allowed = self._TRANSITIONS.get(self._state, ())
            if target not in allowed:
                log.debug("无效转换: %s -> %s", self._state.name, target.name)
                return False
            self._state = target
            log.info("状态切换: %s", target.name)

        if self._on_change:
            self._on_change(target)

        return True

    def set_on_change(self, callback: Callable[[State], None] | None) -> None:
        self._on_change = callback

    def force_reset(self) -> None:
        """强制回到 IDLE（灰色，重新检测）。"""
        with self._lock:
            old = self._state
            self._state = State.IDLE
        log.info("强制重置: %s -> IDLE", old.name)
        if self._on_change:
            self._on_change(State.IDLE)


# ---------------------------------------------------------------------------
# 图标渲染器（Pillow 动态生成）
# ---------------------------------------------------------------------------
class IconRenderer:
    """
    为系统托盘生成 16x16 RGBA 图标。
    使用低饱和度莫兰迪色系，确保隐蔽不刺眼。
    """

    _PALETTE = {
        State.IDLE:       "#9CA3AF",  # 中性灰
        State.REQUESTING: "#D4A373",  # 暗沙金
        State.READY:      "#81B29A",  # 灰绿
        State.TYPING:     "#8D99AE",  # 灰蓝
        State.ERROR:      "#E07A5F",  # 砖红
    }

    _SIZE = 16

    @classmethod
    def render(cls, state: State) -> Image.Image:
        hex_color = cls._PALETTE.get(state, cls._PALETTE[State.IDLE])
        rgb = tuple(int(hex_color[i : i + 2], 16) for i in (1, 3, 5))
        img = Image.new("RGBA", (cls._SIZE, cls._SIZE), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        # 实心圆角矩形，完全填充，无描边，无文字
        margin = 2
        draw.rounded_rectangle(
            (margin, margin, cls._SIZE - margin, cls._SIZE - margin),
            radius=4,
            fill=(*rgb, 255),
        )
        return img
