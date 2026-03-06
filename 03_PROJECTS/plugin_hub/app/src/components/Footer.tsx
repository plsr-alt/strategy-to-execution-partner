export default function Footer() {
  return (
    <footer className="border-t border-gray-800 bg-gray-900/50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-2 text-gray-400">
            <span className="text-lg" role="img" aria-label="puzzle piece">
              🧩
            </span>
            <span className="text-sm font-medium">
              Plugin Hub &copy; 2026
            </span>
          </div>
          <p className="text-sm text-gray-500">
            Built with{" "}
            <span className="text-gray-400 font-medium">Next.js</span>
          </p>
        </div>
      </div>
    </footer>
  );
}
