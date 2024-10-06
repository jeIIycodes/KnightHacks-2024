//Loading.js
import React from 'react';
import './App.css'; // Could give issues if the name is not changed to "./loading.css"

function App() {
  return (
    <div className="loading-screen">
      <div className="loading-text">
        Here Are Your Potential Candidates
      </div>
      <div className="swipe-instructions">
        <p>To accept, click right or the <span style={{ color: 'red' }}>♥</span></p>
        <p>To reject, click left or the <span style={{ color: 'red' }}>✘</span></p>      </div>
    </div>
  );
}

export default App;
