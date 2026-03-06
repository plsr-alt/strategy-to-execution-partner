"use client";

import { useEffect, useState } from "react";
import Link from "next/link";

interface Stats {
  pluginCount: number;
  categoryCount: number;
  userCount: number;
  favoriteCount: number;
  recentPlugins: {
    id: string;
    name: string;
    author: string;
    createdAt: string;
    category: { name: string };
  }[];
}

const statCards = [
  { key: "pluginCount" as const, label: "Total Plugins", icon: "🧩", color: "violet" },
  { key: "categoryCount" as const, label: "Total Categories", icon: "📁", color: "blue" },
  { key: "userCount" as const, label: "Total Users", icon: "👥", color: "emerald" },
  { key: "favoriteCount" as const, label: "Total Favorites", icon: "⭐", color: "amber" },
];

const colorMap: Record<string, { bg: string; border: string; text: string }> = {
  violet: { bg: "bg-violet-500/10", border: "border-violet-500/30", text: "text-violet-400" },
  blue: { bg: "bg-blue-500/10", border: "border-blue-500/30", text: "text-blue-400" },
  emerald: { bg: "bg-emerald-500/10", border: "border-emerald-500/30", text: "text-emerald-400" },
  amber: { bg: "bg-amber-500/10", border: "border-amber-500/30", text: "text-amber-400" },
};

export default function AdminDashboard() {
  const [stats, setStats] = useState<Stats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    async function fetchStats() {
      try {
        const res = await fetch("/api/admin/stats");
        if (!res.ok) throw new Error("Failed to fetch stats");
        const data = await res.json();
        setStats(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to load dashboard");
      } finally {
        setLoading(false);
      }
    }
    fetchStats();
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[40vh]">
        <div className="animate-spin rounded-full h-10 w-10 border-t-2 border-b-2 border-violet-500"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-500/10 border border-red-500/30 rounded-lg p-4 text-red-400">
        {error}
      </div>
    );
  }

  return (
    <div>
      <h1 className="text-2xl font-bold text-gray-100 mb-8">Dashboard</h1>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-10">
        {statCards.map((card) => {
          const colors = colorMap[card.color];
          return (
            <div
              key={card.key}
              className={`${colors.bg} border ${colors.border} rounded-xl p-5 transition-transform hover:scale-[1.02]`}
            >
              <div className="flex items-center justify-between mb-3">
                <span className="text-2xl">{card.icon}</span>
                <span className={`text-3xl font-bold ${colors.text}`}>
                  {stats?.[card.key] ?? 0}
                </span>
              </div>
              <p className="text-sm text-gray-400 font-medium">{card.label}</p>
            </div>
          );
        })}
      </div>

      {/* Recent Plugins */}
      <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
        <div className="flex items-center justify-between mb-5">
          <h2 className="text-lg font-semibold text-gray-200">
            Recent Plugins
          </h2>
          <Link
            href="/admin/plugins"
            className="text-sm text-violet-400 hover:text-violet-300 transition-colors"
          >
            View all →
          </Link>
        </div>

        {stats?.recentPlugins && stats.recentPlugins.length > 0 ? (
          <div className="space-y-3">
            {stats.recentPlugins.map((plugin) => (
              <div
                key={plugin.id}
                className="flex items-center justify-between py-3 px-4 rounded-lg bg-gray-800/50 hover:bg-gray-800 transition-colors"
              >
                <div>
                  <p className="text-sm font-medium text-gray-200">
                    {plugin.name}
                  </p>
                  <p className="text-xs text-gray-500 mt-0.5">
                    by {plugin.author} &middot; {plugin.category.name}
                  </p>
                </div>
                <span className="text-xs text-gray-500">
                  {new Date(plugin.createdAt).toLocaleDateString()}
                </span>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-sm text-gray-500 text-center py-6">
            No plugins yet. Add your first plugin!
          </p>
        )}
      </div>
    </div>
  );
}
