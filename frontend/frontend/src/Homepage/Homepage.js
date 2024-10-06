// src/pages/Homepage/Homepage.js
import React from 'react';
import Button from 'react-bootstrap/Button';

function Homepage({ onNext }) {
  return (
    <div>
      <h1>Welcome to the Homepage</h1>
      <Button onClick={onNext}>Start Quiz</Button>
    </div>
  );
}

export default Homepage;
