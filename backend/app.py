from flask import Flask, request, jsonify
from utils_geo import (
    nominatim_autocomplete,
    photon_autocomplete,
    nominatim_lookup,
    overpass_candidates_near,
    compute_candidate_metrics,
    normalize_scores_and_rank,
    fallback_generate_empty_spaces
)
from flask_cors import CORS
from cache import get_cached_result, set_cached_result, clear_expired_cache  # ← ADD THIS LINE
import os

app = Flask(__name__)
CORS(app)

# Clean up expired cache on startup
clear_expired_cache()  # ← ADD THIS LINE


@app.route("/autocomplete")
def autocomplete():
    q = request.args.get("q", "")
    if not q:
        return jsonify({"results": []})
    res = nominatim_autocomplete(q, limit=8)
    if not res:
        res = photon_autocomplete(q, limit=8)
    return jsonify({"results": res})


@app.route("/recommend")
def recommend():
    place = request.args.get("place")
    infra = request.args.get("infra", "hospital")
    radius_m = int(request.args.get("radius", "2500"))

    lat = request.args.get("lat")
    lon = request.args.get("lon")

    if not lat or not lon:
        loc = nominatim_lookup(place)
        if not loc:
            return jsonify({"error": "Place not found"})
        lat = float(loc["lat"])
        lon = float(loc["lon"])
    else:
        lat = float(lat)
        lon = float(lon)

    # ✅ CHECK CACHE FIRST (ADD THIS BLOCK)
    cached = get_cached_result(lat, lon, infra, radius_m)
    if cached:
        print("⚡ Returning cached result - INSTANT!")
        return jsonify(cached)
    # ✅ END OF CACHE CHECK

    # If not cached, compute normally
    print("🔍 Computing fresh results (will be cached for next time)...")
    
    # 1) First try Overpass
    candidates = overpass_candidates_near(lat, lon, radius_m, infra)

    # 2) FALLBACK if Overpass returns nothing
    if len(candidates) == 0:
        candidates = fallback_generate_empty_spaces(lat, lon, radius_m)

    enriched = []
    for cand in candidates:
        metrics = compute_candidate_metrics(cand, infra, origin=(lat, lon))
        cand.update(metrics)
        enriched.append(cand)

    ranked_full = normalize_scores_and_rank(enriched, topk=None)

    good = ranked_full[:3]
    danger_sorted = sorted(enriched, key=lambda x: x.get("danger_score", 0.0), reverse=True)
    danger = danger_sorted[:2]

    result = {
        "good": good,
        "danger": danger
    }

    # ✅ SAVE TO CACHE (ADD THIS BLOCK)
    set_cached_result(lat, lon, infra, radius_m, result)
    print("💾 Result saved to cache")
    # ✅ END OF CACHE SAVE

    return jsonify(result)


# ✅ ADD THIS NEW ENDPOINT (OPTIONAL - for manual cache clearing)
@app.route("/clear-cache", methods=["POST"])
def clear_cache_endpoint():
    from cache import clear_cache
    clear_cache()
    return jsonify({"message": "Cache cleared successfully"})
# ✅ END OF NEW ENDPOINT


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
