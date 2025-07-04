// ========================================
// MAIN.JS - FONCTIONS PRINCIPALES CHEM SPOT
// ========================================

// Variables globales
let currentPage = 1;
let itemsPerPage = 12;
let currentFilters = {};

// Données simulées
const products = [
    {
        id: 1,
        name: "Paracétamol",
        category: "api",
        price: "15.20",
        origin: "Inde",
        purity: "99.8%",
        stock: "En stock",
        supplier: "PharmaCorp India",
        cas: "103-90-2",
        formula: "C8H9NO2"
    },
    {
        id: 2,
        name: "Lactose Monohydraté",
        category: "excipient",
        price: "3.45",
        origin: "France",
        purity: "99.5%",
        stock: "En stock",
        supplier: "Roquette Pharma",
        cas: "64044-51-5",
        formula: "C12H22O11·H2O"
    },
    {
        id: 3,
        name: "Ibuprofène",
        category: "api",
        price: "22.80",
        origin: "Chine",
        purity: "99.9%",
        stock: "Stock limité",
        supplier: "ChemChina Exports",
        cas: "15687-27-1",
        formula: "C13H18O2"
    },
    {
        id: 4,
        name: "Stéarate de Magnésium",
        category: "excipient",
        price: "4.20",
        origin: "Allemagne",
        purity: "99.0%",
        stock: "En stock",
        supplier: "BASF Pharma",
        cas: "557-04-0",
        formula: "C36H70MgO4"
    },
    {
        id: 5,
        name: "Aspirine",
        category: "api",
        price: "18.50",
        origin: "Suisse",
        purity: "99.7%",
        stock: "En stock",
        supplier: "Novartis Ingredients",
        cas: "50-78-2",
        formula: "C9H8O4"
    },
    {
        id: 6,
        name: "Colorant Rouge E124",
        category: "colorant",
        price: "45.60",
        origin: "Allemagne",
        purity: "98.5%",
        stock: "En stock",
        supplier: "ColorTech GmbH",
        cas: "25956-17-6",
        formula: "C20H11N2NaO10S3"
    }
];

const suppliers = [
    {
        name: "PharmaCorp India",
        logo: "PH",
        country: "Mumbai, Inde",
        rating: 4.8,
        specialties: ["Paracétamol", "Ibuprofène", "Aspirine"],
        badge: "Certifié BPF",
        verified: true
    },
    {
        name: "BASF Pharma",
        logo: "BF",
        country: "Ludwigshafen, Allemagne",
        rating: 4.9,
        specialties: ["Polymères", "Liants", "Enrobages"],
        badge: "Premium",
        verified: true
    },
    {
        name: "Roquette Pharma",
        logo: "RQ",
        country: "Lestrem, France",
        rating: 4.7,
        specialties: ["Amidon", "Sorbitol", "Mannitol"],
        badge: "Local",
        verified: true
    },
    {
        name: "ChemChina Exports",
        logo: "CC",
        country: "Shanghai, Chine",
        rating: 4.4,
        specialties: ["Antibiotiques", "Vitamines", "Hormones"],
        badge: "Express",
        verified: true
    },
    {
        name: "Novartis Ingredients",
        logo: "NV",
        country: "Bâle, Suisse",
        rating: 4.9,
        specialties: ["APIs Premium", "Oncologie", "Neurologie"],
        badge: "Premium",
        verified: true
    },
    {
        name: "Givaudan Pharma",
        logo: "GV",
        country: "Genève, Suisse",
        rating: 4.6,
        specialties: ["Arômes", "Édulcorants", "Masqueurs"],
        badge: "Innovation",
        verified: true
    }
];

// Initialisation de l'application
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

function initializeApp() {
    setupEventListeners();
    setupScrollAnimations();
    animateCounters();
    initializePage();
}

