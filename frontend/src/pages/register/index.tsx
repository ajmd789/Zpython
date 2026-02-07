import React, { useState } from 'react';
import { View, Text, Input, Button, Image, Navigator } from '@tarojs/components';
import { redirectTo } from '@tarojs/taro';
import { iconUser, iconLock, iconEye, iconEyeOff, iconLoader } from '../../utils/icons';
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

  // UI States
  const [focusedField, setFocusedField] = useState<string | null>(null);
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);

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
      setError('Username, Password and Confirm Password are required');
      return;
    }

    if (formData.password !== formData.confirmPassword) {
      setError('Passwords do not match');
      return;
    }

    if (formData.username.length < 3 || formData.username.length > 150) {
      setError('Username must be between 3 and 150 characters');
      return;
    }

    if (formData.password.length < 6 || formData.password.length > 128) {
      setError('Password must be between 6 and 128 characters');
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

      const response = await fetch(`${BASE_URL}/apipy/api/auth/register`, {
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
      setLoading(false);
    }
  };

  const renderInput = (
    field: string,
    label: string,
    icon: string,
    placeholder: string,
    isPassword = false,
    showPassState = false,
    setShowPassState?: (val: boolean) => void,
    optional = false
  ) => (
    <View className="form-item">
      <Text className="label">{label} {optional && <Text className="optional">(Optional)</Text>}</Text>
      <View className={`input-wrapper ${focusedField === field ? 'focused' : ''}`}>
        <Image src={icon} className="input-icon left" />
        <Input
          className="taro-input"
          value={formData[field as keyof typeof formData]}
          password={isPassword && !showPassState}
          onInput={(e) => handleInputChange(field, e.detail.value)}
          onFocus={() => setFocusedField(field)}
          onBlur={() => setFocusedField(null)}
          placeholder={placeholder}
          placeholderClass="placeholder"
        />
        {isPassword && setShowPassState && (
          <View 
            className="input-icon right-clickable"
            onClick={() => setShowPassState(!showPassState)}
          >
            <Image src={showPassState ? iconEyeOff : iconEye} className="icon-img" />
          </View>
        )}
      </View>
    </View>
  );

  return (
    <View className="register-container">
      <View className="register-form">
        <View className="header">
          <Text className="title">Create Account</Text>
          <Text className="subtitle">Enter your information to create an account</Text>
        </View>

        <View className="form-content">
          {renderInput('username', 'Username', iconUser, 'Enter your username')}
          {renderInput('password', 'Password', iconLock, 'Enter your password', true, showPassword, setShowPassword)}
          {renderInput('confirmPassword', 'Confirm Password', iconLock, 'Confirm your password', true, showConfirmPassword, setShowConfirmPassword)}
          
          {/* Optional fields can use User icon or add more specific icons later */}
          {renderInput('email', 'Email', iconUser, 'Enter your email', false, false, undefined, true)}
          {renderInput('phone', 'Phone', iconUser, 'Enter your phone', false, false, undefined, true)}
          {renderInput('nickname', 'Nickname', iconUser, 'Enter your nickname', false, false, undefined, true)}

          {error && <View className="error-alert"><Text className="error-text">{error}</Text></View>}

          <Button
            className={`register-button ${loading ? 'loading' : ''}`}
            onClick={handleRegister}
            disabled={loading}
          >
            {loading && <Image src={iconLoader} className="spinner" />}
            <Text>{loading ? 'Registering...' : 'Register'}</Text>
          </Button>
        </View>

        <View className="footer">
          <Text className="footer-text">Already have an account? </Text>
          <Navigator url="/pages/login/index" className="link-navigator">
            <Text className="link">Login now</Text>
          </Navigator>
        </View>
      </View>
    </View>
  );
};

export default RegisterPage;
