// database.js - Module de connexion à Supabase pour ChemSpot
// VERSION CORRIGÉE POUR TES VRAIES COLONNES SUPABASE

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

// Charger toutes les données depuis Supabase - ADAPTÉ À TES COLONNES
async function loadAllData() {
    try {
        console.log('🔄 Chargement des données...');
        
        // Charger les fournisseurs - COLONNES RÉELLES
        const { data: suppliers, error: suppliersError } = await supabase
            .from('suppliers')
            .select('id, name, country, speciality, website')
            .order('name');
        
        if (suppliersError) throw suppliersError;
        allSuppliers = suppliers || [];
        console.log(`✅ ${allSuppliers.length} fournisseurs chargés`);

        // Charger les produits avec informations fournisseurs
       // Charger les produits avec informations fournisseurs
const { data: products, error: productsError } = await supabase
    .from('products')
    .select(`
        *,
        supplier_id (  // Changez 'suppliers' par le nom exact de votre colonne de relation
            id,
            name,
            country,
            speciality,
            website
        )
    `)
    .order('name');
        
        if (productsError) throw productsError;
        allProducts = products || [];
        console.log(`✅ ${allProducts.length} produits chargés`);

        // Charger les stats des devis
        const { data: quotes, error: quotesError } = await supabase
            .from('quotes')
            .select('id');
        
        if (quotesError) throw quotesError;
        console.log(`✅ ${quotes?.length || 0} devis trouvés`);

        // Mettre à jour l'interface
        updateStats(allSuppliers.length, allProducts.length, quotes?.length || 0);
        displaySuppliers();
        populateFilters();
        
        console.log('✅ Toutes les données chargées avec succès');

    } catch (error) {
        console.error('❌ Erreur lors du chargement des données:', error);
        throw error;
    }
}

// Afficher les fournisseurs - ADAPTÉ AUX VRAIES COLONNES
function displaySuppliers() {
    const container = document.getElementById('suppliersContainer');
    if (!container) {
        console.log('⚠️ Container suppliersContainer non trouvé');
        return;
    }
    
    if (allSuppliers.length === 0) {
        container.innerHTML = `
            <div class="empty-state" style="grid-column: 1/-1; text-align: center; padding: 3rem;">
                <i class="fas fa-building" style="font-size: 3rem; color: #cbd5e0; margin-bottom: 1rem;"></i>
                <h3 style="color: #4a5568; margin-bottom: 0.5rem;">Aucun fournisseur disponible</h3>
                <p style="color: #718096;">Les fournisseurs seront bientôt disponibles</p>
            </div>
        `;
        return;
    }

    console.log(`🔄 Affichage de ${allSuppliers.length} fournisseurs`);
    container.innerHTML = allSuppliers.map(supplier => createSupplierCard(supplier)).join('');
    container.style.display = 'grid';
}

