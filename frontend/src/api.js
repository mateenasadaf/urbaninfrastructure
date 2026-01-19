const BASE = "http://127.0.0.1:5000";


export async function autocomplete(q) {
  const r = await fetch(`${BASE}/autocomplete?q=${encodeURIComponent(q)}`);
  return r.json();
}


export async function recommend({ place, infra, radius, lat, lon }) {
  let url = `${BASE}/recommend?place=${encodeURIComponent(place)}&infra=${infra}&radius=${radius}`;
  if (lat && lon) url += `&lat=${lat}&lon=${lon}`;
  const r = await fetch(url);
  return r.json();
}
