from collections.abc import Callable
from typing import Any

from src.workers.schemas import Request, Response
from src.workers.tasks import create_game_events, create_report

Task = Callable[..., dict[str, Any]]


class Handler:
    _task_map: dict[str, Task] = {"report": create_report, "events": create_game_events}

    def _resolve(self, name: str) -> Task:
        return self._task_map[name]

    def process(self, message: Request) -> Response:
        handler = self._resolve(message.name)
        try:
            result = handler(message.payload)
            return Response(id=message.id, done=True, payload=result)
        except Exception:
            return Response(id=message.id, done=False, payload={})
