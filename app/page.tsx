"use client";

import { useState } from "react";
import ChatPanel from "./components/ChatPanel";
import MapView from "./components/MapView";

export default function Home() {
  const [coords, setCoords] = useState({
    lat: 28.6139,
    lon: 77.209,
  });

  const handleSearch = async (query: string) => {
    const res = await fetch(
      `https://nominatim.openstreetmap.org/search?format=json&q=${query}`
    );
    const data = await res.json();

    if (data.length > 0) {
      setCoords({
        lat: parseFloat(data[0].lat),
        lon: parseFloat(data[0].lon),
      });
    }
  };

  return (
    <div className="flex h-screen">
      <div className="w-1/4 border-r">
        <ChatPanel onSearch={handleSearch} />
      </div>
      <div className="w-3/4">
        <MapView lat={coords.lat} lon={coords.lon} />
      </div>
    </div>
  );
}