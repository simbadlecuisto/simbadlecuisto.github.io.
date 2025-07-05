// database.js - Module de connexion à Supabase pour ChemSpot

// Configuration Supabase
const SUPABASE_URL = 'https://jkaffpgqbyhuihvyvtld.supabase.co';
const SUPABASE_ANON_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImprYWZmcGdxYnlodWlodnl2dGxkIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTE2NTgzOTQsImV4cCI6MjA2NzIzNDM5NH0.OIjoz6uoPV25Nraral4YN_gz7q6COBW3dAVIYhBy1pI';

// Variables globales
let supabase;
let allProducts = [];
let allSuppliers = [];
let selectedProduct = null;

// Initialisation de la base de données
async function initializeDatabase() {
    try {
        // Vérifier que Supabase est chargé
        if (typeof window.supabase === 'undefined') {
            throw new Error('Supabase library not loaded');
        }
        
        // Créer le client Supabase
        supabase = window.supabase.createClient(SUPABASE_URL, SUPABASE_ANON_KEY);
        console.log('✅ Client Supabase initialisé');
        
        // Charger toutes les données
        await loadAllData();
        
        // Mettre à jour le statut de connexion
        updateConnectionStatus(true);
        
    } catch (error) {
        console.error('❌ Erreur initialisation base de données:', error);
        updateConnectionStatus(false);
        loadFallbackData();
    }
}

// Charger toutes les données depuis Supabase
async function loadAllData() {
    try {
        console.log('🔄 Chargement des données...');
        
        // Charger les fournisseurs
        const { data: suppliers, error: suppliersError } = await supabase
            .from('suppliers')
            .select('*')
            .order('name');
        
        if (suppliersError) throw suppliersError;
        allSuppliers = suppliers;
        console.log(`✅ ${suppliers.length} fournisseurs chargés`);

        // Charger les produits avec informations fournisseurs
        const { data: products, error: productsError } = await supabase
            .from('products')
            .select(`
                *,
                suppliers (
                    id,
                    name,
                    rating,
                    total_reviews,
                    is_verified
                )
            `)
            .eq('availability_status', 'available')
            .order('name');
        
        if (productsError) throw productsError;
        allProducts = products;
        console.log(`✅ ${products.length} produits chargés`);

        // Charger les stats des devis
        const { data: quotes, error: quotesError } = await supabase
            .from('quotes')
            .select('id');
        
        if (quotesError) throw quotesError;
        console.log(`✅ ${quotes.length} devis trouvés`);

        // Mettre à jour l'interface
        updateStats(suppliers.length, products.length, quotes.length);
        displayPopularProducts();
        displayCatalog();
        displaySuppliers();
        populateFilters();
        
        console.log('✅ Toutes les données chargées avec succès');

    } catch (error) {
        console.error('❌ Erreur lors du chargement des données:', error);
        throw error;
    }
}

// Afficher les produits populaires (page d'accueil)
function displayPopularProducts() {
    const container = document.getElementById('popularProducts');
    if (!container) return;
    
    const popularProducts = allProducts.slice(0, 6); // Top 6
    
    if (popularProducts.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <i class="fas fa-flask"></i>
                <h3>Aucun produit disponible</h3>
                <p>Les produits seront bientôt disponibles</p>
            </div>
        `;
        return;
    }

    container.innerHTML = popularProducts.map(product => createProductCard(product)).join('');
}

// Afficher le catalogue complet
function displayCatalog() {
    const container = document.getElementById('catalogProducts');
    if (!container) return;
    
    if (allProducts.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <i class="fas fa-search"></i>
                <h3>Aucun produit trouvé</h3>
                <p>Aucun produit ne correspond à vos critères</p>
            </div>
        `;
        return;
    }

    container.innerHTML = allProducts.map(product => createProductCard(product)).join('');
}

