import React from 'react';
import './App.css';
import { KindeProvider, useKindeAuth } from '@kinde-oss/kinde-auth-react'; // Import Kinde

function AuthenticatedApp() {
  const { isAuthenticated, login, logout, user } = useKindeAuth();

  return (
    <div className="App">
      {/* Home Button in the top-left corner */}
      <button className="home-button" onClick={() => alert('Navigating to Home')}>
        Home
      </button>

      {/* Profile Section */}
      {isAuthenticated ? (
        <div className="profile-section">
          <div className="profile-circle">
            <img
              src={user?.picture || 'https://via.placeholder.com/150'}
              alt="Profile"
              className="profile-image"
            />
          </div>
          <p className="profile-name">{user?.given_name || 'User'}</p>
          <button className="logout-button" onClick={logout}>
            Logout
          </button>
        </div>
      ) : (
        <button className="auth-button" onClick={login}>Login</button>
      )}

      {/* Center Content */}
      <div className="center-content">
        <h1 className="heading">
          <span style={{ color: 'green' }}>MATCH</span>
          <span style={{ color: 'black' }}>CELERATOR</span>
        </h1>
        <h6 className="sub-heading">Find Your Perfect Accelerator!</h6>
        <button
          className="quiz-button"
          onClick={() => alert('Starting Quiz...')}
        >
          Start Quiz
        </button>
      </div>
    </div>
  );
}

function App() {
  return (
    <KindeProvider
      domain="https://accelermatch.kinde.com"  // Replace with your actual Kinde domain
      clientId="5a2d3db40c8b48c49e9dd982838df08d"    // Replace with your actual client ID
      redirectUri={window.location.origin}
    >
      <AuthenticatedApp />
    </KindeProvider>
  );
}

export default App;
