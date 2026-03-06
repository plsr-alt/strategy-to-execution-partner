"use client";

import { useEffect, useState } from "react";
import Link from "next/link";

interface Plugin {
  id: string;
  name: string;
  author: string;
  featured: boolean;
  createdAt: string;
  category: { id: string; name: string };
  _count: { favorites: number };
}

export default function AdminPluginsPage() {
  const [plugins, setPlugins] = useState<Plugin[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [actionLoading, setActionLoading] = useState<string | null>(null);

  async function fetchPlugins() {
    try {
      const res = await fetch("/api/plugins");
      if (!res.ok) throw new Error("Failed to fetch plugins");
      const data = await res.json();
      setPlugins(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load plugins");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    fetchPlugins();
  }, []);

  async function handleDelete(id: string, name: string) {
    if (!window.confirm(`Delete plugin "${name}"? This action cannot be undone.`)) {
      return;
    }

    setActionLoading(id);
    try {
      const res = await fetch(`/api/plugins/${id}`, { method: "DELETE" });
      if (!res.ok) {
        const data = await res.json();
        throw new Error(data.error || "Failed to delete plugin");
      }
      setPlugins((prev) => prev.filter((p) => p.id !== id));
    } catch (err) {
      alert(err instanceof Error ? err.message : "Delete failed");
    } finally {
      setActionLoading(null);
    }
  }

  async function handleToggleFeatured(id: string, currentFeatured: boolean) {
    setActionLoading(id);
    try {
      const res = await fetch(`/api/plugins/${id}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ featured: !currentFeatured }),
      });
      if (!res.ok) {
        const data = await res.json();
        throw new Error(data.error || "Failed to update plugin");
      }
      setPlugins((prev) =>
        prev.map((p) =>
          p.id === id ? { ...p, featured: !currentFeatured } : p
        )
      );
    } catch (err) {
      alert(err instanceof Error ? err.message : "Update failed");
    } finally {
      setActionLoading(null);
    }
  }

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
      <div className="flex items-center justify-between mb-8">
        <h1 className="text-2xl font-bold text-gray-100">Plugins</h1>
        <Link
          href="/admin/plugins/new"
          className="inline-flex items-center gap-2 bg-violet-600 hover:bg-violet-500 text-white text-sm font-medium px-4 py-2.5 rounded-lg transition-colors"
        >
          <span className="text-lg leading-none">+</span>
          Add New Plugin
        </Link>
      </div>

      {plugins.length === 0 ? (
        <div className="text-center py-16 bg-gray-900 border border-gray-800 rounded-xl">
          <p className="text-gray-500 mb-4">No plugins found.</p>
          <Link
            href="/admin/plugins/new"
            className="text-violet-400 hover:text-violet-300 text-sm"
          >
            Create your first plugin →
          </Link>
        </div>
      ) : (
        <div className="bg-gray-900 border border-gray-800 rounded-xl overflow-hidden">
          <table className="w-full">
            <thead>
              <tr className="border-b border-gray-800">
                <th className="text-left text-xs font-semibold text-gray-400 uppercase tracking-wider px-5 py-3">Name</th>
                <th className="text-left text-xs font-semibold text-gray-400 uppercase tracking-wider px-5 py-3">Author</th>
                <th className="text-left text-xs font-semibold text-gray-400 uppercase tracking-wider px-5 py-3">Category</th>
                <th className="text-center text-xs font-semibold text-gray-400 uppercase tracking-wider px-5 py-3">Featured</th>
                <th className="text-center text-xs font-semibold text-gray-400 uppercase tracking-wider px-5 py-3">Favs</th>
                <th className="text-right text-xs font-semibold text-gray-400 uppercase tracking-wider px-5 py-3">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-800/50">
              {plugins.map((plugin) => (
                <tr key={plugin.id} className="hover:bg-gray-800/40 transition-colors">
                  <td className="px-5 py-3.5">
                    <span className="text-sm font-medium text-gray-200">{plugin.name}</span>
                  </td>
                  <td className="px-5 py-3.5">
                    <span className="text-sm text-gray-400">{plugin.author}</span>
                  </td>
                  <td className="px-5 py-3.5">
                    <span className="inline-flex items-center px-2 py-0.5 rounded-md text-xs font-medium bg-gray-800 text-gray-300 border border-gray-700">
                      {plugin.category.name}
                    </span>
                  </td>
                  <td className="px-5 py-3.5 text-center">
                    <button
                      onClick={() => handleToggleFeatured(plugin.id, plugin.featured)}
                      disabled={actionLoading === plugin.id}
                      className={`text-lg transition-transform hover:scale-110 disabled:opacity-50 ${
                        plugin.featured ? "grayscale-0" : "grayscale opacity-30"
                      }`}
                      title={plugin.featured ? "Remove from featured" : "Mark as featured"}
                    >
                      ⭐
                    </button>
                  </td>
                  <td className="px-5 py-3.5 text-center">
                    <span className="text-sm text-gray-400">{plugin._count.favorites}</span>
                  </td>
                  <td className="px-5 py-3.5 text-right">
                    <div className="flex items-center justify-end gap-2">
                      <Link
                        href={`/admin/plugins/${plugin.id}/edit`}
                        className="text-xs font-medium text-violet-400 hover:text-violet-300 px-2.5 py-1.5 rounded-md hover:bg-violet-500/10 transition-colors"
                      >
                        Edit
                      </Link>
                      <button
                        onClick={() => handleDelete(plugin.id, plugin.name)}
                        disabled={actionLoading === plugin.id}
                        className="text-xs font-medium text-red-400 hover:text-red-300 px-2.5 py-1.5 rounded-md hover:bg-red-500/10 transition-colors disabled:opacity-50"
                      >
                        Delete
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      <p className="text-xs text-gray-600 mt-4">
        {plugins.length} plugin{plugins.length !== 1 ? "s" : ""} total
      </p>
    </div>
  );
}
