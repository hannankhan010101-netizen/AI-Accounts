/** @type {import('next').NextConfig} */
const backendProxy =
  process.env.API_PROXY_TARGET?.replace(/\/$/, "") ?? "http://127.0.0.1:8000";
const ingestionProxy =
  process.env.INGESTION_PROXY_TARGET?.replace(/\/$/, "") ?? "http://127.0.0.1:4100";

const nextConfig = {
  reactStrictMode: true,
  experimental: {
    typedRoutes: false,
    // Default rewrite proxy timeout is 30s; dashboard/overview can exceed that on large tenants.
    proxyTimeout: 180_000,
  },
  async headers() {
    return [
      {
        source: "/_next/static/:path*",
        headers: [
          {
            key: "Cache-Control",
            value: "public, max-age=31536000, immutable",
          },
        ],
      },
      {
        source: "/brand/:path*",
        headers: [
          {
            key: "Cache-Control",
            value: "public, max-age=86400, stale-while-revalidate=604800",
          },
        ],
      },
      {
        source: "/favicon.ico",
        headers: [
          {
            key: "Cache-Control",
            value: "public, max-age=86400, stale-while-revalidate=604800",
          },
        ],
      },
      {
        source: "/api/v1/:path*",
        headers: [
          {
            key: "Cache-Control",
            value: "private, no-store",
          },
        ],
      },
    ];
  },
  async rewrites() {
    if (process.env.NODE_ENV === "production") return [];
    return [
      {
        source: "/api/v1/:path*",
        destination: `${backendProxy}/api/v1/:path*`,
      },
      {
        source: "/api/ingestion/v1/:path*",
        destination: `${ingestionProxy}/api/v1/:path*`,
      },
    ];
  },
};
export default nextConfig;
