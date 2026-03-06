"use client";

import { useEffect, useState, use } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";

interface Category {
  id: string;
  name: string;
  slug: string;
}

export default function EditPluginPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = use(params);
  const router = useRouter();
  const [categories, setCategories] = useState<Category[]>([]);
  const [loading, setLoading] = useState(false);
  const [initialLoading, setInitialLoading] = useState(true);
  const [error, setError] = useState("");
  const [form, setForm] = useState({
    name: "", description: "", author: "", imageUrl: "",
    figmaUrl: "", categoryId: "", tags: "", featured: false,
  });

  useEffect(() => {
    async function fetchData() {
      try {
        const [pluginRes, categoriesRes] = await Promise.all([
          fetch(`/api/plugins/${id}`),
          fetch("/api/categories"),
        ]);
        if (!pluginRes.ok) throw new Error("Plugin not found");
        if (!categoriesRes.ok) throw new Error("Failed to fetch categories");
        const plugin = await pluginRes.json();
        const cats = await categoriesRes.json();
        setForm({
          name: plugin.name || "", description: plugin.description || "",
          author: plugin.author || "", imageUrl: plugin.imageUrl || "",
          figmaUrl: plugin.figmaUrl || "", categoryId: plugin.categoryId || "",
          tags: plugin.tags || "", featured: plugin.featured || false,
        });
        setCategories(cats);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to load plugin data");
      } finally {
        setInitialLoading(false);
      }
    }
    fetchData();
  }, [id]);

  function handleChange(e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) {
    const { name, value, type } = e.target;
    setForm((prev) => ({
      ...prev,
      [name]: type === "checkbox" ? (e.target as HTMLInputElement).checked : value,
    }));
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    if (!form.name.trim()) { setError("Plugin name is required"); return; }
    if (!form.description.trim()) { setError("Description is required"); return; }
    if (!form.author.trim()) { setError("Author is required"); return; }
    if (!form.categoryId) { setError("Category is required"); return; }

    setLoading(true);
    try {
      const res = await fetch(`/api/plugins/${id}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          ...form, name: form.name.trim(), description: form.description.trim(),
          author: form.author.trim(), imageUrl: form.imageUrl.trim() || null,
          figmaUrl: form.figmaUrl.trim() || null, tags: form.tags.trim(),
        }),
      });
      if (!res.ok) {
        const data = await res.json();
        throw new Error(data.error || "Failed to update plugin");
      }
      router.push("/admin/plugins");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to update plugin");
    } finally {
      setLoading(false);
    }
  }

  const inputClasses = "w-full bg-gray-800 border border-gray-700 rounded-lg px-4 py-2.5 text-sm text-gray-200 placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-violet-500/50 focus:border-violet-500 transition-colors";
  const labelClasses = "block text-sm font-medium text-gray-300 mb-1.5";

  if (initialLoading) {
    return (
      <div className="flex items-center justify-center min-h-[40vh]">
        <div className="animate-spin rounded-full h-10 w-10 border-t-2 border-b-2 border-violet-500"></div>
      </div>
    );
  }

  return (
    <div className="max-w-2xl">
      <div className="flex items-center gap-3 mb-8">
        <Link href="/admin/plugins" className="text-gray-500 hover:text-gray-300 transition-colors">←</Link>
        <h1 className="text-2xl font-bold text-gray-100">Edit Plugin</h1>
      </div>
      {error && (<div className="bg-red-500/10 border border-red-500/30 rounded-lg p-3 mb-6 text-sm text-red-400">{error}</div>)}
      <form onSubmit={handleSubmit} className="bg-gray-900 border border-gray-800 rounded-xl p-6 space-y-5">
        <div>
          <label htmlFor="name" className={labelClasses}>Name <span className="text-red-400">*</span></label>
          <input id="name" name="name" type="text" value={form.name} onChange={handleChange} placeholder="e.g., Auto Layout Helper" className={inputClasses} required />
        </div>
        <div>
          <label htmlFor="description" className={labelClasses}>Description <span className="text-red-400">*</span></label>
          <textarea id="description" name="description" value={form.description} onChange={handleChange} placeholder="Describe what this plugin does..." rows={4} className={inputClasses + " resize-vertical"} required />
        </div>
        <div>
          <label htmlFor="author" className={labelClasses}>Author <span className="text-red-400">*</span></label>
          <input id="author" name="author" type="text" value={form.author} onChange={handleChange} placeholder="Plugin author name" className={inputClasses} required />
        </div>
        <div>
          <label htmlFor="categoryId" className={labelClasses}>Category <span className="text-red-400">*</span></label>
          <select id="categoryId" name="categoryId" value={form.categoryId} onChange={handleChange} className={inputClasses} required>
            <option value="">Select a category</option>
            {categories.map((cat) => (<option key={cat.id} value={cat.id}>{cat.name}</option>))}
          </select>
        </div>
        <div>
          <label htmlFor="imageUrl" className={labelClasses}>Image URL</label>
          <input id="imageUrl" name="imageUrl" type="url" value={form.imageUrl} onChange={handleChange} placeholder="https://example.com/image.png" className={inputClasses} />
        </div>
        <div>
          <label htmlFor="figmaUrl" className={labelClasses}>Figma URL</label>
          <input id="figmaUrl" name="figmaUrl" type="url" value={form.figmaUrl} onChange={handleChange} placeholder="https://www.figma.com/community/plugin/..." className={inputClasses} />
        </div>
        <div>
          <label htmlFor="tags" className={labelClasses}>Tags</label>
          <input id="tags" name="tags" type="text" value={form.tags} onChange={handleChange} placeholder="Comma-separated tags: design, layout, utility" className={inputClasses} />
          <p className="text-xs text-gray-500 mt-1">Separate multiple tags with commas</p>
        </div>
        <div className="flex items-center gap-3">
          <input id="featured" name="featured" type="checkbox" checked={form.featured} onChange={handleChange} className="w-4 h-4 rounded border-gray-600 bg-gray-800 text-violet-600 focus:ring-violet-500 focus:ring-offset-0" />
          <label htmlFor="featured" className="text-sm text-gray-300">Featured plugin (displayed prominently on the homepage)</label>
        </div>
        <div className="flex items-center gap-3 pt-3 border-t border-gray-800">
          <button type="submit" disabled={loading} className="bg-violet-600 hover:bg-violet-500 disabled:bg-violet-600/50 disabled:cursor-not-allowed text-white text-sm font-medium px-6 py-2.5 rounded-lg transition-colors">
            {loading ? "Saving..." : "Save Changes"}
          </button>
          <Link href="/admin/plugins" className="text-sm text-gray-400 hover:text-gray-300 px-4 py-2.5 transition-colors">Cancel</Link>
        </div>
      </form>
    </div>
  );
}