// Initialisation spécifique selon la page
function initializePage() {
    const currentPath = window.location.pathname;
    
    if (currentPath.includes('catalogue.html')) {
        renderCatalogProducts();
        setupCatalogFilters();
    } else if (currentPath.includes('fournisseurs.html')) {
        renderSuppliers();
        setupSupplierFilters();
    } else if (currentPath.includes('index.html') || currentPath === '/') {
        renderFeaturedProducts();
        renderFeaturedSuppliers();
    }
}

// Configuration des écouteurs d'événements
function setupEventListeners() {
    // Gestion du scroll pour l'header
    window.addEventListener('scroll', handleHeaderScroll);
    
    // Fermeture des modals en cliquant à l'extérieur
    window.addEventListener('click', function(e) {
        if (e.target.classList.contains('modal')) {
            e.target.style.display = 'none';
            document.body.style.overflow = 'auto';
        }
    });
    
    // Gestion des erreurs globales
    window.addEventListener('error', function(e) {
        console.error('Erreur détectée:', e.error);
        showNotification('Une erreur s\'est produite. Veuillez rafraîchir la page.', 'error');
    });
}

// Gestion du scroll de l'header
function handleHeaderScroll() {
    const header = document.querySelector('header');
    if (!header) return;
    
    if (window.scrollY > 100) {
        header.style.background = 'rgba(255, 255, 255, 0.98)';
        header.style.boxShadow = '0 4px 20px rgba(0, 0, 0, 0.1)';
    } else {
        header.style.background = 'rgba(255, 255, 255, 0.95)';
        header.style.boxShadow = '0 4px 6px rgba(0, 0, 0, 0.05)';
    }
}

// Rendu des produits pour la page d'accueil
function renderFeaturedProducts() {
    const grid = document.getElementById('productsGrid');
    if (!grid) return;
    
    grid.innerHTML = '';
    products.slice(0, 4).forEach(product => {
        grid.appendChild(createProductCard(product));
    });
}

// Rendu des fournisseurs pour la page d'accueil
function renderFeaturedSuppliers() {
    const container = document.querySelector('.suppliers-grid');
    if (!container) return;
    
    container.innerHTML = '';
    suppliers.slice(0, 3).forEach(supplier => {
        container.appendChild(createSupplierCard(supplier));
    });
}

// Rendu complet pour la page catalogue
function renderCatalogProducts(filteredProducts = null) {
    const grid = document.getElementById('catalogProductsGrid');
    const resultsCount = document.getElementById('resultsCount');
    
    if (!grid) return;
    
    const productsToRender = filteredProducts || products;
    
    // Mise à jour du compteur
    if (resultsCount) {
        resultsCount.textContent = `${productsToRender.length} produit${productsToRender.length > 1 ? 's' : ''} trouvé${productsToRender.length > 1 ? 's' : ''}`;
    }
    
    // Pagination
    const startIndex = (currentPage - 1) * itemsPerPage;
    const endIndex = startIndex + itemsPerPage;
    const paginatedProducts = productsToRender.slice(startIndex, endIndex);
    
    // Rendu des produits
    grid.innerHTML = '';
    paginatedProducts.forEach(product => {
        grid.appendChild(createProductCard(product));
    });
    
    // Mise à jour de la pagination
    updatePagination(productsToRender.length);
}

// Rendu des fournisseurs pour la page fournisseurs
function renderSuppliers(filteredSuppliers = null) {
    const grid = document.getElementById('suppliersGrid');
    if (!grid) return;
    
    const suppliersToRender = filteredSuppliers || suppliers;
    
    grid.innerHTML = '';
    suppliersToRender.forEach(supplier => {
        grid.appendChild(createSupplierCard(supplier));
    });
}

