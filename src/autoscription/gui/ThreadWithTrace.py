import sys
import threading
from types import FrameType
from typing import Any


class ThreadWithTrace(threading.Thread):
    def __init__(self, *args: Any, **keywords: Any) -> None:
        super().__init__(*args, **keywords)
        self.killed: bool = False

    def start(self) -> None:
        threading.Thread.start(self)

    def run(self) -> None:
        sys.settrace(self.globaltrace)
        super().run()

    def globaltrace(self, frame: FrameType, event: str, arg: Any) -> Any:  # noqa: ignore[U100]
        if event == "call":
            return self.localtrace
        else:
            return None

    def localtrace(self, frame: FrameType, event: str, arg: Any) -> Any:  # noqa: ignore[U100]
        if self.killed:
            if event == "line":
                raise SystemExit()
        return self.localtrace

    def kill(self) -> None:
        self.killed = True
