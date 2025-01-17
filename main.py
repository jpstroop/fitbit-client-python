from json import dumps
from json import load

from client import FitbitClient


def print_json(obj):
    print(dumps(obj, ensure_ascii=False, indent=2))


def main():
    # Example usage:
    """
    client = FitbitClient(...)
    client.authenticate()

    # Profile operations
    profile = client.profile.get_profile()
    badges = client.profile.get_badges()

    # Update profile
    client.profile.update_profile({
        'gender': 'MALE',
        'height': 180.0,
        'weight': 75.0
    })

    # Food logging
    client.nutrition.log_food(
        food_name="Banana",
        calories=105,
        meal_type_id=1  # Breakfast
    )

    # Search foods
    bananas = client.nutrition.search_foods("banana")

    # Water tracking
    client.nutrition.log_water(amount=8, unit='cup')
    water_logs = client.nutrition.get_water_logs()
    """
    with open("secrets.json") as f:
        secrets = load(f)

    # Fitbit OAuth2 configuration
    client_id = secrets["client_id"]  # Get this from dev.fitbit.com
    client_secret = secrets["client_secret"]  # Get this from dev.fitbit.com
    redirect_uri = secrets["redirect_uri"]  # Must match what you registered

    # Initialize Fitbit OAuth2 PKCE flow
    client = FitbitClient(client_id=client_id, client_secret=client_secret, redirect_uri=redirect_uri)

    try:
        client.authenticate()
        profile = client.user.get_profile()
        print_json(profile)
        # activities = client.activity.get_daily_activity()
        # sleep = client.sleep.get_sleep_logs()
        # heart = client.heart.get_heart_rate_intraday()
    except Exception as e:
        print(f"Error: {str(e)}")


if __name__ == "__main__":
    main()