// Création d'une card produit
function createProductCard(product) {
    const card = document.createElement('div');
    card.className = 'product-card fade-in';
    card.innerHTML = `
        <div class="availability-badge status-badge ${product.stock === 'En stock' ? 'success' : 'warning'}">${product.stock}</div>
        <div class="product-header">
            <div class="product-icon">
                <i class="fas fa-pills"></i>
            </div>
            <h3>${product.name}</h3>
        </div>
        <div class="product-details">
            <div class="product-meta">
                <span class="product-price">${product.price}€/kg</span>
                <span style="font-size: 0.8rem; color: var(--text-light);">
                    <i class="fas fa-map-marker-alt"></i> ${product.origin}
                </span>
            </div>
            <div class="product-specs">
                <div class="spec-item">
                    <span class="spec-label">Pureté:</span>
                    <span class="spec-value">${product.purity}</span>
                </div>
                <div class="spec-item">
                    <span class="spec-label">CAS:</span>
                    <span class="spec-value">${product.cas}</span>
                </div>
                <div class="spec-item">
                    <span class="spec-label">Formule:</span>
                    <span class="spec-value">${product.formula}</span>
                </div>
                <div class="spec-item">
                    <span class="spec-label">Fournisseur:</span>
                    <span class="spec-value">${product.supplier}</span>
                </div>
            </div>
            <div style="display: flex; gap: 0.5rem; margin-top: 1rem;">
                <button class="btn btn-primary btn-sm" style="flex: 1;" onclick="requestQuote(${product.id})">
                    <i class="fas fa-calculator"></i> Devis
                </button>
                <button class="btn btn-outline btn-sm" onclick="viewProductDetails(${product.id})">
                    <i class="fas fa-info"></i>
                </button>
            </div>
        </div>
    `;
    return card;
}

// Création d'une card fournisseur
function createSupplierCard(supplier) {
    const card = document.createElement('div');
    card.className = 'supplier-card fade-in';
    
    const stars = generateStarsHTML(supplier.rating);
    
    card.innerHTML = `
        <div class="supplier-badge status-badge success">${supplier.badge}</div>
        <div class="supplier-header">
            <div class="supplier-logo">${supplier.logo}</div>
            <h3>${supplier.name}</h3>
        </div>
        <div class="supplier-details">
            <div class="supplier-meta">
                <span class="supplier-location">
                    <i class="fas fa-map-marker-alt"></i> ${supplier.country}
                </span>
                <div class="supplier-rating">
                    <span class="rating-stars">${stars}</span>
                    <span class="rating-score">${supplier.rating}</span>
                </div>
            </div>
            <p>Fournisseur certifié spécialisé dans les matières premières de haute qualité</p>
            <div class="supplier-specialties">
                ${supplier.specialties.map(spec => 
                    `<span class="specialty-tag">${spec}</span>`
                ).join('')}
            </div>
            <div style="display: flex; gap: 0.5rem; margin-top: 1.5rem;">
                <button class="btn btn-primary btn-sm" style="flex: 1;" onclick="contactSupplier('${supplier.name}')">
                    <i class="fas fa-envelope"></i> Contacter
                </button>
                <button class="btn btn-outline btn-sm" onclick="viewSupplierProfile('${supplier.name}')">
                    <i class="fas fa-eye"></i> Profil
                </button>
            </div>
        </div>
    `;
    return card;
}

// Génération des étoiles pour la notation
function generateStarsHTML(rating) {
    const fullStars = Math.floor(rating);
    const hasHalfStar = rating % 1 !== 0;
    let starsHTML = '';
    
    for (let i = 0; i < fullStars; i++) {
        starsHTML += '★';
    }
    
    if (hasHalfStar) {
        starsHTML += '☆';
    }
    
    return starsHTML;
}

// Fonctions d'interaction
function requestQuote(productId) {
    const product = products.find(p => p.id === productId);
    if (product) {
        showNotification(`Demande de devis envoyée pour ${product.name}. Vous recevrez une réponse sous 2h.`, 'success');
    }
}

function viewProductDetails(productId) {
    const product = products.find(p => p.id === productId);
    if (product) {
        showProductModal(product);
    }
}

function contactSupplier(supplierName) {
    showNotification(`Message envoyé à ${supplierName}. Ils vous répondront sous 24h.`, 'success');
}

function viewSupplierProfile(supplierName) {
    const supplier = suppliers.find(s => s.name === supplierName);
    if (supplier) {
        showSupplierModal(supplier);
    }
}