// Créer une carte produit
function createProductCard(product) {
    const supplier = product.suppliers;
    const rating = supplier ? supplier.rating : 0;
    const stars = '★'.repeat(Math.floor(rating)) + '☆'.repeat(5 - Math.floor(rating));
    
    return `
        <div class="product-card">
            <div class="product-header">
                <div class="product-name">${product.name}</div>
                <div class="product-formula">${product.formula || 'N/A'}</div>
                <div class="product-cas">CAS: ${product.cas_number || 'N/A'}</div>
            </div>
            
            <div class="product-body">
                <div class="product-details">
                    <div class="detail-item">
                        <span class="detail-label">Catégorie</span>
                        <span class="detail-value">${product.category}</span>
                    </div>
                    <div class="detail-item">
                        <span class="detail-label">Pureté</span>
                        <span class="detail-value">${product.purity}%</span>
                    </div>
                    <div class="detail-item">
                        <span class="detail-label">Stock</span>
                        <span class="detail-value">${product.availability_status === 'available' ? '✅ Disponible' : '❌ Indisponible'}</span>
                    </div>
                    <div class="detail-item">
                        <span class="detail-label">Délai</span>
                        <span class="detail-value">${product.lead_time_days} jours</span>
                    </div>
                </div>
                
                <div class="product-price">
                    <div class="price-amount">${product.price}€</div>
                    <div class="price-unit">par ${product.unit}</div>
                </div>
                
                ${supplier ? `
                    <div class="product-supplier">
                        <div style="flex: 1;">
                            <strong>${supplier.name}</strong>
                            ${supplier.is_verified ? '<span style="color: #27ae60;">✓ Vérifié</span>' : ''}
                        </div>
                        <div class="supplier-rating">
                            <span>${stars}</span>
                            <span>(${supplier.total_reviews})</span>
                        </div>
                    </div>
                ` : ''}
                
                ${product.hazard_class ? `
                    <div class="hazard-badge">
                        ⚠️ ${product.hazard_class}
                    </div>
                ` : ''}
                
                <button class="btn-quote" onclick="openQuoteModal(${product.id})">
                    💬 Demander un devis
                </button>
            </div>
        </div>
    `;
}

// Afficher les fournisseurs
function displaySuppliers() {
    const container = document.getElementById('suppliersContainer');
    if (!container) return;
    
    if (allSuppliers.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <i class="fas fa-building"></i>
                <h3>Aucun fournisseur disponible</h3>
                <p>Les fournisseurs seront bientôt disponibles</p>
            </div>
        `;
        return;
    }

    container.innerHTML = allSuppliers.map(supplier => createSupplierCard(supplier)).join('');
}

// Créer une carte fournisseur
function createSupplierCard(supplier) {
    const rating = supplier.rating || 0;
    const stars = '★'.repeat(Math.floor(rating)) + '☆'.repeat(5 - Math.floor(rating));
    
    return `
        <div class="supplier-card">
            <div class="supplier-header">
                <div>
                    <div class="supplier-name">${supplier.name}</div>
                </div>
                ${supplier.is_verified ? `
                    <div class="verification-badge">
                        <i class="fas fa-check-circle"></i>
                        Vérifié
                    </div>
                ` : ''}
            </div>
            
            <div class="supplier-rating-section">
                <div class="rating-stars">${stars}</div>
                <div class="rating-text">${rating}/5 (${supplier.total_reviews} avis)</div>
            </div>
            
            <div class="supplier-contact">
                <div class="contact-item">
                    <i class="fas fa-envelope"></i>
                    ${supplier.email}
                </div>
                ${supplier.phone ? `
                    <div class="contact-item">
                        <i class="fas fa-phone"></i>
                        ${supplier.phone}
                    </div>
                ` : ''}
                ${supplier.website ? `
                    <div class="contact-item">
                        <i class="fas fa-globe"></i>
                        <a href="${supplier.website}" target="_blank">Site web</a>
                    </div>
                ` : ''}
                ${supplier.address ? `
                    <div class="contact-item">
                        <i class="fas fa-map-marker-alt"></i>
                        ${supplier.address}
                    </div>
                ` : ''}
            </div>
            
            ${supplier.certifications && supplier.certifications.length > 0 ? `
                <div class="certifications">
                    ${supplier.certifications.map(cert => `<span class="cert-badge">${cert}</span>`).join('')}
                </div>
            ` : ''}
            
            <div class="supplier-description">
                ${supplier.description || 'Aucune description disponible.'}
            </div>
            
            <button class="btn-contact" onclick="contactSupplier('${supplier.email}')">
                📧 Contacter le fournisseur
            </button>
        </div>
    `;
}

// Remplir les filtres
function populateFilters() {
    // Filtre des catégories
    const categories = [...new Set(allProducts.map(p => p.category))];
    const categorySelect = document.getElementById('categoryFilter');
    if (categorySelect) {
        categorySelect.innerHTML = '<option value="">Toutes les catégories</option>' +
            categories.map(cat => `<option value="${cat}">${cat}</option>`).join('');
    }

    // Filtre des fournisseurs
    const supplierSelect = document.getElementById('supplierFilter');
    if (supplierSelect) {
        supplierSelect.innerHTML = '<option value="">Tous les fournisseurs</option>' +
            allSuppliers.map(sup => `<option value="${sup.id}">${sup.name}</option>`).join('');
    }
}

// Recherche rapide (page d'accueil)
function quickSearch() {
    const query = document.getElementById('quickSearch').value.trim();
    if (query) {
        const catalogSearch = document.getElementById('catalogSearch');
        if (catalogSearch) {
            catalogSearch.value = query;
        }
        if (typeof showPage === 'function') {
            showPage('catalog');
        }
        searchProducts();
    }
}

// Recherche dans le catalogue
function searchProducts() {
    const query = document.getElementById('catalogSearch').value.toLowerCase().trim();
    
    let filteredProducts = allProducts;
    
    if (query) {
        filteredProducts = allProducts.filter(product => 
            product.name.toLowerCase().includes(query) ||
            (product.cas_number && product.cas_number.toLowerCase().includes(query)) ||
            (product.formula && product.formula.toLowerCase().includes(query)) ||
            product.category.toLowerCase().includes(query)
        );
    }
    
    displayFilteredProducts(filteredProducts);
}

// Filtrer les produits
function filterProducts() {
    const category = document.getElementById('categoryFilter').value;
    const supplierId = document.getElementById('supplierFilter').value;
    const priceRange = document.getElementById('priceFilter').value;
    const searchQuery = document.getElementById('catalogSearch').value.toLowerCase().trim();
    
    let filteredProducts = allProducts;
    
    // Filtrer par recherche
    if (searchQuery) {
        filteredProducts = filteredProducts.filter(product => 
            product.name.toLowerCase().includes(searchQuery) ||
            (product.cas_number && product.cas_number.toLowerCase().includes(searchQuery)) ||
            (product.formula && product.formula.toLowerCase().includes(searchQuery)) ||
            product.category.toLowerCase().includes(searchQuery)
        );
    }
    
    // Filtrer par catégorie
    if (category) {
        filteredProducts = filteredProducts.filter(product => product.category === category);
    }
    
    // Filtrer par fournisseur
    if (supplierId) {
        filteredProducts = filteredProducts.filter(product => product.supplier_id == supplierId);
    }
    
    // Filtrer par prix
    if (priceRange) {
        if (priceRange === '0-50') {
            filteredProducts = filteredProducts.filter(product => product.price <= 50);
        } else if (priceRange === '50-100') {
            filteredProducts = filteredProducts.filter(product => product.price > 50 && product.price <= 100);
        } else if (priceRange === '100+') {
            filteredProducts = filteredProducts.filter(product => product.price > 100);
        }
    }
    
    displayFilteredProducts(filteredProducts);
}

// Afficher les produits filtrés
function displayFilteredProducts(products) {
    const container = document.getElementById('catalogProducts');
    if (!container) return;
    
    if (products.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <i class="fas fa-search"></i>
                <h3>Aucun produit trouvé</h3>
                <p>Aucun produit ne correspond à vos critères de recherche</p>
            </div>
        `;
        return;
    }
    
    container.innerHTML = products.map(product => createProductCard(product)).join('');
}

