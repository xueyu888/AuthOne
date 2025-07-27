import Link from 'next/link';
import Image from 'next/image';
import { ReactNode } from 'react';
import { useRouter } from 'next/router';
import { BarChart3, Users, Shield, Archive, Settings, Bell, User } from 'lucide-react';

interface LayoutProps {
  children: ReactNode;
}

const navItems = [
  { href: '/', label: '仪表盘', icon: BarChart3 },
  { href: '/accounts', label: '用户管理', icon: Users },
  { href: '/permissions', label: '权限管理', icon: Shield },
  { href: '/resources', label: '资源管理', icon: Archive },
];

export default function Layout({ children }: LayoutProps) {
  const router = useRouter();

  return (
    <div className="min-h-screen bg-slate-50">
      {/* 顶部导航栏 - 固定在页面顶部 */}
      <nav className="fixed top-0 left-0 right-0 z-50 bg-white/95 backdrop-blur-sm border-b border-slate-200/60 shadow-sm">
        <div className="max-w-full px-6">
          <div className="flex items-center justify-between h-16">
            {/* 左侧 Logo */}
            <div className="flex items-center flex-shrink-0">
              <div className="flex items-center">
                <Image 
                  src="/logo.png" 
                  alt="AuthOne Logo" 
                  width={36} 
                  height={36}
                  className="rounded-lg"
                />
                <span className="ml-3 text-xl font-bold bg-gradient-to-r from-slate-900 to-slate-700 bg-clip-text text-transparent">
                  AuthOne
                </span>
              </div>
            </div>
            
            {/* 中间选项卡 */}
            <div className="flex items-center justify-center flex-1">
              <div className="flex items-center space-x-1 bg-slate-100/80 rounded-xl p-1">
                {navItems.map((item) => {
                  const Icon = item.icon;
                  const isActive = router.pathname === item.href;
                  return (
                    <Link
                      key={item.href}
                      href={item.href}
                      className={`flex items-center px-4 py-2.5 rounded-lg text-sm font-medium transition-all duration-200 ${
                        isActive
                          ? 'bg-white text-slate-900 shadow-sm'
                          : 'text-slate-600 hover:text-slate-900 hover:bg-white/50'
                      }`}
                    >
                      <Icon className="w-4 h-4 mr-2" />
                      {item.label}
                    </Link>
                  );
                })}
              </div>
            </div>

            {/* 右侧功能按钮 */}
            <div className="flex items-center space-x-2">
              <button className="p-2.5 rounded-lg text-slate-500 hover:text-slate-700 hover:bg-slate-100 transition-colors duration-200">
                <Bell className="w-5 h-5" />
              </button>
              <button className="p-2.5 rounded-lg text-slate-500 hover:text-slate-700 hover:bg-slate-100 transition-colors duration-200">
                <Settings className="w-5 h-5" />
              </button>
              <button className="p-2.5 rounded-lg text-slate-500 hover:text-slate-700 hover:bg-slate-100 transition-colors duration-200">
                <User className="w-5 h-5" />
              </button>
            </div>
          </div>
        </div>
      </nav>

      {/* 主内容区域 - 添加顶部padding以避免被固定导航栏遮挡 */}
      <main className="pt-16">
        <div className="max-w-7xl mx-auto py-8 px-6">
          {children}
        </div>
      </main>
    </div>
  );
}