import Link from 'next/link';
import Image from 'next/image';
import { ReactNode, useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import { BarChart3, Users, Shield, Archive, Settings, Bell, User, Check, X, Cog, Palette, Globe, Info, Sun, Moon, Monitor, ChevronDown } from 'lucide-react';
import { useTranslation } from '../contexts/TranslationContext';

interface LayoutProps {
  children: ReactNode;
}

const translations = {
  'zh-CN': {
    dashboard: '仪表盘',
    userManagement: '用户管理',
    permissionManagement: '权限管理',
    resourceManagement: '资源管理',
    notifications: '通知',
    settings: '设置',
    systemSettings: '系统设置',
    appearance: '外观',
    language: '语言',
    about: '关于 AuthOne',
    markAllRead: '全部已读',
    noNotifications: '暂无通知',
    viewAllNotifications: '查看所有通知',
    newUserRegistration: '新用户注册',
    permissionChange: '权限变更',
    systemMaintenance: '系统维护',
    resourceAccess: '资源访问',
    userRegistered: '用户 张三 已成功注册账户',
    roleUpdated: '角色 "管理员" 的权限已更新',
    maintenanceNotice: '系统将于今晚23:00进行维护',
    datasetAccessed: '数据集 "用户行为分析" 被访问',
    minutesAgo: '分钟前',
    hoursAgo: '小时前',
    appearanceSettings: '外观设置',
    chooseTheme: '选择你喜欢的界面主题',
    lightMode: '白天模式',
    lightModeDesc: '明亮清晰的界面风格',
    darkMode: '黑夜模式',
    darkModeDesc: '护眼的深色界面风格',
    systemMode: '跟随系统',
    systemModeDesc: '自动跟随系统外观设置',
    done: '完成',
    languageSettings: '语言设置',
    chooseLanguage: '选择你偏好的界面语言',
    interfaceLanguage: '界面语言',
    currentLanguage: '当前选择的语言',
    // 用户管理相关
    users: '用户',
    roles: '角色',
    groups: '用户组',
    userManagementTitle: '用户管理',
    roleManagementTitle: '角色管理',
    groupManagementTitle: '用户组管理',
    createUser: '新建用户',
    createRole: '新建角色',
    createGroup: '新建用户组',
    createNewUser: '创建新用户',
    createNewRole: '创建新角色',
    createNewGroup: '创建新用户组',
    username: '用户名',
    email: '邮箱',
    roleName: '角色名称',
    groupName: '用户组名称',
    description: '描述',
    permissionCount: '权限数量',
    roleCount: '角色数量',
    actions: '操作',
    edit: '编辑',
    assignPermissions: '分配权限',
    assignRoles: '分配角色',
    cancel: '取消',
    create: '创建',
    creating: '创建中...',
    permissions: '个权限',
    rolesCount: '个角色'
  },
  'zh-TW': {
    dashboard: '儀表板',
    userManagement: '用戶管理',
    permissionManagement: '權限管理',
    resourceManagement: '資源管理',
    notifications: '通知',
    settings: '設置',
    systemSettings: '系統設置',
    appearance: '外觀',
    language: '語言',
    about: '關於 AuthOne',
    markAllRead: '全部已讀',
    noNotifications: '暫無通知',
    viewAllNotifications: '查看所有通知',
    newUserRegistration: '新用戶註冊',
    permissionChange: '權限變更',
    systemMaintenance: '系統維護',
    resourceAccess: '資源訪問',
    userRegistered: '用戶 張三 已成功註冊賬戶',
    roleUpdated: '角色 "管理員" 的權限已更新',
    maintenanceNotice: '系統將於今晚23:00進行維護',
    datasetAccessed: '數據集 "用戶行為分析" 被訪問',
    minutesAgo: '分鐘前',
    hoursAgo: '小時前',
    appearanceSettings: '外觀設置',
    chooseTheme: '選擇你喜歡的界面主題',
    lightMode: '白天模式',
    lightModeDesc: '明亮清晰的界面風格',
    darkMode: '黑夜模式',
    darkModeDesc: '護眼的深色界面風格',
    systemMode: '跟隨系統',
    systemModeDesc: '自動跟隨系統外觀設置',
    done: '完成',
    languageSettings: '語言設置',
    chooseLanguage: '選擇你偏好的界面語言',
    interfaceLanguage: '界面語言',
    currentLanguage: '當前選擇的語言',
    // 用戶管理相關
    users: '用戶',
    roles: '角色',
    groups: '用戶組',
    userManagementTitle: '用戶管理',
    roleManagementTitle: '角色管理',
    groupManagementTitle: '用戶組管理',
    createUser: '新建用戶',
    createRole: '新建角色',
    createGroup: '新建用戶組',
    createNewUser: '創建新用戶',
    createNewRole: '創建新角色',
    createNewGroup: '創建新用戶組',
    username: '用戶名',
    email: '郵箱',
    roleName: '角色名稱',
    groupName: '用戶組名稱',
    description: '描述',
    permissionCount: '權限數量',
    roleCount: '角色數量',
    actions: '操作',
    edit: '編輯',
    assignPermissions: '分配權限',
    assignRoles: '分配角色',
    cancel: '取消',
    create: '創建',
    creating: '創建中...',
    permissions: '個權限',
    rolesCount: '個角色'
  },
  'en': {
    dashboard: 'Dashboard',
    userManagement: 'User Management',
    permissionManagement: 'Permission Management',
    resourceManagement: 'Resource Management',
    notifications: 'Notifications',
    settings: 'Settings',
    systemSettings: 'System Settings',
    appearance: 'Appearance',
    language: 'Language',
    about: 'About AuthOne',
    markAllRead: 'Mark All Read',
    noNotifications: 'No notifications',
    viewAllNotifications: 'View All Notifications',
    newUserRegistration: 'New User Registration',
    permissionChange: 'Permission Change',
    systemMaintenance: 'System Maintenance',
    resourceAccess: 'Resource Access',
    userRegistered: 'User Zhang San has successfully registered',
    roleUpdated: 'Role "Administrator" permissions updated',
    maintenanceNotice: 'System maintenance scheduled for 23:00 tonight',
    datasetAccessed: 'Dataset "User Behavior Analysis" accessed',
    minutesAgo: 'minutes ago',
    hoursAgo: 'hours ago',
    appearanceSettings: 'Appearance Settings',
    chooseTheme: 'Choose your preferred interface theme',
    lightMode: 'Light Mode',
    lightModeDesc: 'Bright and clear interface style',
    darkMode: 'Dark Mode',
    darkModeDesc: 'Eye-friendly dark interface style',
    systemMode: 'Follow System',
    systemModeDesc: 'Automatically follow system appearance settings',
    done: 'Done',
    languageSettings: 'Language Settings',
    chooseLanguage: 'Choose your preferred interface language',
    interfaceLanguage: 'Interface Language',
    currentLanguage: 'Currently selected language',
    // User Management Related
    users: 'Users',
    roles: 'Roles',
    groups: 'Groups',
    userManagementTitle: 'User Management',
    roleManagementTitle: 'Role Management',
    groupManagementTitle: 'Group Management',
    createUser: 'Create User',
    createRole: 'Create Role',
    createGroup: 'Create Group',
    createNewUser: 'Create New User',
    createNewRole: 'Create New Role',
    createNewGroup: 'Create New Group',
    username: 'Username',
    email: 'Email',
    roleName: 'Role Name',
    groupName: 'Group Name',
    description: 'Description',
    permissionCount: 'Permission Count',
    roleCount: 'Role Count',
    actions: 'Actions',
    edit: 'Edit',
    assignPermissions: 'Assign Permissions',
    assignRoles: 'Assign Roles',
    cancel: 'Cancel',
    create: 'Create',
    creating: 'Creating...',
    permissions: ' permissions',
    rolesCount: ' roles'
  }
};

const navItems = [
  { href: '/', key: 'dashboard' as keyof typeof translations['zh-CN'], icon: BarChart3 },
  { href: '/accounts', key: 'userManagement' as keyof typeof translations['zh-CN'], icon: Users },
  { href: '/permissions', key: 'permissionManagement' as keyof typeof translations['zh-CN'], icon: Shield },
  { href: '/resources', key: 'resourceManagement' as keyof typeof translations['zh-CN'], icon: Archive },
];

export default function Layout({ children }: LayoutProps) {
  const router = useRouter();
  const { t, language, setLanguage } = useTranslation();
  const [showNotifications, setShowNotifications] = useState(false);
  const [isClosing, setIsClosing] = useState(false);
  const [showSettings, setShowSettings] = useState(false);
  const [isSettingsClosing, setIsSettingsClosing] = useState(false);
  const [showThemeModal, setShowThemeModal] = useState(false);
  const [theme, setTheme] = useState<'light' | 'dark' | 'system'>('light');
  const [showLanguageModal, setShowLanguageModal] = useState(false);

  const notifications = [
    {
      id: 1,
      titleKey: 'newUserRegistration' as keyof typeof translations['zh-CN'],
      messageKey: 'userRegistered' as keyof typeof translations['zh-CN'],
      time: `2${t('minutesAgo')}`,
      unread: true,
      type: 'user'
    },
    {
      id: 2,
      titleKey: 'permissionChange' as keyof typeof translations['zh-CN'],
      messageKey: 'roleUpdated' as keyof typeof translations['zh-CN'],
      time: `15${t('minutesAgo')}`,
      unread: true,
      type: 'permission'
    },
    {
      id: 3,
      titleKey: 'systemMaintenance' as keyof typeof translations['zh-CN'],
      messageKey: 'maintenanceNotice' as keyof typeof translations['zh-CN'],
      time: `1${t('hoursAgo')}`,
      unread: false,
      type: 'system'
    },
    {
      id: 4,
      titleKey: 'resourceAccess' as keyof typeof translations['zh-CN'],
      messageKey: 'datasetAccessed' as keyof typeof translations['zh-CN'],
      time: `2${t('hoursAgo')}`,
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


  useEffect(() => {
    const savedTheme = localStorage.getItem('theme') as 'light' | 'dark' | 'system' || 'system';
    
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
  }, []);

  return (
    <div className="h-screen bg-slate-50 dark:bg-slate-900 transition-colors duration-300 overflow-hidden">
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
                      {t(item.key)}
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
                        <h3 className="text-lg font-bold text-slate-900 dark:text-slate-100">{t('notifications')}</h3>
                        <div className="flex items-center space-x-2">
                          {unreadCount > 0 && (
                            <button className="text-xs text-blue-600 dark:text-blue-400 hover:text-blue-700 dark:hover:text-blue-300 font-medium">
                              {t('markAllRead')}
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
                                        {t(notification.titleKey)}
                                      </h4>
                                      {notification.unread && (
                                        <div className="flex-shrink-0 w-2 h-2 bg-blue-500 rounded-full"></div>
                                      )}
                                    </div>
                                    <p className="text-sm text-slate-600 dark:text-slate-300 mt-1 line-clamp-2">
                                      {t(notification.messageKey)}
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
                            <p className="text-slate-500 dark:text-slate-400 font-medium">{t('noNotifications')}</p>
                          </div>
                        )}
                      </div>

                      {/* 底部 */}
                      {notifications.length > 0 && (
                        <div className="p-3 border-t border-slate-200/60 dark:border-slate-600/60">
                          <button className="w-full text-center text-sm text-blue-600 dark:text-blue-400 hover:text-blue-700 dark:hover:text-blue-300 font-medium py-2 rounded-lg hover:bg-blue-50 dark:hover:bg-blue-900/20 transition-colors">
                            {t('viewAllNotifications')}
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
                        <h3 className="text-lg font-bold text-slate-900 dark:text-slate-100">{t('settings')}</h3>
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
                          <span className="text-sm font-medium text-slate-900 dark:text-slate-100">{t('systemSettings')}</span>
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
                          <span className="text-sm font-medium text-slate-900 dark:text-slate-100">{t('appearance')}</span>
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
                          <span className="text-sm font-medium text-slate-900 dark:text-slate-100">{t('language')}</span>
                        </button>

                        {/* 分割线 */}
                        <hr className="my-2 border-slate-200 dark:border-slate-600" />

                        {/* 关于 AuthOne */}
                        <button className="w-full flex items-center px-4 py-3 text-left hover:bg-slate-50 dark:hover:bg-slate-700 transition-colors">
                          <Info className="w-4 h-4 text-slate-600 dark:text-slate-400 mr-3" />
                          <span className="text-sm font-medium text-slate-900 dark:text-slate-100">{t('about')}</span>
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
      <main className="pt-16 h-full overflow-hidden">
        <div className="py-8 px-6 h-full overflow-hidden">
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
            <div className="flex h-full items-center justify-center p-4">
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
                      <h3 className="text-2xl font-bold text-gray-900 dark:text-slate-100 mb-2 tracking-tight">{t('appearanceSettings')}</h3>
                      <p className="text-base font-medium text-gray-600 dark:text-slate-400">{t('chooseTheme')}</p>
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
                          <h4 className="text-lg font-semibold text-gray-900 dark:text-slate-100">{t('lightMode')}</h4>
                          <p className="text-sm text-gray-600 dark:text-slate-400 mt-1">{t('lightModeDesc')}</p>
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
                          <h4 className="text-lg font-semibold text-gray-900 dark:text-slate-100">{t('darkMode')}</h4>
                          <p className="text-sm text-gray-600 dark:text-slate-400 mt-1">{t('darkModeDesc')}</p>
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
                          <h4 className="text-lg font-semibold text-gray-900 dark:text-slate-100">{t('systemMode')}</h4>
                          <p className="text-sm text-gray-600 dark:text-slate-400 mt-1">{t('systemModeDesc')}</p>
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
                      {t('done')}
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
            <div className="flex h-full items-center justify-center p-4">
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
                      <h3 className="text-2xl font-bold text-gray-900 dark:text-slate-100 mb-2 tracking-tight">{t('languageSettings')}</h3>
                      <p className="text-base font-medium text-gray-600 dark:text-slate-400">{t('chooseLanguage')}</p>
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
                        {t('interfaceLanguage')}
                      </label>
                      <div className="relative">
                        <select
                          value={language}
                          onChange={(e) => setLanguage(e.target.value as 'zh-CN' | 'zh-TW' | 'en')}
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
                            {t('currentLanguage')}
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
                      {t('done')}
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