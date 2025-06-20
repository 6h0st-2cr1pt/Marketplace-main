// Toast notification function
function showToast(message, type = 'success') {
    const toast = document.createElement('div');
    toast.className = `toast align-items-center text-white bg-${type} border-0`;
    toast.setAttribute('role', 'alert');
    toast.setAttribute('aria-live', 'assertive');
    toast.setAttribute('aria-atomic', 'true');
    
    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">
                ${message}
            </div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
        </div>
    `;
    
    const container = document.createElement('div');
    container.className = 'toast-container position-fixed bottom-0 end-0 p-3';
    container.appendChild(toast);
    document.body.appendChild(container);
    
    const bsToast = new bootstrap.Toast(toast);
    bsToast.show();
    
    toast.addEventListener('hidden.bs.toast', () => {
        container.remove();
    });
}

// Splash screen functionality
document.addEventListener('DOMContentLoaded', function() {
    const splashScreen = document.getElementById('splash-screen');
    const mainContent = document.querySelector('.main-content');
    const navbar = document.querySelector('.navbar');
    const footer = document.querySelector('.footer-glass');
    const hasSeenSplash = localStorage.getItem('hasSeenSplash');

    // Hide main content initially
    if (mainContent) mainContent.style.display = 'none';
    if (navbar) navbar.style.display = 'none';
    if (footer) footer.style.display = 'none';

    if (splashScreen && !hasSeenSplash) {
        // Show splash screen
        splashScreen.style.opacity = '1';
        splashScreen.style.visibility = 'visible';
        
        // Set flag in localStorage
        localStorage.setItem('hasSeenSplash', 'true');
        
        // After 3 seconds, hide splash screen and show main content
        setTimeout(() => {
            splashScreen.style.opacity = '0';
            splashScreen.style.visibility = 'hidden';
            
            // Show main content with a fade-in effect
            if (mainContent) {
                mainContent.style.display = 'block';
                mainContent.style.opacity = '0';
                mainContent.style.transition = 'opacity 0.5s ease-in-out';
                setTimeout(() => {
                    mainContent.style.opacity = '1';
                }, 50);
            }
            
            // Show navbar with a fade-in effect
            if (navbar) {
                navbar.style.display = 'block';
                navbar.style.opacity = '0';
                navbar.style.transition = 'opacity 0.5s ease-in-out';
                setTimeout(() => {
                    navbar.style.opacity = '1';
                }, 50);
            }
            
            // Show footer with a fade-in effect
            if (footer) {
                footer.style.display = 'block';
                footer.style.opacity = '0';
                footer.style.transition = 'opacity 0.5s ease-in-out';
                setTimeout(() => {
                    footer.style.opacity = '1';
                }, 50);
            }
        }, 3000);
    } else {
        // If splash has been seen before, show main content immediately
        if (mainContent) {
            mainContent.style.display = 'block';
            mainContent.style.opacity = '1';
        }
        if (navbar) {
            navbar.style.display = 'block';
            navbar.style.opacity = '1';
        }
        if (footer) {
            footer.style.display = 'block';
            footer.style.opacity = '1';
        }
    }

    // Add to cart buttons
    const addToCartButtons = document.querySelectorAll('.add-to-cart');
    addToCartButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const productId = this.dataset.productId;
            const quantity = document.querySelector(`#quantity-${productId}`)?.value || 1;
            
            fetch('/api/cart/add/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: `product_id=${productId}&quantity=${quantity}`
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    showToast(data.message);
                    updateCartCount(data.cart_count);
                } else {
                    showToast(data.message, 'danger');
                }
            })
            .catch(error => {
                showToast('An error occurred', 'danger');
            });
        });
    });
    
    // Wishlist toggle
    const wishlistButtons = document.querySelectorAll('.wishlist-toggle');
    wishlistButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const productId = this.dataset.productId;
            
            fetch('/api/wishlist/toggle/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: `product_id=${productId}`
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    showToast(data.message);
                    this.classList.toggle('active');
                } else {
                    showToast(data.message, 'danger');
                }
            })
            .catch(error => {
                showToast('An error occurred', 'danger');
            });
        });
    });
    
    // Search functionality
    const searchInput = document.querySelector('#search-input');
    if (searchInput) {
        let timeout = null;
        searchInput.addEventListener('input', function() {
            clearTimeout(timeout);
            timeout = setTimeout(() => {
                const query = this.value;
                if (query.length >= 2) {
                    fetch(`/api/search/?q=${encodeURIComponent(query)}`)
                        .then(response => response.json())
                        .then(data => {
                            if (data.success) {
                                updateSearchResults(data.results);
                            }
                        });
                }
            }, 300);
        });
    }
});

