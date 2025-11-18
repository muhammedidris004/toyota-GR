/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  // API proxy configuration (optional - we'll use direct API calls)
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: `${process.env.NEXT_PUBLIC_API_URL || 'https://toyota-gr.onrender.com'}/api/:path*`,
      },
    ];
  },
}

module.exports = nextConfig

