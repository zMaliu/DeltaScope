from app import create_app
from app.config import FLASK_DEBUG, FLASK_HOST, FLASK_PORT

app = create_app()


def main():
    app.run(host=FLASK_HOST, port=FLASK_PORT, debug=FLASK_DEBUG)


if __name__ == "__main__":
    main()
