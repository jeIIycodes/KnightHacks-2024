import React from 'react';
import './App.css'; // Keeping the CSS import

function App() {
  return (
    <div className="App">
      {/* Left Corner Home Button */}
      <button className="home-button" onClick={() => alert('Navigating to Home')}>
        Home
      </button>

      <div style={{ textAlign: 'center' }}>
        <h1 style={{ fontSize: '48px' }}>
          <span style={{ color: 'green' }}>MATCH</span>
          <span style={{ color: 'black' }}>CELERATOR</span>
        </h1>
        <h6 style={{ fontSize: '24px', color: 'white' }}>Find Your Perfect Accelerator! </h6>
        <button
          style={{
            padding: '15px 30px',
            fontSize: '24px',
            fontWeight: 'bold',
            backgroundColor: '#FFFFF',
            color: 'black',
            border: 'none',
            borderRadius: '10px',
            cursor: 'pointer'
          }}
          onClick={() => alert('Starting Quiz...')}
        >
          Start Quiz
        </button>

        {/* Circle Button with Image and Username */}
        <div className="profile-section">
          <div className="profile-circle">
            <img
              src="https://via.placeholder.com/150" // Placeholder image
              alt="Profile"
              className="profile-image"
            />
          </div>
          <p className="profile-name">Josh</p>
        </div>
      </div>
    </div>
  );
}

export default App;
