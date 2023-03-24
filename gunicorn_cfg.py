import multiprocessing

bind = "0.0.0.0:5000"  # noqa

workers = (  # noqa
    multiprocessing.cpu_count() * 2 + 1 if multiprocessing.cpu_count() > 0 else 3
)
print(f"Using {workers} workers")

worker_class = "sync"  # noqa
print(f"Using {worker_class} worker_class")

timeout = 3600  # noqa
print(f"Using {timeout} timeout")

keepalive = 60  # noqa
print(f"Using {keepalive} keepalive")

# https://docs.gunicorn.org/en/20.1.0/settings.html#capture-output
capture_output = False
accesslog = "-"
