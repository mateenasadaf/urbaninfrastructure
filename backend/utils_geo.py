# backend/utils_geo.py
import requests, math, statistics, random
from urllib.parse import quote_plus

NOMINATIM = "https://nominatim.openstreetmap.org"
OVERPASS = "https://overpass-api.de/api/interpreter"
OPENWEATHER_API_KEY = "adff2d5a559c17cdcfba073eaf41c04b"

HEADERS = {"User-Agent":"UrbanInfraDashboard/1.0 (sadaf@example.com)"}

def is_point_actually_empty(lat, lon):
    """Quick check if point is empty - FAST VERSION"""
    q_standard = f"""
    [out:json][timeout:3];
    (
      way(around:20,{lat},{lon})["building"];
      way(around:20,{lat},{lon})["highway"];
    );
    out ids;
    """
    try:
        r = requests.post(OVERPASS, data={"data": q_standard}, headers=HEADERS, timeout=4)
        data = r.json()
        return len(data.get("elements", [])) == 0
    except:
        return True


# ------------------------------------------------
# AUTOCOMPLETE WITH SMART RANKING
# ------------------------------------------------

def rank_search_results(results, query):
    """
    ✅ Ranks results so that places STARTING with query appear first
    Example: typing "hen" → Hennur first, then other matches
    """
    query_lower = query.lower().strip()
    
    ranked = []
    for result in results:
        name = result["display_name"].lower()
        
        # Extract the first part (actual place name)
        place_name = name.split(",")[0].strip()
        
        # Calculate priority
        if place_name.startswith(query_lower):
            priority = 1  # Highest priority - starts with query
        elif query_lower in place_name[:len(query_lower) + 3]:
            priority = 2  # High priority - query in first few chars
        elif place_name.startswith(query_lower[0]):
            priority = 3  # Medium priority - same first letter
        elif query_lower in name:
            priority = 4  # Lower priority - contains query anywhere
        else:
            priority = 5  # Lowest priority
        
        ranked.append({
            "priority": priority,
            "result": result
        })
    
    # Sort by priority (1 = highest)
    ranked.sort(key=lambda x: x["priority"])
    
    return [item["result"] for item in ranked]


def nominatim_autocomplete(q, limit=8):
    """✅ Smart search - shows places STARTING with your query first"""
    query = q
    if "bengaluru" not in q.lower() and "bangalore" not in q.lower():
        query = f"{q}, Bengaluru"
    
    url = (
        "https://nominatim.openstreetmap.org/search?"
        f"format=json&addressdetails=1&limit={limit * 3}&countrycodes=in&q={quote_plus(query)}"
    )
    headers = {"User-Agent": "UrbanInfraAI/1.0"}

    try:
        r = requests.get(url, headers=headers, timeout=10)
        data = r.json()

        results = []
        for el in data:
            name = el.get("display_name", "")
            address = el.get("address", {})
            
            city = address.get("city", "").lower()
            state = address.get("state", "").lower()
            county = address.get("county", "").lower()
            
            is_bengaluru = (
                "bengaluru" in name.lower() or 
                "bangalore" in name.lower() or
                "bengaluru" in city or 
                "bangalore" in city or
                "bangalore urban" in county or
                "bengaluru urban" in county
            )
            
            is_karnataka = "karnataka" in state
            
            if is_bengaluru and is_karnataka:
                results.append({
                    "display_name": name,
                    "lat": float(el["lat"]),
                    "lon": float(el["lon"])
                })
        
        # If no results, try backup
        if not results:
            backup_query = f"{q}, Bangalore, Karnataka"
            url2 = (
                "https://nominatim.openstreetmap.org/search?"
                f"format=json&addressdetails=1&limit={limit}&q={quote_plus(backup_query)}"
            )
            r2 = requests.get(url2, headers=headers, timeout=10)
            data2 = r2.json()
            
            for el in data2:
                name = el.get("display_name", "")
                if "bangalore" in name.lower() or "bengaluru" in name.lower():
                    results.append({
                        "display_name": name,
                        "lat": float(el["lat"]),
                        "lon": float(el["lon"])
                    })

        # ✅ RANK RESULTS - Places starting with query appear first
        ranked_results = rank_search_results(results, q)
        
        return ranked_results[:limit]
    except:
        return []


