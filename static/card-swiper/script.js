// static/card-swiper/script.js

// DOM elements
const swiper = document.querySelector('#swiper');
const likeButton = document.querySelector('#like');
const dislikeButton = document.querySelector('#dislike');

// Variables
let cardCount = 0;
let cardsData = [];

// Functions

// Fetch card data from the backend
async function fetchCardData() {
  try {
    const response = await fetch('/api/get_cards');
    if (!response.ok) {
      throw new Error(`HTTP error! Status: ${response.status}`);
    }
    const data = await response.json();
    return data.cards;
  } catch (error) {
    console.error('Error fetching card data:', error);
    return [];
  }
}

// Append a new card to the swiper
async function appendNewCard() {
  if (cardCount >= cardsData.length) {
    console.log('No more cards to display.');
    return;
  }

  const cardData = cardsData[cardCount];
  if (!cardData) {
    console.log('No more cards to display.');
    return;
  }

  const card = new Card({
    title: cardData.title,
    imageUrl: cardData.imageUrl,
    description: cardData.description,
    onDismiss: appendNewCard,
    onLike: () => {
      console.log("Card liked");
      animateButton(likeButton);
      showFeedback('like');
      sendSwipeAction('like', cardData.id);
    },
    onDislike: () => {
      console.log("Card disliked");
      animateButton(dislikeButton);
      showFeedback('dislike');
      sendSwipeAction('dislike', cardData.id);
    }
  });

  swiper.append(card.element);
  console.log("Appended new card element:", card.element);
  cardCount++;

  const cards = swiper.querySelectorAll('.card:not(.dismissing)');
  cards.forEach((card, index) => {
    card.style.setProperty('--i', index);
  });
}

// Show feedback message
function showFeedback(action) {
  const feedback = document.createElement('div');
  feedback.classList.add('feedback', action);
  feedback.textContent = action === 'like' ? 'Liked!' : 'Disliked!';
  document.body.appendChild(feedback);

  setTimeout(() => {
    feedback.remove();
  }, 1000);
}

// Animate button when clicked
function animateButton(button) {
  button.classList.add('active');
  setTimeout(() => {
    button.classList.remove('active');
  }, 500);
}

// Get Card instance from DOM element
function getCardInstance(cardElement) {
  return cardElement.cardInstance;
}

// Send swipe action to the backend
async function sendSwipeAction(action, cardId) {
  try {
    const response = await fetch('/api/swipe', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ action, card_id: cardId })
    });
    const data = await response.json();
    if (data.status === 'success') {
      console.log(`Swipe action '${action}' recorded successfully.`);
    } else {
      console.error('Failed to record swipe action:', data);
    }
  } catch (error) {
    console.error('Error sending swipe action:', error);
  }
}

// Button Click Handlers
likeButton.addEventListener('click', () => {
  const currentCard = swiper.querySelector('.card:not(.dismissing)');
  if (currentCard) {
    const cardInstance = getCardInstance(currentCard);
    if (cardInstance) {
      cardInstance.dismiss(1); // Swipe right (like)
    }
  }
});

dislikeButton.addEventListener('click', () => {
  const currentCard = swiper.querySelector('.card:not(.dismissing)');
  if (currentCard) {
    const cardInstance = getCardInstance(currentCard);
    if (cardInstance) {
      cardInstance.dismiss(-1); // Swipe left (dislike)
    }
  }
});

// Initialize the swiper by fetching card data and appending initial cards
(async () => {
  cardsData = await fetchCardData();
  // Append the first 5 cards or as many as available
  const initialCards = Math.min(5, cardsData.length);
  for (let i = 0; i < initialCards; i++) {
    appendNewCard();
  }
})();
