// src/pages/Loading/Loading.js
import React from 'react';
import Button from 'react-bootstrap/Button';

function Loading({ onNext }) {
  return (
    <div>
      <h1>Loading...</h1>
      <p>Please wait while we process your input.</p>
    </div>
  );
}

export default Loading;