// Créer une carte fournisseur - ADAPTÉ AUX VRAIES COLONNES
function createSupplierCard(supplier) {
    // Fonction pour obtenir emoji pays
    function getCountryFlag(country) {
        const flags = {
            'France': '🇫🇷', 'Allemagne': '🇩🇪', 'Inde': '🇮🇳', 'Chine': '🇨🇳',
            'Italie': '🇮🇹', 'Espagne': '🇪🇸', 'Pays-Bas': '🇳🇱', 'Belgique': '🇧🇪',
            'Suisse': '🇨🇭', 'Pologne': '🇵🇱', 'USA': '🇺🇸', 'États-Unis': '🇺🇸',
            'Japon': '🇯🇵', 'Corée': '🇰🇷', 'Brésil': '🇧🇷'
        };
        return flags[country] || '🌍';
    }
    
    return `
        <div class="supplier-card">
            <div class="supplier-header">
                <div>
                    <div class="supplier-name">${supplier.name || 'Nom non disponible'}</div>
                    <div class="supplier-id">#${supplier.id}</div>
                </div>
            </div>
            
            <div class="supplier-info">
                ${supplier.country ? `
                    <div class="info-item">
                        <span class="country-flag">${getCountryFlag(supplier.country)}</span>
                        <strong>Pays:</strong> ${supplier.country}
                    </div>
                ` : ''}
                
                ${supplier.website ? `
                    <div class="info-item">
                        <i class="fas fa-globe"></i>
                        <strong>Site web:</strong> <a href="${supplier.website}" target="_blank">${supplier.website}</a>
                    </div>
                ` : ''}
                
                ${supplier.speciality ? `
                    <div class="info-item">
                        <i class="fas fa-tags"></i>
                        <strong>Spécialité:</strong> ${supplier.speciality}
                    </div>
                ` : ''}
            </div>
            
            ${supplier.speciality ? `
                <div class="specialties">
                    <span class="specialty-tag">${supplier.speciality}</span>
                </div>
            ` : ''}
            
            <div class="supplier-actions">
                <button class="btn btn-primary" onclick="contactSupplier('${supplier.name}', ${supplier.id})">
                    <i class="fas fa-envelope"></i> Contacter
                </button>
                ${supplier.website ? `
                    <button class="btn btn-outline" onclick="visitWebsite('${supplier.website}')">
                        <i class="fas fa-external-link-alt"></i> Site web
                    </button>
                ` : ''}
                <button class="btn btn-outline" onclick="viewSupplierProducts(${supplier.id})">
                    <i class="fas fa-eye"></i> Voir produits
                </button>
            </div>
        </div>
    `;
}

// Remplir les filtres - ADAPTÉ AUX VRAIES COLONNES
function populateFilters() {
    // Filtre des pays
    const countries = [...new Set(allSuppliers.map(s => s.country).filter(Boolean))];
    const countrySelect = document.getElementById('countryFilter');
    if (countrySelect) {
        countrySelect.innerHTML = '<option value="">Tous les pays</option>' +
            countries.map(country => `<option value="${country}">${country}</option>`).join('');
    }

    // Filtre des spécialités
    const specialties = [...new Set(allSuppliers.map(s => s.speciality).filter(Boolean))];
    const specialtySelect = document.getElementById('specialtyFilter');
    if (specialtySelect) {
        specialtySelect.innerHTML = '<option value="">Toutes les spécialités</option>' +
            specialties.map(specialty => `<option value="${specialty}">${specialty}</option>`).join('');
    }

    // Filtre des catégories produits
    const categories = [...new Set(allProducts.map(p => p.category).filter(Boolean))];
    const categorySelect = document.getElementById('categoryFilter');
    if (categorySelect) {
        categorySelect.innerHTML = '<option value="">Toutes les catégories</option>' +
            categories.map(cat => `<option value="${cat}">${cat}</option>`).join('');
    }
}

// Fonction de filtrage des fournisseurs
function filterSuppliers() {
    const countryFilter = document.getElementById('countryFilter');
    const specialtyFilter = document.getElementById('specialtyFilter');
    
    if (!countryFilter || !specialtyFilter) return;
    
    const country = countryFilter.value;
    const specialty = specialtyFilter.value;

    let filteredSuppliers = allSuppliers.filter(supplier => {
        const matchCountry = !country || supplier.country === country;
        const matchSpecialty = !specialty || supplier.speciality === specialty;
        return matchCountry && matchSpecialty;
    });

    // Mettre à jour l'affichage
    displayFilteredSuppliers(filteredSuppliers);
}

// Afficher les fournisseurs filtrés
function displayFilteredSuppliers(suppliers) {
    const container = document.getElementById('suppliersContainer');
    const countEl = document.getElementById('resultsCount');
    
    if (!container) return;
    
    // Mettre à jour le compteur
    if (countEl) {
        countEl.textContent = `${suppliers.length} fournisseur(s) trouvé(s)`;
    }
    
    if (suppliers.length === 0) {
        container.innerHTML = `
            <div class="empty-state" style="grid-column: 1/-1; text-align: center; padding: 3rem;">
                <i class="fas fa-search" style="font-size: 3rem; color: #cbd5e0; margin-bottom: 1rem;"></i>
                <h3 style="color: #4a5568; margin-bottom: 0.5rem;">Aucun fournisseur trouvé</h3>
                <p style="color: #718096;">Aucun fournisseur ne correspond à vos critères</p>
            </div>
        `;
        return;
    }

    container.innerHTML = suppliers.map(supplier => createSupplierCard(supplier)).join('');
    container.style.display = 'grid';
}

