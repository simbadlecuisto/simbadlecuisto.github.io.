// ========================================
// API.JS - COMMUNICATION AVEC LE BACK-END CHEM SPOT
// ========================================

// Configuration API
const API_CONFIG = {
    baseUrl: '/api/v1',
    timeout: 30000,
    retryAttempts: 3,
    retryDelay: 1000
};

// État de l'API
let apiState = {
    isOnline: true,
    requestCount: 0,
    errors: [],
    cache: new Map()
};

// Initialisation de l'API
document.addEventListener('DOMContentLoaded', function() {
    initializeAPI();
    setupAPIMonitoring();
});

function initializeAPI() {
    // Configuration des intercepteurs
    setupRequestInterceptors();
    setupResponseInterceptors();
    
    // Vérification de la connectivité
    checkAPIHealth();
    
    // Configuration du cache
    setupCache();
}

// Fonction principale de requête API
async function apiRequest(endpoint, options = {}) {
    const config = {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
            'X-Client-Version': '1.0.0',
            'X-Request-ID': generateRequestId(),
            ...options.headers
        },
        timeout: API_CONFIG.timeout,
        ...options
    };
    
    // Ajouter le token d'authentification si disponible
    const token = getAuthToken();
    if (token) {
        config.headers['Authorization'] = `Bearer ${token}`;
    }
    
    const url = `${API_CONFIG.baseUrl}${endpoint}`;
    const cacheKey = `${config.method}:${url}`;
    
    // Vérifier le cache pour les requêtes GET
    if (config.method === 'GET' && apiState.cache.has(cacheKey)) {
        const cached = apiState.cache.get(cacheKey);
        if (Date.now() - cached.timestamp < getCacheTimeout(endpoint)) {
            console.log('Données récupérées du cache:', endpoint);
            return cached.data;
        }
    }
    
    try {
        apiState.requestCount++;
        
        // Simulation d'API (à remplacer par de vraies requêtes)
        const response = await simulateAPIRequest(endpoint, config);
        
        // Mise en cache des réponses GET réussies
        if (config.method === 'GET' && response.success) {
            apiState.cache.set(cacheKey, {
                data: response.data,
                timestamp: Date.now()
            });
        }
        
        return response.data;
        
    } catch (error) {
        console.error('Erreur API:', error);
        apiState.errors.push({
            endpoint,
            error: error.message,
            timestamp: Date.now()
        });
        
        throw error;
    }
}

// Simulation d'API (à remplacer par de vraies requêtes fetch)
async function simulateAPIRequest(endpoint, config) {
    await new Promise(resolve => setTimeout(resolve, 200 + Math.random() * 800));
    
    // Simulation d'erreurs aléatoires (5% de chance)
    if (Math.random() < 0.05) {
        throw new Error('Erreur de communication avec le serveur');
    }
    
    // Routes simulées
    switch (true) {
        case endpoint.includes('/products'):
            return handleProductsAPI(endpoint, config);
        case endpoint.includes('/suppliers'):
            return handleSuppliersAPI(endpoint, config);
        case endpoint.includes('/quotes'):
            return handleQuotesAPI(endpoint, config);
        case endpoint.includes('/orders'):
            return handleOrdersAPI(endpoint, config);
        case endpoint.includes('/analytics'):
            return handleAnalyticsAPI(endpoint, config);
        default:
            return { success: true, data: { message: 'Endpoint simulé' } };
    }
}

// API Produits
function handleProductsAPI(endpoint, config) {
    const products = window.products || [];
    
    if (endpoint === '/products') {
        return {
            success: true,
            data: {
                products: products,
                total: products.length,
                page: 1,
                limit: 50
            }
        };
    }
    
    if (endpoint.includes('/products/')) {
        const id = parseInt(endpoint.split('/').pop());
        const product = products.find(p => p.id === id);
        
        if (product) {
            return {
                success: true,
                data: {
                    ...product,
                    specifications: generateProductSpecs(product),
                    documentation: generateProductDocs(product),
                    pricing: generatePricingTiers(product)
                }
            };
        } else {
            throw new Error('Produit non trouvé');
        }
    }
    
    return { success: true, data: [] };
}

