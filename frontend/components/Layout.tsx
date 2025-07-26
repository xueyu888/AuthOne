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
          padding: '0.75rem 1.5rem',
          backgroundColor: '#1f2937',
          color: 'white',
          boxShadow: '0 2px 4px rgba(0, 0, 0, 0.08)',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center' }}>
          <Image src="/logo.png" alt="AuthOne Logo" width={40} height={40} />
          <span
            style={{
              marginLeft: '0.75rem',
              fontWeight: 700,
              fontSize: '1.25rem',
              letterSpacing: '0.5px',
            }}
          >
            AuthOne
          </span>
        </div>
        <ul
          style={{
            listStyle: 'none',
            display: 'flex',
            gap: '1.25rem',
            margin: 0,
            padding: 0,
          }}
        >
          <li>
            <Link href="/" style={{ color: 'white', fontWeight: 500 }}>主页</Link>
          </li>
          <li>
            <Link href="/roles" style={{ color: 'white', fontWeight: 500 }}>角色</Link>
          </li>
          <li>
            <Link href="/permissions" style={{ color: 'white', fontWeight: 500 }}>权限</Link>
          </li>
          <li>
            <Link href="/accounts" style={{ color: 'white', fontWeight: 500 }}>账户</Link>
          </li>
          <li>
            <Link href="/groups" style={{ color: 'white', fontWeight: 500 }}>用户组</Link>
          </li>
          <li>
            <Link href="/resources" style={{ color: 'white', fontWeight: 500 }}>资源</Link>
          </li>
        </ul>
      </nav>
      <main style={{ padding: '1.5rem' }}>{children}</main>
    </div>
  );
}