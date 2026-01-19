import json
import os
import time
from hashlib import md5

CACHE_FILE = "search_cache.json"
CACHE_DURATION = 86400  # 24 hours in seconds

def load_cache():
    """Load cache from file"""
    if not os.path.exists(CACHE_FILE):
        return {}
    try:
        with open(CACHE_FILE, 'r') as f:
            return json.load(f)
    except:
        return {}

def save_cache(cache):
    """Save cache to file"""
    try:
        with open(CACHE_FILE, 'w') as f:
            json.dump(cache, f, indent=2)
    except Exception as e:
        print(f"Cache save error: {e}")

def get_cache_key(lat, lon, infra, radius):
    """Generate unique cache key"""
    key_str = f"{lat:.5f}_{lon:.5f}_{infra}_{radius}"
    return md5(key_str.encode()).hexdigest()

def get_cached_result(lat, lon, infra, radius):
    """Check if result exists in cache"""
    cache = load_cache()
    key = get_cache_key(lat, lon, infra, radius)
    
    if key in cache:
        entry = cache[key]
        # Check if cache is still valid (not expired)
        if time.time() - entry.get("timestamp", 0) < CACHE_DURATION:
            print(f"✅ Cache HIT for {key}")
            return entry.get("result")
        else:
            print(f"⏰ Cache EXPIRED for {key}")
    
    print(f"❌ Cache MISS for {key}")
    return None

def set_cached_result(lat, lon, infra, radius, result):
    """Save result to cache"""
    cache = load_cache()
    key = get_cache_key(lat, lon, infra, radius)
    
    cache[key] = {
        "timestamp": time.time(),
        "lat": lat,
        "lon": lon,
        "infra": infra,
        "radius": radius,
        "result": result,
        "readable_location": f"{lat:.5f}, {lon:.5f}"
    }
    
    save_cache(cache)
    print(f"💾 Cached result for {key}")

def clear_cache():
    """Clear all cached data"""
    if os.path.exists(CACHE_FILE):
        os.remove(CACHE_FILE)
        print("🗑️ Cache cleared")

def clear_expired_cache():
    """Remove expired entries from cache"""
    cache = load_cache()
    current_time = time.time()
    
    cleaned_cache = {
        k: v for k, v in cache.items()
        if current_time - v.get("timestamp", 0) < CACHE_DURATION
    }
    
    removed = len(cache) - len(cleaned_cache)
    if removed > 0:
        save_cache(cleaned_cache)
        print(f"🧹 Removed {removed} expired entries")
    
    return removed