// Affichage du modal produit
function showProductModal(product) {
    const modal = document.getElementById('productModal');
    const content = document.getElementById('productModalContent');
    
    if (!modal || !content) return;
    
    content.innerHTML = `
        <div class="product-modal-header">
            <h2><i class="fas fa-pills"></i> ${product.name}</h2>
            <div class="status-badge ${product.stock === 'En stock' ? 'success' : 'warning'}">${product.stock}</div>
        </div>
        
        <div class="product-modal-content">
            <div class="product-modal-info">
                <div class="info-section">
                    <h3>Informations générales</h3>
                    <div class="info-grid">
                        <div class="info-item">
                            <span class="label">Numéro CAS:</span>
                            <span class="value">${product.cas}</span>
                        </div>
                        <div class="info-item">
                            <span class="label">Formule moléculaire:</span>
                            <span class="value">${product.formula}</span>
                        </div>
                        <div class="info-item">
                            <span class="label">Pureté:</span>
                            <span class="value">${product.purity}</span>
                        </div>
                        <div class="info-item">
                            <span class="label">Origine:</span>
                            <span class="value">${product.origin}</span>
                        </div>
                    </div>
                </div>
                
                <div class="info-section">
                    <h3>Fournisseur</h3>
                    <p><strong>${product.supplier}</strong></p>
                    <p>Fournisseur certifié BPF/GMP avec plus de 15 ans d'expérience</p>
                </div>
                
                <div class="info-section">
                    <h3>Prix et conditions</h3>
                    <div class="price-info">
                        <span class="price-large">${product.price}€/kg</span>
                        <p>Prix indicatif HT - Devis personnalisé selon quantité</p>
                        <p>MOQ: 25kg | Délai: 10-15 jours | Livraison incluse</p>
                    </div>
                </div>
            </div>
            
            <div class="product-modal-actions">
                <button class="btn btn-primary btn-lg" onclick="requestQuote(${product.id}); closeModal('productModal');">
                    <i class="fas fa-calculator"></i> Demander un devis
                </button>
                <button class="btn btn-outline" onclick="contactSupplier('${product.supplier}')">
                    <i class="fas fa-envelope"></i> Contacter le fournisseur
                </button>
            </div>
        </div>
    `;
    
    openModal('productModal');
}

// Affichage du modal fournisseur
function showSupplierModal(supplier) {
    const modal = document.getElementById('supplierDetailModal');
    const content = document.getElementById('supplierDetailContent');
    
    if (!modal || !content) return;
    
    const stars = generateStarsHTML(supplier.rating);
    
    content.innerHTML = `
        <div class="supplier-modal-header">
            <div class="supplier-logo-large">${supplier.logo}</div>
            <div class="supplier-info">
                <h2>${supplier.name}</h2>
                <p><i class="fas fa-map-marker-alt"></i> ${supplier.country}</p>
                <div class="rating-large">
                    <span class="stars">${stars}</span>
                    <span class="score">${supplier.rating}/5</span>
                </div>
            </div>
            <div class="status-badge success">${supplier.badge}</div>
        </div>
        
        <div class="supplier-modal-content">
            <div class="supplier-description">
                <h3>À propos</h3>
                <p>Fournisseur leader dans l'industrie pharmaceutique avec plus de 20 ans d'expérience. 
                Certifié BPF/GMP et ISO 9001, nous garantissons la plus haute qualité pour tous nos produits.</p>
            </div>
            
            <div class="supplier-specialties-section">
                <h3>Spécialités</h3>
                <div class="specialties-grid">
                    ${supplier.specialties.map(spec => 
                        `<span class="specialty-tag">${spec}</span>`
                    ).join('')}
                </div>
            </div>
            
            <div class="supplier-certifications">
                <h3>Certifications</h3>
                <div class="certifications-list">
                    <span class="cert-badge"><i class="fas fa-certificate"></i> BPF/GMP</span>
                    <span class="cert-badge"><i class="fas fa-certificate"></i> ISO 9001:2015</span>
                    <span class="cert-badge"><i class="fas fa-certificate"></i> FDA Approved</span>
                </div>
            </div>
            
            <div class="supplier-actions">
                <button class="btn btn-primary btn-lg" onclick="contactSupplier('${supplier.name}'); closeModal('supplierDetailModal');">
                    <i class="fas fa-envelope"></i> Envoyer un message
                </button>
                <button class="btn btn-outline" onclick="showNotification('Demande de catalogue envoyée', 'success')">
                    <i class="fas fa-download"></i> Demander le catalogue
                </button>
            </div>
        </div>
    `;
    
    openModal('supplierDetailModal');
}

