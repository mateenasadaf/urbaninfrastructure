import React from "react";

export default function PopupCard({ info, type }) {
  if (!info) return null;

  const bullets = info.reason
    .split(".")
    .map((b) => b.trim())
    .filter((b) => b.length > 2);

  return (
    <div
      style={{
        position: "absolute",
        top: "20px",
        left: "20px",
        padding: "18px",
        width: "320px",
        background: "rgba(255, 255, 255, 0.85)",
        backdropFilter: "blur(10px)",
        borderRadius: "12px",
        boxShadow: "0 4px 18px rgba(0,0,0,0.2)",
        zIndex: 1000,
      }}
    >
      <div
        style={{
          fontWeight: "bold",
          fontSize: "16px",
          marginBottom: "10px",
          color: type === "good" ? "green" : "red",
        }}
      >
        {type === "good" ? "Recommended Location" : "Danger Location"}
      </div>

      <ul style={{ paddingLeft: "18px" }}>
        {bullets.map((b, i) => (
          <li key={i} style={{ marginBottom: "6px" }}>
            {b}
          </li>
        ))}
      </ul>

      <a
        href={`https://www.google.com/maps?q=${info.lat},${info.lon}`}
        target="_blank"
        rel="noreferrer"
        style={{
          color: "#2563eb",
          marginTop: "10px",
          display: "inline-block",
        }}
      >
        Open in Google Maps
      </a>
    </div>
  );
}
