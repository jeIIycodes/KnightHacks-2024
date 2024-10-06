import React from 'react';
import './App.css'; // Keeping the CSS import

function App() {
  return (
    <div className="App">
      <div style={{ textAlign: 'center' }}>
        <h1 style={{ fontSize: '48px' }}>
          <span style={{ color: 'green' }}>MATCH</span>
          <span style={{ color: 'black' }}>CELERATOR</span>
        </h1>
        <p style={{ fontSize: '24px', color: 'white' }}>Find Your Match</p>
        <button
          style={{
            padding: '15px 30px',
            fontSize: '24px',
            backgroundColor: '#90A4AE',
            color: 'white',
            border: 'none',
            borderRadius: '10px',
            cursor: 'pointer'
          }}
          onClick={() => alert('Starting Quiz...')}
        >
          Start Quiz
        </button>
      </div>
    </div>
  );
}

export default App;