def photon_autocomplete(q, limit=8):
    """✅ Fallback with smart ranking"""
    query = q
    if "bengaluru" not in q.lower() and "bangalore" not in q.lower():
        query = f"{q} Bengaluru Karnataka"
    
    url = f"https://photon.komoot.io/api/?q={quote_plus(query)}&limit=20"

    try:
        r = requests.get(url, timeout=10)
        data = r.json()

        results = []
        for f in data.get("features", []):
            props = f["properties"]
            coords = f["geometry"]["coordinates"]
            
            country = props.get("country", "").lower()
            if country != "india":
                continue
            
            city = props.get("city", "").lower()
            state = props.get("state", "").lower()
            name = props.get("name", "").lower()
            
            is_bengaluru = (
                "bengaluru" in city or 
                "bangalore" in city or
                "bengaluru" in name or
                "bangalore" in name
            )
            
            is_karnataka = "karnataka" in state
            
            if is_bengaluru and is_karnataka:
                display = props.get("name", "")
                if props.get("street"):
                    display += ", " + props.get("street")
                display += ", Bengaluru"
                
                results.append({
                    "display_name": display,
                    "lat": coords[1],
                    "lon": coords[0]
                })

        # ✅ RANK RESULTS
        ranked_results = rank_search_results(results, q)
        
        return ranked_results[:limit]
    except:
        return []


def nominatim_lookup(q):
    url = f"{NOMINATIM}/search?format=jsonv2&q={quote_plus(q)}&limit=1"
    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
        res = r.json()
        if not res: return None
        return res[0]
    except:
        return None


# ------------------------------------------------
# HAVERSINE DISTANCE
# ------------------------------------------------

def haversine_m(a_lat, a_lon, b_lat, b_lon):
    R = 6371000
    phi1, phi2 = math.radians(a_lat), math.radians(b_lat)
    dphi = math.radians(b_lat - a_lat)
    dl = math.radians(b_lon - a_lon)
    x = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dl/2)**2
    return 2 * R * math.asin(math.sqrt(x))


# ------------------------------------------------
# FAST EMPTY LAND SEARCH
# ------------------------------------------------

def overpass_query(q):
    r = requests.post(OVERPASS, data={"data": q}, headers=HEADERS, timeout=60)
    r.raise_for_status()
    return r.json()


def overpass_candidates_near(lat, lon, radius_m, infra_type, max_candidates=10):
    """✅ FAST VERSION: Finds empty land quickly"""
    
    q = f"""
    [out:json][timeout:20];
    (
      way(around:{radius_m},{lat},{lon})["landuse"~"brownfield|greenfield|farmland|grass|meadow"];
      way(around:{radius_m},{lat},{lon})["natural"~"scrub|heath"];
    );
    out center;
    """

    try:
        res = overpass_query(q)
    except:
        print("⚠️ Overpass query failed")
        return []

    elements = res.get("elements", [])
    
    if len(elements) == 0:
        print("⚠️ No empty land found - using fallback")
        return []

    candidates = []
    seen = set()

    print(f"🔎 Found {len(elements)} potential sites. Quick validation...")

    for el in elements[:15]:
        if len(candidates) >= max_candidates:
            break

        if "center" not in el:
            continue
            
        cx, cy = el["center"]["lat"], el["center"]["lon"]
        
        key = (round(cx, 5), round(cy, 5))
        if key in seen:
            continue
        seen.add(key)

        tags = el.get("tags", {})
        
        if "building" in tags or "highway" in tags or "amenity" in tags:
            continue
        
        if len(candidates) < 5:
            if not is_point_actually_empty(cx, cy):
                print(f"❌ Rejected {cx:.5f},{cy:.5f}")
                continue
        
        print(f"✅ Accepted: {cx:.5f},{cy:.5f}")
        candidates.append({
            "lat": cx,
            "lon": cy,
            "tags": tags,
            "type": "verified_empty_land",
            "geom": None
        })

    print(f"✅ Found {len(candidates)} candidates")
    return candidates


