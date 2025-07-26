import type { AppProps } from 'next/app';
import Layout from '../components/Layout';
import '../styles/globals.css';

/**
 * 应用根组件。将所有页面包裹在统一的布局之下。
 */
export default function MyApp({ Component, pageProps }: AppProps) {
  return (
    <Layout>
      <Component {...pageProps} />
    </Layout>
  );
}