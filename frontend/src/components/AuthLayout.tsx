import React from 'react';
import { View, Text } from '@tarojs/components';
import './AuthLayout.scss';

interface AuthLayoutProps {
  children: React.ReactNode;
}

export const AuthLayout: React.FC<AuthLayoutProps> = ({ children }) => {
  return (
    <View className="auth-layout">
      {/* Left decorative panel - hidden on mobile */}
      <View className="auth-layout__left-panel">
        <View className="auth-layout__left-content">
          <View className="auth-layout__logo-container">
            <View className="auth-layout__logo">
              <Text className="auth-layout__logo-text">🛡️</Text>
            </View>
          </View>
          <Text className="auth-layout__title">IP Access Tracker</Text>
          <Text className="auth-layout__description">
            Secure and efficient IP access record management system, providing comprehensive access logging and analysis capabilities.
          </Text>
        </View>
        <Text className="auth-layout__powered-by">Powered by Django & React</Text>
      </View>

      {/* Right form panel */}
      <View className="auth-layout__right-panel">
        {/* Mobile logo */}
        <View className="auth-layout__mobile-logo">
          <View className="auth-layout__mobile-logo-icon">
            <Text className="auth-layout__mobile-logo-text">🛡️</Text>
          </View>
          <Text className="auth-layout__mobile-logo-title">IP Access Tracker</Text>
        </View>

        <View className="auth-layout__form-container">
          {children}
        </View>
      </View>
    </View>
  );
};
