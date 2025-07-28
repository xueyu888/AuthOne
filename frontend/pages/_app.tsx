import type { AppProps } from 'next/app';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useState } from 'react';
import Layout from '../components/Layout';
import '../styles/globals.css';
import { TranslationProvider } from '../contexts/TranslationContext';

/**
 * 应用根组件。将所有页面包裹在统一的布局之下。
 */
export default function MyApp({ Component, pageProps }: AppProps) {
  const [queryClient] = useState(() => new QueryClient());

  return (
    <QueryClientProvider client={queryClient}>
      <TranslationProvider>
        <Layout>
          <Component {...pageProps} />
        </Layout>
      </TranslationProvider>
    </QueryClientProvider>
  );
}