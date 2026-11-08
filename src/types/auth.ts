export type UserRole = 'ADMINISTRATOR' | 'NETWORK_ENGINEER' | 'OPERATOR' | 'VIEWER';

export interface User {
  username: string;
  role: UserRole;
  display_name?: string;
  full_name?: string;
}

export interface LoginResponse {
  token: string;
  role: UserRole;
  user?: User;
  error?: string;
}

export interface AuthState {
  token: string | null;
  user: User | null;
  role: UserRole;
  isAuthenticated: boolean;
  isLoading: boolean;
  sessionExpired: boolean;
}
