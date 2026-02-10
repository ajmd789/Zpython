import React, { useState } from 'react';
import { View, Text, Input, Button, Navigator } from '@tarojs/components';
import { redirectTo } from '@tarojs/taro';
import { AuthLayout } from '../../components/AuthLayout';
import './index.scss';

const LoginPage: React.FC = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    if (!username.trim()) {
      setError('Please enter your username');
      return;
    }
    if (!password.trim()) {
      setError('Please enter your password');
      return;
    }

    setIsLoading(true);

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
        // 登录成功，跳转到首页
        redirectTo({ url: '/' });
      } else {
        setError(data.message || '登录失败');
      }
    } catch (err) {
      setError('网络错误，请稍后重试');
      console.error('Login error:', err);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <AuthLayout>
      <View className="login-form" onSubmit={handleSubmit}>
        <View className="login-form__header">
          <Text className="login-form__title">Account Login</Text>
          <Text className="login-form__subtitle">Enter your credentials to access your account</Text>
        </View>

        <View className="login-form__body">
          <View className="login-form__input-group">
            <Text className="login-form__label">Username</Text>
            <View className="login-form__input-container">
              <Text className="login-form__input-icon">👤</Text>
              <Input
                className="login-form__input"
                placeholder="Enter your username"
                value={username}
                onChange={(e) => setUsername(e.detail.value)}
                autoComplete="username"
                disabled={isLoading}
              />
            </View>
          </View>

          <View className="login-form__input-group">
            <Text className="login-form__label">Password</Text>
            <View className="login-form__input-container">
              <Text className="login-form__input-icon">🔒</Text>
              <Input
                className="login-form__input"
                type={showPassword ? 'text' : 'password'}
                placeholder="Enter your password"
                value={password}
                onChange={(e) => setPassword(e.detail.value)}
                autoComplete="current-password"
                disabled={isLoading}
              />
              <Button
                className="login-form__password-toggle"
                onClick={() => setShowPassword(!showPassword)}
                disabled={isLoading}
              >
                {showPassword ? '👁️‍🗨️' : '👁️'}
              </Button>
            </View>
          </View>

          {error && (
            <View className="login-form__error">
              <Text className="login-form__error-text">{error}</Text>
            </View>
          )}

          <Button
            className="login-form__submit-button"
            type="submit"
            disabled={isLoading}
          >
            {isLoading ? (
              <View className="login-form__loading">
                <Text className="login-form__loading-spinner">⏳</Text>
                <Text className="login-form__loading-text">Logging in...</Text>
              </View>
            ) : (
              'Login'
            )}
          </Button>
        </View>

        <View className="login-form__footer">
          <Text className="login-form__footer-text">
            Don't have an account?
            <Navigator url="/pages/register/index">
              <Text className="login-form__footer-link"> Register now</Text>
            </Navigator>
          </Text>
        </View>
      </View>
    </AuthLayout>
  );
};

export default LoginPage;