// Réinitialiser les filtres
function resetFilters() {
    const countryFilter = document.getElementById('countryFilter');
    const specialtyFilter = document.getElementById('specialtyFilter');
    
    if (countryFilter) countryFilter.value = '';
    if (specialtyFilter) specialtyFilter.value = '';
    
    displaySuppliers();
    
    const countEl = document.getElementById('resultsCount');
    if (countEl) {
        countEl.textContent = `${allSuppliers.length} fournisseur(s) trouvé(s)`;
    }
}

// Actions sur les fournisseurs
function contactSupplier(supplierName, supplierId) {
    const subject = encodeURIComponent(`Demande de renseignements - ${supplierName} via ChemSpot`);
    const body = encodeURIComponent(`Bonjour,\n\nJe vous contacte via la plateforme ChemSpot concernant vos produits.\n\nFournisseur ID: ${supplierId}\n\nCordialement`);
    
    window.open(`mailto:?subject=${subject}&body=${body}`);
}

function visitWebsite(url) {
    if (!url.startsWith('http://') && !url.startsWith('https://')) {
        url = 'https://' + url;
    }
    window.open(url, '_blank');
}

function viewSupplierProducts(supplierId) {
    // Rediriger vers le catalogue avec filtre fournisseur
    window.location.href = `catalogue.html?supplier=${supplierId}`;
}

// Mettre à jour les statistiques
function updateStats(suppliersCount, productsCount, quotesCount) {
    // Mise à jour avec animation
    animateCounter('statsSuppliers', suppliersCount);
    animateCounter('statsProducts', productsCount);
    animateCounter('statsQuotes', quotesCount);
}

// Animation des compteurs
function animateCounter(elementId, targetValue) {
    const element = document.getElementById(elementId);
    if (!element) return;
    
    let current = 0;
    const increment = Math.ceil(targetValue / 20);
    
    const timer = setInterval(() => {
        current += increment;
        if (current >= targetValue) {
            current = targetValue;
            clearInterval(timer);
        }
        element.textContent = current;
    }, 50);
}

