"use client";

import { useSession } from "next-auth/react";
import { useState, useEffect } from "react";
import Link from "next/link";
import PluginCard from "@/components/PluginCard";

type Plugin = {
  id: string;
  name: string;
  description: string | null;
  imageUrl: string | null;
  featured: boolean;
  author: string;
  category: { id: string; name: string } | null;
  tags: string;
};

type FavoriteWithPlugin = {
  pluginId: string;
  plugin: Plugin;
};

export default function FavoritesPage() {
  const { data: session, status } = useSession();
  const [favorites, setFavorites] = useState<FavoriteWithPlugin[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (status === "loading") return;
    if (!session) {
      setLoading(false);
      return;
    }

    fetch("/api/favorites")
      .then((res) => res.json())
      .then((data) => {
        setFavorites(data || []);
      })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [session, status]);

  const handleToggleFavorite = async (pluginId: string) => {
    setFavorites((prev) => prev.filter((f) => f.pluginId !== pluginId));

    try {
      const res = await fetch("/api/favorites", {
        method: "DELETE",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ pluginId }),
      });
      if (!res.ok) throw new Error();
    } catch {
      fetch("/api/favorites")
        .then((res) => res.json())
        .then((data) => setFavorites(data || []))
        .catch(() => {});
    }
  };

  if (status !== "loading" && !session) {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16 text-center">
        <div className="max-w-md mx-auto space-y-4">
          <div className="text-5xl">🔒</div>
          <h1 className="text-2xl font-bold text-white">Sign in to view favorites</h1>
          <p className="text-gray-400">Please log in to save and manage your favorite plugins.</p>
          <Link href="/login" className="inline-block mt-4 px-6 py-3 rounded-xl text-sm font-semibold text-white bg-violet-600 hover:bg-violet-500 transition-colors shadow-lg shadow-violet-500/20">
            Sign In
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-white">My Favorites</h1>
        <p className="mt-1 text-gray-400">Plugins you have saved for quick access</p>
      </div>

      {loading ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
          {Array.from({ length: 3 }).map((_, i) => (
            <div key={i} className="bg-gray-800/80 rounded-xl border border-gray-700/50 overflow-hidden animate-pulse">
              <div className="h-40 bg-gray-700/50" />
              <div className="p-4 space-y-3">
                <div className="h-5 bg-gray-700/50 rounded w-3/4" />
                <div className="h-4 bg-gray-700/50 rounded w-1/2" />
                <div className="h-4 bg-gray-700/50 rounded w-full" />
              </div>
            </div>
          ))}
        </div>
      ) : favorites.length > 0 ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
          {favorites.map((fav) => (
            <PluginCard
              key={fav.pluginId}
              plugin={fav.plugin}
              isFavorited={true}
              onToggleFavorite={handleToggleFavorite}
            />
          ))}
        </div>
      ) : (
        <div className="text-center py-16">
          <div className="text-5xl mb-4">💜</div>
          <h3 className="text-lg font-semibold text-white mb-2">No favorites yet</h3>
          <p className="text-gray-400 mb-6">Browse plugins and tap the heart icon to save your favorites.</p>
          <Link href="/plugins" className="inline-flex items-center gap-2 text-violet-400 hover:text-violet-300 font-medium transition-colors">
            Browse Plugins
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
            </svg>
          </Link>
        </div>
      )}
    </div>
  );
}
