"""AutoSHiFt: Automatically redeem Gearbox SHiFT Codes"""

from .auto import run as run_cli
from .tui import run_tui

__all__ = ["run_cli", "run_tui"]