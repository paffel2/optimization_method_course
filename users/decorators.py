from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.decorators import user_passes_test


def user_has_access(
    view_func=None,
    redirect_field_name=REDIRECT_FIELD_NAME,
    login_url="computations:login",
):

    actual_decorator = user_passes_test(
        lambda u: (
            u.is_staff
            or u.is_superuser
            or (hasattr(u, "is_worker") and u.is_researcher)
        )
        and u.is_active,
        login_url=login_url,
        redirect_field_name=redirect_field_name,
    )
    if view_func:
        return actual_decorator(view_func)
    return actual_decorator
