# fitbit_client/resources/subscription.py

# Standard library imports
from typing import Any
from typing import Dict
from typing import Optional

# Local imports
from fitbit_client.exceptions import ValidationException
from fitbit_client.resources.base import BaseResource
from fitbit_client.resources.constants import SubscriptionCategory


class SubscriptionResource(BaseResource):
    """
    Handles Fitbit Subscription API endpoints for managing webhook notifications
    when users have new data available. This prevents the need to poll for updates.

    Subscriptions can be created for specific data categories or for all categories.
    Note that creating both specific and all-category subscriptions will result in
    duplicate notifications.

    API Reference: https://dev.fitbit.com/build/reference/web-api/subscription/
    """

    def create_subscription(
        self,
        subscription_id: str,
        category: Optional[SubscriptionCategory] = None,
        subscriber_id: Optional[str] = None,
        user_id: str = "-",
    ) -> Dict[str, Any]:
        """
        Creates a subscription to notify the application when a user has new data.

        Args:
            subscription_id: Unique ID for this subscription (max 50 chars)
            category: Optional specific data category to subscribe to
            subscriber_id: Optional subscriber ID from dev.fitbit.com
            user_id: Optional user ID, defaults to current user

        Returns:
            Subscription details including category and owner info

        Raises:
            ValidationException: If subscription_id exceeds 50 characters
            InvalidRequestException: If subscriber_id is invalid

        Note:
            Each subscriber can only have one subscription per user's category.
            If no category is specified, all categories will be subscribed,
            but this requires all relevant OAuth scopes.
        """
        if len(subscription_id) > 50:
            raise ValidationException(
                message="subscription_id must not exceed 50 characters",
                status_code=400,
                error_type="validation",
                field_name="subscription_id",
            )

        endpoint = (
            f"{category.value}/apiSubscriptions/{subscription_id}.json"
            if category
            else f"apiSubscriptions/{subscription_id}.json"
        )

        headers = {}
        if subscriber_id:
            headers["X-Fitbit-Subscriber-Id"] = subscriber_id

        return self._make_request(endpoint, user_id=user_id, headers=headers, http_method="POST")

    def delete_subscription(
        self,
        subscription_id: str,
        category: Optional[SubscriptionCategory] = None,
        subscriber_id: Optional[str] = None,
        user_id: str = "-",
    ) -> Dict[str, Any]:
        """
        Deletes a subscription for a specific user.

        Args:
            subscription_id: ID of the subscription to delete
            category: Optional specific data category subscription
            subscriber_id: Optional subscriber ID from dev.fitbit.com
            user_id: Optional user ID, defaults to current user
        """
        endpoint = (
            f"{category.value}/apiSubscriptions/{subscription_id}.json"
            if category
            else f"apiSubscriptions/{subscription_id}.json"
        )

        headers = {}
        if subscriber_id:
            headers["X-Fitbit-Subscriber-Id"] = subscriber_id

        return self._make_request(endpoint, user_id=user_id, headers=headers, http_method="DELETE")

    def get_subscription_list(
        self,
        category: Optional[SubscriptionCategory] = None,
        subscriber_id: Optional[str] = None,
        user_id: str = "-",
    ) -> Dict[str, Any]:
        """
        Gets a list of subscriptions created by your application for a user.

        Args:
            category: Optional specific data category to list
            subscriber_id: Optional subscriber ID from dev.fitbit.com
            user_id: Optional user ID, defaults to current user

        Returns:
            List of subscription details including categories and owner info

        Note:
            For best practice, maintain this list in your application and only use
            this endpoint periodically to ensure data consistency.
        """
        endpoint = (
            f"{category.value}/apiSubscriptions.json" if category else "apiSubscriptions.json"
        )

        headers = {}
        if subscriber_id:
            headers["X-Fitbit-Subscriber-Id"] = subscriber_id

        return self._make_request(endpoint, user_id=user_id, headers=headers)
