// App.js
import React from 'react';
import './App.css'; // If you have any global styles
import CardSwiper from './card-swiper/CardSwiper'; // Import your CardSwiper component

function App() {
  return (
    <div className="App">
      <header className="App-header">
        <h1>Accelerator Project</h1>
        {/* Render your CardSwiper component */}
        <CardSwiper />
      </header>
    </div>
  );
}

export default App;

