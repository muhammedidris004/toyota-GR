/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  // API proxy configuration - proxy API calls to Render backend
  async rewrites() {
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'https://toyota-gr.onrender.com';
    return [
      {
        source: '/api/:path*',
        destination: `${apiUrl}/api/:path*`,
      },
    ];
  },
}

module.exports = nextConfig

