import Link from 'next/link';
import Image from 'next/image';
import { ReactNode } from 'react';
import { useRouter } from 'next/router';
import { Shield, Users, Key, UserCheck, Archive, Settings } from 'lucide-react';

interface LayoutProps {
  children: ReactNode;
}

const navItems = [
  { href: '/', label: '仪表盘', icon: Shield },
  { href: '/accounts', label: '账户', icon: Users },
  { href: '/roles', label: '角色', icon: UserCheck },
  { href: '/permissions', label: '权限', icon: Key },
  { href: '/groups', label: '用户组', icon: Users },
  { href: '/resources', label: '资源', icon: Archive },
];

export default function Layout({ children }: LayoutProps) {
  const router = useRouter();

  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <div className="flex-shrink-0 flex items-center">
                <Image 
                  src="/logo.png" 
                  alt="AuthOne Logo" 
                  width={32} 
                  height={32}
                  className="rounded-lg"
                />
                <span className="ml-3 text-xl font-bold text-gray-900">
                  AuthOne
                </span>
              </div>
            </div>
            
            <div className="hidden md:block">
              <div className="ml-10 flex items-baseline space-x-4">
                {navItems.map((item) => {
                  const Icon = item.icon;
                  const isActive = router.pathname === item.href;
                  return (
                    <Link
                      key={item.href}
                      href={item.href}
                      className={`flex items-center px-3 py-2 rounded-md text-sm font-medium transition-colors duration-200 ${
                        isActive
                          ? 'bg-blue-100 text-blue-700'
                          : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
                      }`}
                    >
                      <Icon className="w-4 h-4 mr-2" />
                      {item.label}
                    </Link>
                  );
                })}
              </div>
            </div>

            <div className="flex items-center">
              <button className="p-2 rounded-md text-gray-400 hover:text-gray-500 hover:bg-gray-100">
                <Settings className="w-5 h-5" />
              </button>
            </div>
          </div>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
        {children}
      </main>
    </div>
  );
}