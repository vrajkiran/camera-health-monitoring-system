import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { useTheme } from '../context/ThemeContext';
import { DashboardPage } from '../pages/DashboardPage';

interface AppShellProps {
  children?: React.ReactNode;
}

export const AppShell: React.FC<AppShellProps> = ({ children }) => {
  const { user, role, logout } = useAuth();
  const { theme, toggleTheme } = useTheme();
  const [currentTime, setCurrentTime] = useState<string>('');
  const [activeNav, setActiveNav] = useState<'dashboard' | 'cameras' | 'topology' | 'alerts' | 'analytics' | 'reports' | 'settings'>('dashboard');

  useEffect(() => {
    const updateTime = () => {
      const now = new Date();
      setCurrentTime(now.toUTCString().replace('GMT', 'UTC'));
    };
    updateTime();
    const interval = setInterval(updateTime, 1000);
    return () => clearInterval(interval);
  }, []);

  const navItems = [
    { id: 'dashboard', label: 'Executive Dashboard', icon: 'dashboard' },
    { id: 'cameras', label: 'Camera Nodes', icon: 'videocam' },
    { id: 'topology', label: 'Network Topology', icon: 'hub' },
    { id: 'alerts', label: 'Incidents & Alerts', icon: 'notifications' },
    { id: 'analytics', label: 'AI Risk Analytics', icon: 'monitoring' },
    { id: 'reports', label: 'Enterprise Reports', icon: 'summarize' },
    { id: 'settings', label: 'System Settings', icon: 'settings' },
  ];

  return (
    <div className="min-h-screen flex flex-col font-sans bg-slate-50 dark:bg-[#090d16] text-slate-800 dark:text-slate-100 transition-colors duration-200">
      {/* Top Enterprise Header (Resolves ISSUE-34) */}
      <header className="h-16 px-6 border-b border-slate-200 dark:border-slate-800 bg-white/80 dark:bg-[#0c1424]/80 backdrop-blur-md flex items-center justify-between sticky top-0 z-50">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-xl bg-blue-600 text-white flex items-center justify-center shadow-md shadow-blue-500/25">
            <span className="material-symbols-outlined text-xl">shield_locked</span>
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="font-extrabold text-sm tracking-wider uppercase text-slate-900 dark:text-white">
                UCEK-JNTUK
              </span>
              <span className="text-[10px] px-2 py-0.5 rounded-full font-semibold bg-blue-50 text-blue-700 dark:bg-blue-950/80 dark:text-blue-300 border border-blue-200/60 dark:border-blue-800/60">
                NODE: AP-KKD-01
              </span>
            </div>
            <p className="text-[11px] text-slate-500 dark:text-slate-400 font-medium">
              Surveillance Operations Center
            </p>
          </div>
        </div>

        <div className="flex items-center gap-4">
          {/* Telemetry Badge */}
          <div className="hidden sm:flex items-center gap-2 px-3 py-1.5 rounded-full bg-emerald-50 dark:bg-emerald-950/60 border border-emerald-200 dark:border-emerald-800/60 text-emerald-700 dark:text-emerald-300 text-xs font-semibold">
            <span className="relative flex h-2 w-2">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
            </span>
            <span>Cluster Healthy (26/26 Online)</span>
          </div>

          {/* UTC Clock */}
          <div className="hidden md:flex items-center gap-1.5 text-xs text-slate-500 dark:text-slate-400 font-mono">
            <span className="material-symbols-outlined text-[16px]">schedule</span>
            <span>{currentTime || 'Syncing clock...'}</span>
          </div>

          {/* Theme Switcher */}
          <button
            onClick={toggleTheme}
            type="button"
            className="p-2 rounded-xl text-slate-500 hover:text-slate-900 dark:text-slate-400 dark:hover:text-white bg-slate-100 hover:bg-slate-200 dark:bg-slate-800 dark:hover:bg-slate-700 transition-colors border border-slate-200 dark:border-slate-700"
            title="Toggle color mode"
          >
            <span className="material-symbols-outlined text-[20px]">
              {theme === 'dark' ? 'light_mode' : 'dark_mode'}
            </span>
          </button>

          {/* User Profile Pill & Logout */}
          <div className="flex items-center gap-2 pl-2 border-l border-slate-200 dark:border-slate-800">
            <div className="text-right hidden sm:block">
              <div className="text-xs font-bold text-slate-900 dark:text-white leading-tight">
                {user?.display_name || user?.username || 'System User'}
              </div>
              <span className="text-[10px] font-mono text-blue-600 dark:text-blue-400 font-semibold">
                {role}
              </span>
            </div>
            <button
              onClick={logout}
              title="Sign Out"
              className="p-2 rounded-xl text-rose-600 hover:bg-rose-50 dark:hover:bg-rose-950/40 transition-colors border border-rose-200 dark:border-rose-900/50 flex items-center justify-center text-xs gap-1 font-semibold cursor-pointer"
            >
              <span className="material-symbols-outlined text-[18px]">logout</span>
              <span className="hidden md:inline">Sign Out</span>
            </button>
          </div>
        </div>
      </header>

      {/* Main App Body with Sidebar */}
      <div className="flex flex-1 overflow-hidden">
        {/* Sidebar */}
        <aside className="w-64 border-r border-slate-200 dark:border-slate-800 bg-white dark:bg-[#0c1424] flex flex-col justify-between p-4 hidden md:flex shrink-0">
          <nav className="space-y-1">
            <div className="px-3 py-2 text-[10px] font-bold uppercase tracking-wider text-slate-400 dark:text-slate-500">
              Operations
            </div>
            {navItems.map((item) => {
              const isActive = activeNav === item.id;
              return (
                <button
                  key={item.id}
                  onClick={() => setActiveNav(item.id as any)}
                  className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-xs font-semibold transition-all cursor-pointer ${
                    isActive
                      ? 'bg-blue-50 text-blue-700 dark:bg-blue-900/40 dark:text-blue-200 shadow-sm border border-blue-200/50 dark:border-blue-700/50'
                      : 'text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800/60 hover:text-slate-900 dark:hover:text-white'
                  }`}
                >
                  <span className="material-symbols-outlined text-[18px]">{item.icon}</span>
                  <span>{item.label}</span>
                </button>
              );
            })}
          </nav>

          {/* Legacy Bridge Shortcut */}
          <div className="pt-4 border-t border-slate-200 dark:border-slate-800 text-xs">
            <a
              href="/legacy.html"
              target="_blank"
              rel="noreferrer"
              className="flex items-center justify-between p-2.5 rounded-xl bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300 hover:text-blue-600 dark:hover:text-blue-400 transition-colors font-medium text-[11px]"
            >
              <span className="flex items-center gap-1.5">
                <span className="material-symbols-outlined text-[16px]">open_in_new</span>
                Legacy Inspector
              </span>
              <span className="text-[10px] bg-slate-200 dark:bg-slate-700 px-1.5 py-0.5 rounded font-mono">
                v3.8
              </span>
            </a>
          </div>
        </aside>

        {/* Dynamic Content Area */}
        <main className="flex-1 overflow-auto p-4 md:p-6 lg:p-8">
          {children ? (
            children
          ) : activeNav === 'dashboard' ? (
            <DashboardPage />
          ) : (
            <div className="space-y-4 max-w-7xl mx-auto">
              <div className="p-4 rounded-2xl bg-amber-50 dark:bg-amber-950/40 border border-amber-200 dark:border-amber-800 text-amber-800 dark:text-amber-200 text-xs flex items-center justify-between">
                <span>
                  <strong>{activeNav.toUpperCase()}</strong> view is scheduled for redesign in the upcoming roadmap step. Displaying the live surveillance telemetry bridge below:
                </span>
                <button
                  onClick={() => setActiveNav('dashboard')}
                  className="font-bold underline text-amber-900 dark:text-amber-100"
                >
                  Return to Dashboard
                </button>
              </div>
              <div className="rounded-2xl border border-slate-200 dark:border-slate-800 overflow-hidden shadow-sm bg-white dark:bg-[#11192b]">
                <iframe
                  src="/legacy.html"
                  title="Campus Surveillance Bridge"
                  className="w-full h-[740px] border-0"
                />
              </div>
            </div>
          )}
        </main>
      </div>
    </div>
  );
};
