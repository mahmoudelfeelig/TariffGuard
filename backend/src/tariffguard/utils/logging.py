from __future__ import annotations

import json
import logging
from typing import Any

logger = logging.getLogger("tariffguard")
logger.setLevel(logging.INFO)


def log(event: str, **fields: Any) -> None:
    logger.info(json.dumps({"event": event, **fields}, default=str))