def fallback_generate_empty_spaces(lat, lon, radius_m, count=8):
    """✅ FAST FALLBACK"""
    results = []
    attempts = 0
    max_attempts = count * 2

    print("⚠️ Using quick fallback...")

    while len(results) < count and attempts < max_attempts:
        attempts += 1
        
        angle = random.uniform(0, 2 * math.pi)
        dist = random.uniform(0.3 * radius_m, 0.8 * radius_m)

        dx = (dist / 111320) * math.cos(angle)
        dy = (dist / 110540) * math.sin(angle)

        new_lat = lat + dy
        new_lon = lon + dx

        if is_point_actually_empty(new_lat, new_lon):
            results.append({
                "lat": new_lat,
                "lon": new_lon,
                "tags": {"fallback": "generated_vacant_plot"},
                "type": "verified_empty_space",
                "geom": None
            })

    print(f"✅ Generated {len(results)} fallback points")
    return results


# ------------------------------------------------
# AIR QUALITY
# ------------------------------------------------

def get_air_quality_openweather(lat, lon):
    url = f"https://api.openweathermap.org/data/2.5/air_pollution"
    params = {"lat": lat, "lon": lon, "appid": OPENWEATHER_API_KEY}
    
    try:
        resp = requests.get(url, params=params, timeout=5)
        resp.raise_for_status()
        data = resp.json()
        
        if "list" in data and len(data["list"]) > 0:
            aqi = data["list"][0]["main"]["aqi"]
            components = data["list"][0]["components"]
            pm25 = components.get("pm2_5", None)
            return aqi, pm25
        return 3, None
    except Exception as e:
        print(f"Air quality error: {e}")
        return 3, None


# ------------------------------------------------
# METRICS HELPERS
# ------------------------------------------------

def buildings_count_proxy(lat, lon, radius_m):
    q = f"""
    [out:json][timeout:15];
    (
      way(around:{radius_m},{lat},{lon})[building];
      node(around:{radius_m},{lat},{lon})[building];
    );
    out;
    """
    try:
        res = requests.post(OVERPASS, data={"data": q}, headers=HEADERS, timeout=30).json()
        return float(len(res.get("elements", [])))
    except:
        return 20.0


def distance_to_nearest_road(lat, lon, radius_m):
    q = f"""
    [out:json][timeout:15];
    (
      way(around:{radius_m},{lat},{lon})["highway"];
    );
    out center;
    """
    try:
        res = requests.post(OVERPASS, data={"data": q}, headers=HEADERS, timeout=20).json()
        dmin = radius_m
        for el in res.get("elements", []):
            if "center" in el:
                d = haversine_m(lat, lon, el["center"]["lat"], el["center"]["lon"])
                if d < dmin: dmin = d
        return float(dmin)
    except:
        return float(radius_m)


def lake_proximity(lat, lon, radius_m):
    q = f"""
    [out:json][timeout:20];
    (
      way(around:{radius_m},{lat},{lon})["natural"="water"];
      way(around:{radius_m},{lat},{lon})["water"];
      relation(around:{radius_m},{lat},{lon})["water"];
    );
    out center;
    """
    try:
        res = requests.post(OVERPASS, data={"data": q}, headers=HEADERS, timeout=20).json()
        dmin = radius_m
        for el in res.get("elements", []):
            if "center" in el:
                d = haversine_m(lat, lon, el["center"]["lat"], el["center"]["lon"])
                if d < dmin: dmin = d
        near = dmin <= 300
        return float(dmin), near
    except:
        return float(radius_m), False