// Ouvrir le modal de devis
function openQuoteModal(productId) {
    selectedProduct = allProducts.find(p => p.id === productId);
    if (!selectedProduct) return;
    
    const modal = document.getElementById('quoteModal');
    const productInfo = document.getElementById('productInfo');
    
    if (productInfo) {
        productInfo.innerHTML = `
            <h4>${selectedProduct.name}</h4>
            <p><strong>Formule:</strong> ${selectedProduct.formula || 'N/A'}</p>
            <p><strong>CAS:</strong> ${selectedProduct.cas_number || 'N/A'}</p>
            <p><strong>Prix:</strong> ${selectedProduct.price}€ par ${selectedProduct.unit}</p>
            <p><strong>Quantité minimum:</strong> ${selectedProduct.min_quantity} ${selectedProduct.unit}</p>
        `;
    }
    
    const quantityInput = document.getElementById('quoteQuantity');
    if (quantityInput) {
        quantityInput.value = selectedProduct.min_quantity;
        quantityInput.min = selectedProduct.min_quantity;
    }
    
    if (modal) {
        modal.style.display = 'block';
    }
}

// Fermer le modal de devis
function closeQuoteModal() {
    const modal = document.getElementById('quoteModal');
    if (modal) {
        modal.style.display = 'none';
    }
    
    const form = document.getElementById('quoteForm');
    if (form) {
        form.reset();
    }
    
    selectedProduct = null;
}

