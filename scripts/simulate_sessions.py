from __future__ import annotations

import argparse
import copy
import json
from urllib.request import Request, urlopen

from seed import SESSIONS


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--api-url", required=True)
    parser.add_argument("--count", type=int, default=5)
    args = parser.parse_args()

    for index in range(args.count):
        payload = copy.deepcopy(SESSIONS[index % len(SESSIONS)])
        payload["sessionId"] = f"{payload['sessionId']}_{index}"
        request = Request(
            f"{args.api_url.rstrip('/')}/sessions",
            data=json.dumps(payload).encode("utf-8"),
            headers={"content-type": "application/json"},
            method="POST",
        )
        with urlopen(request, timeout=10) as response:
            print(response.status, response.read().decode("utf-8"))


if __name__ == "__main__":
    main()
