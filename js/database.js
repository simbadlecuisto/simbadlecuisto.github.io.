// database.js - Module de connexion à Supabase pour ChemSpot CORRIGÉ

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
        
        // ✅ CORRECTION 1: Charger depuis pharma_products (pas products)
        const { data: products, error: productsError } = await supabase
            .from('pharma_products')  // ✅ Table qui contient les vraies données
            .select('*')
            .order('name');
        
        if (productsError) {
            console.error('Erreur produits:', productsError);
            throw productsError;
        }
        
        allProducts = products || [];
        console.log(`✅ ${allProducts.length} produits chargés depuis pharma_products`);

        // ✅ CORRECTION 2: Charger les fournisseurs (même table)
        const { data: suppliers, error: suppliersError } = await supabase
            .from('suppliers')
            .select('*')
            .order('company_name');  // ✅ Utiliser company_name au lieu de name
        
        if (suppliersError) {
            console.error('Erreur fournisseurs:', suppliersError);
            // Ne pas faire échouer si pas de fournisseurs
        }
        
        allSuppliers = suppliers || [];
        console.log(`✅ ${allSuppliers.length} fournisseurs chargés`);

        // Charger les stats des devis
        const { data: quotes, error: quotesError } = await supabase
            .from('quotes')
            .select('id');
        
        if (quotesError) {
            console.error('Erreur devis:', quotesError);
        }
        
        const quotesCount = quotes?.length || 0;
        console.log(`✅ ${quotesCount} devis trouvés`);

        // Mettre à jour l'interface
        updateStats(allSuppliers.length, allProducts.length, quotesCount);
        displayPopularProducts();
        displayCatalog();
        displaySuppliers();
        populateFilters();
        
        console.log('✅ Toutes les données chargées avec succès');
        console.log('📊 Résumé:', {
            produits: allProducts.length,
            fournisseurs: allSuppliers.length,
            devis: quotesCount
        });

    } catch (error) {
        console.error('❌ Erreur lors du chargement des données:', error);
        throw error;
    }
}

// ✅ CORRECTION 3: Fonction updateStats améliorée
function updateStats(suppliers, products, quotes) {
    console.log('📊 Mise à jour stats:', { suppliers, products, quotes });
    
    // Mettre à jour tous les éléments possibles
    const elements = [
        { ids: ['statsSuppliers', 'supplier-count', 'total-suppliers'], value: suppliers },
        { ids: ['statsProducts', 'product-count', 'total-products'], value: products },
        { ids: ['statsQuotes', 'quote-count', 'total-quotes'], value: quotes }
    ];
    
    elements.forEach(({ ids, value }) => {
        ids.forEach(id => {
            const element = document.getElementById(id);
            if (element) {
                // Animation du compteur
                animateCounter(element, value);
            }
        });
    });
}

// ✅ Animation compteur améliorée
function animateCounter(element, targetValue) {
    const startValue = 0;
    const duration = 1000; // 1 seconde
    const startTime = performance.now();
    
    function updateCounter(currentTime) {
        const elapsed = currentTime - startTime;
        const progress = Math.min(elapsed / duration, 1);
        
        const currentValue = Math.floor(startValue + (targetValue - startValue) * progress);
        element.textContent = currentValue;
        
        if (progress < 1) {
            requestAnimationFrame(updateCounter);
        }
    }
    
    requestAnimationFrame(updateCounter);
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
                <h3>Chargement des produits...</h3>
                <p>Les produits seront affichés dans quelques instants</p>
            </div>
        `;
        return;
    }

    container.innerHTML = popularProducts.map(product => createProductCard(product)).join('');
    console.log(`📦 ${popularProducts.length} produits populaires affichés`);
}

// Afficher le catalogue complet
function displayCatalog() {
    const container = document.getElementById('catalogProducts');
    if (!container) return;
    
    if (allProducts.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <i class="fas fa-search"></i>
                <h3>Chargement du catalogue...</h3>
                <p>Les produits sont en cours de chargement</p>
            </div>
        `;
        return;
    }

    container.innerHTML = allProducts.map(product => createProductCard(product)).join('');
    console.log(`📦 ${allProducts.length} produits du catalogue affichés`);
}

