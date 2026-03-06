"use client";

import { useSession } from "next-auth/react";
import { useState, useEffect } from "react";
import PluginCard from "./PluginCard";

type Plugin = {
  id: string;
  name: string;
  description: string | null;
  imageUrl: string | null;
  featured: boolean;
  author: string;
  category: {
    id: string;
    name: string;
  } | null;
  tags: string;
};

type PluginCardGridProps = {
  plugins: Plugin[];
};

export default function PluginCardGrid({ plugins }: PluginCardGridProps) {
  const { data: session } = useSession();
  const [favoritedIds, setFavoritedIds] = useState<Set<string>>(new Set());

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

  const handleToggleFavorite = async (pluginId: string) => {
    if (!session) return;

    const isFavorited = favoritedIds.has(pluginId);
    const method = isFavorited ? "DELETE" : "POST";

    // Optimistic update
    setFavoritedIds((prev) => {
      const next = new Set(prev);
      if (isFavorited) {
        next.delete(pluginId);
      } else {
        next.add(pluginId);
      }
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
      // Revert on failure
      setFavoritedIds((prev) => {
        const next = new Set(prev);
        if (isFavorited) {
          next.add(pluginId);
        } else {
          next.delete(pluginId);
        }
        return next;
      });
    }
  };

  return (
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
  );
}
