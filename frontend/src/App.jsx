import React, { useState } from "react";
import SearchBar from "./components/SearchBar";
import MapComponent from "./components/MapComponent";

export default function App() {
  const [best, setBest] = useState([]);
  const [danger, setDanger] = useState([]);

  return (
    // Main Container: Full Screen, Flex Column
    <div 
      style={{ 
        width: "100vw", 
        height: "100vh", 
        display: "flex", 
        flexDirection: "column",
        overflow: "hidden" 
      }}
    >
      {/* Header Section */}
      <div
        style={{
          position: "relative",
          zIndex: 1001,
          flexShrink: 0, // Prevents header from shrinking when map grows
          boxShadow: "0 4px 20px rgba(0,0,0,0.1)" // Adds a nice separation shadow
        }}
      >
        {/* Background image layer */}
        <div
          style={{
            position: "absolute",
            top: 0,
            left: 0,
            width: "100%",
            height: "100%",
            backgroundImage: "url('/background.png')",
            backgroundSize: "cover",
            backgroundPosition: "center",
            backgroundRepeat: "no-repeat",
            opacity: 0.3,
            zIndex: -1
          }}
        />

        {/* Content */}
        <div style={{ paddingBottom: "20px" }}>
          <div
            style={{
              width: "100%",
              textAlign: "center",
              fontSize: "36px",
              padding: "20px 0",
              fontWeight: "bold",
              color: "#2563eb",
              fontFamily: "'Georgia', serif",
              textShadow: "1px 1px 2px rgba(255,255,255,0.8)"
            }}
          >
            Ooru Dev
          </div>

          {/* Search Bar */}
          <SearchBar
            onResults={(good, bad) => {
              setBest(good);
              setDanger(bad);
            }}
          />
        </div>
      </div>

      {/* Map Section: Fills remaining space automatically */}
      <div style={{ flex: 1, position: "relative", zIndex: 1 }}>
        <MapComponent best={best} danger={danger} />
      </div>
    </div>
  );
}