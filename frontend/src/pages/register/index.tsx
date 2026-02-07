import React, { useState } from 'react';
import { View, Text, Input, Button, Navigator } from '@tarojs/components';
import { redirectTo } from '@tarojs/taro';
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

  const handleRegister = async () => {
    // 表单验证
    if (!formData.username || !formData.password || !formData.confirmPassword) {
      setError('账号、密码和确认密码不能为空');
      return;
    }

    if (formData.password !== formData.confirmPassword) {
      setError('两次输入的密码不一致');
      return;
    }

    if (formData.username.length < 3 || formData.username.length > 150) {
      setError('账号长度应在3-150字符之间');
      return;
    }

    if (formData.password.length < 6 || formData.password.length > 128) {
      setError('密码长度应在6-128字符之间');
      return;
    }

    setLoading(true);
    setError('');

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
        setError(data.message || '注册失败');
      }
    } catch (err) {
      setError('网络错误，请稍后重试');
      console.error('Register error:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <View className="register-container">
      <Text className="logo">账号注册</Text>

      <View className="register-form">
        <View className="form-item">
          <Text className="label">账号</Text>
          <Input
            className="input"
            value={formData.username}
            onChange={(e) => handleInputChange('username', e.detail.value)}
            placeholder="请输入账号（3-150字符）"
            placeholderStyle={{ color: '#999' }}
          />
        </View>

        <View className="form-item">
          <Text className="label">密码</Text>
          <Input
            className="input"
            value={formData.password}
            onChange={(e) => handleInputChange('password', e.detail.value)}
            placeholder="请输入密码（6-128字符）"
            placeholderStyle={{ color: '#999' }}
            password
          />
        </View>

        <View className="form-item">
          <Text className="label">确认密码</Text>
          <Input
            className="input"
            value={formData.confirmPassword}
            onChange={(e) => handleInputChange('confirmPassword', e.detail.value)}
            placeholder="请再次输入密码"
            placeholderStyle={{ color: '#999' }}
            password
          />
        </View>

        <View className="form-item">
          <Text className="label">邮箱（可选）</Text>
          <Input
            className="input"
            value={formData.email}
            onChange={(e) => handleInputChange('email', e.detail.value)}
            placeholder="请输入邮箱"
            placeholderStyle={{ color: '#999' }}
            type="email"
          />
        </View>

        <View className="form-item">
          <Text className="label">手机号（可选）</Text>
          <Input
            className="input"
            value={formData.phone}
            onChange={(e) => handleInputChange('phone', e.detail.value)}
            placeholder="请输入手机号"
            placeholderStyle={{ color: '#999' }}
            type="number"
          />
        </View>

        <View className="form-item">
          <Text className="label">昵称（可选）</Text>
          <Input
            className="input"
            value={formData.nickname}
            onChange={(e) => handleInputChange('nickname', e.detail.value)}
            placeholder="请输入昵称"
            placeholderStyle={{ color: '#999' }}
          />
        </View>

        {error && <Text className="error-message">{error}</Text>}

        <Button
          className="register-button"
          onClick={handleRegister}
          disabled={loading}
        >
          {loading ? '注册中...' : '注册'}
        </Button>

        <View className="login-link">
          <Text>已有账号？</Text>
          <Navigator url="/pages/login/index">
            <Text style={{ color: '#1890ff' }}>立即登录</Text>
          </Navigator>
        </View>
      </View>
    </View>
  );
};

export default RegisterPage;
