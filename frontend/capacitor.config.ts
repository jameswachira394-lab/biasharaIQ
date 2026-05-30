import type { CapacitorConfig } from '@capacitor/cli';

const config: CapacitorConfig = {
  appId: 'com.biasharaiq.app',
  appName: 'BiasharaIQ',
  server: {
    url: 'https://biashara-iq.vercel.app',
    cleartext: false
  }
};

export default config;