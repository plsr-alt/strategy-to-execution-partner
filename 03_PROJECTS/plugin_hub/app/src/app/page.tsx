import Link from "next/link";
import PluginCardGrid from "@/components/PluginCardGrid";

async function getFeaturedPlugins() {
  try {
    const baseUrl = process.env.NEXTAUTH_URL || "http://localhost:3000";
    const res = await fetch(`${baseUrl}/api/plugins?featured=true&limit=6`, {
      cache: "no-store",
    });
    if (!res.ok) return [];
    const data = await res.json();
    return data.plugins || data || [];
  } catch {
    return [];
  }
}

async function getCategories() {
  try {
    const baseUrl = process.env.NEXTAUTH_URL || "http://localhost:3000";
    const res = await fetch(`${baseUrl}/api/categories`, {
      cache: "no-store",
    });
    if (!res.ok) return [];
    return await res.json();
  } catch {
    return [];
  }
}

export default async function HomePage() {
  const [featuredPlugins, categories] = await Promise.all([
    getFeaturedPlugins(),
    getCategories(),
  ]);

  return (
    <div>
      {/* Hero Section */}
      <section className="relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-b from-violet-600/10 via-purple-600/5 to-transparent" />
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-violet-900/20 via-transparent to-transparent" />

        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-24 sm:py-32">
          <div className="text-center space-y-6 max-w-3xl mx-auto">
            <h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold tracking-tight">
              <span className="bg-gradient-to-r from-violet-400 via-purple-400 to-pink-400 bg-clip-text text-transparent">
                Discover
              </span>{" "}
              the best
              <br />
              Figma plugins
            </h1>
            <p className="text-lg sm:text-xl text-gray-400 max-w-2xl mx-auto">
              Browse, search, and save your favorite Figma plugins. Curated
              collection for designers and developers.
            </p>

            {/* Search bar */}
            <form
              action="/plugins"
              method="GET"
              className="max-w-xl mx-auto mt-8"
            >
              <div className="relative group">
                <div className="absolute -inset-0.5 bg-gradient-to-r from-violet-600 to-purple-600 rounded-xl opacity-30 group-hover:opacity-50 blur transition-opacity" />
                <div className="relative flex items-center">
                  <svg
                    className="absolute left-4 w-5 h-5 text-gray-400"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
                    />
                  </svg>
                  <input
                    type="text"
                    name="search"
                    placeholder="Search plugins..."
                    className="w-full pl-12 pr-4 py-3.5 bg-gray-800 border border-gray-700 rounded-xl text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-violet-500 focus:border-transparent transition-all"
                  />
                </div>
              </div>
            </form>

            <div className="flex items-center justify-center gap-4 pt-4">
              <Link
                href="/plugins"
                className="px-6 py-3 rounded-xl text-sm font-semibold text-white bg-violet-600 hover:bg-violet-500 transition-colors shadow-lg shadow-violet-500/20"
              >
                Browse All Plugins
              </Link>
              <Link
                href="/register"
                className="px-6 py-3 rounded-xl text-sm font-semibold text-gray-300 bg-gray-800 hover:bg-gray-700 border border-gray-700 hover:border-gray-600 transition-colors"
              >
                Create Account
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Featured Plugins */}
      {featuredPlugins.length > 0 && (
        <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
          <div className="flex items-center justify-between mb-8">
            <div>
              <h2 className="text-2xl font-bold text-white">
                Featured Plugins
              </h2>
              <p className="mt-1 text-sm text-gray-400">
                Hand-picked plugins by our team
              </p>
            </div>
            <Link
              href="/plugins?featured=true"
              className="text-sm font-medium text-violet-400 hover:text-violet-300 transition-colors"
            >
              View all &rarr;
            </Link>
          </div>
          <PluginCardGrid plugins={featuredPlugins} />
        </section>
      )}

      {/* Categories Grid */}
      {categories.length > 0 && (
        <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
          <div className="mb-8">
            <h2 className="text-2xl font-bold text-white">
              Browse by Category
            </h2>
            <p className="mt-1 text-sm text-gray-400">
              Find plugins by what they do
            </p>
          </div>
          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-4">
            {categories.map(
              (category: { id: string; name: string; _count?: { plugins: number } }) => (
                <Link
                  key={category.id}
                  href={`/plugins?category=${category.id}`}
                  className="group p-6 rounded-xl bg-gray-800/60 border border-gray-700/50 hover:border-violet-500/50 hover:bg-gray-800 transition-all duration-300"
                >
                  <h3 className="font-semibold text-white group-hover:text-violet-300 transition-colors">
                    {category.name}
                  </h3>
                  {category._count && (
                    <p className="mt-1 text-sm text-gray-500">
                      {category._count.plugins} plugin
                      {category._count.plugins !== 1 ? "s" : ""}
                    </p>
                  )}
                </Link>
              )
            )}
          </div>
        </section>
      )}

      {/* Empty state if no featured plugins or categories */}
      {featuredPlugins.length === 0 && categories.length === 0 && (
        <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16 text-center">
          <div className="max-w-md mx-auto space-y-4">
            <div className="text-5xl">🧩</div>
            <h2 className="text-xl font-semibold text-white">
              Getting Started
            </h2>
            <p className="text-gray-400">
              No plugins yet. Add some plugins through the admin panel to get
              started.
            </p>
          </div>
        </section>
      )}
    </div>
  );
}
