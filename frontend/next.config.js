/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: `${process.env.NEXT_PUBLIC_API_URL || 'https://biasharaiq.onrender.com/_/backend'}/:path*`,
      },
    ]
  },
}

module.exports = nextConfig
