// src/Pages/Decisions/Decisions.js
import React from 'react';
import SwipeCard from './SwipeCard'; // Import the SwipeCard component
import './Decisions.css';

const data = [
  {
    name: 'Product 1',
    imageUrl: 'https://source.unsplash.com/random/600x400?product',
  },
  {
    name: 'Product 2',
    imageUrl: 'https://source.unsplash.com/random/600x400?tech',
  },
  {
    name: 'Product 3',
    imageUrl: 'https://source.unsplash.com/random/600x400?software',
  },
  // Add more items as needed
];

const Decisions = () => {
  return (
    <div className="decisions">
      <h1>Swipe on Products</h1>
      <SwipeCard data={data} />
    </div>
  );
};

export default Decisions;
