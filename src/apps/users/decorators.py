from django.contrib.auth.decorators import user_passes_test
from django.utils.decorators import method_decorator


def forbidden_user(function=None, forbidden_usertypes=[]):
    """
    Decorator for views that checks that the user allowed, redirecting
    to the log-in page if necessary.
    """
    actual_decorator = user_passes_test(
        lambda u: u.__class__.__name__ not in forbidden_usertypes,
    )
    if function:
        return actual_decorator(function)
    return actual_decorator


def ForbiddenUser(cls=None, **login_args):
    """
    Apply the ``auth_required`` decorator to all the handlers in a class-based
    view that delegate to the ``dispatch`` method.

    Usage:
      @LoginRequired
      class MyListView (ListView):
        ...
    """
    if cls is not None:
        # Check that the View class is a class-based view. This can either be
        # done by checking inheritance from django.views.generic.View, or by
        # checking that the ViewClass has a ``dispatch`` method.
        if not hasattr(cls, 'dispatch'):
            raise TypeError(('View class is not valid: %r.  Class-based views '
                             'must have a dispatch method.') % cls)

        original = cls.dispatch
        modified = method_decorator(forbidden_user(**login_args))(original)
        cls.dispatch = modified

        return cls

    else:
        # If ViewClass is None, then this was applied as a decorator with
        # parameters. An inner decorator will be used to capture the ViewClass,
        # and return the actual decorator method.
        def inner_decorator(inner_cls):
            return ForbiddenUser(inner_cls, **login_args)

        return inner_decorator