// API Fournisseurs
function handleSuppliersAPI(endpoint, config) {
    const suppliers = window.suppliers || [];
    
    if (endpoint === '/suppliers') {
        return {
            success: true,
            data: {
                suppliers: suppliers.map(s => ({
                    ...s,
                    certifications: generateCertifications(s),
                    products_count: Math.floor(Math.random() * 50) + 10,
                    response_time: Math.floor(Math.random() * 24) + 1
                })),
                total: suppliers.length
            }
        };
    }
    
    if (endpoint.includes('/suppliers/')) {
        const name = decodeURIComponent(endpoint.split('/').pop());
        const supplier = suppliers.find(s => s.name === name);
        
        if (supplier) {
            return {
                success: true,
                data: {
                    ...supplier,
                    detailed_info: generateSupplierDetails(supplier),
                    certifications: generateCertifications(supplier),
                    products: generateSupplierProducts(supplier)
                }
            };
        } else {
            throw new Error('Fournisseur non trouvé');
        }
    }
    
    return { success: true, data: [] };
}

// API Devis
function handleQuotesAPI(endpoint, config) {
    if (config.method === 'POST' && endpoint === '/quotes') {
        const quoteData = JSON.parse(config.body || '{}');
        
        return {
            success: true,
            data: {
                quote_id: generateQuoteId(),
                status: 'pending',
                estimated_response_time: '2-4 heures',
                products: quoteData.products || [],
                total_estimated: calculateEstimatedTotal(quoteData.products || []),
                expires_at: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString()
            }
        };
    }
    
    if (endpoint === '/quotes') {
        return {
            success: true,
            data: {
                quotes: generateUserQuotes(),
                total: 5
            }
        };
    }
    
    return { success: true, data: [] };
}

// API Commandes
function handleOrdersAPI(endpoint, config) {
    if (config.method === 'POST' && endpoint === '/orders') {
        const orderData = JSON.parse(config.body || '{}');
        
        return {
            success: true,
            data: {
                order_id: generateOrderId(),
                status: 'confirmed',
                tracking_number: generateTrackingNumber(),
                estimated_delivery: calculateDeliveryDate(),
                total: orderData.total || 0
            }
        };
    }
    
    if (endpoint === '/orders') {
        return {
            success: true,
            data: {
                orders: generateUserOrders(),
                total: 8
            }
        };
    }
    
    return { success: true, data: [] };
}

// API Analytics
function handleAnalyticsAPI(endpoint, config) {
    return {
        success: true,
        data: {
            dashboard: {
                total_products: 847,
                total_suppliers: 127,
                total_transactions: 5200000,
                countries_covered: 24,
                price_trends: generatePriceTrends(),
                popular_products: generatePopularProducts(),
                market_insights: generateMarketInsights()
            }
        }
    };
}

// Fonctions spécifiques à l'API

// Récupération des produits
async function getProducts(filters = {}) {
    try {
        const queryParams = new URLSearchParams(filters).toString();
        const endpoint = `/products${queryParams ? `?${queryParams}` : ''}`;
        const response = await apiRequest(endpoint);
        return response;
    } catch (error) {
        showNotification('Erreur lors du chargement des produits', 'error');
        throw error;
    }
}

// Récupération d'un produit spécifique
async function getProduct(productId) {
    try {
        const response = await apiRequest(`/products/${productId}`);
        return response;
    } catch (error) {
        showNotification('Erreur lors du chargement du produit', 'error');
        throw error;
    }
}

// Récupération des fournisseurs
async function getSuppliers(filters = {}) {
    try {
        const queryParams = new URLSearchParams(filters).toString();
        const endpoint = `/suppliers${queryParams ? `?${queryParams}` : ''}`;
        const response = await apiRequest(endpoint);
        return response;
    } catch (error) {
        showNotification('Erreur lors du chargement des fournisseurs', 'error');
        throw error;
    }
}

// Demande de devis
async function requestQuote(quoteData) {
    try {
        const response = await apiRequest('/quotes', {
            method: 'POST',
            body: JSON.stringify(quoteData)
        });
        
        showNotification('Demande de devis envoyée avec succès', 'success');
        return response;
    } catch (error) {
        showNotification('Erreur lors de l\'envoi de la demande de devis', 'error');
        throw error;
    }
}

// Filtrage des produits
async function filterProducts(filters) {
    try {
        // Appliquer les filtres côté client pour la démo
        let filteredProducts = window.products || [];
        
        if (filters.category && filters.category !== 'all') {
            filteredProducts = filteredProducts.filter(p => p.category === filters.category);
        }
        
        if (filters.origin) {
            filteredProducts = filteredProducts.filter(p => p.origin === filters.origin);
        }
        
        if (filters.priceMin) {
            filteredProducts = filteredProducts.filter(p => parseFloat(p.price) >= filters.priceMin);
        }
        
        if (filters.priceMax) {
            filteredProducts = filteredProducts.filter(p => parseFloat(p.price) <= filters.priceMax);
        }
        
        if (filters.stock) {
            filteredProducts = filteredProducts.filter(p => p.stock === filters.stock);
        }
        
        return {
            products: filteredProducts,
            total: filteredProducts.length
        };
    } catch (error) {
        console.error('Erreur lors du filtrage:', error);
        return { products: [], total: 0 };
    }
}

