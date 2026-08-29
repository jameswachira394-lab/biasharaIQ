import '@fontsource-variable/inter'
import '@fontsource-variable/syne'
import '@fontsource-variable/jetbrains-mono'
import './globals.css'
import { AuthProvider } from '@/context/AuthContext'
import CapacitorAppInit from '@/components/CapacitorAppInit'

export const metadata = {
  title: 'BiasharaIQ – Smart Business Finance',
  description: 'Financial intelligence for Kenyan SMEs',
  verification: {
    google: 'CflFsi1EUZEMR8MgRjj1i4FKmSb2PSaKTSMmjeOyhys'
  },
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
    <html lang="en" className="bg-semantic-bgMain">
      <body className="bg-semantic-bgMain text-semantic-white antialiased">
        <AuthProvider>
          <CapacitorAppInit />
          {children}
        </AuthProvider>
      </body>
    </html>
  )
}