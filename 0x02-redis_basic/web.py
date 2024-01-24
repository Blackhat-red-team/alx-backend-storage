import requests
from functools import lru_cache
from datetime import datetime, timedelta

CACHE_EXPIRATION_SECONDS = 10

def track_access_count(url):
    def decorator(func):
        def wrapper(*args, **kwargs):
            key = f"count:{url}"
            access_count = kwargs.get(key, 0) + 1
            kwargs[key] = access_count
            result = func(*args, **kwargs)
            return result
        return wrapper
    return decorator

def cache_with_expiration(func):
    cache = {}

    def wrapper(url, *args, **kwargs):
        key = f"cache:{url}"
        cached_result = cache.get(key)

        if cached_result and datetime.now() - cached_result["timestamp"] < timedelta(seconds=CACHE_EXPIRATION_SECONDS):
            return cached_result["content"]
        
        result = func(url, *args, **kwargs)
        cache[key] = {"content": result, "timestamp": datetime.now()}
        return result

    return wrapper

@track_access_count("http://slowwly.robertomurray.co.uk/delay/1000/url/https://www.example.com")
@cache_with_expiration
def get_page(url):
    response = requests.get(url)
    return response.text

if __name__ == "__main__":
    # Test the get_page function
    url = "http://slowwly.robertomurray.co.uk/delay/1000/url/https://www.example.com"
    
    for _ in range(3):  # Access the URL three times
        html_content = get_page(url)
        print(f"HTML Content:\n{html_content}")

    # Sleep for more than 10 seconds to test cache expiration
    import time
    time.sleep(11)

    # Access the URL again to see if it fetches a fresh copy after expiration
    html_content = get_page(url)
    print(f"HTML Content:\n{html_content}")
    
    # Access count example
    access_count_key = f"count:{url}"
    access_count = get_page.__wrapped__.__wrapped__.__wrapped__.__dict__[access_count_key]
    print(f"Access count for {url}: {access_count}")
