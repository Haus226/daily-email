// Filter functionality
let currentFilterTag = 'ALL';

function flipCard(card) {
    card.classList.toggle('flipped');
}

function filterPapers(tag) {
    currentFilterTag = tag;
    
    document.querySelectorAll('.hf-card').forEach(card => {
        const tags = card.dataset.tags ? card.dataset.tags.split(" ") : [];
        const shouldShow = tag === "ALL" || tags.includes(tag);
        card.style.display = shouldShow ? "block" : "none";
    });
    
    updateFilterButtonStyles();
}

function updateFilterButtonStyles() {
    document.querySelectorAll('.filter-btn').forEach(btn => {
        btn.classList.toggle('active', btn.dataset.tag === currentFilterTag);
    });
}

function sortPapersByDateOnce() {
    const container = document.getElementById('hf-grid');
    if (!container) return;
    
    const cards = Array.from(document.querySelectorAll('.hf-card'));
    
    if (cards.length === 0) return;
    
    cards.sort((a, b) => {
        const dateA = new Date(a.dataset.date || '1970-01-01');
        const dateB = new Date(b.dataset.date || '1970-01-01');
        return dateB - dateA; // newest first
    });

    // Clear and append in sorted order
    container.innerHTML = '';
    cards.forEach(card => container.appendChild(card));
}

// Smooth scrolling for navigation links
document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('.nav-links a').forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const targetId = this.getAttribute('href').substring(1);
            const targetElement = document.getElementById(targetId);
            if (targetElement) {
                targetElement.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });

    // Initialize on page load
    sortPapersByDateOnce();
    filterPapers('ALL');
});