// ✅ CORRECTION 4: Créer une carte produit compatible avec pharma_products
function createProductCard(product) {
    // Adapter les champs selon la structure de pharma_products
    const productName = product.name || 'Produit sans nom';
    const productPrice = product.price || 'Prix non disponible';
    const productCategory = product.category || 'Non catégorisé';
    const productDescription = product.description || 'Aucune description disponible';
    const productStock = product.stock || 0;
    const productDosage = product.dosage || 'N/A';
    const productManufacturer = product.manufacturer || 'Fabricant non spécifié';
    const requiresPrescription = product.requires_prescription ? '🔒 Sur ordonnance' : '✅ Libre';
    
    return `
        <div class="product-card">
            <div class="product-header">
                <div class="product-name">${productName}</div>
                <div class="product-category">${productCategory}</div>
                <div class="prescription-status">${requiresPrescription}</div>
            </div>
            
            <div class="product-body">
                <div class="product-details">
                    <div class="detail-item">
                        <span class="detail-label">Dosage</span>
                        <span class="detail-value">${productDosage}</span>
                    </div>
                    <div class="detail-item">
                        <span class="detail-label">Stock</span>
                        <span class="detail-value">${productStock > 0 ? '✅ Disponible' : '❌ Rupture'}</span>
                    </div>
                    <div class="detail-item">
                        <span class="detail-label">Fabricant</span>
                        <span class="detail-value">${productManufacturer}</span>
                    </div>
                </div>
                
                <div class="product-description">
                    <p>${productDescription.substring(0, 100)}${productDescription.length > 100 ? '...' : ''}</p>
                </div>
                
                <div class="product-price">
                    <div class="price-amount">${productPrice}€</div>
                    <div class="price-unit">par unité</div>
                </div>
                
                <div class="product-actions">
                    <button class="btn-quote" onclick="openQuoteModal(${product.id})">
                        💬 Demander un devis
                    </button>
                    <button class="btn-details" onclick="viewProductDetails(${product.id})">
                        👁️ Voir détails
                    </button>
                </div>
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
                <h3>Import des fournisseurs en cours...</h3>
                <p>Les fournisseurs seront bientôt disponibles</p>
                <button onclick="importSampleSuppliers()" class="btn btn-primary">
                    📥 Importer des fournisseurs de test
                </button>
            </div>
        `;
        return;
    }

    container.innerHTML = allSuppliers.map(supplier => createSupplierCard(supplier)).join('');
    console.log(`🏢 ${allSuppliers.length} fournisseurs affichés`);
}

// ✅ CORRECTION 5: Créer une carte fournisseur compatible
function createSupplierCard(supplier) {
    const companyName = supplier.company_name || supplier.name || 'Fournisseur';
    const country = supplier.country || 'Pays non spécifié';
    const speciality = supplier.speciality || supplier.description || 'Spécialité non spécifiée';
    const certifications = supplier.certifications || 'Non spécifiées';
    const contact = supplier.contact || supplier.email || 'Contact non disponible';
    const website = supplier.website || '';
    const notes = supplier.notes || 'Aucune note disponible';
    
    return `
        <div class="supplier-card">
            <div class="supplier-header">
                <div class="supplier-name">${companyName}</div>
                <div class="supplier-country">📍 ${country}</div>
            </div>
            
            <div class="supplier-speciality">
                <strong>Spécialité:</strong> ${speciality}
            </div>
            
            <div class="supplier-certifications">
                <strong>Certifications:</strong> ${certifications}
            </div>
            
            <div class="supplier-contact">
                <div class="contact-item">
                    <i class="fas fa-envelope"></i>
                    ${contact}
                </div>
                ${website ? `
                    <div class="contact-item">
                        <i class="fas fa-globe"></i>
                        <a href="${website}" target="_blank">Site web</a>
                    </div>
                ` : ''}
            </div>
            
            <div class="supplier-notes">
                ${notes}
            </div>
            
            <div class="supplier-actions">
                <button class="btn-contact" onclick="contactSupplier('${contact}')">
                    📧 Contacter
                </button>
                <button class="btn-profile" onclick="viewSupplierProfile(${supplier.id})">
                    👁️ Voir profil
                </button>
            </div>
        </div>
    `;
}

