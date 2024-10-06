import React from 'react';
import Card from 'react-bootstrap/Card';
import './Gallery.css';

function Gallery() {
  const cardsData = [
    { title: "Card 1", text: "This is Card 1's content.", footer: "2 days ago" },
    { title: "Card 2", text: "This is Card 2's content.", footer: "3 days ago" },
    { title: "Card 3", text: "This is Card 3's content.", footer: "4 days ago" },
    { title: "Card 4", text: "This is Card 4's content.", footer: "5 days ago" },
    { title: "Card 5", text: "This is Card 5's content.", footer: "6 days ago" },
    { title: "Card 6", text: "This is Card 6's content.", footer: "1 week ago" }
  ];

  return (
    <div className="gallery-container">
      <div className="gallery-title">
        <h1>Your matches.</h1>
      </div>
      <div className="gallery-description">
        <p>Here is a grid of swiped-right candidates.</p>
      </div>
      <div className="gallery">
        {cardsData.map((card, index) => (
          <Card key={index}>
            <Card.Header as="h3">{`Card ${index + 1} header`}</Card.Header>
            <Card.Body>
              <Card.Title>{`Special title treatment for ${card.title}`}</Card.Title>
              <Card.Subtitle className="mb-2 text-muted">Support card subtitle</Card.Subtitle>
            </Card.Body>
            <svg
              xmlns="http://www.w3.org/2000/svg"
              className="d-block user-select-none"
              width="100%"
              height="200"
              aria-label="Placeholder: Image cap"
              focusable="false"
              role="img"
              preserveAspectRatio="xMidYMid slice"
              viewBox="0 0 318 180"
              style={{ fontSize: '1.125rem', textAnchor: 'middle' }}
            >
              <rect width="100%" height="100%" fill="#868e96"></rect>
              <text x="50%" y="50%" fill="#dee2e6" dy=".3em">Image cap</text>
            </svg>
            <Card.Body>
              <Card.Text>{card.text}</Card.Text>
            </Card.Body>
            <ul className="list-group list-group-flush">
              <li className="list-group-item">Cras justo odio</li>
              <li className="list-group-item">Dapibus ac facilisis in</li>
              <li className="list-group-item">Vestibulum at eros</li>
            </ul>
            <Card.Body>
              <Card.Link href="#">Card link</Card.Link>
              <Card.Link href="#">Another link</Card.Link>
            </Card.Body>
            <Card.Footer className="text-muted">{card.footer}</Card.Footer>
          </Card>
        ))}
      </div>
    </div>
  );
}

export default Gallery;
