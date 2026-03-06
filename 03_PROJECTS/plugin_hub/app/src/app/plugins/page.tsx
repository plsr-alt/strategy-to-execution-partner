"use client";

import { useSearchParams, useRouter } from "next/navigation";
import { useSession } from "next-auth/react";
import { useState, useEffect, useCallback, Suspense } from "react";
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

type Category = {
  id: string;
  name: string;
};

function PluginsContent() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const { data: session } = useSession();

  const [plugins, setPlugins] = useState<Plugin[]>([]);
  const [categories, setCategories] = useState<Category[]>([]);
  const [favoritedIds, setFavoritedIds] = useState<Set<string>>(new Set());
  const [loading, setLoading] = useState(true);

  const search = searchParams.get("search") || "";
  const categoryId = searchParams.get("category") || "";

  const [searchInput, setSearchInput] = useState(search);

  useEffect(() => {
    fetch("/api/categories")
      .then((res) => res.json())
      .then(setCategories)
      .catch(() => {});
  }, []);

  useEffect(() => {
    if (!session) return;
    fetch("/api/favorites")
      .then((res) => res.json())
      .then((data) => {
        const ids = new Set<string>(
          (data || []).map((fav: { pluginId: string }) => fav.pluginId)
        );
        setFavoritedIds(ids);
      })
      .catch(() => {});
  }, [session]);

  const fetchPlugins = useCallback(async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams();
      if (search) params.set("search", search);
      if (categoryId) params.set("categoryId", categoryId);

      const res = await fetch(`/api/plugins?${params.toString()}`);
      const data = await res.json();
      setPlugins(data.plugins || data || []);
    } catch {
      setPlugins([]);
    } finally {
      setLoading(false);
    }
  }, [search, categoryId]);

  useEffect(() => {
    fetchPlugins();
  }, [fetchPlugins]);

  const updateURL = (newSearch?: string, newCategory?: string) => {
    const params = new URLSearchParams();
    const s = newSearch !== undefined ? newSearch : search;
    const c = newCategory !== undefined ? newCategory : categoryId;
    if (s) params.set("search", s);
    if (c) params.set("category", c);
    router.push(`/plugins?${params.toString()}`);
  };

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    updateURL(searchInput, undefined);
  };

  const handleCategoryClick = (catId: string) => {
    const newCat = catId === categoryId ? "" : catId;
    updateURL(undefined, newCat);
  };

  const handleToggleFavorite = async (pluginId: string) => {
    if (!session) return;

    const isFavorited = favoritedIds.has(pluginId);
    const method = isFavorited ? "DELETE" : "POST";

    setFavoritedIds((prev) => {
      const next = new Set(prev);
      if (isFavorited) next.delete(pluginId);
      else next.add(pluginId);
      return next;
    });

    try {
      const res = await fetch("/api/favorites", {
        method,
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ pluginId }),
      });
      if (!res.ok) throw new Error();
    } catch {
      setFavoritedIds((prev) => {
        const next = new Set(prev);
        if (isFavorited) next.add(pluginId);
        else next.delete(pluginId);
        return next;
      });
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-white">Plugins</h1>
        <p className="mt-1 text-gray-400">Browse and discover Figma plugins</p>
      </div>

      <form onSubmit={handleSearch} className="mb-6">
        <div className="relative">
          <svg className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
          <input
            type="text"
            value={searchInput}
            onChange={(e) => setSearchInput(e.target.value)}
            placeholder="Search plugins by name, description, or tags..."
            className="w-full pl-12 pr-4 py-3 bg-gray-800 border border-gray-700 rounded-xl text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-violet-500 focus:border-transparent transition-all"
          />
        </div>
      </form>

      {categories.length > 0 && (
        <div className="mb-8 flex gap-2 overflow-x-auto pb-2 scrollbar-thin">
          <button
            onClick={() => handleCategoryClick("")}
            className={`flex-shrink-0 px-4 py-2 rounded-full text-sm font-medium transition-colors ${
              !categoryId
                ? "bg-violet-600 text-white"
                : "bg-gray-800 text-gray-300 hover:bg-gray-700 border border-gray-700"
            }`}
          >
            All
          </button>
          {categories.map((cat) => (
            <button
              key={cat.id}
              onClick={() => handleCategoryClick(cat.id)}
              className={`flex-shrink-0 px-4 py-2 rounded-full text-sm font-medium transition-colors ${
                categoryId === cat.id
                  ? "bg-violet-600 text-white"
                  : "bg-gray-800 text-gray-300 hover:bg-gray-700 border border-gray-700"
              }`}
            >
              {cat.name}
            </button>
          ))}
        </div>
      )}

      {loading ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
          {Array.from({ length: 6 }).map((_, i) => (
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
      ) : plugins.length > 0 ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
          {plugins.map((plugin) => (
            <PluginCard
              key={plugin.id}
              plugin={plugin}
              isFavorited={favoritedIds.has(plugin.id)}
              onToggleFavorite={handleToggleFavorite}
            />
          ))}
        </div>
      ) : (
        <div className="text-center py-16">
          <div className="text-5xl mb-4">🔍</div>
          <h3 className="text-lg font-semibold text-white mb-2">No plugins found</h3>
          <p className="text-gray-400">
            {search
              ? `No results for "${search}". Try a different search term.`
              : "No plugins available yet."}
          </p>
        </div>
      )}
    </div>
  );
}

export default function PluginsPage() {
  return (
    <Suspense
      fallback={
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="animate-pulse space-y-4">
            <div className="h-8 bg-gray-700/50 rounded w-48" />
            <div className="h-12 bg-gray-700/50 rounded" />
          </div>
        </div>
      }
    >
      <PluginsContent />
    </Suspense>
  );
}