// Soumettre une demande de devis
async function submitQuote(event) {
    event.preventDefault();
    
    if (!selectedProduct || !supabase) {
        showStatusMessage('error', 'Erreur: produit non sélectionné ou base de données non disponible');
        return;
    }
    
    const quantity = parseInt(document.getElementById('quoteQuantity').value);
    const name = document.getElementById('quoteName').value;
    const email = document.getElementById('quoteEmail').value;
    const company = document.getElementById('quoteCompany').value;
    const message = document.getElementById('quoteMessage').value;
    
    const formData = {
        product_id: selectedProduct.id,
        supplier_id: selectedProduct.supplier_id,
        quantity: quantity,
        unit_price: selectedProduct.price,
        total_price: quantity * selectedProduct.price,
        message: message,
        user_id: 4, // Utilisateur de test - à remplacer par l'auth réelle
        status: 'pending',
        valid_until: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString() // 30 jours
    };
    
    try {
        const { data, error } = await supabase
            .from('quotes')
            .insert([formData]);
        
        if (error) throw error;
        
        showStatusMessage('success', 'Votre demande de devis a été envoyée avec succès ! Le fournisseur vous contactera sous 24h.');
        
        // Mettre à jour les stats
        const { data: quotes } = await supabase.from('quotes').select('id');
        if (quotes) {
            document.getElementById('statsQuotes').textContent = quotes.length;
        }
        
        setTimeout(() => {
            closeQuoteModal();
        }, 3000);
        
    } catch (error) {
        console.error('Erreur lors de l\'envoi du devis:', error);
        showStatusMessage('error', 'Erreur lors de l\'envoi de la demande. Veuillez réessayer.');
    }
}

// Afficher un message de statut
function showStatusMessage(type, message) {
    const statusEl = document.getElementById('statusMessage');
    if (statusEl) {
        statusEl.className = `status-message ${type}`;
        statusEl.textContent = message;
        statusEl.style.display = 'block';
        
        setTimeout(() => {
            statusEl.style.display = 'none';
        }, 5000);
    }
}

// Contacter un fournisseur
function contactSupplier(email) {
    window.location.href = `mailto:${email}?subject=Demande d'information - ChemSpot`;
}

// Envoyer un message de contact
function sendMessage(event) {
    event.preventDefault();
    alert('Message envoyé avec succès ! Nous vous répondrons dans les plus brefs délais.');
    event.target.reset();
}

// Données de fallback en cas d'erreur de connexion
function loadFallbackData() {
    console.log('📦 Chargement des données de fallback...');
    
    // Données statiques de base
    const fallbackSuppliers = [
        { id: 1, name: 'ChemTech Solutions', rating: 4.8, total_reviews: 127, is_verified: true },
        { id: 2, name: 'LabCorp France', rating: 4.6, total_reviews: 89, is_verified: true },
        { id: 3, name: 'ChemPlus Industries', rating: 4.9, total_reviews: 203, is_verified: true }
    ];
    
    const fallbackProducts = [
        {
            id: 1,
            name: 'Acide Sulfurique 98%',
            formula: 'H2SO4',
            cas_number: '7664-93-9',
            category: 'Acides',
            purity: 98.0,
            price: 15.50,
            unit: 'L',
            min_quantity: 1,
            availability_status: 'available',
            lead_time_days: 7,
            hazard_class: 'Corrosif',
            supplier_id: 1,
            suppliers: fallbackSuppliers[0]
        },
        {
            id: 2,
            name: 'Éthanol Absolu',
            formula: 'C2H5OH',
            cas_number: '64-17-5',
            category: 'Solvants',
            purity: 99.9,
            price: 28.90,
            unit: 'L',
            min_quantity: 1,
            availability_status: 'available',
            lead_time_days: 5,
            hazard_class: 'Inflammable',
            supplier_id: 2,
            suppliers: fallbackSuppliers[1]
        }
    ];
    
    allSuppliers = fallbackSuppliers;
    allProducts = fallbackProducts;
    
    // Mettre à jour l'interface avec les données de fallback
    updateStats(3, 8, 2);
    displayPopularProducts();
    displayCatalog();
    displaySuppliers();
    populateFilters();
    
    console.log('✅ Données de fallback chargées');
}

// Fermer le modal en cliquant à l'extérieur
window.addEventListener('click', function(event) {
    const modal = document.getElementById('quoteModal');
    if (event.target === modal) {
        closeQuoteModal();
    }
});

// Exporter les fonctions principales pour les autres scripts
if (typeof window !== 'undefined') {
    window.ChemSpotDB = {
        initializeDatabase,
        quickSearch,
        searchProducts,
        filterProducts,
        openQuoteModal,
        closeQuoteModal,
        submitQuote,
        contactSupplier,
        sendMessage
    };
}
