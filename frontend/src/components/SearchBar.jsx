import React, { useState } from "react";
import { autocomplete, recommend } from "../api";

export default function SearchBar({ onResults }) {
  const [text, setText] = useState("");
  const [sug, setSug] = useState([]);
  const [lat, setLat] = useState(null);
  const [lon, setLon] = useState(null);
  const [infra, setInfra] = useState("hospital");
  const [radius, setRadius] = useState(2000);
  const [loading, setLoading] = useState(false);

  async function handleInput(e) {
    const q = e.target.value;
    setText(q);
    if (q.length < 2) return setSug([]);
    const data = await autocomplete(q);
    setSug(data.results || []);
  }

  function choose(item) {
    setText(item.display_name);
    setLat(item.lat);
    setLon(item.lon);
    setSug([]);
  }

  async function runSearch() {
    if (!lat || !lon) {
      alert("Please select a location from suggestions!");
      return;
    }
    setLoading(true);
    try {
      const r = await recommend({ place: text, infra, radius, lat, lon });
      onResults(r.good || [], r.danger || []);
    } catch (error) {
      console.error("Error:", error);
      alert("Failed to fetch recommendations.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div style={{ 
      width: "100%", 
      padding: "20px", 
      boxSizing: "border-box",
      position: "relative",
      zIndex: 2000              // ← Increased
    }}>
      <div style={{ maxWidth: "1400px", margin: "0 auto" }}>
        
        <div
          style={{
            display: "flex",
            gap: "12px",
            alignItems: "center",
          }}
        >
          {/* Search Box */}
          <div style={{ flex: 1, position: "relative", zIndex: 2001 }}>
            <input
              value={text}
              onChange={handleInput}
              placeholder="Search area…"
              disabled={loading}
              style={{
                width: "100%",
                padding: "12px",
                borderRadius: "8px",
                border: "1px solid #ccc",
                fontSize: "15px",
                boxSizing: "border-box",
                background: loading ? "#d4c5b0" : "#f5f5dc",
                color: "#222",
              }}
            />
            {sug.length > 0 && !loading && (
              <div
                style={{
                  position: "fixed",           // ← Changed from absolute to fixed
                  top: "auto",
                  marginTop: "4px",
                  left: "auto",
                  right: "auto",
                  background: "#f5f5dc",
                  borderRadius: "8px",
                  boxShadow: "0 4px 12px rgba(0,0,0,0.3)",
                  zIndex: 999999,              // ← Maximum z-index
                  maxHeight: "200px",
                  overflowY: "auto",
                  border: "2px solid #ccc",
                  width: "calc(100% - 24px)",  // Match input width
                  maxWidth: "1076px"           // Adjust based on your layout
                }}
              >
                {sug.map((s, i) => (
                  <div
                    key={i}
                    onClick={() => choose(s)}
                    style={{
                      padding: "10px",
                      cursor: "pointer",
                      borderBottom: "1px solid #ccc",
                      color: "#222",
                    }}
                    onMouseEnter={(e) => (e.target.style.background = "#e8e3d3")}
                    onMouseLeave={(e) => (e.target.style.background = "#f5f5dc")}
                  >
                    {s.display_name}
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Infra Dropdown */}
          <select
            value={infra}
            onChange={(e) => setInfra(e.target.value)}
            disabled={loading}
            style={{
              padding: "12px",
              borderRadius: "8px",
              border: "1px solid #ccc",
              background: "#f5f5dc",
              color: "#222",
              fontSize: "14px",
              minWidth: "110px",
            }}
          >
            <option value="hospital">Hospital</option>
            <option value="school">School</option>
            <option value="park">Park</option>
            <option value="clinic">Clinic</option>
            <option value="pharmacy">Pharmacy</option>
          </select>

          {/* Radius */}
          <select
            value={radius}
            onChange={(e) => setRadius(Number(e.target.value))}
            disabled={loading}
            style={{
              padding: "12px",
              borderRadius: "8px",
              border: "1px solid #ccc",
              background: "#f5f5dc",
              color: "#222",
              fontSize: "14px",
              minWidth: "90px",
            }}
          >
            <option value={2000}>2 km</option>
            <option value={4000}>4 km</option>
            <option value={6000}>6 km</option>
            <option value={8000}>8 km</option>
            <option value={10000}>10 km</option>
          </select>

          {/* Search Button */}
          <button
            onClick={runSearch}
            disabled={loading}
            style={{
              padding: "12px 24px",
              background: loading ? "#94a3b8" : "#2563eb",
              color: "white",
              border: "none",
              borderRadius: "8px",
              fontSize: "15px",
              cursor: loading ? "not-allowed" : "pointer",
              whiteSpace: "nowrap",
            }}
          >
            {loading ? "Searching..." : "Search"}
          </button>
        </div>

        {loading && (
          <div
            style={{
              marginTop: "15px",
              padding: "12px",
              background: "#dbeafe",
              borderRadius: "8px",
              color: "#1e40af",
              fontSize: "14px",
              textAlign: "center",
            }}
          >
            🔍 Analyzing location...
          </div>
        )}
      </div>
    </div>
  );
}
