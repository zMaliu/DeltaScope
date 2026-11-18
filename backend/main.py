import json
import socket
from urllib.error import HTTPError, URLError
from urllib.request import urlopen

from app import create_app
from app.config import FLASK_DEBUG, FLASK_HOST, FLASK_PORT

app = create_app()


def _probe_host(host):
    return "127.0.0.1" if host in {"", "0.0.0.0", "::"} else host


def _port_is_open(host, port):
    try:
        with socket.create_connection((_probe_host(host), port), timeout=0.5):
            return True
    except OSError:
        return False


def _existing_backend_state(host, port):
    base_url = "http://{}:{}".format(_probe_host(host), port)
    try:
        with urlopen(base_url + "/health/live", timeout=1) as response:
            live = json.loads(response.read().decode("utf-8"))
        if live.get("status") != "ok":
            return "unrecognized"
        with urlopen(base_url + "/health/ready", timeout=2) as response:
            ready = json.loads(response.read().decode("utf-8"))
            return "ready" if response.status == 200 and ready.get("status") == "ok" else "not_ready"
    except HTTPError as error:
        if error.code == 503:
            return "not_ready"
        return "unrecognized"
    except (OSError, URLError, ValueError, TypeError):
        return "unrecognized"


def main():
    if _port_is_open(FLASK_HOST, FLASK_PORT):
        state = _existing_backend_state(FLASK_HOST, FLASK_PORT)
        if state == "ready":
            print("DeltaScope backend is already running and ready at http://{}:{}".format(
                _probe_host(FLASK_HOST), FLASK_PORT
            ))
            return
        if state == "not_ready":
            raise SystemExit(
                "DeltaScope backend is already listening on port {}, but it is not ready. "
                "Check /health/ready and the database service.".format(FLASK_PORT)
            )
        raise SystemExit(
            "Port {} is occupied by another program. Stop that process or set "
            "FLASK_RUN_PORT to an unused port.".format(FLASK_PORT)
        )
    app.run(host=FLASK_HOST, port=FLASK_PORT, debug=FLASK_DEBUG)


if __name__ == "__main__":
    main()
