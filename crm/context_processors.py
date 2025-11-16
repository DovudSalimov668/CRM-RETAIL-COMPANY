from __future__ import annotations

from typing import Dict, Any

from django.contrib.auth import get_user_model

from .models import Customer

User = get_user_model()


def customer_profile(request) -> Dict[str, Any]:
    """
    Inject authenticated customer's profile into every template.
    Safe-guards staff and anonymous requests.
    """
    user = getattr(request, 'user', None)
    if not user or not user.is_authenticated or user.is_staff:
        return {}

    try:
        return {'customer_profile': user.customer_profile}
    except (Customer.DoesNotExist, AttributeError):
        return {}

