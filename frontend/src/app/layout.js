import { Inter, Syne, JetBrains_Mono } from 'next/font/google'
import './globals.css'
import { AuthProvider } from '@/context/AuthContext'

const inter = Inter({ subsets: ['latin'], variable: '--font-inter' })
const syne = Syne({ subsets: ['latin'], variable: '--font-syne', weight: ['400', '500', '600', '700', '800'] })
const jetbrains = JetBrains_Mono({ subsets: ['latin'], variable: '--font-jetbrains' })

export const metadata = {
  title: 'BiasharaIQ – Smart Business Finance',
  description: 'Financial intelligence for Kenyan SMEs',
  icons: {
    icon: '/biasharaiq.png',
    apple: '/biasharaiq.png',
  },
  openGraph: {
    title: 'BiasharaIQ – Smart Business Finance',
    description: 'Financial intelligence for Kenyan SMEs',
    images: ['/biasharaiq.png'],
  },
}

export default function RootLayout({ children }) {
  return (
    <html lang="en" className={`${inter.variable} ${syne.variable} ${jetbrains.variable} bg-semantic-bgMain`}>
      <body className="bg-semantic-bgMain text-semantic-white antialiased">
        <AuthProvider>
          {children}
        </AuthProvider>
      </body>
    </html>
  )
}
