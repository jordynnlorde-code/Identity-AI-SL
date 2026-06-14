import time

REQUEST_LOG = []

def log_request(data):
    timestamp = time.strftime("%H:%M:%S")
    REQUEST_LOG.append(f"[{timestamp}] {data}")
    if len(REQUEST_LOG) > 50:
        REQUEST_LOG.pop(0)
