import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { useTheme } from '../context/ThemeContext';
import { UserRole } from '../types/auth';

export const LoginPage: React.FC = () => {
  const { login, isLoading, sessionExpired, dismissSessionExpired } = useAuth();
  const { theme, toggleTheme } = useTheme();

  const [username, setUsername] = useState('admin');
  const [password, setPassword] = useState('Admin@1234');
  const [showPassword, setShowPassword] = useState(false);
  const [selectedRole, setSelectedRole] = useState<UserRole>('ADMINISTRATOR');
  const [rememberMe, setRememberMe] = useState(true);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMessage(null);

    if (!username.trim() || !password) {
      setErrorMessage('Please enter both campus username and security password.');
      return;
    }

    try {
      await login(username.trim(), password, rememberMe);
    } catch (err: any) {
      setErrorMessage(err.message || 'Invalid credentials provided. Contact UCEK Network Operations.');
    }
  };

  const fillDemo = (user: string, pass: string, role: UserRole) => {
    setUsername(user);
    setPassword(pass);
    setSelectedRole(role);
    setErrorMessage(null);
    if (sessionExpired) dismissSessionExpired();
  };

  const handleResetNotice = () => {
    alert('Security key resets require campus root authorization. Contact UCEK NetOps: net-ops@jntuk.edu.in');
  };

  return (
    <div className="min-h-screen flex flex-col font-sans transition-colors duration-200 relative overflow-x-hidden select-none bg-slate-50 dark:bg-[#090d16] text-slate-800 dark:text-slate-100">
      {/* Background Topology Grid & Ambient Glow */}
      <div 
        className="fixed inset-0 pointer-events-none z-0 opacity-40 dark:opacity-60"
        style={{
          backgroundImage: `linear-gradient(to right, rgba(37, 99, 235, 0.08) 1px, transparent 1px), linear-gradient(to bottom, rgba(37, 99, 235, 0.08) 1px, transparent 1px)`,
          backgroundSize: '32px 32px'
        }}
      />
      <div 
        className="fixed inset-0 pointer-events-none z-0"
        style={{
          background: 'radial-gradient(circle at 50% 25%, rgba(37, 99, 235, 0.15) 0%, transparent 70%)'
        }}
      />

      {/* Top Enterprise Status Navigation Bar */}
      <header className="relative z-10 w-full px-6 py-4 flex items-center justify-between border-b border-slate-200/80 dark:border-slate-800/80 bg-white/70 dark:bg-[#0c1424]/70 backdrop-blur-md">
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
            <p className="text-xs text-slate-500 dark:text-slate-400 font-medium">
              Camera Health & Network Surveillance System
            </p>
          </div>
        </div>

        <div className="flex items-center gap-3">
          {/* Operational Badge */}
          <div className="hidden sm:flex items-center gap-2 px-3 py-1.5 rounded-full bg-emerald-50 dark:bg-emerald-950/60 border border-emerald-200 dark:border-emerald-800/60 text-emerald-700 dark:text-emerald-300 text-xs font-semibold">
            <span className="relative flex h-2 w-2">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
            </span>
            <span>Telemetry Active: 99.8% Online</span>
          </div>

          {/* Theme Switcher (Resolves ISSUE-21) */}
          <button
            onClick={toggleTheme}
            type="button"
            className="p-2 rounded-xl text-slate-500 hover:text-slate-900 dark:text-slate-400 dark:hover:text-white bg-slate-100 hover:bg-slate-200 dark:bg-slate-800 dark:hover:bg-slate-700 transition-colors border border-slate-200 dark:border-slate-700"
            title="Toggle color mode"
            aria-label="Toggle dark/light mode"
          >
            <span className="material-symbols-outlined text-[20px]">
              {theme === 'dark' ? 'light_mode' : 'dark_mode'}
            </span>
          </button>
        </div>
      </header>

      {/* Central Authentication Card */}
      <main className="relative z-10 flex-1 flex items-center justify-center p-4 sm:p-6 lg:p-8">
        <div className="w-full max-w-[460px]">
          
          {/* Security Banner Pill */}
          <div className="mb-5 flex items-center justify-between px-4 py-2.5 rounded-2xl bg-white/80 dark:bg-slate-900/80 border border-slate-200 dark:border-slate-800 shadow-sm backdrop-blur-sm text-xs">
            <div className="flex items-center gap-2 text-slate-600 dark:text-slate-300">
              <span className="material-symbols-outlined text-blue-600 dark:text-blue-400 text-base">
                verified_user
              </span>
              <span className="font-medium">JNTUK Intranet Access Portal</span>
            </div>
            <span className="font-mono text-[11px] text-slate-400 dark:text-slate-500">
              TLS 1.3 / AES-256
            </span>
          </div>

          {/* Session Expired Banner (Resolves ISSUE-31) */}
          {sessionExpired && (
            <div className="mb-4 p-3.5 rounded-2xl bg-amber-50 dark:bg-amber-950/60 border border-amber-200 dark:border-amber-800/80 text-amber-800 dark:text-amber-200 text-xs flex items-center justify-between shadow-sm animate-pulse">
              <div className="flex items-center gap-2">
                <span className="material-symbols-outlined text-amber-600 dark:text-amber-400 text-lg">
                  timer_off
                </span>
                <span>Your session has expired. Please sign in again.</span>
              </div>
              <button 
                onClick={dismissSessionExpired} 
                className="text-amber-600 hover:text-amber-900 font-bold ml-2 text-sm"
              >
                ✕
              </button>
            </div>
          )}

          {/* Main Login Card */}
          <div className="bg-white dark:bg-[#11192b] rounded-3xl border border-slate-200 dark:border-slate-800/90 shadow-2xl shadow-slate-200/50 dark:shadow-black/60 p-7 sm:p-9 transition-all">
            
            {/* Header & Identity */}
            <div className="text-center mb-7">
              <div className="mx-auto w-16 h-16 rounded-2xl bg-gradient-to-tr from-blue-700 to-indigo-500 text-white flex items-center justify-center mb-4 shadow-lg shadow-blue-600/30 border border-blue-400/30 relative">
                <span className="material-symbols-outlined text-3xl">videocam</span>
                <span className="absolute -bottom-1 -right-1 w-5 h-5 rounded-full bg-emerald-500 border-2 border-white dark:border-[#11192b] flex items-center justify-center text-[10px] text-white font-bold">
                  ✓
                </span>
              </div>

              <h1 className="text-2xl font-bold text-slate-900 dark:text-white tracking-tight">
                Vigilant Enterprise
              </h1>
              <p className="text-xs font-semibold uppercase tracking-wider text-blue-600 dark:text-blue-400 mt-1">
                Surveillance Core v4.2
              </p>
              <p className="text-sm text-slate-500 dark:text-slate-400 mt-2">
                Sign in to monitor campus CCTV nodes, AI diagnostics & switch infrastructure
              </p>
            </div>

            {/* Role Selector Segmented Control */}
            <div className="mb-6">
              <div className="flex items-center justify-between mb-2">
                <span className="text-xs font-semibold text-slate-600 dark:text-slate-300 uppercase tracking-wider">
                  Target Role
                </span>
                <span className="text-blue-600 dark:text-blue-400 font-mono text-[11px] font-bold">
                  {selectedRole}
                </span>
              </div>
              <div className="grid grid-cols-3 gap-1.5 p-1 bg-slate-100 dark:bg-slate-900/80 rounded-xl border border-slate-200 dark:border-slate-800">
                {(['ADMINISTRATOR', 'NETWORK_ENGINEER', 'VIEWER'] as UserRole[]).map((r) => {
                  const isActive = selectedRole === r;
                  const label = r === 'ADMINISTRATOR' ? 'Admin' : r === 'NETWORK_ENGINEER' ? 'Engineer' : 'Viewer';
                  const icon = r === 'ADMINISTRATOR' ? 'admin_panel_settings' : r === 'NETWORK_ENGINEER' ? 'hub' : 'visibility';
                  return (
                    <button
                      key={r}
                      type="button"
                      onClick={() => setSelectedRole(r)}
                      className={`py-2 px-2 text-xs rounded-lg transition-all flex items-center justify-center gap-1.5 ${
                        isActive
                          ? 'font-semibold bg-white dark:bg-blue-600 text-blue-700 dark:text-white shadow-sm'
                          : 'font-medium text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white'
                      }`}
                    >
                      <span className="material-symbols-outlined text-[16px]">{icon}</span>
                      <span>{label}</span>
                    </button>
                  );
                })}
              </div>
            </div>

            {/* Controlled Form Elements (Resolves ISSUE-04) */}
            <form onSubmit={handleSubmit} className="space-y-4">
              {/* Username Input */}
              <div>
                <label 
                  htmlFor="usernameInput" 
                  className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1.5"
                >
                  Campus ID / Username
                </label>
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-400">
                    <span className="material-symbols-outlined text-[19px]">account_circle</span>
                  </div>
                  <input
                    id="usernameInput"
                    type="text"
                    required
                    value={username}
                    onChange={(e) => setUsername(e.target.value)}
                    disabled={isLoading}
                    autoComplete="username"
                    placeholder="e.g. admin or staff.ece"
                    className="w-full pl-10 pr-4 py-2.5 rounded-xl border border-slate-300 dark:border-slate-700 bg-slate-50/50 dark:bg-slate-900/60 text-slate-900 dark:text-white placeholder-slate-400 text-sm font-medium focus:ring-2 focus:ring-blue-600/30 focus:border-blue-600 dark:focus:border-blue-500 outline-none transition-all disabled:opacity-50"
                  />
                </div>
              </div>

              {/* Password Input with Visibility Toggle */}
              <div>
                <div className="flex items-center justify-between mb-1.5">
                  <label 
                    htmlFor="passwordInput" 
                    className="block text-xs font-semibold text-slate-700 dark:text-slate-300"
                  >
                    Security Password
                  </label>
                  <button
                    type="button"
                    onClick={handleResetNotice}
                    className="text-xs text-blue-600 hover:text-blue-700 dark:text-blue-400 dark:hover:text-blue-300 font-medium"
                  >
                    Reset Key
                  </button>
                </div>
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-400">
                    <span className="material-symbols-outlined text-[19px]">lock</span>
                  </div>
                  <input
                    id="passwordInput"
                    type={showPassword ? 'text' : 'password'}
                    required
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    disabled={isLoading}
                    autoComplete="current-password"
                    placeholder="••••••••••••"
                    className="w-full pl-10 pr-11 py-2.5 rounded-xl border border-slate-300 dark:border-slate-700 bg-slate-50/50 dark:bg-slate-900/60 text-slate-900 dark:text-white placeholder-slate-400 text-sm font-mono tracking-wider focus:ring-2 focus:ring-blue-600/30 focus:border-blue-600 dark:focus:border-blue-500 outline-none transition-all disabled:opacity-50"
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute inset-y-0 right-0 pr-3.5 flex items-center text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 transition-colors"
                    title={showPassword ? "Hide password" : "Show password"}
                  >
                    <span className="material-symbols-outlined text-[20px]">
                      {showPassword ? 'visibility_off' : 'visibility'}
                    </span>
                  </button>
                </div>
              </div>

              {/* Remember Authorization */}
              <div className="flex items-center justify-between pt-1">
                <label className="flex items-center gap-2 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={rememberMe}
                    onChange={(e) => setRememberMe(e.target.checked)}
                    className="w-4 h-4 text-blue-600 rounded border-slate-300 dark:border-slate-700 bg-slate-50 dark:bg-slate-900 focus:ring-blue-500"
                  />
                  <span className="text-xs text-slate-600 dark:text-slate-400 select-none">
                    Remember terminal authorization
                  </span>
                </label>
                <span className="text-[11px] font-mono text-slate-400">UCEK-LAN</span>
              </div>

              {/* Error Alert Banner (Resolves ISSUE-26) */}
              {errorMessage && (
                <div 
                  role="alert"
                  className="p-3 rounded-xl bg-rose-50 dark:bg-rose-950/60 border border-rose-200 dark:border-rose-900/70 text-rose-700 dark:text-rose-300 text-xs flex items-center gap-2.5 animate-fadeIn"
                >
                  <span className="material-symbols-outlined text-rose-600 dark:text-rose-400 text-base flex-shrink-0">
                    error
                  </span>
                  <span>{errorMessage}</span>
                </div>
              )}

              {/* Submit Button with Loading State (Resolves ISSUE-26) */}
              <div className="pt-2">
                <button
                  type="submit"
                  disabled={isLoading}
                  className={`w-full relative py-3 px-4 rounded-xl font-semibold text-sm shadow-md transition-all flex items-center justify-center gap-2 text-white ${
                    isLoading
                      ? 'bg-blue-500 opacity-90 cursor-wait'
                      : 'bg-blue-600 hover:bg-blue-700 active:bg-blue-800 shadow-blue-600/25 cursor-pointer'
                  }`}
                >
                  {isLoading ? (
                    <>
                      <svg className="animate-spin h-5 w-5 text-white" fill="none" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                      </svg>
                      <span>Verifying Credentials...</span>
                    </>
                  ) : (
                    <>
                      <span className="material-symbols-outlined text-[20px]">login</span>
                      <span>Authenticate & Launch Dashboard</span>
                    </>
                  )}
                </button>
              </div>
            </form>

            {/* Quick Demo Credentials Tool */}
            <div className="mt-6 pt-5 border-t border-slate-100 dark:border-slate-800/80">
              <div className="flex items-center justify-between mb-2.5">
                <span className="text-[11px] uppercase tracking-wider font-bold text-slate-400 dark:text-slate-500">
                  Quick Test Credentials
                </span>
                <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-slate-100 dark:bg-slate-800 text-slate-500 dark:text-slate-400">
                  Click to fill
                </span>
              </div>

              <div className="grid grid-cols-2 gap-2">
                <button
                  type="button"
                  onClick={() => fillDemo('admin', 'Admin@1234', 'ADMINISTRATOR')}
                  className="text-left p-2.5 rounded-xl border border-slate-200 dark:border-slate-800 hover:border-blue-400 dark:hover:border-blue-500 bg-slate-50/50 dark:bg-slate-900/50 hover:bg-blue-50/50 dark:hover:bg-blue-950/30 transition-all text-xs group"
                >
                  <div className="flex items-center justify-between font-semibold text-slate-700 dark:text-slate-200 group-hover:text-blue-600 dark:group-hover:text-blue-400">
                    <span>Administrator</span>
                    <span className="material-symbols-outlined text-[14px]">bolt</span>
                  </div>
                  <p className="font-mono text-[10px] text-slate-500 dark:text-slate-400 mt-0.5">
                    admin / Admin@1234
                  </p>
                </button>

                <button
                  type="button"
                  onClick={() => fillDemo('engineer', 'Eng@Pass2026', 'NETWORK_ENGINEER')}
                  className="text-left p-2.5 rounded-xl border border-slate-200 dark:border-slate-800 hover:border-blue-400 dark:hover:border-blue-500 bg-slate-50/50 dark:bg-slate-900/50 hover:bg-blue-50/50 dark:hover:bg-blue-950/30 transition-all text-xs group"
                >
                  <div className="flex items-center justify-between font-semibold text-slate-700 dark:text-slate-200 group-hover:text-blue-600 dark:group-hover:text-blue-400">
                    <span>Net Engineer</span>
                    <span className="material-symbols-outlined text-[14px]">bolt</span>
                  </div>
                  <p className="font-mono text-[10px] text-slate-500 dark:text-slate-400 mt-0.5">
                    engineer / Eng@Pass2026
                  </p>
                </button>
              </div>
            </div>

          </div>

          {/* Compliance & Node Metadata Footer */}
          <div className="mt-6 text-center text-xs text-slate-500 dark:text-slate-400 space-y-2">
            <div className="flex items-center justify-center gap-4 text-[11px]">
              <span className="flex items-center gap-1">
                <span className="material-symbols-outlined text-[14px] text-blue-500">router</span>
                19 Core Switches Linked
              </span>
              <span>•</span>
              <span className="flex items-center gap-1">
                <span className="material-symbols-outlined text-[14px] text-emerald-500">videocam</span>
                26 CCTV Nodes Online
              </span>
              <span>•</span>
              <span className="flex items-center gap-1">
                <span className="material-symbols-outlined text-[14px] text-amber-500">psychology</span>
                AI Prediction Engine
              </span>
            </div>
            <p className="text-[11px] text-slate-400 dark:text-slate-600">
              University College of Engineering Kakinada — JNTUK Surveillance Infrastructure &copy; 2026
            </p>
          </div>

        </div>
      </main>
    </div>
  );
};
