# fitbit_client/resources/subscription.py

# Standard library imports
from typing import Optional
from typing import cast

# Local imports
from fitbit_client.resources._base import BaseResource
from fitbit_client.resources._constants import SubscriptionCategory
from fitbit_client.utils.types import JSONDict


class SubscriptionResource(BaseResource):
    """Provides access to Fitbit Subscription API for managing webhook notifications.

    This resource enables applications to receive real-time notifications when users have
    new data available, eliminating the need to continuously poll the API. Subscriptions
    can be created for specific data categories (activities, body, foods, sleep) or for
    all categories at once.

    Developer Guide: https://dev.fitbit.com/build/reference/web-api/developer-guide/using-subscriptions/
    API Reference: https://dev.fitbit.com/build/reference/web-api/subscription/

    Required Scopes:
        - For activity subscriptions: activity
        - For body subscriptions: weight
        - For foods subscriptions: nutrition
        - For sleep subscriptions: sleep
        - For all-category subscriptions: all relevant scopes above

    Implementation Requirements:
        1. A verification endpoint that responds to GET requests with verification challenges
        2. A notification endpoint that processes POST requests with updates
        3. Proper SSL certificates (self-signed certificates are not supported)
        4. Adherence to rate limits and notification processing timeouts

    Note:
        Currently only `get_subscription_list` is fully implemented in this library.
        The `create_subscription` and `delete_subscription` methods are defined but raise
        NotImplementedError. Their documentation is provided as a reference for future implementation.

        Creating both specific and all-category subscriptions will result in duplicate
        notifications for the same data changes, so choose one approach.

        Subscription notifications are sent as JSON payloads with information about what
        changed, but not the actual data. Your application still needs to make API calls
        to retrieve the updated data.
    """

    def create_subscription(
        self,
        subscription_id: str,
        category: Optional[SubscriptionCategory] = None,
        subscriber_id: Optional[str] = None,
        user_id: str = "-",
        debug: bool = False,
    ) -> JSONDict:
        """Creates a subscription to notify the application when a user has new data.

        API Reference: https://dev.fitbit.com/build/reference/web-api/subscription/create-subscription/

        Args:
            subscription_id: Unique ID for this subscription (max 50 chars)
            category: Optional specific data category to subscribe to (e.g., SubscriptionCategory.ACTIVITIES,
                     SubscriptionCategory.BODY). If None, subscribes to all categories.
            subscriber_id: Optional subscriber ID from dev.fitbit.com app settings
            user_id: Optional user ID, defaults to current user ("-")
            debug: If True, prints a curl command to stdout to help with debugging (default: False)

        Returns:
            JSONDict: Subscription details including collection type, owner and subscription identifiers

        Raises:
            fitbit_client.exceptions.ValidationException: If subscription_id exceeds 50 characters
            fitbit_client.exceptions.InvalidRequestException: If subscriber_id is invalid
            fitbit_client.exceptions.InsufficientScopeException: If missing required OAuth scopes for the category

        Note:
            Each subscriber can only have one subscription per user's category.
            If no category is specified, all categories will be subscribed,
            but this requires all relevant OAuth scopes (activity, weight, nutrition, sleep).

            Subscribers must implement a verification endpoint that can respond to both
            GET (verification) and POST (notification) requests. See the API documentation
            for details on endpoint requirements.
        """
        raise NotImplementedError
        # if len(subscription_id) > 50:
        #     raise ValidationException(
        #         message="subscription_id must not exceed 50 characters",
        #         error_type="validation",
        #         field_name="subscription_id",
        #     )

        # endpoint = (
        #     f"{category.value}/apiSubscriptions/{subscription_id}.json"
        #     if category
        #     else f"apiSubscriptions/{subscription_id}.json"
        # )

        # headers = {}
        # if subscriber_id:
        #     headers["X-Fitbit-Subscriber-Id"] = subscriber_id

        # return self._make_request(
        #     endpoint, user_id=user_id, headers=headers, http_method="POST", debug=debug
        # )

    def delete_subscription(
        self,
        subscription_id: str,
        category: Optional[SubscriptionCategory] = None,
        subscriber_id: Optional[str] = None,
        user_id: str = "-",
        debug: bool = False,
    ) -> JSONDict:
        """Deletes a subscription for a specific user.

        API Reference: https://dev.fitbit.com/build/reference/web-api/subscription/delete-subscription/

        Args:
            subscription_id: ID of the subscription to delete
            category: Optional specific data category subscription (e.g., SubscriptionCategory.ACTIVITIES,
                     SubscriptionCategory.BODY). Must match the category used when creating the subscription.
            subscriber_id: Optional subscriber ID from dev.fitbit.com app settings
            user_id: Optional user ID, defaults to current user ("-")
            debug: If True, prints a curl command to stdout to help with debugging (default: False)

        Returns:
            JSONDict: Empty dictionary on successful deletion

        Raises:
            fitbit_client.exceptions.InvalidRequestException: If subscription_id is invalid
            fitbit_client.exceptions.NotFoundException: If subscription doesn't exist
            fitbit_client.exceptions.AuthorizationException: If authentication fails or insufficient permissions

        Note:
            When deleting a subscription:
            - You must specify the same category that was used when creating the subscription
            - After deletion, your application will no longer receive notifications for that user's data
            - You may want to maintain a local record of active subscriptions to ensure proper cleanup
        """
        raise NotImplementedError
        # endpoint = (
        #     f"{category.value}/apiSubscriptions/{subscription_id}.json"
        #     if category
        #     else f"apiSubscriptions/{subscription_id}.json"
        # )

        # headers = {}
        # if subscriber_id:
        #     headers["X-Fitbit-Subscriber-Id"] = subscriber_id

        # return self._make_request(
        #     endpoint, user_id=user_id, headers=headers, http_method="DELETE", debug=debug
        # )

    def get_subscription_list(
        self,
        category: Optional[SubscriptionCategory] = None,
        subscriber_id: Optional[str] = None,
        user_id: str = "-",
        debug: bool = False,
    ) -> JSONDict:
        """Returns a list of subscriptions created by your application for a user.

        API Reference: https://dev.fitbit.com/build/reference/web-api/subscription/get-subscription-list/

        Args:
            category: Optional specific data category to filter by (e.g., SubscriptionCategory.ACTIVITIES,
                     SubscriptionCategory.BODY). If omitted, returns all subscriptions.
            subscriber_id: Optional subscriber ID from your app settings on dev.fitbit.com
            user_id: Optional user ID, defaults to current user ("-")
            debug: If True, prints a curl command to stdout to help with debugging (default: False)

        Returns:
            JSONDict: List of active subscriptions with their collection types and identifiers

        Raises:
            fitbit_client.exceptions.InvalidRequestException: If request parameters are invalid
            fitbit_client.exceptions.AuthorizationException: If authentication fails
            fitbit_client.exceptions.InsufficientScopeException: If missing scopes for requested categories

        Note:
            For best practice, maintain subscription information in your own database
            and only use this endpoint periodically to ensure data consistency.

            Each subscription requires the appropriate OAuth scope for that category:
            - activities: activity scope
            - body: weight scope
            - foods: nutrition scope
            - sleep: sleep scope

            This endpoint returns all subscriptions for a user across all applications
            associated with your subscriber ID.
        """
        endpoint = (
            f"{category.value}/apiSubscriptions.json" if category else "apiSubscriptions.json"
        )

        headers = {}
        if subscriber_id:
            headers["X-Fitbit-Subscriber-Id"] = subscriber_id

        result = self._make_request(endpoint, user_id=user_id, headers=headers, debug=debug)
        return cast(JSONDict, result)
