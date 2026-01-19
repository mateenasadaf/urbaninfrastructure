import React from "react";
import { MapContainer, TileLayer, Marker, Popup } from "react-leaflet";
import L from "leaflet";
import "leaflet/dist/leaflet.css";

// Blue drop (best location)
const blueIcon = new L.Icon({
  iconUrl:
    "https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-blue.png",
  shadowUrl: "https://unpkg.com/leaflet@1.7.1/dist/images/marker-shadow.png",
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41],
});

// Red drop (danger location)
const redIcon = new L.Icon({
  iconUrl:
    "https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-red.png",
  shadowUrl: "https://unpkg.com/leaflet@1.7.1/dist/images/marker-shadow.png",
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41],
});

export default function MapComponent({ best = [], danger = [] }) {
  const center =
    best.length > 0
      ? [best[0].lat, best[0].lon]
      : danger.length > 0
      ? [danger[0].lat, danger[0].lon]
      : [12.9716, 77.5946]; // Bangalore default

  return (
    <div
      style={{
        height: "100vh", // 🔥 FULL SCREEN FIX
        width: "100%",
        overflow: "hidden",
      }}
    >
      <MapContainer
        center={center}
        zoom={15} // 🔥 BETTER ZOOM
        style={{ height: "100%", width: "100%" }}
      >
        <TileLayer
          attribution='© OpenStreetMap contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />

        {/* Recommended Locations */}
        {best.map((loc, i) => (
          <Marker
            key={`best-${i}`}
            position={[loc.lat, loc.lon]}
            icon={blueIcon}
          >
            <Popup maxWidth={300}>
              <div>
                <div
                  style={{
                    color: "#16a34a",
                    fontWeight: "bold",
                    fontSize: "18px",
                    marginBottom: "10px",
                  }}
                >
                  ✅ Recommended Location
                </div>

                <ul style={{ paddingLeft: "1.2em", margin: "10px 0" }}>
                  {loc.reason
                    ?.split(". ")
                    .filter((t) => t.length)
                    .map((bullet, idx) => (
                      <li key={idx} style={{ marginBottom: "5px" }}>
                        {bullet}
                      </li>
                    ))}
                </ul>

                <a
                  href={`https://www.google.com/maps?q=${loc.lat},${loc.lon}`}
                  target="_blank"
                  rel="noopener noreferrer"
                  style={{
                    color: "#2563eb",
                    textDecoration: "underline",
                    fontWeight: "500",
                  }}
                >
                  📍 Open in Google Maps
                </a>
              </div>
            </Popup>
          </Marker>
        ))}

        {/* Danger Locations */}
        {danger.map((loc, i) => (
          <Marker
            key={`danger-${i}`}
            position={[loc.lat, loc.lon]}
            icon={redIcon}
          >
            <Popup maxWidth={300}>
              <div>
                <div
                  style={{
                    color: "#dc2626",
                    fontWeight: "bold",
                    fontSize: "18px",
                    marginBottom: "10px",
                  }}
                >
                  ⚠️ Danger Location
                </div>

                <ul style={{ paddingLeft: "1.2em", margin: "10px 0" }}>
                  {loc.reason
                    ?.split(". ")
                    .filter((t) => t.length)
                    .map((bullet, idx) => (
                      <li key={idx} style={{ marginBottom: "5px" }}>
                        {bullet}
                      </li>
                    ))}
                </ul>

                <a
                  href={`https://www.google.com/maps?q=${loc.lat},${loc.lon}`}
                  target="_blank"
                  rel="noopener noreferrer"
                  style={{
                    color: "#2563eb",
                    textDecoration: "underline",
                    fontWeight: "500",
                  }}
                >
                  📍 Open in Google Maps
                </a>
              </div>
            </Popup>
          </Marker>
        ))}
      </MapContainer>
    </div>
  );
}
