"""An implementation of the decorator design pattern for enforcing timeout.

    Typical usage example:

    @timeout(10)
    def function_that_will_return_none_after_ten_seconds():
        ...
"""
from functools import wraps
from time import sleep
from kthread import KThread


def timeout(seconds):
    """A decorator which enforces a timeout on the decorated function.

    Forces the function it decorates to return None after a specified number
    of seconds.

    Args:
        seconds: The number of seconds after which the function should return None.

    Returns:
        The decorator. When the decorated function is executed, the return value
        will either be the return value of that function if completed
        successfully within the time alotted, or else None.
    """
    def decorator(func):
        @wraps(func)
        def wrapped_func(*args, **kwargs):
            res = [] # When the thread completes successfully, this contains the result of func
            terminating_thread = False # This is set to true right before the threak is terminated
            def thread_func():
                try:
                    res.append(func(*args, **kwargs))
                except:
                    # Only raise errors that were not the result of killing the thread
                    if not terminating_thread:
                        raise
            # Create a new thread
            thread = KThread(target=thread_func)
            thread.start()
            # Join the thread until it exits or the timeout is up
            thread.join(seconds)
            # If the thread is still alive after the join call exits, kill it
            if thread.is_alive():
                terminating_thread = True
                thread.terminate()
            # If res contains something (meaning the function completed successfully), return it
            if len(res) > 0:
                return res[0]
            # Otherwise, return None
            return None
        return wrapped_func
    return decorator
