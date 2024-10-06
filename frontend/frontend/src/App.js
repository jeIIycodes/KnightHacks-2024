import React, { useState } from 'react';
import Homepage from './Homepage/Homepage';
import Quiz from './Quiz/Quiz';
import Loading from './Loading/Loading';
import Decisions from './Decision/Decision';
import Gallery from './Gallery/Gallery';
import './App.css';
import 'bootstrap/dist/css/bootstrap.min.css';

function App() {
  const [currentPage, setCurrentPage] = useState(0);

  const handleNext = () => {
    setCurrentPage(prevPage => prevPage + 1);
  };

  const handleBack = () => {
    setCurrentPage(prevPage => prevPage - 1);
  };

  const pages = [
    <Homepage onNext={handleNext} />,
    <Quiz onNext={handleNext} />,
    <Loading onNext={handleNext} />,
    <Decisions onNext={handleNext} />,
    <Gallery />
  ];

  return (
    <div className="App">
      {pages[currentPage]}

      {/* Back and Next Buttons */}
      <div className="navigation-buttons">
        {currentPage > 0 && (
          <button className="back-button" onClick={handleBack}>
            Back
          </button>
        )}

        {currentPage < pages.length - 1 && (
          <button className="next-button" onClick={handleNext}>
            Next
          </button>
        )}
      </div>
    </div>
  );
}

export default App;
