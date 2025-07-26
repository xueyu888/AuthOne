import Link from 'next/link';
import Image from 'next/image';
import { ReactNode } from 'react';

interface LayoutProps {
  children: ReactNode;
}

/**
 * 应用布局组件，包含导航栏和内容区域。
 *
 * 导航栏展示项目 Logo 和主要功能链接。
 */
export default function Layout({ children }: LayoutProps) {
  return (
    <div>
      <nav
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          padding: '0.5rem 1rem',
          borderBottom: '1px solid #eee',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center' }}>
          <Image src="/logo.png" alt="AuthOne Logo" width={36} height={36} />
          <span style={{ marginLeft: '0.5rem', fontWeight: 600, fontSize: '1.2rem' }}>AuthOne</span>
        </div>
        <ul style={{ listStyle: 'none', display: 'flex', gap: '1rem', margin: 0 }}>
          <li>
            <Link href="/">主页</Link>
          </li>
          <li>
            <Link href="/roles">角色</Link>
          </li>
          <li>
            <Link href="/permissions">权限</Link>
          </li>
          <li>
            <Link href="/accounts">账户</Link>
          </li>
          <li>
            <Link href="/groups">用户组</Link>
          </li>
          <li>
            <Link href="/resources">资源</Link>
          </li>
        </ul>
      </nav>
      <main style={{ padding: '1rem' }}>{children}</main>
    </div>
  );
}