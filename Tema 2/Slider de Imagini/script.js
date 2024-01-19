let currentSlide = 0;
const slides = document.querySelectorAll('.slider-image');
const totalSlides = slides.length;

function showSlide(n) {
    currentSlide = (n + totalSlides) % totalSlides;
    slides.forEach(slide => (slide.style.display = 'none'));
    slides[currentSlide].style.display = 'block';
}

function changeSlide(n) {
    showSlide(currentSlide + n);
}

function autoSlide() {
    changeSlide(1);
}

const interval = setInterval(autoSlide, 15000);

document.getElementById('slider-container').addEventListener('mouseenter', () => clearInterval(interval));
document.getElementById('slider-container').addEventListener('mouseleave', () => setInterval(autoSlide, 3000));

showSlide(currentSlide);