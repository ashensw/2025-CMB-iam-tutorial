import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAuthContext } from "@asgardeo/auth-react";
import { LoadingSpinner } from './LoadingSpinner';

interface ProtectedRouteProps {
  children: React.ReactNode;
}

export const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ children }) => {
  const { state } = useAuthContext();
  const location = useLocation();

  if (state?.isLoading) {
    return <LoadingSpinner />;
  }

  if (!state?.isAuthenticated) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  return <>{children}</>;
};
