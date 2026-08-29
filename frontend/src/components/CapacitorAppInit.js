'use client'

import { useEffect } from 'react'
import { useRouter, usePathname } from 'next/navigation'

export default function CapacitorAppInit() {
  const router = useRouter()
  const pathname = usePathname()

  useEffect(() => {
    let cleanup = () => {}

    async function initCapacitor() {
      if (typeof window === 'undefined') return

      try {
        const { Capacitor } = await import('@capacitor/core')
        if (!Capacitor.isNativePlatform()) return

        // 1. Splash Screen
        try {
          const { SplashScreen } = await import('@capacitor/splash-screen')
          await SplashScreen.hide()
        } catch (e) {
          // Plugin optional or not installed yet
        }

        // 2. Status Bar
        try {
          const { StatusBar, Style } = await import('@capacitor/status-bar')
          await StatusBar.setStyle({ style: Style.Dark })
        } catch (e) {
          // Plugin optional or not installed yet
        }

        // 3. Android Hardware Back Button
        try {
          const { App } = await import('@capacitor/app')
          const backListener = await App.addListener('backButton', ({ canGoBack }) => {
            if (pathname === '/' || pathname === '/dashboard' || pathname === '/login') {
              App.exitApp()
            } else if (canGoBack) {
              router.back()
            } else {
              App.exitApp()
            }
          })
          cleanup = () => {
            backListener.remove()
          }
        } catch (e) {
          // App plugin optional or not installed yet
        }
      } catch (err) {
        console.warn('Capacitor initialization error:', err)
      }
    }

    initCapacitor()

    return () => {
      cleanup()
    }
  }, [pathname, router])

  return null
}