def green_proxy(lat, lon, radius_m):
    q = f"""
    [out:json][timeout:20];
    (
      way(around:{radius_m},{lat},{lon})["landuse"~"forest|meadow|grass"];
      way(around:{radius_m},{lat},{lon})["leisure"~"park|garden"];
    );
    out;
    """
    try:
        res = requests.post(OVERPASS, data={"data": q}, headers=HEADERS, timeout=20).json()
        cnt = len(res.get("elements", []))
        return float(min(80.0, (cnt / 10.0) * 80.0))
    except:
        return 10.0


def distance_to_nearest_amenity(lat, lon, infra_type, radius_m):
    mapping = {
        "hospital": "hospital",
        "clinic": "clinic",
        "pharmacy": "pharmacy",
        "school": "school",
        "park": "park",
        "metro": "train_station",
        "bus_stop": "bus_stop",
        "market": "marketplace"
    }
    amen = mapping.get(infra_type, infra_type)

    q = f"""
    [out:json][timeout:15];
    (
      node(around:{radius_m},{lat},{lon})[amenity={amen}];
      way(around:{radius_m},{lat},{lon})[amenity={amen}];
      relation(around:{radius_m},{lat},{lon})[amenity={amen}];
    );
    out center;
    """
    try:
        res = requests.post(OVERPASS, data={"data": q}, headers=HEADERS, timeout=25).json()
        min_d = radius_m
        for el in res.get("elements", []):
            if "center" in el:
                d = haversine_m(lat, lon, el["center"]["lat"], el["center"]["lon"])
                if d < min_d: min_d = d
            elif "lat" in el and "lon" in el:
                d = haversine_m(lat, lon, el["lat"], el["lon"])
                if d < min_d: min_d = d
        return float(min_d)
    except:
        return float(radius_m)


# ------------------------------------------------
# COMPUTE METRICS
# ------------------------------------------------

def compute_candidate_metrics(candidate, infra_type, origin=(0,0)):
    lat = candidate.get("lat")
    lon = candidate.get("lon")
    origin_lat, origin_lon = origin

    dist_m = haversine_m(origin_lat, origin_lon, lat, lon)
    pop_proxy = buildings_count_proxy(lat, lon, radius_m=500)
    dist_road = distance_to_nearest_road(lat, lon, radius_m=2000)
    lake_dist_m, near_lake = lake_proximity(lat, lon, radius_m=2000)
    green_pct = green_proxy(lat, lon, radius_m=500)
    aqi, pm25 = get_air_quality_openweather(lat, lon)
    dist_same = distance_to_nearest_amenity(lat, lon, infra_type, radius_m=3000)

    scores = {
        "accessibility": max(0.0, 1 - (dist_road / 2000.0)),
        "population_need": min(1.0, pop_proxy / 200.0),
        "lake_protection": 0.0 if near_lake else 1.0,
        "green_balance": min(1.0, (green_pct or 0) / 40.0),
        "pollution_risk": 1.0 if aqi <= 2 else (0.5 if aqi == 3 else 0.0),
        "redundancy": max(0.0, 1 - (dist_same / 3000.0))
    }

    infra = infra_type.lower()
    if infra in ["hospital", "clinic", "pharmacy"]:
        scores["accessibility"] = max(scores["accessibility"], 1 - (dist_road / 1500.0))
        if aqi >= 4:
            scores["pollution_risk"] = 0.0
        if near_lake:
            scores["lake_protection"] = 0.0

    if infra == "school":
        scores["population_need"] = min(1.0, pop_proxy / 120.0)
        if aqi >= 4:
            scores["pollution_risk"] = 0.0
        if dist_road < 40:
            scores["accessibility"] *= 0.6

    if infra == "park":
        scores["green_balance"] = min(1.0, (green_pct or 0) / 20.0)
        if aqi >= 4:
            scores["pollution_risk"] = 0.0

    reason = build_reason_text(candidate, infra_type, dist_m, pop_proxy, dist_road, near_lake, lake_dist_m, green_pct, aqi, pm25, dist_same, scores)

    return {
        "pop": float(pop_proxy),
        "dist_m": float(dist_m),
        "dist_road_m": float(dist_road),
        "near_lake": bool(near_lake),
        "lake_dist_m": float(lake_dist_m),
        "green_pct": float(green_pct) if green_pct is not None else None,
        "aqi": int(aqi),
        "pm25": float(pm25) if pm25 is not None else None,
        "dist_to_same_infra_m": float(dist_same),
        "raw_scores": scores,
        "reason": reason
    }


