import React, { useState } from 'react';
import { View, Text, Input, Button, Image, Navigator } from '@tarojs/components';
import { redirectTo } from '@tarojs/taro';
import { iconUser, iconLock, iconEye, iconEyeOff, iconLoader } from '../../utils/icons';
import './index.scss';

const LoginPage: React.FC = () => {
  const [formData, setFormData] = useState({
    username: '',
    password: ''
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  
  // UI States
  const [focusedField, setFocusedField] = useState<string | null>(null);
  const [showPassword, setShowPassword] = useState(false);

  const handleInputChange = (field: string, value: string) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
    if (error) {
      setError('');
    }
  };

  const handleLogin = async () => {
    if (!formData.username || !formData.password) {
      setError('Username and password are required');
      return;
    }

    setLoading(true);
    setError('');

    try {
      // Keep existing API logic
      const response = await fetch(`${BASE_URL}/apipy/api/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded'
        },
        body: `username=${encodeURIComponent(formData.username)}&password=${encodeURIComponent(formData.password)}`
      });

      const data = await response.json();

      if (data.code === 200) {
        redirectTo({ url: '/pages/index/index' });
      } else {
        setError(data.message || 'Login failed');
      }
    } catch (err) {
      setError('Network error, please try again later');
      console.error('Login error:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <View className="login-container">
      <View className="login-form">
        <View className="header">
          <Text className="title">Account Login</Text>
          <Text className="subtitle">Enter your credentials to access your account</Text>
        </View>

        <View className="form-content">
          {/* Username Field */}
          <View className="form-item">
            <Text className="label">Username</Text>
            <View className={`input-wrapper ${focusedField === 'username' ? 'focused' : ''}`}>
              <Image src={iconUser} className="input-icon left" />
              <Input
                className="taro-input"
                value={formData.username}
                onInput={(e) => handleInputChange('username', e.detail.value)}
                onFocus={() => setFocusedField('username')}
                onBlur={() => setFocusedField(null)}
                placeholder="Enter your username"
                placeholderClass="placeholder"
              />
            </View>
          </View>

          {/* Password Field */}
          <View className="form-item">
            <Text className="label">Password</Text>
            <View className={`input-wrapper ${focusedField === 'password' ? 'focused' : ''}`}>
              <Image src={iconLock} className="input-icon left" />
              <Input
                className="taro-input"
                value={formData.password}
                password={!showPassword}
                onInput={(e) => handleInputChange('password', e.detail.value)}
                onFocus={() => setFocusedField('password')}
                onBlur={() => setFocusedField(null)}
                placeholder="Enter your password"
                placeholderClass="placeholder"
              />
              <View 
                className="input-icon right-clickable"
                onClick={() => setShowPassword(!showPassword)}
              >
                <Image src={showPassword ? iconEyeOff : iconEye} className="icon-img" />
              </View>
            </View>
          </View>

          {error && <View className="error-alert"><Text className="error-text">{error}</Text></View>}

          <Button
            className={`login-button ${loading ? 'loading' : ''}`}
            onClick={handleLogin}
            disabled={loading}
          >
            {loading && <Image src={iconLoader} className="spinner" />}
            <Text>{loading ? 'Logging in...' : 'Login'}</Text>
          </Button>
        </View>

        <View className="footer">
          <Text className="footer-text">Don't have an account? </Text>
          <Navigator url="/pages/register/index" className="link-navigator">
            <Text className="link">Register now</Text>
          </Navigator>
        </View>
      </View>
    </View>
  );
};

export default LoginPage;
