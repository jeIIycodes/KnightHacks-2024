// src/pages/Quiz/Quiz.js
import React from 'react';
import Button from 'react-bootstrap/Button';

function Quiz({ onNext }) {
  return (
    <div>
      <h1>Quiz Page</h1>
      <p>This is where the questionnaire will go.</p>
      <Button onClick={onNext}>Next</Button>
    </div>
  );
}

export default Quiz;
