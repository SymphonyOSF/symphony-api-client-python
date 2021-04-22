from ..auth.exception import AuthUnauthorizedError

try:
    from inspect import iscoroutinefunction
except ImportError:
    iscoroutinefunction = None

from typing import Callable
from functools import wraps

from tenacity.retry import retry_if_exception
from tenacity import stop_after_attempt, wait_exponential, RetryCallState

from symphony.bdk.core.config.model.bdk_retry_config import BdkRetryConfig
from symphony.bdk.gen import ApiException

from ._asyncio import AsyncRetrying


def retry(*dargs, **dkw):  # noqa
    """A decorator that provides a mechanism to repeat requests

    :param dargs: positional arguments passed to be added or to override the default configuration
    :param dkw: keyword arguments passed to be added or to override the default configuration
    """
    # support both @retry and @retry() as valid syntax
    if len(dargs) == 1 and callable(dargs[0]):
        return retry()(dargs[0])
    else:
        def retry_decorator(fun: Callable):
            @wraps(fun)
            def decorator_f(self, *args, **kwargs):
                """Fetches a BdkRetryConfiguration object from the instance of the called function

                If no _retry_config attribute is present, use a default AsyncRetrying configuration
                Passed retry configuration arguments override the default configuration"""
                default_kwargs = {}
                retry_config: BdkRetryConfig = getattr(self, '_retry_config', None)
                if retry_config is not None:
                    config_kwargs = dict(retry=retry_if_exception(is_network_or_minor_error),
                                         wait=wait_exponential(multiplier=retry_config.multiplier,
                                                               min=retry_config.initial_interval,
                                                               max=retry_config.max_interval),
                                         stop=stop_after_attempt(retry_config.max_attempts),
                                         reraise=True)
                    default_kwargs.update(config_kwargs)
                # update default arguments by the ones passed as parameters
                default_kwargs.update(**dkw)
                return AsyncRetrying(*dargs, **default_kwargs).wraps(fun)(self, *args, **kwargs)

            return decorator_f

        return retry_decorator


def is_network_or_minor_error(exception: Exception) -> bool:
    """Checks if the exception is a network issue or an :py:class:`ApiException` minor error
    This is the default function used to check if a given exception should lead to a retry
    """
    if isinstance(exception, ApiException):
        if exception.status == 500 or exception.status == 401 or exception.status == 429:
            return True
    return isinstance(exception, ConnectionError)

def authentication_retry(retry_state: RetryCallState):
    unauthorized_message = "Service account is not authorized to authenticate. Check if credentials are valid."
    if retry_state.outcome.failed:
        exception = retry_state.outcome.exception()
        if isinstance(exception, ApiException):
            if exception.status == 401:
                raise AuthUnauthorizedError(unauthorized_message, exception) from exception