import React, { createContext, useState, useEffect, useContext, ReactNode } from 'react';

interface User {
  user_id: number;
  username: string;
  email: string;
  phone: string;
  nickname: string;
}

interface AuthContextType {
  isAuthenticated: boolean;
  user: User | null;
  loading: boolean;
  login: (username: string, password: string) => Promise<boolean>;
  logout: () => Promise<boolean>;
  register: (userData: {
    username: string;
    password: string;
    email?: string;
    phone?: string;
    nickname?: string;
  }) => Promise<boolean>;
  updateUserInfo: (userData: {
    email?: string;
    phone?: string;
    nickname?: string;
  }) => Promise<boolean>;
  getUserInfo: () => Promise<boolean>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const checkAuth = async () => {
      try {
        await getUserInfo();
      } catch (error) {
        console.error('Check auth error:', error);
      } finally {
        setLoading(false);
      }
    };

    checkAuth();
  }, []);

  const getUserInfo = async (): Promise<boolean> => {
    try {
      const response = await fetch('/apipy/auth/userinfo');

      // 检查响应状态
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      // 检查响应类型
      const contentType = response.headers.get('content-type');
      if (!contentType || !contentType.includes('application/json')) {
        throw new Error('Expected JSON response');
      }

      const data = await response.json();

      if (data.code === 200) {
        setUser(data.data);
        setIsAuthenticated(true);
        return true;
      } else {
        setUser(null);
        setIsAuthenticated(false);
        return false;
      }
    } catch (error) {
      console.error('Get user info error:', error);
      setUser(null);
      setIsAuthenticated(false);
      return false;
    }
  };

  const login = async (username: string, password: string): Promise<boolean> => {
    try {
      const response = await fetch('/apipy/auth/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded'
        },
        body: `username=${encodeURIComponent(username)}&password=${encodeURIComponent(password)}`
      });

      const data = await response.json();

      if (data.code === 200) {
        await getUserInfo();
        return true;
      } else {
        return false;
      }
    } catch (error) {
      console.error('Login error:', error);
      return false;
    }
  };

  const logout = async (): Promise<boolean> => {
    try {
      const response = await fetch('/apipy/auth/logout', {
        method: 'POST'
      });

      const data = await response.json();

      if (data.code === 200) {
        setUser(null);
        setIsAuthenticated(false);
        return true;
      } else {
        return false;
      }
    } catch (error) {
      console.error('Logout error:', error);
      setUser(null);
      setIsAuthenticated(false);
      return true;
    }
  };

  const register = async (userData: {
    username: string;
    password: string;
    email?: string;
    phone?: string;
    nickname?: string;
  }): Promise<boolean> => {
    try {
      const formData = new URLSearchParams();
      formData.append('username', userData.username);
      formData.append('password', userData.password);
      if (userData.email) formData.append('email', userData.email);
      if (userData.phone) formData.append('phone', userData.phone);
      if (userData.nickname) formData.append('nickname', userData.nickname);

      const response = await fetch('/apipy/auth/register', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded'
        },
        body: formData.toString()
      });

      const data = await response.json();

      if (data.code === 200) {
        return true;
      } else {
        return false;
      }
    } catch (error) {
      console.error('Register error:', error);
      return false;
    }
  };

  const updateUserInfo = async (userData: {
    email?: string;
    phone?: string;
    nickname?: string;
  }): Promise<boolean> => {
    try {
      const formData = new URLSearchParams();
      if (userData.email !== undefined) formData.append('email', userData.email);
      if (userData.phone !== undefined) formData.append('phone', userData.phone);
      if (userData.nickname !== undefined) formData.append('nickname', userData.nickname);

      const response = await fetch('/apipy/auth/update', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded'
        },
        body: formData.toString()
      });

      const data = await response.json();

      if (data.code === 200) {
        await getUserInfo();
        return true;
      } else {
        return false;
      }
    } catch (error) {
      console.error('Update user info error:', error);
      return false;
    }
  };

  const value: AuthContextType = {
    isAuthenticated,
    user,
    loading,
    login,
    logout,
    register,
    updateUserInfo,
    getUserInfo
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
