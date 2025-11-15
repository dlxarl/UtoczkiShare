import { useState } from 'react';
import Login from './Login';
import Register from './Register';
import UploadPhoto from './UploadPhoto';
import PhotosList from './PhotosList';
import './App.css';

function App() {
  const [token, setToken] = useState<string | null>(() => {
    return localStorage.getItem('authToken');
  });
  const [email, setEmail] = useState<string | null>(() => {
    return localStorage.getItem('userEmail');
  });
  
  const [authView, setAuthView] = useState<'login' | 'register'>('login');
  const [refreshPhotos, setRefreshPhotos] = useState(0);

  const handleLoginSuccess = (newToken: string, userEmail?: string) => {
    localStorage.setItem('authToken', newToken);
    if (userEmail) {
      localStorage.setItem('userEmail', userEmail);
      setEmail(userEmail);
    }
    setToken(newToken);
  };

  const handleLogout = () => {
    localStorage.removeItem('authToken');
    localStorage.removeItem('userEmail');
    setToken(null);
    setEmail(null);
    setAuthView('login');
  };
  
  const handleRegisterSuccess = () => {
    setAuthView('login');
  };

  const handleUploadSuccess = () => {
    setRefreshPhotos(prev => prev + 1);
  };

  if (!token) {
    if (authView === 'login') {
      return (
        <Login 
          onLogin={handleLoginSuccess} 
          onSwitchToRegister={() => setAuthView('register')} 
        />
      );
    }
    return (
      <Register 
        onSwitchToLogin={() => setAuthView('login')}
        onRegisterSuccess={handleRegisterSuccess}
      />
    );
  }

  return (
    <div className="app-container">
      <header className="app-header">
        <h1><img src="src/assets/logo.png" id="logo-img"></img><b>Utoczki</b>Share</h1>
        <div className="header-right">
          {email && <span className="account-email">{email}</span>}
          <button onClick={handleLogout} className="logout-button">
            Logout
          </button>
        </div>
      </header>
      
      <main className="app-content">
        <div className="content-sidebar">
          <UploadPhoto token={token} onUploadSuccess={handleUploadSuccess} />
        </div>
        <div className="content-main">
          <PhotosList token={token} key={refreshPhotos} />
        </div>
      </main>

      <footer className="app-footer">
        Made by <b>Utoczki Team</b>
        <img src="src/assets/icons/heart.svg" alt="<3>" className="footer-icon"></img>
      </footer>
    </div>
  );
}

export default App;