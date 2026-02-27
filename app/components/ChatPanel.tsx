"use client";

import { useState } from "react";

type Props = {
  onSearch: (query: string) => void;
};

export default function ChatPanel({ onSearch }: Props) {
  const [text, setText] = useState("");

  return (
    <div className="p-4 h-full border-r flex flex-col">
      <h2 className="font-bold mb-4">CortexGIS Chat</h2>

      <input
        className="border p-2 mb-2 rounded"
        placeholder="e.g. show Delhi"
        value={text}
        onChange={(e) => setText(e.target.value)}
      />

      <button
        className="bg-black text-white px-4 py-2 rounded"
        onClick={() => onSearch(text)}
        disabled={!text}
      >
        Search
      </button>
    </div>
  );
}