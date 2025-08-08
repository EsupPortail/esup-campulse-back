from functools import wraps
import time

from rest_framework import generics

from django.db import connection
from django.test.utils import CaptureQueriesContext


def capture_queries(show_queries=False):
    def decorator(view_func):
        @wraps(view_func)
        def wrapper_view(*args, **kwargs):
            with CaptureQueriesContext(connection) as queries:
                t = time.time()
                func = view_func(*args, **kwargs)
                capture_repr = f'{view_func.__module__} {view_func.__name__}'
                print(f'===== {capture_repr}')
                print(f'\t==> Nb de requêtes : {len(queries.captured_queries)}, Temps : {time.time() - t:.2f} sec')
                if show_queries:
                     print('\n'.join(f'\t=> {q["sql"]}' for q in queries.captured_queries))
            return func
        return wrapper_view
    return decorator
