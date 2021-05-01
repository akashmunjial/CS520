from functools import wraps
from time import sleep
from kthread import KThread

def timeout(seconds):
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
            # If res contains something, return it
            if len(res) > 0:
                return res[0]
            # Otherwise, return None
            return None
        return wrapped_func
    return decorator
