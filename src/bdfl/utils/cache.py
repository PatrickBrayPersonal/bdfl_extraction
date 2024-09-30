import os
import pickle
import functools
import time
import hashlib
import json
from loguru import logger


def disk_cache(cache_dir, expiration=86400):  # 86400 seconds = 1 day
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Check if caching is disabled via environment variable
            if os.environ.get("CACHE", "").lower() == "false":
                return func(*args, **kwargs)

            # Create a consistent, unique filename based on the function name and arguments
            arg_string = json.dumps(args) + json.dumps(kwargs, sort_keys=True)
            hash_object = hashlib.md5(arg_string.encode())
            file_hash = hash_object.hexdigest()
            cache_file = os.path.join(cache_dir, f"{func.__name__}_{file_hash}.pkl")

            # Check if cache file exists and is not expired
            if os.path.exists(cache_file):
                modification_time = os.path.getmtime(cache_file)
                if time.time() - modification_time < expiration:
                    logger.info(f"loading cached {cache_file}")
                    with open(cache_file, "rb") as f:
                        return pickle.load(f)

            # If not cached, expired, or caching is disabled, call the original function
            result = func(*args, **kwargs)

            # Save the result to cache
            os.makedirs(cache_dir, exist_ok=True)
            with open(cache_file, "wb") as f:
                pickle.dump(result, f)

            return result

        return wrapper

    return decorator