// Filtrage des fournisseurs
async function filterSuppliers(filters) {
    try {
        let filteredSuppliers = window.suppliers || [];
        
        if (filters.country) {
            filteredSuppliers = filteredSuppliers.filter(s => 
                s.country.toLowerCase().includes(filters.country.toLowerCase())
            );
        }
        
        if (filters.specialty) {
            filteredSuppliers = filteredSuppliers.filter(s => 
                s.specialties.some(spec => spec.toLowerCase().includes(filters.specialty.toLowerCase()))
            );
        }
        
        if (filters.rating) {
            filteredSuppliers = filteredSuppliers.filter(s => s.rating >= parseFloat(filters.rating));
        }
        
        return {
            suppliers: filteredSuppliers,
            total: filteredSuppliers.length
        };
    } catch (error) {
        console.error('Erreur lors du filtrage des fournisseurs:', error);
        return { suppliers: [], total: 0 };
    }
}

// Configuration des filtres pour le catalogue
function setupCatalogFilters() {
    const filterInputs = document.querySelectorAll('[data-filter]');
    
    filterInputs.forEach(input => {
        input.addEventListener('change', debounce(applyFilters, 300));
    });
    
    // Filtres de prix
    const priceMin = document.getElementById('priceMin');
    const priceMax = document.getElementById('priceMax');
    
    if (priceMin && priceMax) {
        [priceMin, priceMax].forEach(slider => {
            slider.addEventListener('input', updatePriceFilter);
        });
    }
}

// Configuration des filtres pour les fournisseurs
function setupSupplierFilters() {
    const filterSelects = document.querySelectorAll('#countryFilter, #specialtyFilter, #certificationFilter, #ratingFilter');
    
    filterSelects.forEach(select => {
        select.addEventListener('change', debounce(applySupplierFilters, 300));
    });
}

// Application des filtres produits
async function applyFilters() {
    const filters = {};
    
    // Catégories
    const categoryFilters = document.querySelectorAll('[data-filter="category"]:checked');
    if (categoryFilters.length > 0) {
        filters.categories = Array.from(categoryFilters).map(f => f.value);
    }
    
    // Origine
    const originFilters = document.querySelectorAll('[data-filter="origin"]:checked');
    if (originFilters.length > 0) {
        filters.origins = Array.from(originFilters).map(f => f.value);
    }
    
    // Stock
    const stockFilters = document.querySelectorAll('[data-filter="stock"]:checked');
    if (stockFilters.length > 0) {
        filters.stocks = Array.from(stockFilters).map(f => f.value);
    }
    
    // Prix
    const priceMin = document.getElementById('priceMin');
    const priceMax = document.getElementById('priceMax');
    if (priceMin && priceMax) {
        filters.priceMin = parseFloat(priceMin.value);
        filters.priceMax = parseFloat(priceMax.value);
    }
    
    try {
        showLoadingState();
        const result = await filterProducts(filters);
        
        if (window.renderCatalogProducts) {
            window.renderCatalogProducts(result.products);
        }
        
        hideLoadingState();
    } catch (error) {
        hideLoadingState();
        showNotification('Erreur lors de l\'application des filtres', 'error');
    }
}

// Application des filtres fournisseurs
async function applySupplierFilters() {
    const filters = {};
    
    const countryFilter = document.getElementById('countryFilter');
    const specialtyFilter = document.getElementById('specialtyFilter');
    const certificationFilter = document.getElementById('certificationFilter');
    const ratingFilter = document.getElementById('ratingFilter');
    
    if (countryFilter && countryFilter.value) {
        filters.country = countryFilter.value;
    }
    
    if (specialtyFilter && specialtyFilter.value) {
        filters.specialty = specialtyFilter.value;
    }
    
    if (certificationFilter && certificationFilter.value) {
        filters.certification = certificationFilter.value;
    }
    
    if (ratingFilter && ratingFilter.value) {
        filters.rating = ratingFilter.value;
    }
    
    try {
        showLoadingState();
        const result = await filterSuppliers(filters);
        
        if (window.renderSuppliers) {
            window.renderSuppliers(result.suppliers);
        }
        
        hideLoadingState();
    } catch (error) {
        hideLoadingState();
        showNotification('Erreur lors de l\'application des filtres', 'error');
    }
}