def build_reason_text(candidate, infra_type, dist_m, pop_proxy, dist_road, near_lake, lake_dist_m, green_pct, aqi, pm25, dist_same, scores):
    parts = []

    if pop_proxy > 120:
        parts.append("High building density nearby (strong demand)")
    elif pop_proxy > 50:
        parts.append("Moderate building density nearby")
    else:
        parts.append("Low building density nearby")

    if dist_road < 100:
        parts.append("Excellent road access")
    elif dist_road < 500:
        parts.append("Good road connectivity")
    else:
        parts.append("Limited road access")

    if near_lake:
        parts.append(f"Close to water body ({int(lake_dist_m)}m) — flood risk")
    else:
        parts.append("Safe from flood zones")

    if green_pct is None:
        parts.append("Green cover data not available")
    elif green_pct < 15:
        parts.append("Low green cover")
    elif green_pct < 40:
        parts.append("Moderate green cover")
    else:
        parts.append("Good green cover")

    aqi_labels = {1: "Good", 2: "Fair", 3: "Moderate", 4: "Poor", 5: "Very Poor"}
    aqi_label = aqi_labels.get(aqi, "Unknown")
    
    if pm25 is not None:
        parts.append(f"Air quality: {aqi_label} (AQI: {aqi}, PM2.5: {pm25:.0f} µg/m³)")
    else:
        parts.append(f"Air quality: {aqi_label} (AQI: {aqi})")

    if dist_same is not None and dist_same < 800:
        parts.append(f"Similar facility {int(dist_same)}m away — redundancy risk")
    else:
        parts.append("No similar facility nearby")

    infra = infra_type.lower()
    if infra == "hospital":
        parts.append("Hospitals require high accessibility and good air quality")
    elif infra == "school":
        parts.append("Schools prefer residential proximity and good air quality")
    elif infra == "park":
        parts.append("Parks should have high green cover and low pollution")

    return ". ".join(parts) + "."


# ------------------------------------------------
# NORMALIZE & RANK
# ------------------------------------------------

def normalize_scores_and_rank(candidates, topk=3):
    keys = ["accessibility", "population_need", "lake_protection", "green_balance", "pollution_risk", "redundancy"]
    vals = {k: [c["raw_scores"].get(k, 0.0) for c in candidates] for k in keys}

    weights = {
        "accessibility": 0.16,
        "population_need": 0.22,
        "lake_protection": 0.20,
        "green_balance": 0.16,
        "pollution_risk": 0.14,
        "redundancy": 0.12
    }

    for c in candidates:
        score = 0.0
        for k in keys:
            v = c["raw_scores"].get(k, 0.0)
            arr = vals[k]
            mn = min(arr) if arr else 0.0
            mx = max(arr) if arr else 1.0
            if mx - mn > 1e-9:
                v_norm = (v - mn) / (mx - mn)
            else:
                v_norm = v
            score += weights.get(k, 0.0) * v_norm
        c["score"] = float(score * 100)

    sorted_list = sorted(candidates, key=lambda x: x.get("score", 0.0), reverse=True)
    
    for i, cand in enumerate(sorted_list[:topk if topk else len(sorted_list)]):
        rank = i + 1
        cand["rank"] = rank
        cand["reason"] = f"🏆 Rank {rank} - Score: {cand['score']:.0f}/100. {cand['reason']}"
    
    if topk is None:
        return sorted_list
    return sorted_list[:topk]
