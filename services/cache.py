import time
import sys

# In-memory store. Easy to replace with Redis later.
CACHE = {}

def set_cache(key: str, value: any, ttl: int = 600):
    """Store an item in the cache with a Time-To-Live (in seconds)."""
    key_str = str(key)
    CACHE[key_str] = {
        "value": value,
        "expiry": time.time() + ttl
    }
    print(f"[CACHE SET] key='{key_str}' ttl={ttl}s")

def get_cache(key: str) -> any:
    """Retrieve an item from the cache if it hasn't expired."""
    key_str = str(key)
    data = CACHE.get(key_str)
    if not data:
        print(f"[CACHE MISS] key='{key_str}'")
        return None
    
    if time.time() > data["expiry"]:
        print(f"[CACHE EXPIRED] key='{key_str}'")
        del CACHE[key_str]
        return None
        
    print(f"[CACHE HIT] key='{key_str}'")
    return data["value"]

def clear_cache(prefix: str = None):
    """Clear all keys starting with `prefix`. If prefix is None, clear all."""
    if prefix:
        keys_to_delete = [k for k in CACHE if k.startswith(prefix)]
        for k in keys_to_delete:
            del CACHE[k]
        print(f"[CACHE CLEAR] prefix={prefix}")
    else:
        print(f"[CACHE CLEAR] all")
        CACHE.clear()

def get_cache_status() -> dict:
    """Return diagnostic info about the cache."""
    active_keys = []
    expired_keys = 0
    now = time.time()
    
    for k, v in list(CACHE.items()):
        if now > v["expiry"]:
            expired_keys += 1
            del CACHE[k]
        else:
            active_keys.append(k)
            
    # approximate size
    memory_usage = sys.getsizeof(CACHE)
            
    return {
        "total_keys": len(active_keys),
        "keys": active_keys,
        "memory_usage": f"{memory_usage} bytes"
    }