// ✅ CORRECTION 6: Fonction d'import de fournisseurs de test
async function importSampleSuppliers() {
    if (!supabase) {
        alert('Base de données non disponible');
        return;
    }
    
    const sampleSuppliers = [
        {
            company_name: "ChemTech Solutions France",
            country: "France", 
            speciality: "APIs et excipients pharmaceutiques",
            website: "https://www.chemtech.fr",
            certifications: "GMP, ISO 9001, FDA",
            contact: "contact@chemtech.fr",
            notes: "Fournisseur français spécialisé dans les matières premières pharmaceutiques"
        },
        {
            company_name: "EuroPharma Supply",
            country: "Allemagne",
            speciality: "Principes actifs de spécialité",
            website: "https://www.europharma.de",
            certifications: "GMP, ISO 9001, EMA",
            contact: "info@europharma.de",
            notes: "Leader européen dans la fourniture d'APIs innovants"
        },
        {
            company_name: "MedChem International",
            country: "Suisse",
            speciality: "Chimie fine pharmaceutique",
            website: "https://www.medchem.ch",
            certifications: "GMP, ISO 13485, Swissmedic",
            contact: "sales@medchem.ch",
            notes: "Synthèse sur mesure et production d'APIs de haute qualité"
        }
    ];
    
    try {
        const { data, error } = await supabase
            .from('suppliers')
            .insert(sampleSuppliers)
            .select();
        
        if (error) throw error;
        
        console.log('✅ Fournisseurs de test importés:', data);
        
        // Recharger les données
        await loadAllData();
        
        alert('✅ Fournisseurs de test importés avec succès !');
        
    } catch (error) {
        console.error('❌ Erreur import fournisseurs:', error);
        alert('❌ Erreur lors de l\'import des fournisseurs');
    }
}

// Remplir les filtres
function populateFilters() {
    // Filtre des catégories
    const categories = [...new Set(allProducts.map(p => p.category))].filter(Boolean);
    const categorySelect = document.getElementById('categoryFilter');
    if (categorySelect && categories.length > 0) {
        categorySelect.innerHTML = '<option value="">Toutes les catégories</option>' +
            categories.map(cat => `<option value="${cat}">${cat}</option>`).join('');
    }

    // Filtre des fournisseurs
    const supplierSelect = document.getElementById('supplierFilter');
    if (supplierSelect && allSuppliers.length > 0) {
        supplierSelect.innerHTML = '<option value="">Tous les fournisseurs</option>' +
            allSuppliers.map(sup => `<option value="${sup.id}">${sup.company_name || sup.name}</option>`).join('');
    }
}

// ✅ CORRECTION 7: Recherche améliorée
function searchProducts() {
    const searchInput = document.getElementById('catalogSearch') || document.getElementById('searchInput');
    if (!searchInput) return;
    
    const query = searchInput.value.toLowerCase().trim();
    
    let filteredProducts = allProducts;
    
    if (query) {
        filteredProducts = allProducts.filter(product => 
            (product.name && product.name.toLowerCase().includes(query)) ||
            (product.category && product.category.toLowerCase().includes(query)) ||
            (product.manufacturer && product.manufacturer.toLowerCase().includes(query)) ||
            (product.description && product.description.toLowerCase().includes(query))
        );
        
        console.log(`🔍 Recherche "${query}": ${filteredProducts.length} résultats`);
    }
    
    displayFilteredProducts(filteredProducts);
}

// Recherche rapide (page d'accueil)
function quickSearch() {
    const query = document.getElementById('quickSearch');
    if (query && query.value.trim()) {
        const catalogSearch = document.getElementById('catalogSearch');
        if (catalogSearch) {
            catalogSearch.value = query.value;
        }
        if (typeof showPage === 'function') {
            showPage('catalog');
        }
        searchProducts();
    }
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
                <button onclick="loadAllData()" class="btn btn-primary">
                    🔄 Actualiser
                </button>
            </div>
        `;
        return;
    }
    
    container.innerHTML = products.map(product => createProductCard(product)).join('');
    console.log(`📦 ${products.length} produits filtrés affichés`);
}

// ✅ CORRECTION 8: Statut de connexion
function updateConnectionStatus(connected) {
    const statusDiv = document.createElement('div');
    statusDiv.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 12px 20px;
        border-radius: 6px;
        color: white;
        font-weight: 600;
        z-index: 10000;
        transition: all 0.3s ease;
        ${connected ? 'background: #10b981;' : 'background: #ef4444;'}
    `;
    statusDiv.textContent = connected ? '✅ Base de données connectée' : '❌ Erreur de connexion';
    
    document.body.appendChild(statusDiv);
    
    setTimeout(() => {
        statusDiv.style.opacity = '0';
        setTimeout(() => {
            if (document.body.contains(statusDiv)) {
                document.body.removeChild(statusDiv);
            }
        }, 300);
    }, 3000);
}

