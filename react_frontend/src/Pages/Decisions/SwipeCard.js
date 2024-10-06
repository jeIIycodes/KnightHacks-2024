// src/Pages/Decisions/SwipeCard.js
import React from 'react';
import TinderCard from 'react-tinder-card';
import './Decisions.css'; // Optional, for styling

const SwipeCard = ({ data }) => {
  const onSwipe = (direction) => {
    console.log('You swiped: ' + direction);
  };

  const onCardLeftScreen = (myIdentifier) => {
    console.log(myIdentifier + ' left the screen');
  };

  return (
    <div className="swipe-container">
      {data.map((item, index) => (
        <TinderCard
          className="swipe"
          key={index}
          onSwipe={(dir) => onSwipe(dir)}
          onCardLeftScreen={() => onCardLeftScreen(item.name)}
        >
          <div
            style={{ backgroundImage: `url(${item.imageUrl})` }}
            className="card"
          >
            <h3>{item.name}</h3>
          </div>
        </TinderCard>
      ))}
    </div>
  );
};

export default SwipeCard;
