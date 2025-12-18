let currentSlide = 0;
const carousel = document.getElementById('carousel');
const slides = carousel.children.length;

function moveCarousel(direction) {
    currentSlide = (currentSlide + direction + slides) % slides;
    carousel.style.transform = `translateX(-${currentSlide * 100 / (window.innerWidth >= 768 ? 3 : 1)}%)`;
}

// Auto-resize carousel for responsiveness
window.addEventListener('resize', () => {
    carousel.style.transform = `translateX(-${currentSlide * 100 / (window.innerWidth >= 768 ? 3 : 1)}%)`;
});