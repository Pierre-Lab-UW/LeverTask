from LeverEventBase import LeverEventBase
from LeverBase import LeverBase, STATE_PRESSED
from typing import Callable, Optional, Dict




class LeverStateChangedEvent(LeverEventBase):
    def __init__(
        self,
        event_name: str,
        lever: LeverBase,
        callback_fn: Optional[Callable[[LeverBase, int, float], None]]
    ) -> None:
        super().__init__(event_name, lever)
        self.callback_fn: Optional[Callable[[LeverBase, int, float], None]] = callback_fn

    def on_lever_state_change(self, new_lever_state: int, time_since_last_change: float) -> None:
        if self.callback_fn:
            self.callback_fn(self.lever, new_lever_state, time_since_last_change)