// src/pages/Decisions/Decisions.js
import React from 'react';
import Button from 'react-bootstrap/Button';

function Decisions({ onNext }) {
  return (
    <div>
      <h1>Swipe your Decisions</h1>
      <p>Swipe left or right to choose your compatible matches.</p>
      <Button onClick={onNext}>Next</Button>
    </div>
  );
}

export default Decisions;
