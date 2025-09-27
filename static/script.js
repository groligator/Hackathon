// Example: highlight message on hover
document.querySelectorAll('.message-card').forEach(card => {
    card.addEventListener('mouseenter', () => {
        card.style.backgroundColor = '#f0f8ff';
    });
    card.addEventListener('mouseleave', () => {
        card.style.backgroundColor = 'white';
    });
});
