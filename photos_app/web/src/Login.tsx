import { useState } from 'react';
import API from './api';
import './Auth.css';
import alertIcon from './assets/icons/alert.svg';

import eyeIcon from './assets/icons/eye.svg';
import eyeOffIcon from './assets/icons/eye-off.svg';

interface LoginProps {
  onLogin: (token: string, email?: string) => void;
  onSwitchToRegister: () => void; 
}

export default function Login({ onLogin, onSwitchToRegister }: LoginProps) {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState<string | null>(null);

  const [showPassword, setShowPassword] = useState(false);

  const handleLogin = async () => {
    setError(null);
    try {
      const res = await API.post('/auth/login/', { username, password });
      const userEmail = res.data.email || username;
      onLogin(res.data.access, userEmail);
    } catch {
      setError('Invalid username or password');
    }
  };

  return (
    <div className="auth-container">
      <div className="auth-form">
        <h2>Login</h2>
        {error && (
          <div className="auth-error">
            <img src={alertIcon} alt="Error" className="error-icon" />
            <span>{error}</span>
          </div>
        )}
        <input
          placeholder="Username"
          value={username}
          onChange={e => setUsername(e.target.value)}
        />

        <div className="password-wrapper">
          <input
            placeholder="Password"
            type={showPassword ? 'text' : 'password'}
            value={password}
            onChange={e => setPassword(e.target.value)}
          />
          <img
            src={showPassword ? eyeOffIcon : eyeIcon}
            alt={showPassword ? "Hide password" : "Show password"}
            className="password-toggle-icon"
            onClick={() => setShowPassword(!showPassword)}
          />
        </div>
        
        <button onClick={handleLogin}>Login</button>
        <p className="auth-switch">
          Don't have an account?{' '}
          <span onClick={onSwitchToRegister}>Register</span>
        </p>
      </div>
    </div>
  );
}