// Helper function to get CSRF token
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Update cart count in navbar
function updateCartCount(count) {
    const cartCount = document.querySelector('#cart-count');
    if (cartCount) {
        cartCount.textContent = count;
    }
}

// Update search results
function updateSearchResults(results) {
    const resultsContainer = document.querySelector('#search-results');
    if (resultsContainer) {
        resultsContainer.innerHTML = results.map(product => `
            <a href="/product/${product.slug}/" class="list-group-item list-group-item-action">
                <div class="d-flex align-items-center">
                    <img src="${product.image}" alt="${product.name}" class="me-3" style="width: 50px; height: 50px; object-fit: cover;">
                    <div>
                        <h6 class="mb-0">${product.name}</h6>
                        <small class="text-muted">$${product.price}</small>
                    </div>
                </div>
            </a>
        `).join('');
    }
}

// Product Image Gallery
function initImageGallery() {
    const thumbnails = document.querySelectorAll('.thumbnail-images img');
    const mainImage = document.getElementById('mainImage');
    
    if (thumbnails.length && mainImage) {
        thumbnails.forEach(thumb => {
            thumb.addEventListener('click', () => {
                mainImage.src = thumb.src;
                thumbnails.forEach(t => t.classList.remove('active'));
                thumb.classList.add('active');
            });
        });
    }
}

// Search Functionality
function initSearch() {
    const searchInput = document.querySelector('.search-input');
    const searchResults = document.querySelector('.search-results');
    
    if (searchInput && searchResults) {
        let timeout = null;
        
        searchInput.addEventListener('input', (e) => {
            clearTimeout(timeout);
            const query = e.target.value;
            
            if (query.length < 2) {
                searchResults.style.display = 'none';
                return;
            }
            
            timeout = setTimeout(() => {
                fetch(`/api/search/?q=${encodeURIComponent(query)}`)
                    .then(response => response.json())
                    .then(data => {
                        if (data.results.length) {
                            searchResults.innerHTML = data.results.map(product => `
                                <a href="/product/${product.slug}" class="search-result-item">
                                    <img src="${product.image}" alt="${product.name}">
                                    <div>
                                        <h6>${product.name}</h6>
                                        <p>$${product.price}</p>
                                    </div>
                                </a>
                            `).join('');
                            searchResults.style.display = 'block';
                        } else {
                            searchResults.innerHTML = '<p class="no-results">No products found</p>';
                            searchResults.style.display = 'block';
                        }
                    });
            }, 300);
        });
        
        // Close search results when clicking outside
        document.addEventListener('click', (e) => {
            if (!searchInput.contains(e.target) && !searchResults.contains(e.target)) {
                searchResults.style.display = 'none';
            }
        });
    }
}

// Initialize all functionality when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    initImageGallery();
    initSearch();
    
    // Add smooth scrolling to all links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth'
                });
            }
        });
    });
    
    // Add animation to elements when they come into view
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animate-fade-in');
            }
        });
    });
    
    document.querySelectorAll('.card, .section-title, .feature-item').forEach(el => {
        observer.observe(el);
    });
}); 