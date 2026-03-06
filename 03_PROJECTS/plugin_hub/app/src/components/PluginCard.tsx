"use client";

import Link from "next/link";
import { useSession } from "next-auth/react";

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

type PluginCardProps = {
  plugin: Plugin;
  isFavorited?: boolean;
  onToggleFavorite?: (pluginId: string) => void;
};

// Generate a consistent gradient from plugin name
function getGradient(name: string): string {
  const gradients = [
    "from-violet-600 to-purple-600",
    "from-purple-600 to-pink-600",
    "from-blue-600 to-violet-600",
    "from-indigo-600 to-purple-600",
    "from-fuchsia-600 to-pink-600",
    "from-violet-600 to-indigo-600",
    "from-purple-600 to-blue-600",
    "from-pink-600 to-violet-600",
  ];
  const index =
    name.split("").reduce((acc, char) => acc + char.charCodeAt(0), 0) %
    gradients.length;
  return gradients[index];
}

function parseTags(tags: string): string[] {
  if (!tags) return [];
  return tags.split(",").map((t) => t.trim()).filter(Boolean);
}

export default function PluginCard({
  plugin,
  isFavorited = false,
  onToggleFavorite,
}: PluginCardProps) {
  const { data: session } = useSession();
  const tagList = parseTags(plugin.tags);

  return (
    <div className="group relative bg-gray-800/80 rounded-xl border border-gray-700/50 hover:border-violet-500/50 hover:shadow-lg hover:shadow-violet-500/5 transition-all duration-300 overflow-hidden">
      {/* Featured badge */}
      {plugin.featured && (
        <div className="absolute top-3 right-3 z-10 flex items-center gap-1 px-2 py-1 rounded-full bg-amber-500/20 border border-amber-500/30 text-amber-400 text-xs font-medium">
          <svg
            className="w-3 h-3"
            fill="currentColor"
            viewBox="0 0 20 20"
          >
            <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
          </svg>
          Featured
        </div>
      )}

      {/* Image / Gradient placeholder */}
      <Link href={`/plugins/${plugin.id}`}>
        <div
          className={`relative h-40 bg-gradient-to-br ${getGradient(
            plugin.name
          )} flex items-center justify-center overflow-hidden`}
        >
          {plugin.imageUrl ? (
            <img
              src={plugin.imageUrl}
              alt={plugin.name}
              className="w-full h-full object-cover"
            />
          ) : (
            <span className="text-5xl font-bold text-white/30 select-none">
              {plugin.name.charAt(0).toUpperCase()}
            </span>
          )}
          {/* Hover overlay */}
          <div className="absolute inset-0 bg-black/0 group-hover:bg-black/20 transition-colors duration-300" />
        </div>
      </Link>

      {/* Content */}
      <div className="p-4 space-y-3">
        <div className="flex items-start justify-between gap-2">
          <div className="min-w-0 flex-1">
            <Link href={`/plugins/${plugin.id}`}>
              <h3 className="text-base font-semibold text-white truncate group-hover:text-violet-300 transition-colors">
                {plugin.name}
              </h3>
            </Link>
            <p className="text-sm text-gray-400 truncate">
              by {plugin.author}
            </p>
          </div>

          {/* Favorite button */}
          {session && onToggleFavorite && (
            <button
              onClick={() => onToggleFavorite(plugin.id)}
              className="flex-shrink-0 p-1.5 rounded-lg hover:bg-gray-700/50 transition-colors"
              aria-label={isFavorited ? "Remove from favorites" : "Add to favorites"}
            >
              <svg
                className={`w-5 h-5 transition-colors ${
                  isFavorited
                    ? "fill-rose-500 text-rose-500"
                    : "fill-none text-gray-500 hover:text-rose-400"
                }`}
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
            </button>
          )}
        </div>

        {/* Description */}
        {plugin.description && (
          <p className="text-sm text-gray-400 line-clamp-2">
            {plugin.description}
          </p>
        )}

        {/* Category + Tags */}
        <div className="flex flex-wrap gap-1.5">
          {plugin.category && (
            <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-violet-500/20 text-violet-300 border border-violet-500/30">
              {plugin.category.name}
            </span>
          )}
          {tagList.slice(0, 3).map((tag) => (
            <span
              key={tag}
              className="inline-flex items-center px-2 py-0.5 rounded-full text-xs text-gray-400 bg-gray-700/50 border border-gray-600/30"
            >
              {tag}
            </span>
          ))}
          {tagList.length > 3 && (
            <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs text-gray-500">
              +{tagList.length - 3}
            </span>
          )}
        </div>
      </div>
    </div>
  );
}