// Mise à jour du filtre de prix
function updatePriceFilter() {
    const priceMin = document.getElementById('priceMin');
    const priceMax = document.getElementById('priceMax');
    const priceDisplay = document.getElementById('priceDisplay');
    
    if (priceMin && priceMax && priceDisplay) {
        const min = parseInt(priceMin.value);
        const max = parseInt(priceMax.value);
        
        // S'assurer que min <= max
        if (min > max) {
            priceMin.value = max;
        }
        if (max < min) {
            priceMax.value = min;
        }
        
        priceDisplay.textContent = `${priceMin.value}€ - ${priceMax.value}€`;
    }
}

// Réinitialisation des filtres
function resetFilters() {
    // Réinitialiser tous les checkboxes
    document.querySelectorAll('[data-filter]').forEach(input => {
        if (input.type === 'checkbox') {
            input.checked = true;
        }
    });
    
    // Réinitialiser les sliders de prix
    const priceMin = document.getElementById('priceMin');
    const priceMax = document.getElementById('priceMax');
    
    if (priceMin && priceMax) {
        priceMin.value = priceMin.min;
        priceMax.value = priceMax.max;
        updatePriceFilter();
    }
    
    // Réappliquer les filtres
    applyFilters();
    
    showNotification('Filtres réinitialisés', 'info');
}

// États de chargement
function showLoadingState() {
    const grids = document.querySelectorAll('.products-grid, .suppliers-grid');
    grids.forEach(grid => {
        grid.classList.add('loading');
        
        // Ajouter des placeholders de chargement
        const loadingItems = Array.from({ length: 6 }, () => createLoadingCard()).join('');
        grid.innerHTML = loadingItems;
    });
}

function hideLoadingState() {
    const grids = document.querySelectorAll('.products-grid, .suppliers-grid');
    grids.forEach(grid => {
        grid.classList.remove('loading');
    });
}

function createLoadingCard() {
    return `
        <div class="product-card card-loading">
            <div class="loading-placeholder" style="height: 200px;"></div>
        </div>
    `;
}

// Gestion du cache
function setupCache() {
    // Nettoyer le cache périodiquement
    setInterval(cleanCache, 5 * 60 * 1000); // Toutes les 5 minutes
}

function cleanCache() {
    const now = Date.now();
    const maxAge = 10 * 60 * 1000; // 10 minutes
    
    for (const [key, value] of apiState.cache.entries()) {
        if (now - value.timestamp > maxAge) {
            apiState.cache.delete(key);
        }
    }
}

function getCacheTimeout(endpoint) {
    // Différents timeouts selon le type d'endpoint
    if (endpoint.includes('/analytics')) return 5 * 60 * 1000; // 5 minutes
    if (endpoint.includes('/products')) return 2 * 60 * 1000; // 2 minutes
    if (endpoint.includes('/suppliers')) return 3 * 60 * 1000; // 3 minutes
    return 1 * 60 * 1000; // 1 minute par défaut
}

// Monitoring de l'API
function setupAPIMonitoring() {
    // Vérifier la santé de l'API toutes les 30 secondes
    setInterval(checkAPIHealth, 30000);
    
    // Surveiller les erreurs
    window.addEventListener('unhandledrejection', function(event) {
        if (event.reason && event.reason.message) {
            apiState.errors.push({
                type: 'unhandled_rejection',
                error: event.reason.message,
                timestamp: Date.now()
            });
        }
    });
}

async function checkAPIHealth() {
    try {
        // Ping simple à l'API
        await fetch('/api/health', { method: 'HEAD', timeout: 5000 });
        
        if (!apiState.isOnline) {
            apiState.isOnline = true;
            showNotification('Connexion rétablie', 'success');
        }
    } catch (error) {
        if (apiState.isOnline) {
            apiState.isOnline = false;
            showNotification('Connexion interrompue - Mode hors ligne activé', 'warning');
        }
    }
}

// Fonctions utilitaires

function generateRequestId() {
    return Date.now().toString(36) + Math.random().toString(36).substr(2, 5);
}

function getAuthToken() {
    return localStorage.getItem('chemspot_token');
}

function setupRequestInterceptors() {
    // Configuration globale des requêtes
    console.log('Intercepteurs de requête configurés');
}

function setupResponseInterceptors() {
    // Gestion globale des réponses
    console.log('Intercepteurs de réponse configurés');
}

