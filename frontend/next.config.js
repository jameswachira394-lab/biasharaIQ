/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: `${process.env.NEXT_PUBLIC_API_URL || 'https://biasharaiq.onrender.com'}/:path*`,
      },
    ]
  },
}

module.exports = nextConfig
