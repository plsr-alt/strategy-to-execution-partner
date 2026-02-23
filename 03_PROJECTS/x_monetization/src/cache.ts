import * as fs from 'fs';
import * as path from 'path';

// Simple file-based cache mechanism
const CACHE_DIR = path.join(process.cwd(), '.cache');

export function initCache() {
    if (!fs.existsSync(CACHE_DIR)) {
        fs.mkdirSync(CACHE_DIR, { recursive: true });
    }
}

function getCacheKey(endpoint: string, payload: any): string {
    // Simple hash for cache key
    const str = endpoint + JSON.stringify(payload);
    let hash = 0;
    for (let i = 0; i < str.length; i++) {
        const char = str.charCodeAt(i);
        hash = ((hash << 5) - hash) + char;
        hash = hash & hash;
    }
    return `req_${Math.abs(hash)}.json`;
}

export function getCachedResponse<T>(endpoint: string, payload: any, ttlHours: number = 24): T | null {
    initCache();
    const key = getCacheKey(endpoint, payload);
    const cachePath = path.join(CACHE_DIR, key);

    if (fs.existsSync(cachePath)) {
        const stats = fs.statSync(cachePath);
        const ageHrs = (Date.now() - stats.mtimeMs) / (1000 * 60 * 60);
        if (ageHrs <= ttlHours) {
            try {
                const data = fs.readFileSync(cachePath, 'utf8');
                return JSON.parse(data) as T;
            } catch (e) {
                return null;
            }
        }
    }
    return null;
}

export function setCachedResponse(endpoint: string, payload: any, response: any): void {
    initCache();
    const key = getCacheKey(endpoint, payload);
    const cachePath = path.join(CACHE_DIR, key);
    fs.writeFileSync(cachePath, JSON.stringify(response, null, 2), 'utf8');
}