// Générateurs de données simulées

function generateProductSpecs(product) {
    return {
        molecular_weight: (Math.random() * 500 + 100).toFixed(2),
        melting_point: `${Math.floor(Math.random() * 200 + 50)}°C`,
        solubility: 'Soluble dans l\'eau',
        stability: 'Stable dans des conditions normales',
        storage: 'Conserver au sec, à température ambiante'
    };
}

function generateProductDocs(product) {
    return [
        { name: 'Certificat d\'analyse (COA)', type: 'pdf', size: '2.3 MB' },
        { name: 'Fiche de données de sécurité (SDS)', type: 'pdf', size: '1.8 MB' },
        { name: 'Certificat BPF', type: 'pdf', size: '0.9 MB' }
    ];
}

function generatePricingTiers(product) {
    const basePrice = parseFloat(product.price);
    return [
        { quantity: '25-100 kg', price: basePrice.toFixed(2), discount: '0%' },
        { quantity: '100-500 kg', price: (basePrice * 0.95).toFixed(2), discount: '5%' },
        { quantity: '500+ kg', price: (basePrice * 0.90).toFixed(2), discount: '10%' }
    ];
}

function generateCertifications(supplier) {
    const certs = ['BPF/GMP', 'ISO 9001:2015', 'ISO 14001'];
    if (supplier.rating > 4.7) certs.push('FDA Approved');
    if (supplier.country === 'France') certs.push('ANSM');
    return certs;
}

function generateSupplierDetails(supplier) {
    return {
        founded: Math.floor(Math.random() * 30) + 1990,
        employees: Math.floor(Math.random() * 500) + 50,
        production_capacity: `${Math.floor(Math.random() * 100) + 10} tonnes/an`,
        export_countries: Math.floor(Math.random() * 20) + 5,
        response_rate: '98%',
        on_time_delivery: '96%'
    };
}

function generateSupplierProducts(supplier) {
    return window.products?.filter(p => p.supplier === supplier.name) || [];
}

function generateQuoteId() {
    return 'QT' + Date.now().toString(36).toUpperCase();
}

function generateOrderId() {
    return 'ORD' + Date.now().toString(36).toUpperCase();
}

function generateTrackingNumber() {
    return 'CS' + Math.random().toString(36).substr(2, 8).toUpperCase();
}

function calculateDeliveryDate() {
    const date = new Date();
    date.setDate(date.getDate() + Math.floor(Math.random() * 14) + 3);
    return date.toISOString();
}

function calculateEstimatedTotal(products) {
    return products.reduce((total, product) => {
        return total + (parseFloat(product.price) * (product.quantity || 1));
    }, 0);
}

function generateUserQuotes() {
    return [
        {
            id: 'QT001',
            status: 'pending',
            created_at: '2024-01-15T10:30:00Z',
            products: ['Paracétamol', 'Lactose'],
            total: 2840.50
        }
    ];
}

function generateUserOrders() {
    return [
        {
            id: 'ORD001',
            status: 'shipped',
            created_at: '2024-01-10T14:20:00Z',
            tracking: 'CS12345678',
            total: 1520.00
        }
    ];
}

function generatePriceTrends() {
    return {
        paracetamol: { trend: 'up', change: '+2.5%' },
        lactose: { trend: 'stable', change: '0%' },
        ibuprofen: { trend: 'down', change: '-1.2%' }
    };
}

function generatePopularProducts() {
    return [
        { name: 'Paracétamol', searches: 1247 },
        { name: 'Lactose', searches: 892 },
        { name: 'Ibuprofène', searches: 743 }
    ];
}

function generateMarketInsights() {
    return {
        top_category: 'Principes Actifs',
        growth_rate: '+12%',
        new_suppliers: 8,
        price_volatility: 'Faible'
    };
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

// Export des fonctions pour utilisation globale
window.ChemSpotAPI = {
    getProducts,
    getProduct,
    getSuppliers,
    requestQuote,
    filterProducts,
    filterSuppliers,
    setupCatalogFilters,
    setupSupplierFilters,
    updatePriceFilter,
    resetFilters,
    applyFilters,
    applySupplierFilters
};

// Alias pour rétrocompatibilité
window.setupCatalogFilters = setupCatalogFilters;
window.setupSupplierFilters = setupSupplierFilters;
window.updatePriceFilter = updatePriceFilter;
window.resetFilters = resetFilters;
window.filterProducts = filterProducts;
window.filterSuppliers = filterSuppliers;
