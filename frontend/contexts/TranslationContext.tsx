import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';

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

type Language = 'zh-CN' | 'zh-TW' | 'en';
type TranslationKey = keyof typeof translations['zh-CN'];

interface TranslationContextType {
  language: Language;
  setLanguage: (lang: Language) => void;
  t: (key: TranslationKey) => string;
}

const TranslationContext = createContext<TranslationContextType | undefined>(undefined);

export const TranslationProvider = ({ children }: { children: ReactNode }) => {
  const [language, setLanguage] = useState<Language>('zh-CN');

  const t = (key: TranslationKey) => {
    return translations[language][key] || translations['zh-CN'][key];
  };

  const handleLanguageChange = (newLanguage: Language) => {
    localStorage.setItem('language', newLanguage);
    setLanguage(newLanguage);
  };

  useEffect(() => {
    const savedLanguage = localStorage.getItem('language') as Language || 'zh-CN';
    setLanguage(savedLanguage);
  }, []);

  return (
    <TranslationContext.Provider value={{ 
      language, 
      setLanguage: handleLanguageChange, 
      t 
    }}>
      {children}
    </TranslationContext.Provider>
  );
};

export const useTranslation = () => {
  const context = useContext(TranslationContext);
  if (context === undefined) {
    throw new Error('useTranslation must be used within a TranslationProvider');
  }
  return context;
};

export type { TranslationKey };