// Gestion des modals
function openModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.style.display = 'block';
        document.body.style.overflow = 'hidden';
    }
}

function closeModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.style.display = 'none';
        document.body.style.overflow = 'auto';
    }
}

// Animation des compteurs
function animateCounters() {
    const counters = document.querySelectorAll('.stat-number');
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                animateCounter(entry.target);
                observer.unobserve(entry.target);
            }
        });
    });
    
    counters.forEach(counter => observer.observe(counter));
}

function animateCounter(element) {
    const target = parseFloat(element.getAttribute('data-target'));
    const suffix = element.textContent.includes('€') ? '€M+' : 
                  element.textContent.includes('+') ? '+' : '';
    
    let current = 0;
    const increment = target / 100;
    const timer = setInterval(() => {
        current += increment;
        if (current >= target) {
            element.textContent = target + suffix;
            clearInterval(timer);
        } else {
            element.textContent = Math.floor(current * 10) / 10 + suffix;
        }
    }, 20);
}

// Animations au scroll
function setupScrollAnimations() {
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.animationDelay = `${Math.random() * 0.5}s`;
                entry.target.classList.add('fade-in');
            }
        });
    }, {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    });

    // Observer tous les éléments avec animation
    document.querySelectorAll('.feature-card, .product-card, .supplier-card, .contact-card, .stat-card').forEach(el => {
        observer.observe(el);
    });
}

// Système de notifications
function showNotification(message, type = 'info') {
    // Supprimer les notifications existantes
    const existingNotifications = document.querySelectorAll('.notification');
    existingNotifications.forEach(notif => notif.remove());
    
    const notification = document.createElement('div');
    notification.className = 'notification';
    
    const colors = {
        success: '#48bb78',
        warning: '#ed8936',
        error: '#f56565',
        info: '#4299e1'
    };
    
    const icons = {
        success: 'check',
        warning: 'exclamation',
        error: 'times',
        info: 'info'
    };
    
    notification.style.backgroundColor = colors[type];
    notification.innerHTML = `
        <i class="fas fa-${icons[type]}-circle"></i>
        ${message}
    `;
    
    document.body.appendChild(notification);
    
    // Auto-suppression après 5 secondes
    setTimeout(() => {
        if (notification.parentNode) {
            notification.remove();
        }
    }, 5000);
}

// Mise à jour de la pagination
function updatePagination(totalItems) {
    const pagination = document.getElementById('pagination');
    if (!pagination) return;
    
    const totalPages = Math.ceil(totalItems / itemsPerPage);
    
    if (totalPages <= 1) {
        pagination.style.display = 'none';
        return;
    }
    
    pagination.style.display = 'flex';
    pagination.innerHTML = '';
    
    // Bouton précédent
    if (currentPage > 1) {
        const prevBtn = document.createElement('button');
        prevBtn.innerHTML = '<i class="fas fa-chevron-left"></i> Précédent';
        prevBtn.onclick = () => changePage(currentPage - 1);
        pagination.appendChild(prevBtn);
    }
    
    // Numéros de pages
    const startPage = Math.max(1, currentPage - 2);
    const endPage = Math.min(totalPages, currentPage + 2);
    
    for (let i = startPage; i <= endPage; i++) {
        const pageBtn = document.createElement('button');
        pageBtn.textContent = i;
        pageBtn.className = i === currentPage ? 'active' : '';
        pageBtn.onclick = () => changePage(i);
        pagination.appendChild(pageBtn);
    }
    
    // Bouton suivant
    if (currentPage < totalPages) {
        const nextBtn = document.createElement('button');
        nextBtn.innerHTML = 'Suivant <i class="fas fa-chevron-right"></i>';
        nextBtn.onclick = () => changePage(currentPage + 1);
        pagination.appendChild(nextBtn);
    }
}

