import Link from "next/link";
import FavoriteButton from "./FavoriteButton";

type Plugin = {
  id: string;
  name: string;
  description: string | null;
  imageUrl: string | null;
  figmaUrl: string | null;
  featured: boolean;
  createdAt: string;
  author: string;
  category: { id: string; name: string } | null;
  tags: string;
};

async function getPlugin(id: string): Promise<Plugin | null> {
  try {
    const baseUrl = process.env.NEXTAUTH_URL || "http://localhost:3000";
    const res = await fetch(`${baseUrl}/api/plugins/${id}`, {
      cache: "no-store",
    });
    if (!res.ok) return null;
    return await res.json();
  } catch {
    return null;
  }
}

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

export default async function PluginDetailPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  const plugin = await getPlugin(id);

  if (!plugin) {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16 text-center">
        <div className="text-5xl mb-4">😢</div>
        <h1 className="text-2xl font-bold text-white mb-2">Plugin Not Found</h1>
        <p className="text-gray-400 mb-6">
          The plugin you&apos;re looking for doesn&apos;t exist or has been removed.
        </p>
        <Link href="/plugins" className="inline-flex items-center gap-2 text-violet-400 hover:text-violet-300 transition-colors">
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
          </svg>
          Back to Plugins
        </Link>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <Link href="/plugins" className="inline-flex items-center gap-2 text-sm text-gray-400 hover:text-white transition-colors mb-8">
        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
        </svg>
        Back to Plugins
      </Link>

      <div className={`relative h-56 sm:h-72 rounded-2xl bg-gradient-to-br ${getGradient(plugin.name)} flex items-center justify-center overflow-hidden mb-8`}>
        {plugin.imageUrl ? (
          <img src={plugin.imageUrl} alt={plugin.name} className="w-full h-full object-cover" />
        ) : (
          <span className="text-8xl font-bold text-white/20 select-none">
            {plugin.name.charAt(0).toUpperCase()}
          </span>
        )}
        {plugin.featured && (
          <div className="absolute top-4 right-4 flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-amber-500/20 border border-amber-500/30 text-amber-400 text-sm font-medium backdrop-blur-sm">
            <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
              <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
            </svg>
            Featured
          </div>
        )}
      </div>

      <div className="space-y-6">
        <div className="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-4">
          <div>
            <h1 className="text-3xl font-bold text-white">{plugin.name}</h1>
            <p className="mt-1 text-gray-400">by {plugin.author}</p>
          </div>
          <div className="flex items-center gap-3">
            <FavoriteButton pluginId={plugin.id} />
            {plugin.figmaUrl && (
              <a href={plugin.figmaUrl} target="_blank" rel="noopener noreferrer"
                className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl text-sm font-semibold text-white bg-violet-600 hover:bg-violet-500 transition-colors shadow-lg shadow-violet-500/20">
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                </svg>
                Open in Figma
              </a>
            )}
          </div>
        </div>

        <div className="flex flex-wrap gap-2">
          {plugin.category && (
            <Link href={`/plugins?category=${plugin.category.id}`}
              className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-violet-500/20 text-violet-300 border border-violet-500/30 hover:bg-violet-500/30 transition-colors">
              {plugin.category.name}
            </Link>
          )}
          {plugin.tags.split(",").filter(Boolean).map((tag) => (
            <span key={tag.trim()} className="inline-flex items-center px-3 py-1 rounded-full text-sm text-gray-400 bg-gray-700/50 border border-gray-600/30">
              {tag.trim()}
            </span>
          ))}
        </div>

        {plugin.description && (
          <div className="bg-gray-800/60 rounded-xl border border-gray-700/50 p-6">
            <h2 className="text-lg font-semibold text-white mb-3">About this plugin</h2>
            <p className="text-gray-300 leading-relaxed whitespace-pre-wrap">{plugin.description}</p>
          </div>
        )}

        <div className="bg-gray-800/60 rounded-xl border border-gray-700/50 p-6">
          <h2 className="text-lg font-semibold text-white mb-4">Details</h2>
          <dl className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <dt className="text-sm text-gray-500">Author</dt>
              <dd className="text-sm text-gray-300 mt-1">{plugin.author}</dd>
            </div>
            <div>
              <dt className="text-sm text-gray-500">Category</dt>
              <dd className="text-sm text-gray-300 mt-1">{plugin.category?.name || "Uncategorized"}</dd>
            </div>
            <div>
              <dt className="text-sm text-gray-500">Added</dt>
              <dd className="text-sm text-gray-300 mt-1">
                {new Date(plugin.createdAt).toLocaleDateString("en-US", { year: "numeric", month: "long", day: "numeric" })}
              </dd>
            </div>
            {plugin.figmaUrl && (
              <div>
                <dt className="text-sm text-gray-500">Figma URL</dt>
                <dd className="text-sm mt-1">
                  <a href={plugin.figmaUrl} target="_blank" rel="noopener noreferrer" className="text-violet-400 hover:text-violet-300 transition-colors truncate block">
                    {plugin.figmaUrl}
                  </a>
                </dd>
              </div>
            )}
          </dl>
        </div>
      </div>
    </div>
  );
}
