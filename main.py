from json import dumps
from json import load

from client import FitbitClient


def print_json(obj):
    print(dumps(obj, ensure_ascii=False, indent=2))


def main():
    with open("secrets.json") as f:
        secrets = load(f)

    # Initialize Fitbit OAuth2 PKCE flow
    client = FitbitClient(**secrets, use_callback_server=True)

    try:
        client.authenticate()
        profile = client.user.get_profile()
        print_json(profile)

    except Exception as e:
        print(f"Error: {str(e)}")


if __name__ == "__main__":
    main()