function changePage(page) {
    currentPage = page;
    renderCatalogProducts();
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

// Tri des produits
function sortProducts() {
    const sortSelect = document.getElementById('sortSelect');
    if (!sortSelect) return;
    
    const sortValue = sortSelect.value;
    let sortedProducts = [...products];
    
    switch (sortValue) {
        case 'name':
            sortedProducts.sort((a, b) => a.name.localeCompare(b.name));
            break;
        case 'price-asc':
            sortedProducts.sort((a, b) => parseFloat(a.price) - parseFloat(b.price));
            break;
        case 'price-desc':
            sortedProducts.sort((a, b) => parseFloat(b.price) - parseFloat(a.price));
            break;
        case 'purity':
            sortedProducts.sort((a, b) => parseFloat(b.purity) - parseFloat(a.purity));
            break;
    }
    
    currentPage = 1;
    renderCatalogProducts(sortedProducts);
}

// Simulation des prix en temps réel
function updatePrices() {
    const priceElements = document.querySelectorAll('.product-price');
    priceElements.forEach(el => {
        if (Math.random() > 0.8) { // 20% chance de mise à jour
            const currentPrice = parseFloat(el.textContent);
            const change = (Math.random() - 0.5) * 0.1; // ±5% max
            const newPrice = (currentPrice * (1 + change)).toFixed(2);
            
            el.style.transition = 'all 0.3s ease';
            el.style.transform = 'scale(1.05)';
            
            setTimeout(() => {
                el.textContent = newPrice + '€/kg';
                el.style.transform = 'scale(1)';
            }, 150);
        }
    });
}

// Fonctions utilitaires
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

function throttle(func, limit) {
    let inThrottle;
    return function() {
        const args = arguments;
        const context = this;
        if (!inThrottle) {
            func.apply(context, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    }
}

// FAQ Toggle
function toggleFaq(element) {
    const faqItem = element.closest('.faq-item');
    const answer = faqItem.querySelector('.faq-answer');
    const isActive = faqItem.classList.contains('active');
    
    // Fermer toutes les autres FAQ
    document.querySelectorAll('.faq-item').forEach(item => {
        item.classList.remove('active');
    });
    
    // Ouvrir celle-ci si elle n'était pas active
    if (!isActive) {
        faqItem.classList.add('active');
    }
}

// Fonctions spécifiques aux pages de contact
function startLiveChat() {
    showNotification('Connexion au chat en cours...', 'info');
    setTimeout(() => {
        showNotification('Chat démarré ! Un agent va vous répondre.', 'success');
    }, 1500);
}

function openDocumentation() {
    showNotification('Ouverture de la documentation...', 'info');
    // Simuler l'ouverture de la documentation
}

function openGoogleMaps() {
    const address = "15 Rue de la Paix, 25000 Besançon, France";
    const url = `https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(address)}`;
    window.open(url, '_blank');
}

// Mise à jour des prix toutes les 30 secondes
setInterval(updatePrices, 30000);

// Performance monitoring
window.addEventListener('load', function() {
    console.log('Site chargé en:', performance.now(), 'ms');
});

// Export des fonctions pour utilisation globale
window.ChemSpot = {
    openModal,
    closeModal,
    showNotification,
    requestQuote,
    viewProductDetails,
    contactSupplier,
    viewSupplierProfile,
    toggleFaq,
    startLiveChat,
    openDocumentation,
    openGoogleMaps,
    sortProducts,
    changePage
};
