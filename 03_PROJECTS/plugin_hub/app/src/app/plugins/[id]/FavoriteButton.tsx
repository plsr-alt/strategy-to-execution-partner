"use client";

import { useSession } from "next-auth/react";
import { useState, useEffect } from "react";

export default function FavoriteButton({ pluginId }: { pluginId: string }) {
  const { data: session } = useSession();
  const [isFavorited, setIsFavorited] = useState(false);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!session) return;
    fetch("/api/favorites")
      .then((res) => res.json())
      .then((data) => {
        const ids = (data || []).map(
          (fav: { pluginId: string }) => fav.pluginId
        );
        setIsFavorited(ids.includes(pluginId));
      })
      .catch(() => {});
  }, [session, pluginId]);

  const handleToggle = async () => {
    if (!session || loading) return;
    setLoading(true);

    const method = isFavorited ? "DELETE" : "POST";
    setIsFavorited(!isFavorited);

    try {
      const res = await fetch("/api/favorites", {
        method,
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ pluginId }),
      });
      if (!res.ok) throw new Error();
    } catch {
      setIsFavorited(isFavorited);
    } finally {
      setLoading(false);
    }
  };

  if (!session) return null;

  return (
    <button
      onClick={handleToggle}
      disabled={loading}
      className={`inline-flex items-center gap-2 px-4 py-2.5 rounded-xl text-sm font-medium transition-all ${
        isFavorited
          ? "bg-rose-500/20 text-rose-400 border border-rose-500/30 hover:bg-rose-500/30"
          : "bg-gray-800 text-gray-300 border border-gray-700 hover:bg-gray-700 hover:border-gray-600"
      } ${loading ? "opacity-50 cursor-not-allowed" : ""}`}
    >
      <svg
        className={`w-4 h-4 ${isFavorited ? "fill-current" : "fill-none"}`}
        stroke="currentColor"
        strokeWidth={isFavorited ? 0 : 1.5}
        viewBox="0 0 24 24"
      >
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          d="M21 8.25c0-2.485-2.099-4.5-4.688-4.5-1.935 0-3.597 1.126-4.312 2.733-.715-1.607-2.377-2.733-4.313-2.733C5.1 3.75 3 5.765 3 8.25c0 7.22 9 12 9 12s9-4.78 9-12z"
        />
      </svg>
      {isFavorited ? "Favorited" : "Favorite"}
    </button>
  );
}
