// script.js

// DOM elements
const swiper = document.querySelector('#swiper');
const like = document.querySelector('#like');
const dislike = document.querySelector('#dislike');

console.log("Swiper Element:", swiper); // Check if swiper is selected
console.log("Like Element:", like);
console.log("Dislike Element:", dislike);

// variables
let cardCount = 0;

// functions
function appendNewCard() {
  const card = new Card({
    onDismiss: appendNewCard,
    onLike: () => {
      console.log("Card liked");
      like.style.animationPlayState = 'running';
      like.classList.toggle('trigger');
    },
    onDislike: () => {
      console.log("Card disliked");
      dislike.style.animationPlayState = 'running';
      dislike.classList.toggle('trigger');
    }
  });

  swiper.append(card.element);
  console.log("Appended new card element:", card.element); // Log the created card element
  cardCount++;

  const cards = swiper.querySelectorAll('.card:not(.dismissing)');
  cards.forEach((card, index) => {
    card.style.setProperty('--i', index);
  });
}


// Create the first 5 placeholder cards
for (let i = 0; i < 5; i++) {
  appendNewCard();
}
