import { useState } from 'react';
import API from './api';
import './Auth.css';
import alertIcon from './assets/icons/alert.svg';
import eyeIcon from './assets/icons/eye.svg';
import eyeOffIcon from './assets/icons/eye-off.svg';

interface RegisterProps {
  onSwitchToLogin: () => void;
  onRegisterSuccess: () => void;
}

export default function Register({ onSwitchToLogin, onRegisterSuccess }: RegisterProps) {
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [passwordConfirm, setPasswordConfirm] = useState('');
  const [error, setError] = useState<string | null>(null);

  const [showPassword, setShowPassword] = useState(false);
  const [showPasswordConfirm, setShowPasswordConfirm] = useState(false);

  const [strength, setStrength] = useState(0);

  const getPasswordStrength = (password: string) => {
    let score = 0;
    
    if (password.length === 0) {
      return { score: 0 };
    }

    if (password.length >= 8) score++;
    if (/[A-Z]/.test(password)) score++;
    if (/[a-z]/.test(password)) score++;
    if (/[0-9]/.test(password)) score++;
    if (/[^A-Za-z0-9]/.test(password)) score++;

    let finalScore = 0;
    if (password.length > 0 && score <= 2) {
      finalScore = 1;
    } else if (score === 3) {
      finalScore = 2;
    } else if (score === 4) {
      finalScore = 3;
    } else if (score >= 5) {
      finalScore = 4;
    }

    return { score: finalScore };
  };

  const handlePasswordChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newPassword = e.target.value;
    setPassword(newPassword);
    const { score } = getPasswordStrength(newPassword);
    setStrength(score);
  };

  const handleRegister = async () => {
    setError(null); 
    if (!username || !password || !passwordConfirm || !email) {
      setError('Please fill in all fields');
      return;
    }

    if (password !== passwordConfirm) {
      setError('Passwords do not match');
      return;
    }

    try {
      await API.post('/auth/register/', { username, email, password, password_confirm: passwordConfirm });
      onRegisterSuccess();
    } catch (err: any) {
      const errData = err.response?.data;
      if (typeof errData === 'object') {
        const messages = Object.values(errData).flat().join(', ');
        setError(messages || 'Registration error. Please try again.');
      } else {
        setError('Registration error. Please try again.');
      }
      console.error(err);
    }
  };

  return (
    <div className="auth-container">
      <div className="auth-form">
        <h2>Register</h2>
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
        <input
          placeholder="Email"
          type="email"
          value={email}
          onChange={e => setEmail(e.target.value)}
        />
        
        <div className="password-wrapper">
          <input
            placeholder="Password"
            type={showPassword ? 'text' : 'password'}
            value={password}
            onChange={handlePasswordChange}
          />
          <img
            src={showPassword ? eyeOffIcon : eyeIcon}
            alt={showPassword ? "Hide password" : "Show password"}
            className="password-toggle-icon"
            onClick={() => setShowPassword(!showPassword)}
          />
        </div>

        <div className="password-field-group">
          <div className="password-wrapper">
            <input
              placeholder="Confirm Password"
              type={showPasswordConfirm ? 'text' : 'password'}
              value={passwordConfirm}
              onChange={e => setPasswordConfirm(e.target.value)}
            />
            <img
              src={showPasswordConfirm ? eyeOffIcon : eyeIcon}
              alt={showPasswordConfirm ? "Hide password" : "Show password"}
              className="password-toggle-icon"
              onClick={() => setShowPasswordConfirm(!showPasswordConfirm)}
            />
          </div>

          <div className="password-strength-meter"
               style={{ visibility: password.length > 0 ? 'visible' : 'hidden', height: password.length > 0 ? '6px' : '0' }}
          >
            <div className="strength-bar-container">
              <div className={`strength-bar-progress strength-level-${strength}`}></div>
            </div>
          </div>
        </div>

        <button onClick={handleRegister}>Register</button>
        <p className="auth-switch">
          Already have an account?{' '}
          <span onClick={onSwitchToLogin}>Login</span>
        </p>
      </div>
    </div>
  );
}