// Mettre à jour le statut de connexion
function updateConnectionStatus(connected) {
    const statusElement = document.getElementById('connectionStatus');
    
    if (!statusElement) {
        // Créer l'élément s'il n'existe pas
        const statusDiv = document.createElement('div');
        statusDiv.id = 'connectionStatus';
        statusDiv.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 1rem;
            border-radius: 8px;
            font-weight: 500;
            z-index: 1000;
            transition: all 0.3s ease;
        `;
        document.body.appendChild(statusDiv);
    }
    
    const statusEl = document.getElementById('connectionStatus');
    
    if (connected) {
        statusEl.className = 'connection-status connected';
        statusEl.style.background = '#10b981';
        statusEl.style.color = 'white';
        statusEl.innerHTML = '✅ Base de données connectée';
        statusEl.style.display = 'block';
        
        setTimeout(() => {
            statusEl.style.display = 'none';
        }, 3000);
    } else {
        statusEl.className = 'connection-status disconnected';
        statusEl.style.background = '#dc2626';
        statusEl.style.color = 'white';
        statusEl.innerHTML = '❌ Erreur de connexion';
        statusEl.style.display = 'block';
    }
}

// Recherche dans les données
function searchInDatabase(query) {
    const lowerQuery = query.toLowerCase();
    
    return allProducts.filter(product => {
        return (
            (product.name && product.name.toLowerCase().includes(lowerQuery)) ||
            (product.cas_number && product.cas_number.toLowerCase().includes(lowerQuery)) ||
            (product.formula && product.formula.toLowerCase().includes(lowerQuery)) ||
            (product.category && product.category.toLowerCase().includes(lowerQuery)) ||
            (product.description && product.description.toLowerCase().includes(lowerQuery))
        );
    });
}

// Données de fallback en cas d'erreur de connexion
function loadFallbackData() {
    console.log('📦 Chargement des données de fallback...');
    
    // Données statiques de base adaptées aux vraies colonnes
    const fallbackSuppliers = [
        { 
            id: 1, 
            name: 'Euro-Chemicals', 
            country: 'Pays-Bas', 
            speciality: 'APIs et excipients',
            website: 'https://www.euro-chemicals.com'
        },
        { 
            id: 2, 
            name: 'EUROAPI', 
            country: 'France', 
            speciality: 'APIs, hormones, prostaglandines, vit B12',
            website: 'https://www.euroapi.com'
        },
        { 
            id: 3, 
            name: 'PCC Group', 
            country: 'Pologne', 
            speciality: 'Matières premières et excipients',
            website: 'https://www.products.pcc.eu'
        }
    ];
    
    allSuppliers = fallbackSuppliers;
    allProducts = []; // Pas de produits en fallback pour le moment
    
    // Mettre à jour l'interface avec les données de fallback
    updateStats(fallbackSuppliers.length, 0, 0);
    displaySuppliers();
    populateFilters();
    
    console.log('✅ Données de fallback chargées');
}

// Fonctions pour le catalogue - compatible avec catalogue.html
function displayProducts(products) {
    const container = document.getElementById('catalogProductsGrid');
    if (!container) return;
    
    if (!products || products.length === 0) {
        container.innerHTML = `
            <div class="empty-state" style="grid-column: 1/-1; text-align: center; padding: 3rem;">
                <i class="fas fa-flask" style="font-size: 3rem; color: #cbd5e0; margin-bottom: 1rem;"></i>
                <h3 style="color: #4a5568; margin-bottom: 0.5rem;">Aucun produit trouvé</h3>
                <p style="color: #718096;">Aucun produit ne correspond à vos critères</p>
            </div>
        `;
        return;
    }

    container.innerHTML = products.map(product => createProductCard(product)).join('');
}

function createProductCard(product) {
    return `
        <div class="product-card" onclick="showProductDetails(${product.id})">
            <div class="product-image">
                <i class="fas fa-flask"></i>
            </div>
            <div class="product-info">
                <h3 class="product-name">${product.name}</h3>
                <p class="product-formula">${product.formula || ''}</p>
                <p class="product-cas">CAS: ${product.cas_number || 'N/A'}</p>
                <div class="product-details">
                    <span class="product-purity">Pureté: ${product.purity}%</span>
                    <span class="product-category">${product.category}</span>
                </div>
                <div class="product-price">
                    <span class="price">${product.price}€/${product.unit}</span>
                </div>
                <div class="product-supplier">
                    ${product.suppliers ? product.suppliers.name : 'Fournisseur disponible'}
                </div>
            </div>
        </div>
    `;
}

// Initialisation automatique pour les pages qui le nécessitent
document.addEventListener('DOMContentLoaded', () => {
    // Détecter si on est sur la page fournisseurs
    if (window.location.pathname.includes('fournisseurs.html')) {
        console.log('🔄 Page fournisseurs détectée');
        if (typeof loadSuppliers === 'undefined') {
            // Si la fonction loadSuppliers n'existe pas, on initialise
            setTimeout(() => {
                if (allSuppliers.length === 0) {
                    initializeDatabase();
                }
            }, 1000);
        }
    }
});

// Exporter les fonctions principales pour les autres scripts
if (typeof window !== 'undefined') {
    window.ChemSpotDB = {
        initializeDatabase,
        searchInDatabase,
        filterSuppliers,
        resetFilters,
        contactSupplier,
        visitWebsite,
        viewSupplierProducts,
        displaySuppliers,
        displayProducts,
        getAllProducts: () => allProducts,
        getAllSuppliers: () => allSuppliers
    };
    
    // Rendre les fonctions disponibles globalement
    window.filterSuppliers = filterSuppliers;
    window.resetFilters = resetFilters;
    window.contactSupplier = contactSupplier;
    window.visitWebsite = visitWebsite;
    window.viewSupplierProducts = viewSupplierProducts;
    window.displaySuppliers = displaySuppliers;
    window.allSuppliers = allSuppliers;
    window.allProducts = allProducts;
}
