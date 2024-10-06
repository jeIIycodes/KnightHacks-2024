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
        <h6 style={{ fontSize: '24px', color: 'white' }}>Find Your Match</h6>
        <button
          style={{
            padding: '15px 30px',
            fontWeight: 'bold',
            fontSize: '24px',
            backgroundColor: '#FFFFFF',
            color: 'black',
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