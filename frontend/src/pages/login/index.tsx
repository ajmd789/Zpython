import React, { useState } from 'react';
import { View, Text, Input, Button, Textarea, Image, Navigator } from '@tarojs/components';
import { redirectTo } from '@tarojs/taro';
import './index.scss';

const LoginPage: React.FC = () => {
  const [formData, setFormData] = useState({
    username: '',
    password: ''
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

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
    // 表单验证
    if (!formData.username || !formData.password) {
      setError('账号和密码不能为空');
      return;
    }

    setLoading(true);
    setError('');

    try {
      const response = await fetch('/apipy/auth/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded'
        },
        body: `username=${encodeURIComponent(formData.username)}&password=${encodeURIComponent(formData.password)}`
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
      setLoading(false);
    }
  };

  return (
    <View className="login-container">
      <Text className="logo">账号登录</Text>

      <View className="login-form">
        <View className="form-item">
          <Text className="label">账号</Text>
          <Input
            className="input"
            value={formData.username}
            onChange={(e) => handleInputChange('username', e.detail.value)}
            placeholder="请输入账号"
            placeholderStyle={{ color: '#999' }}
          />
        </View>

        <View className="form-item">
          <Text className="label">密码</Text>
          <Input
            className="input"
            value={formData.password}
            onChange={(e) => handleInputChange('password', e.detail.value)}
            placeholder="请输入密码"
            placeholderStyle={{ color: '#999' }}
            password
          />
        </View>

        {error && <Text className="error-message">{error}</Text>}

        <Button
          className="login-button"
          onClick={handleLogin}
          disabled={loading}
        >
          {loading ? '登录中...' : '登录'}
        </Button>

        <View className="register-link">
          <Text>还没有账号？</Text>
          <Navigator url="/pages/register/index">
            <Text style={{ color: '#1890ff' }}>立即注册</Text>
          </Navigator>
        </View>
      </View>
    </View>
  );
};

export default LoginPage;
