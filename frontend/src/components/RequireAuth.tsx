import React from 'react';
import { Navigate } from 'react-router-dom';
import { isAuthenticated } from '../utils/api';

interface RequireAuthProps {
  children: React.ReactNode;
}

export const RequireAuth: React.FC<RequireAuthProps> = ({ children }) => {
  if (!isAuthenticated()) {
    return <Navigate to="/auth" replace />;
  }
  return <>{children}</>;
};