// Fonctions modales et interactions (garder les existantes)
function openQuoteModal(productId) {
    selectedProduct = allProducts.find(p => p.id === productId);
    if (!selectedProduct) return;
    
    const modal = document.getElementById('quoteModal');
    const productInfo = document.getElementById('productInfo');
    
    if (productInfo) {
        productInfo.innerHTML = `
            <h4>${selectedProduct.name}</h4>
            <p><strong>Catégorie:</strong> ${selectedProduct.category || 'N/A'}</p>
            <p><strong>Dosage:</strong> ${selectedProduct.dosage || 'N/A'}</p>
            <p><strong>Prix:</strong> ${selectedProduct.price}€</p>
            <p><strong>Fabricant:</strong> ${selectedProduct.manufacturer || 'N/A'}</p>
        `;
    }
    
    if (modal) {
        modal.style.display = 'block';
    }
}

function closeQuoteModal() {
    const modal = document.getElementById('quoteModal');
    if (modal) {
        modal.style.display = 'none';
    }
    selectedProduct = null;
}

function contactSupplier(email) {
    window.location.href = `mailto:${email}?subject=Demande d'information - ChemSpot`;
}

function viewProductDetails(productId) {
    const product = allProducts.find(p => p.id === productId);
    if (product) {
        alert(`Détails du produit:\n\n${product.name}\nCatégorie: ${product.category}\nPrix: ${product.price}€\nDescription: ${product.description}`);
    }
}

function viewSupplierProfile(supplierId) {
    const supplier = allSuppliers.find(s => s.id === supplierId);
    if (supplier) {
        alert(`Profil fournisseur:\n\n${supplier.company_name || supplier.name}\nPays: ${supplier.country}\nSpécialité: ${supplier.speciality}`);
    }
}

// Données de fallback améliorées
function loadFallbackData() {
    console.log('📦 Chargement des données de fallback...');
    
    allProducts = [
        {
            id: 1,
            name: 'Paracétamol USP',
            category: 'Analgésique',
            price: 15.20,
            dosage: '500mg',
            manufacturer: 'PharmaPlus',
            description: 'Principe actif analgésique et antipyrétique de qualité USP',
            stock: 850,
            requires_prescription: false
        },
        {
            id: 2,
            name: 'Aspirine API 99%',
            category: 'Analgésique',
            price: 22.40,
            dosage: '300mg',
            manufacturer: 'MediCorp',
            description: 'Acide acétylsalicylique pureté pharmaceutique',
            stock: 720,
            requires_prescription: false
        }
    ];
    
    allSuppliers = [
        {
            id: 1,
            company_name: 'ChemTech Solutions',
            country: 'France',
            speciality: 'APIs et excipients',
            contact: 'contact@chemtech.fr'
        }
    ];
    
    updateStats(1, 2, 0);
    displayPopularProducts();
    displayCatalog();
    displaySuppliers();
    
    console.log('✅ Données de fallback chargées');
}

// Rendre les fonctions disponibles globalement
if (typeof window !== 'undefined') {
    window.ChemSpotDB = {
        initializeDatabase,
        quickSearch,
        searchProducts,
        openQuoteModal,
        closeQuoteModal,
        contactSupplier,
        importSampleSuppliers,
        loadAllData,
        getAllProducts: () => allProducts,
        getAllSuppliers: () => allSuppliers
    };
    
    // Rendre les fonctions principales accessibles
    window.performSearch = searchProducts;
    window.openQuoteModal = openQuoteModal;
    window.closeQuoteModal = closeQuoteModal;
    window.contactSupplier = contactSupplier;
    window.importSampleSuppliers = importSampleSuppliers;
}
