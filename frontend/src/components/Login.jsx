import React, { useState } from 'react';

function Login({ onLogin }) {
  const [credentials, setCredentials] = useState({ email: '', password: '' });

  const handleCredentialChange = (e) => {
    const { name, value } = e.target;
    setCredentials(prev => ({ ...prev, [name]: value }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    onLogin();
  };

  return (
    <div className="login-card">
      <h2>Login</h2>
      <form className="login-form" onSubmit={handleSubmit}>
        <div className="input-group">
          <span className="input-icon">📧</span>
          <input 
            type="text" 
            name="email"
            placeholder="Username / Email" 
            value={credentials.email}
            onChange={handleCredentialChange}
            required
          />
        </div>
        <div className="input-group">
          <span className="input-icon">🔒</span>
          <input 
            type="password" 
            name="password"
            placeholder="Password" 
            value={credentials.password}
            onChange={handleCredentialChange}
            required
          />
        </div>
        <div className="forgot-password">
          <a href="#">Forgot Password?</a>
        </div>
        <button type="submit" className="login-btn">Login</button>
        <p className="signup-text">
          Don't have an account? <a href="#" className="signup-link">Sign Up</a>
        </p>
      </form>
    </div>
  );
}

export default Login;
