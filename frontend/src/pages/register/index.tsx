import React, { useState } from 'react';
import { View, Text, Input, Button, Navigator } from '@tarojs/components';
import { redirectTo } from '@tarojs/taro';
import { AuthLayout } from '../../components/AuthLayout';
import './index.scss';

const RegisterPage: React.FC = () => {
  const [formData, setFormData] = useState({
    username: '',
    password: '',
    confirmPassword: '',
    email: '',
    phone: '',
    nickname: ''
  });
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const updateField = (field: string, value: string) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
    if (error) {
      setError('');
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    if (!formData.username.trim()) {
      setError('Please enter your username');
      return;
    }
    if (formData.username.length < 3 || formData.username.length > 150) {
      setError('Username must be between 3 and 150 characters');
      return;
    }
    if (!formData.password.trim()) {
      setError('Please enter your password');
      return;
    }
    if (formData.password.length < 6 || formData.password.length > 128) {
      setError('Password must be between 6 and 128 characters');
      return;
    }
    if (!formData.confirmPassword.trim()) {
      setError('Please confirm your password');
      return;
    }
    if (formData.password !== formData.confirmPassword) {
      setError('Passwords do not match');
      return;
    }

    setIsLoading(true);

    try {
      const formDataToSend = new URLSearchParams();
      formDataToSend.append('username', formData.username);
      formDataToSend.append('password', formData.password);
      if (formData.email) formDataToSend.append('email', formData.email);
      if (formData.phone) formDataToSend.append('phone', formData.phone);
      if (formData.nickname) formDataToSend.append('nickname', formData.nickname);

      const response = await fetch('/apipy/auth/register', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded'
        },
        body: formDataToSend.toString()
      });

      const data = await response.json();

      if (data.code === 200) {
        // 注册成功，跳转到登录页
        redirectTo({ url: '/pages/login/index' });
      } else {
        setError(data.message || 'Registration failed');
      }
    } catch (err) {
      setError('Network error, please try again later');
      console.error('Register error:', err);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <AuthLayout>
      <View className="register-form" onSubmit={handleSubmit}>
        <View className="register-form__header">
          <Text className="register-form__title">Create Account</Text>
          <Text className="register-form__subtitle">Register a new account to get started</Text>
        </View>

        <View className="register-form__body">
          {/* Username - required */}
          <View className="register-form__input-group">
            <Text className="register-form__label">
              Username <Text className="register-form__required">*</Text>
            </Text>
            <View className="register-form__input-container">
              <Text className="register-form__input-icon">👤</Text>
              <Input
                className="register-form__input"
                placeholder="3-150 characters"
                value={formData.username}
                onChange={(e) => updateField('username', e.detail.value)}
                autoComplete="username"
                disabled={isLoading}
              />
            </View>
          </View>

          {/* Password - required */}
          <View className="register-form__input-group">
            <Text className="register-form__label">
              Password <Text className="register-form__required">*</Text>
            </Text>
            <View className="register-form__input-container">
              <Text className="register-form__input-icon">🔒</Text>
              <Input
                className="register-form__input"
                type={showPassword ? 'text' : 'password'}
                placeholder="6-128 characters"
                value={formData.password}
                onChange={(e) => updateField('password', e.detail.value)}
                autoComplete="new-password"
                disabled={isLoading}
              />
              <Button
                className="register-form__password-toggle"
                onClick={() => setShowPassword(!showPassword)}
                disabled={isLoading}
              >
                {showPassword ? '👁️‍🗨️' : '👁️'}
              </Button>
            </View>
          </View>

          {/* Confirm Password - required */}
          <View className="register-form__input-group">
            <Text className="register-form__label">
              Confirm Password <Text className="register-form__required">*</Text>
            </Text>
            <View className="register-form__input-container">
              <Text className="register-form__input-icon">🔒</Text>
              <Input
                className="register-form__input"
                type={showConfirmPassword ? 'text' : 'password'}
                placeholder="Re-enter your password"
                value={formData.confirmPassword}
                onChange={(e) => updateField('confirmPassword', e.detail.value)}
                autoComplete="new-password"
                disabled={isLoading}
              />
              <Button
                className="register-form__password-toggle"
                onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                disabled={isLoading}
              >
                {showConfirmPassword ? '👁️‍🗨️' : '👁️'}
              </Button>
            </View>
          </View>

          {/* Optional fields separator */}
          <View className="register-form__separator">
            <View className="register-form__separator-line" />
            <Text className="register-form__separator-text">Optional</Text>
            <View className="register-form__separator-line" />
          </View>

          {/* Email - optional */}
          <View className="register-form__input-group">
            <Text className="register-form__label">Email</Text>
            <View className="register-form__input-container">
              <Text className="register-form__input-icon">📧</Text>
              <Input
                className="register-form__input"
                type="email"
                placeholder="Enter your email"
                value={formData.email}
                onChange={(e) => updateField('email', e.detail.value)}
                autoComplete="email"
                disabled={isLoading}
              />
            </View>
          </View>

          {/* Phone - optional */}
          <View className="register-form__input-group">
            <Text className="register-form__label">Phone</Text>
            <View className="register-form__input-container">
              <Text className="register-form__input-icon">📱</Text>
              <Input
                className="register-form__input"
                type="tel"
                placeholder="Enter your phone number"
                value={formData.phone}
                onChange={(e) => updateField('phone', e.detail.value)}
                autoComplete="tel"
                disabled={isLoading}
              />
            </View>
          </View>

          {/* Nickname - optional */}
          <View className="register-form__input-group">
            <Text className="register-form__label">Nickname</Text>
            <View className="register-form__input-container">
              <Text className="register-form__input-icon">🙋</Text>
              <Input
                className="register-form__input"
                placeholder="Enter your nickname"
                value={formData.nickname}
                onChange={(e) => updateField('nickname', e.detail.value)}
                autoComplete="nickname"
                disabled={isLoading}
              />
            </View>
          </View>

          {error && (
            <View className="register-form__error">
              <Text className="register-form__error-text">{error}</Text>
            </View>
          )}

          <Button
            className="register-form__submit-button"
            type="submit"
            disabled={isLoading}
          >
            {isLoading ? (
              <View className="register-form__loading">
                <Text className="register-form__loading-spinner">⏳</Text>
                <Text className="register-form__loading-text">Registering...</Text>
              </View>
            ) : (
              'Register'
            )}
          </Button>
        </View>

        <View className="register-form__footer">
          <Text className="register-form__footer-text">
            Already have an account?
            <Navigator url="/pages/login/index">
              <Text className="register-form__footer-link"> Login now</Text>
            </Navigator>
          </Text>
        </View>
      </View>
    </AuthLayout>
  );
};

export default RegisterPage;
