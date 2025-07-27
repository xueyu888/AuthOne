import Link from 'next/link';
import Image from 'next/image';
import { ReactNode, useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import { BarChart3, Users, Shield, Archive, Settings, Bell, User, Check, X, Cog, Palette, Globe, Info, Sun, Moon, Monitor, ChevronDown } from 'lucide-react';

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
  const [showNotifications, setShowNotifications] = useState(false);
  const [isClosing, setIsClosing] = useState(false);
  const [showSettings, setShowSettings] = useState(false);
  const [isSettingsClosing, setIsSettingsClosing] = useState(false);
  const [showThemeModal, setShowThemeModal] = useState(false);
  const [theme, setTheme] = useState<'light' | 'dark' | 'system'>('light');
  const [showLanguageModal, setShowLanguageModal] = useState(false);
  const [language, setLanguage] = useState<'zh-CN' | 'zh-TW' | 'en'>('zh-CN');

  // 模拟通知数据
  const notifications = [
    {
      id: 1,
      title: '新用户注册',
      message: '用户 张三 已成功注册账户',
      time: '2分钟前',
      unread: true,
      type: 'user'
    },
    {
      id: 2,
      title: '权限变更',
      message: '角色 "管理员" 的权限已更新',
      time: '15分钟前',
      unread: true,
      type: 'permission'
    },
    {
      id: 3,
      title: '系统维护',
      message: '系统将于今晚23:00进行维护',
      time: '1小时前',
      unread: false,
      type: 'system'
    },
    {
      id: 4,
      title: '资源访问',
      message: '数据集 "用户行为分析" 被访问',
      time: '2小时前',
      unread: false,
      type: 'resource'
    }
  ];

  const unreadCount = notifications.filter(n => n.unread).length;

  const handleCloseNotifications = () => {
    setIsClosing(true);
    setTimeout(() => {
      setShowNotifications(false);
      setIsClosing(false);
    }, 200);
  };

  const handleCloseSettings = () => {
    setIsSettingsClosing(true);
    setTimeout(() => {
      setShowSettings(false);
      setIsSettingsClosing(false);
    }, 200);
  };

  const handleThemeChange = (newTheme: 'light' | 'dark' | 'system') => {
    let actualTheme = newTheme;
    if (newTheme === 'system') {
      actualTheme = window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
    }
    
    const htmlElement = document.documentElement;
    if (actualTheme === 'dark') {
      htmlElement.classList.add('dark');
    } else {
      htmlElement.classList.remove('dark');
    }
    
    localStorage.setItem('theme', newTheme);
    setTheme(newTheme);
  };

  const handleLanguageChange = (newLanguage: 'zh-CN' | 'zh-TW' | 'en') => {
    localStorage.setItem('language', newLanguage);
    setLanguage(newLanguage);
  };

  useEffect(() => {
    const savedTheme = localStorage.getItem('theme') as 'light' | 'dark' | 'system' || 'system';
    const savedLanguage = localStorage.getItem('language') as 'zh-CN' | 'zh-TW' | 'en' || 'zh-CN';
    
    let actualTheme = savedTheme;
    if (savedTheme === 'system') {
      actualTheme = window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
    }
    
    const htmlElement = document.documentElement;
    if (actualTheme === 'dark') {
      htmlElement.classList.add('dark');
    } else {
      htmlElement.classList.remove('dark');
    }
    
    setTheme(savedTheme);
    setLanguage(savedLanguage);
  }, []);

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-900 transition-colors duration-300">
      {/* 顶部导航栏 - 固定在页面顶部 */}
      <nav className="fixed top-0 left-0 right-0 z-50 bg-white/95 dark:bg-slate-800/95 backdrop-blur-sm border-b border-slate-200/60 dark:border-slate-700/60 shadow-sm transition-colors duration-300">
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
                <span className="ml-3 text-xl font-bold bg-gradient-to-r from-slate-900 to-slate-700 dark:from-slate-100 dark:to-slate-300 bg-clip-text text-transparent">
                  AuthOne
                </span>
              </div>
            </div>
            
            {/* 中间选项卡 */}
            <div className="flex items-center justify-center flex-1 mx-2.5">
              <div className="flex items-center space-x-2 bg-slate-100/80 dark:bg-slate-700/80 rounded-xl py-1 px-1 transition-colors duration-300">
                {navItems.map((item) => {
                  const Icon = item.icon;
                  const isActive = router.pathname === item.href;
                  return (
                    <Link
                      key={item.href}
                      href={item.href}
                      className={`flex items-center px-6 py-3 rounded-lg text-sm font-medium transition-all duration-200 min-w-[140px] justify-center ${
                        isActive
                          ? 'bg-white dark:bg-slate-600 text-slate-900 dark:text-slate-100 shadow-sm'
                          : 'text-slate-600 dark:text-slate-300 hover:text-slate-900 dark:hover:text-slate-100 hover:bg-white/50 dark:hover:bg-slate-600/50'
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
              {/* 通知按钮 */}
              <div className="relative">
                <button 
                  onClick={() => {
                    if (showNotifications) {
                      handleCloseNotifications();
                    } else {
                      setShowNotifications(true);
                    }
                  }}
                  className="relative p-2.5 rounded-lg text-slate-500 dark:text-slate-400 hover:text-slate-700 dark:hover:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-700 transition-colors duration-200"
                >
                  <Bell className="w-5 h-5" />
                  {unreadCount > 0 && (
                    <span className="absolute -top-1 -right-1 bg-red-500 text-white text-xs rounded-full w-5 h-5 flex items-center justify-center font-medium animate-pulse">
                      {unreadCount}
                    </span>
                  )}
                </button>

                {/* 通知下拉面板 */}
                {showNotifications && (
                  <>
                    {/* 遮罩层 */}
                    <div 
                      className="fixed inset-0 z-10" 
                      onClick={handleCloseNotifications}
                    />
                    
                    {/* 下拉面板 */}
                    <div className="absolute right-0 top-full mt-2 w-80 bg-white/95 dark:bg-slate-800/95 backdrop-blur-xl rounded-2xl shadow-2xl border border-slate-200/60 dark:border-slate-700/60 z-20 ring-1 ring-black/5 dark:ring-white/5 overflow-hidden"
                         style={{
                           animation: isClosing ? 'collapseUp 0.2s cubic-bezier(0.25, 0.8, 0.25, 1) forwards' : 'expandDown 0.2s cubic-bezier(0.34, 1.56, 0.64, 1) forwards',
                           transformOrigin: 'top'
                         }}>
                      {/* 头部 */}
                      <div className="flex items-center justify-between p-4 border-b border-slate-200/60 dark:border-slate-600/60">
                        <h3 className="text-lg font-bold text-slate-900 dark:text-slate-100">通知</h3>
                        <div className="flex items-center space-x-2">
                          {unreadCount > 0 && (
                            <button className="text-xs text-blue-600 dark:text-blue-400 hover:text-blue-700 dark:hover:text-blue-300 font-medium">
                              全部已读
                            </button>
                          )}
                          <button 
                            onClick={handleCloseNotifications}
                            className="p-1 rounded-md text-slate-400 dark:text-slate-500 hover:text-slate-600 dark:hover:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-700 transition-colors"
                          >
                            <X className="w-4 h-4" />
                          </button>
                        </div>
                      </div>

                      {/* 通知列表 */}
                      <div className="max-h-96 overflow-y-auto">
                        {notifications.length > 0 ? (
                          <div className="p-2">
                            {notifications.map((notification) => (
                              <div 
                                key={notification.id}
                                className={`group p-3 rounded-xl transition-all duration-200 cursor-pointer hover:bg-slate-50 dark:hover:bg-slate-700/50 ${
                                  notification.unread ? 'bg-blue-50/50 dark:bg-blue-900/20' : ''
                                }`}
                              >
                                <div className="flex items-start space-x-3">
                                  {/* 通知图标 */}
                                  <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${
                                    notification.type === 'user' ? 'bg-blue-100 text-blue-600' :
                                    notification.type === 'permission' ? 'bg-orange-100 text-orange-600' :
                                    notification.type === 'system' ? 'bg-green-100 text-green-600' :
                                    'bg-purple-100 text-purple-600'
                                  }`}>
                                    {notification.type === 'user' ? <Users className="w-4 h-4" /> :
                                     notification.type === 'permission' ? <Shield className="w-4 h-4" /> :
                                     notification.type === 'system' ? <Settings className="w-4 h-4" /> :
                                     <Archive className="w-4 h-4" />}
                                  </div>

                                  {/* 通知内容 */}
                                  <div className="flex-1 min-w-0">
                                    <div className="flex items-center justify-between">
                                      <h4 className="text-sm font-semibold text-slate-900 dark:text-slate-100 truncate">
                                        {notification.title}
                                      </h4>
                                      {notification.unread && (
                                        <div className="flex-shrink-0 w-2 h-2 bg-blue-500 rounded-full"></div>
                                      )}
                                    </div>
                                    <p className="text-sm text-slate-600 dark:text-slate-300 mt-1 line-clamp-2">
                                      {notification.message}
                                    </p>
                                    <span className="text-xs text-slate-500 dark:text-slate-400 mt-2 block">
                                      {notification.time}
                                    </span>
                                  </div>
                                </div>
                              </div>
                            ))}
                          </div>
                        ) : (
                          <div className="p-8 text-center">
                            <Bell className="w-8 h-8 text-slate-400 dark:text-slate-500 mx-auto mb-3" />
                            <p className="text-slate-500 dark:text-slate-400 font-medium">暂无通知</p>
                          </div>
                        )}
                      </div>

                      {/* 底部 */}
                      {notifications.length > 0 && (
                        <div className="p-3 border-t border-slate-200/60 dark:border-slate-600/60">
                          <button className="w-full text-center text-sm text-blue-600 dark:text-blue-400 hover:text-blue-700 dark:hover:text-blue-300 font-medium py-2 rounded-lg hover:bg-blue-50 dark:hover:bg-blue-900/20 transition-colors">
                            查看所有通知
                          </button>
                        </div>
                      )}
                    </div>
                  </>
                )}
              </div>

              {/* 设置按钮 */}
              <div className="relative">
                <button 
                  onClick={() => {
                    if (showSettings) {
                      handleCloseSettings();
                    } else {
                      setShowSettings(true);
                    }
                  }}
                  className="p-2.5 rounded-lg text-slate-500 dark:text-slate-400 hover:text-slate-700 dark:hover:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-700 transition-colors duration-200"
                >
                  <Settings className="w-5 h-5" />
                </button>

                {/* 设置下拉面板 */}
                {showSettings && (
                  <>
                    {/* 遮罩层 */}
                    <div 
                      className="fixed inset-0 z-10" 
                      onClick={handleCloseSettings}
                    />
                    
                    {/* 下拉面板 */}
                    <div className="absolute right-0 top-full mt-2 w-64 bg-white/95 dark:bg-slate-800/95 backdrop-blur-xl rounded-2xl shadow-2xl border border-slate-200/60 dark:border-slate-700/60 z-20 ring-1 ring-black/5 dark:ring-white/5 overflow-hidden"
                         style={{
                           animation: isSettingsClosing ? 'collapseUp 0.2s cubic-bezier(0.25, 0.8, 0.25, 1) forwards' : 'expandDown 0.2s cubic-bezier(0.34, 1.56, 0.64, 1) forwards',
                           transformOrigin: 'top'
                         }}>
                      {/* 头部 */}
                      <div className="flex items-center justify-between p-4 border-b border-slate-200/60 dark:border-slate-600/60">
                        <h3 className="text-lg font-bold text-slate-900 dark:text-slate-100">设置</h3>
                        <button 
                          onClick={handleCloseSettings}
                          className="p-1 rounded-md text-slate-400 dark:text-slate-500 hover:text-slate-600 dark:hover:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-700 transition-colors"
                        >
                          <X className="w-4 h-4" />
                        </button>
                      </div>

                      {/* 设置选项列表 */}
                      <div className="py-2">
                        {/* 系统设置 */}
                        <button className="w-full flex items-center px-4 py-3 text-left hover:bg-slate-50 dark:hover:bg-slate-700 transition-colors">
                          <Cog className="w-4 h-4 text-slate-600 dark:text-slate-400 mr-3" />
                          <span className="text-sm font-medium text-slate-900 dark:text-slate-100">系统设置</span>
                        </button>

                        {/* 外观 */}
                        <button 
                          onClick={() => {
                            setShowThemeModal(true);
                            setShowSettings(false);
                          }}
                          className="w-full flex items-center px-4 py-3 text-left hover:bg-slate-50 dark:hover:bg-slate-700 transition-colors"
                        >
                          <Palette className="w-4 h-4 text-slate-600 dark:text-slate-400 mr-3" />
                          <span className="text-sm font-medium text-slate-900 dark:text-slate-100">外观</span>
                        </button>

                        {/* 语言 */}
                        <button 
                          onClick={() => {
                            setShowLanguageModal(true);
                            setShowSettings(false);
                          }}
                          className="w-full flex items-center px-4 py-3 text-left hover:bg-slate-50 dark:hover:bg-slate-700 transition-colors"
                        >
                          <Globe className="w-4 h-4 text-slate-600 dark:text-slate-400 mr-3" />
                          <span className="text-sm font-medium text-slate-900 dark:text-slate-100">语言</span>
                        </button>

                        {/* 分割线 */}
                        <hr className="my-2 border-slate-200 dark:border-slate-600" />

                        {/* 关于 AuthOne */}
                        <button className="w-full flex items-center px-4 py-3 text-left hover:bg-slate-50 dark:hover:bg-slate-700 transition-colors">
                          <Info className="w-4 h-4 text-slate-600 dark:text-slate-400 mr-3" />
                          <span className="text-sm font-medium text-slate-900 dark:text-slate-100">关于 AuthOne</span>
                        </button>
                      </div>
                    </div>
                  </>
                )}
              </div>
              <button className="p-2.5 rounded-lg text-slate-500 dark:text-slate-400 hover:text-slate-700 dark:hover:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-700 transition-colors duration-200">
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

      {/* 主题设置弹窗 */}
      {showThemeModal && (
        <>
          {/* 遮罩层 */}
          <div 
            className="fixed inset-0 bg-black/20 backdrop-blur-md z-50 transition-all duration-300 ease-out"
            onClick={() => setShowThemeModal(false)}
          />
          
          {/* 弹窗容器 */}
          <div className="fixed inset-0 z-50 overflow-y-auto">
            <div className="flex min-h-full items-center justify-center p-4">
              <div 
                className="relative bg-white/95 dark:bg-slate-800/95 backdrop-blur-xl rounded-3xl shadow-2xl border border-white/20 dark:border-slate-700/20 w-full max-w-md transform transition-all duration-200 ease-out"
                onClick={(e) => e.stopPropagation()}
              >
                {/* 装饰性渐变背景 */}
                <div className="absolute inset-0 bg-gradient-to-br from-blue-50/50 to-purple-50/50 dark:from-slate-700/20 dark:to-slate-600/20 rounded-3xl" />
                
                {/* 弹窗内容 */}
                <div className="relative p-8">
                  {/* 头部 */}
                  <div className="flex items-center justify-between mb-8">
                    <div>
                      <h3 className="text-2xl font-bold text-gray-900 dark:text-slate-100 mb-2 tracking-tight">外观设置</h3>
                      <p className="text-base font-medium text-gray-600 dark:text-slate-400">选择你喜欢的界面主题</p>
                    </div>
                    <button
                      onClick={() => setShowThemeModal(false)}
                      className="p-2 text-gray-400 dark:text-slate-500 hover:text-gray-600 dark:hover:text-slate-300 hover:bg-white/60 dark:hover:bg-slate-700/60 rounded-xl transition-all duration-200 backdrop-blur-sm"
                    >
                      <X className="w-5 h-5" />
                    </button>
                  </div>
                  
                  {/* 主题选项 */}
                  <div className="space-y-4">
                    {/* 白天模式 */}
                    <button
                      onClick={() => handleThemeChange('light')}
                      className={`w-full p-4 rounded-2xl border transition-all duration-200 ${
                        theme === 'light'
                          ? 'bg-blue-50 dark:bg-blue-900/20 border-blue-200 dark:border-blue-700 ring-2 ring-blue-500/20'
                          : 'bg-white/70 dark:bg-slate-700/70 border-gray-200 dark:border-slate-600 hover:bg-gray-50 dark:hover:bg-slate-600/70'
                      }`}
                    >
                      <div className="flex items-center space-x-4">
                        <div className="flex-shrink-0">
                          <div className="w-12 h-12 bg-gradient-to-br from-yellow-400 to-orange-500 rounded-full flex items-center justify-center text-white shadow-lg">
                            <Sun className="w-6 h-6" />
                          </div>
                        </div>
                        <div className="flex-1 text-left">
                          <h4 className="text-lg font-semibold text-gray-900 dark:text-slate-100">白天模式</h4>
                          <p className="text-sm text-gray-600 dark:text-slate-400 mt-1">明亮清晰的界面风格</p>
                        </div>
                        {theme === 'light' && (
                          <div className="flex-shrink-0">
                            <div className="w-6 h-6 bg-blue-500 rounded-full flex items-center justify-center">
                              <Check className="w-4 h-4 text-white" />
                            </div>
                          </div>
                        )}
                      </div>
                    </button>

                    {/* 黑夜模式 */}
                    <button
                      onClick={() => handleThemeChange('dark')}
                      className={`w-full p-4 rounded-2xl border transition-all duration-200 ${
                        theme === 'dark'
                          ? 'bg-blue-50 dark:bg-blue-900/20 border-blue-200 dark:border-blue-700 ring-2 ring-blue-500/20'
                          : 'bg-white/70 dark:bg-slate-700/70 border-gray-200 dark:border-slate-600 hover:bg-gray-50 dark:hover:bg-slate-600/70'
                      }`}
                    >
                      <div className="flex items-center space-x-4">
                        <div className="flex-shrink-0">
                          <div className="w-12 h-12 bg-gradient-to-br from-slate-700 to-slate-900 rounded-full flex items-center justify-center text-white shadow-lg">
                            <Moon className="w-6 h-6" />
                          </div>
                        </div>
                        <div className="flex-1 text-left">
                          <h4 className="text-lg font-semibold text-gray-900 dark:text-slate-100">黑夜模式</h4>
                          <p className="text-sm text-gray-600 dark:text-slate-400 mt-1">护眼的深色界面风格</p>
                        </div>
                        {theme === 'dark' && (
                          <div className="flex-shrink-0">
                            <div className="w-6 h-6 bg-blue-500 rounded-full flex items-center justify-center">
                              <Check className="w-4 h-4 text-white" />
                            </div>
                          </div>
                        )}
                      </div>
                    </button>

                    {/* 跟随系统 */}
                    <button
                      onClick={() => handleThemeChange('system')}
                      className={`w-full p-4 rounded-2xl border transition-all duration-200 ${
                        theme === 'system'
                          ? 'bg-blue-50 dark:bg-blue-900/20 border-blue-200 dark:border-blue-700 ring-2 ring-blue-500/20'
                          : 'bg-white/70 dark:bg-slate-700/70 border-gray-200 dark:border-slate-600 hover:bg-gray-50 dark:hover:bg-slate-600/70'
                      }`}
                    >
                      <div className="flex items-center space-x-4">
                        <div className="flex-shrink-0">
                          <div className="w-12 h-12 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center text-white shadow-lg">
                            <Monitor className="w-6 h-6" />
                          </div>
                        </div>
                        <div className="flex-1 text-left">
                          <h4 className="text-lg font-semibold text-gray-900 dark:text-slate-100">跟随系统</h4>
                          <p className="text-sm text-gray-600 dark:text-slate-400 mt-1">自动跟随系统外观设置</p>
                        </div>
                        {theme === 'system' && (
                          <div className="flex-shrink-0">
                            <div className="w-6 h-6 bg-blue-500 rounded-full flex items-center justify-center">
                              <Check className="w-4 h-4 text-white" />
                            </div>
                          </div>
                        )}
                      </div>
                    </button>
                  </div>
                  
                  {/* 底部按钮 */}
                  <div className="flex justify-end mt-8">
                    <button
                      onClick={() => setShowThemeModal(false)}
                      className="px-6 py-3 bg-gradient-to-r from-blue-600 to-blue-700 text-white font-bold text-base rounded-2xl hover:from-blue-700 hover:to-blue-800 focus:outline-none focus:ring-2 focus:ring-blue-500/50 transition-all duration-200 shadow-lg hover:shadow-xl"
                    >
                      完成
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </>
      )}

      {/* 语言设置弹窗 */}
      {showLanguageModal && (
        <>
          {/* 遮罩层 */}
          <div 
            className="fixed inset-0 bg-black/20 backdrop-blur-md z-50 transition-all duration-300 ease-out"
            onClick={() => setShowLanguageModal(false)}
          />
          
          {/* 弹窗容器 */}
          <div className="fixed inset-0 z-50 overflow-y-auto">
            <div className="flex min-h-full items-center justify-center p-4">
              <div 
                className="relative bg-white/95 dark:bg-slate-800/95 backdrop-blur-xl rounded-3xl shadow-2xl border border-white/20 dark:border-slate-700/20 w-full max-w-md transform transition-all duration-200 ease-out"
                onClick={(e) => e.stopPropagation()}
              >
                {/* 装饰性渐变背景 */}
                <div className="absolute inset-0 bg-gradient-to-br from-green-50/50 to-blue-50/50 dark:from-slate-700/20 dark:to-slate-600/20 rounded-3xl" />
                
                {/* 弹窗内容 */}
                <div className="relative p-8">
                  {/* 头部 */}
                  <div className="flex items-center justify-between mb-8">
                    <div>
                      <h3 className="text-2xl font-bold text-gray-900 dark:text-slate-100 mb-2 tracking-tight">语言设置</h3>
                      <p className="text-base font-medium text-gray-600 dark:text-slate-400">选择你偏好的界面语言</p>
                    </div>
                    <button
                      onClick={() => setShowLanguageModal(false)}
                      className="p-2 text-gray-400 dark:text-slate-500 hover:text-gray-600 dark:hover:text-slate-300 hover:bg-white/60 dark:hover:bg-slate-700/60 rounded-xl transition-all duration-200 backdrop-blur-sm"
                    >
                      <X className="w-5 h-5" />
                    </button>
                  </div>
                  
                  {/* 语言选择下拉框 */}
                  <div className="space-y-4">
                    <div className="relative">
                      <label className="block text-sm font-medium text-gray-700 dark:text-slate-300 mb-3">
                        界面语言
                      </label>
                      <div className="relative">
                        <select
                          value={language}
                          onChange={(e) => handleLanguageChange(e.target.value as 'zh-CN' | 'zh-TW' | 'en')}
                          className="w-full p-4 pr-10 bg-white/70 dark:bg-slate-700/70 border border-gray-200 dark:border-slate-600 rounded-2xl text-gray-900 dark:text-slate-100 focus:outline-none focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500 transition-all duration-200 appearance-none font-medium"
                        >
                          <option value="zh-CN">简体中文</option>
                          <option value="zh-TW">繁體中文</option>
                          <option value="en">English</option>
                        </select>
                        <ChevronDown className="absolute right-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400 dark:text-slate-500 pointer-events-none" />
                      </div>
                    </div>

                    {/* 语言预览 */}
                    <div className="mt-6 p-4 bg-slate-50 dark:bg-slate-700/50 rounded-2xl border border-slate-200 dark:border-slate-600">
                      <div className="flex items-center space-x-3">
                        <div className="w-8 h-8 bg-gradient-to-br from-green-400 to-blue-500 rounded-full flex items-center justify-center">
                          <Globe className="w-4 h-4 text-white" />
                        </div>
                        <div>
                          <h4 className="text-sm font-semibold text-gray-900 dark:text-slate-100">
                            {language === 'zh-CN' ? '简体中文' : 
                             language === 'zh-TW' ? '繁體中文' : 
                             'English'}
                          </h4>
                          <p className="text-xs text-gray-600 dark:text-slate-400">
                            {language === 'zh-CN' ? '当前选择的语言' : 
                             language === 'zh-TW' ? '當前選擇的語言' : 
                             'Currently selected language'}
                          </p>
                        </div>
                      </div>
                    </div>
                  </div>
                  
                  {/* 底部按钮 */}
                  <div className="flex justify-end mt-8">
                    <button
                      onClick={() => setShowLanguageModal(false)}
                      className="px-6 py-3 bg-gradient-to-r from-green-600 to-blue-600 text-white font-bold text-base rounded-2xl hover:from-green-700 hover:to-blue-700 focus:outline-none focus:ring-2 focus:ring-green-500/50 transition-all duration-200 shadow-lg hover:shadow-xl"
                    >
                      {language === 'zh-CN' ? '完成' : 
                       language === 'zh-TW' ? '完成' : 
                       'Done'}
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </>
      )}
    </div>
  );
}