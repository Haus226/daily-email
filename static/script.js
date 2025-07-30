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

// Card switching functionality - manual only
let currentCardIndex = 0;
const totalCards = 3;

function showCard(index) {
    console.log('showCard called with index:', index);
    const cards = document.querySelectorAll('.three-column .card');
    console.log('Found cards:', cards.length);
    
    // Force remove active class and reset styles
    cards.forEach((card, i) => {
        card.classList.remove('active');
        card.style.opacity = '0';
        card.style.transform = 'translateX(100px)';
        card.style.pointerEvents = 'none';
        card.style.zIndex = '1';
        console.log(`Card ${i} reset`);
    });
    
    // Force reflow
    cards[0]?.offsetHeight;
    
    // Add active class to current card with forced styles
    if (cards[index]) {
        cards[index].classList.add('active');
        cards[index].style.opacity = '1';
        cards[index].style.transform = 'translateX(0)';
        cards[index].style.pointerEvents = 'all';
        cards[index].style.zIndex = '10';
        console.log(`Card ${index} activated with forced styles`);
    }
    
    currentCardIndex = index;
}

function nextCard() {
    console.log('nextCard called');
    const nextIndex = (currentCardIndex + 1) % totalCards;
    showCard(nextIndex);
}

function prevCard() {
    console.log('prevCard called');
    const prevIndex = (currentCardIndex - 1 + totalCards) % totalCards;
    showCard(prevIndex);
}

// Make functions global for onclick handlers
window.nextCard = nextCard;
window.prevCard = prevCard;

// Full-screen media functionality
function openFullScreen(element) {
    const overlay = document.createElement('div');
    overlay.className = 'fullscreen-overlay';
    overlay.onclick = () => closeFullScreen(overlay);
    
    const container = document.createElement('div');
    container.className = 'fullscreen-container';
    
    const closeBtn = document.createElement('button');
    closeBtn.className = 'fullscreen-close';
    closeBtn.innerHTML = '×';
    closeBtn.onclick = () => closeFullScreen(overlay);
    
    const clonedElement = element.cloneNode(true);
    clonedElement.className = 'fullscreen-media';
    
    container.appendChild(closeBtn);
    container.appendChild(clonedElement);
    overlay.appendChild(container);
    document.body.appendChild(overlay);
    
    // Prevent body scroll
    document.body.style.overflow = 'hidden';
    
    // Animate in
    setTimeout(() => overlay.classList.add('active'), 10);
}

function closeFullScreen(overlay) {
    overlay.classList.remove('active');
    setTimeout(() => {
        document.body.removeChild(overlay);
        document.body.style.overflow = '';
    }, 300);
}

document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM loaded');
    
    // Smooth scrolling for navigation links
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

    // Initialize papers
    sortPapersByDateOnce();
    filterPapers('ALL');
    
    // Initialize card switching with APOD first (index 0)
    const container = document.querySelector('.three-column');
    console.log('Container found:', !!container);
    
    if (container && window.innerWidth > 768) {
        console.log('Desktop mode - initializing card switching');
        
        // Wait for all content to load
        setTimeout(() => {
            const cards = document.querySelectorAll('.three-column .card');
            console.log('Cards found after timeout:', cards.length);
            
            // Force initial state
            cards.forEach((card, i) => {
                card.classList.remove('active');
                card.style.opacity = '0';
                card.style.transform = 'translateX(100px)';
                card.style.pointerEvents = 'none';
                card.style.zIndex = '1';
                console.log(`Initial setup for card ${i}`);
            });
            
            // Show APOD first (index 0)
            showCard(0);
        }, 100);
        
    } else if (container) {
        console.log('Mobile mode - showing all cards');
        const cards = document.querySelectorAll('.three-column .card');
        cards.forEach(card => card.classList.add('active'));
    }
    
    // Extract and place media content
    if (window.innerWidth > 768) {
        // Move APOD media and add click handler
        const apodContent = document.getElementById('apod-content');
        const apodMedia = document.getElementById('apod-media');
        const apodMediaElement = apodContent.querySelector('.apod-media-element');
        if (apodMediaElement && apodMedia) {
            const clonedApod = apodMediaElement.cloneNode(true);
            clonedApod.style.cursor = 'pointer';
            clonedApod.onclick = () => openFullScreen(clonedApod);
            apodMedia.appendChild(clonedApod);
        }
        
        // Move EO media and add click handler
        const eoContent = document.getElementById('eo-content');
        const eoMedia = document.getElementById('eo-media');
        const eoMediaElement = eoContent.querySelector('.eo-media-element');
        if (eoMediaElement && eoMedia) {
            const clonedEo = eoMediaElement.cloneNode(true);
            clonedEo.style.cursor = 'pointer';
            clonedEo.onclick = () => openFullScreen(clonedEo);
            eoMedia.appendChild(clonedEo);
        }
        
        // Move Tarot card and add click handler for the image
        const tarotContent = document.getElementById('tarot-content');
        const tarotMedia = document.getElementById('tarot-media');
        const tarotMediaElement = tarotContent.querySelector('.tarot-media-element');
        if (tarotMediaElement && tarotMedia) {
            const clonedTarot = tarotMediaElement.cloneNode(true);
            // Add click handler to tarot card image specifically
            const tarotImg = clonedTarot.querySelector('img');
            if (tarotImg) {
                tarotImg.style.cursor = 'pointer';
                tarotImg.onclick = (e) => {
                    e.stopPropagation();
                    openFullScreen(tarotImg);
                };
            }
            tarotMedia.appendChild(clonedTarot);
        }
    }
});