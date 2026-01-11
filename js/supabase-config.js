// ===============================================
// SUPABASE CONFIG - CHEMISTRYSPOT V2
// Product-Centric Architecture
// ===============================================

// ⚠️ REMPLACE TES CREDENTIALS ICI
const SUPABASE_URL = 'https://jkaffpgqbyhuihvyvtld.supabase.co';
const SUPABASE_ANON_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImprYWZmcGdxYnlodWlodnl2dGxkIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTE2NTgzOTQsImV4cCI6MjA2NzIzNDM5NH0.OIjoz6uoPV25Nraral4YN_gz7q6COBW3dAVIYhBy1pI';

let supabase;
let productsCache = [];
let referencesCache = [];
let specsCache = [];

// Initialisation Supabase
document.addEventListener('DOMContentLoaded', async () => {
    try {
        console.log('🔄 Initialisation Supabase...');
        
        // Attendre que Supabase soit chargé
        if (typeof window.supabase === 'undefined') {
            console.log('⏳ Attente du chargement de Supabase...');
            await new Promise(resolve => setTimeout(resolve, 1000));
            if (typeof window.supabase === 'undefined') {
                throw new Error('Supabase non chargé');
            }
        }
        
        // Créer client Supabase
        supabase = window.supabase.createClient(SUPABASE_URL, SUPABASE_ANON_KEY);
        console.log('✅ Client Supabase créé');
        
        // Charger les données
        await loadAllData();
        
        // Mettre à jour les stats si présentes
        if (typeof updateDashboardStats === 'function') {
            updateDashboardStats();
        }
        
        showStatus('✅ Base de données connectée', 'success');
        
    } catch (error) {
        console.error('❌ Erreur initialisation:', error);
        showStatus('❌ Erreur connexion base de données', 'error');
    }
});

// ===============================================
// CHARGEMENT DES DONNÉES
// ===============================================

async function loadAllData() {
    try {
        console.log('📊 Chargement des données...');
        
        // Charger produits
        const { data: products, error: productsError } = await supabase
            .from('excipients')  // ✅ NOUVELLE TABLE
            .select('*')
            .eq('actif', true)
            .order('nom');
        
        if (productsError) throw productsError;
        productsCache = products || [];
        console.log(`✅ ${productsCache.length} produits chargés`);
        
        
        if (referencesError) throw referencesError;
        referencesCache = references || [];
        console.log(`✅ ${referencesCache.length} références chargées`);
        
        
        if (specsError) throw specsError;
        specsCache = specs || [];
        console.log(`✅ ${specsCache.length} spécifications chargées`);
        
        console.log('✅ Toutes les données chargées avec succès');
        return true;
        
    } catch (error) {
        console.error('❌ Erreur chargement données:', error);
        return false;
    }
}

// ===============================================
// FONCTIONS D'ACCÈS AUX DONNÉES
// ===============================================

// Récupérer tous les produits avec leurs références
async function getAllProductsWithReferences() {
    try {
        const { data, error } = await supabase
            .from('excipients')  // ✅ NOUVELLE TABLE
            .select(`
                *,
                product_references (
                    *,
                    caracteristiques_techniques (*)
                )
            `)
            .eq('actif', true)
            .order('nom');
        
        if (error) throw error;
        return data || [];
        
    } catch (error) {
        console.error('❌ Erreur getAllProductsWithReferences:', error);
        return [];
    }
}

// Récupérer un produit par ID avec toutes ses références
async function getProductById(productId) {
    try {
        const { data, error } = await supabase
            .from('excipients')  // ✅ NOUVELLE TABLE
            .select(`
                *,
                product_references (
                    *,
                    caracteristiques_techniques (*)
                )
            `)
            .eq('id', productId)
            .eq('actif', true)
            .single();
        
        if (error) throw error;
        return data;
        
    } catch (error) {
        console.error('❌ Erreur getProductById:', error);
        return null;
    }
}

// Récupérer un produit par CAS Number
async function getProductByCAS(casNumber) {
    try {
        const { data, error } = await supabase
            .from('excipients')  // ✅ NOUVELLE TABLE
            .select(`
                *,
                product_references (
                    *,
                    caracteristiques_techniques (*)
                )
            `)
            .eq('cas_number', casNumber)
            .eq('actif', true)
            .single();
        
        if (error) throw error;
        return data;
        
    } catch (error) {
        console.error('❌ Erreur getProductByCAS:', error);
        return null;
    }
}

// Recherche de produits
async function searchProducts(query, filters = {}) {
    try {
        let queryBuilder = supabase
            .from('excipients')  // ✅ NOUVELLE TABLE
            .select(`
                *,
                product_references (
                    *,
                    caracteristiques_techniques (*)
                )
            `)
            .eq('actif', true);
        
        // Recherche textuelle
        if (query) {
            queryBuilder = queryBuilder.or(
                `nom.ilike.%${query}%,` +
                `nom_chimique.ilike.%${query}%,` +
                `cas_number.ilike.%${query}%,` +
                `categorie.ilike.%${query}%`
            );
        }
        
        // Filtres
        if (filters.categorie) {
            queryBuilder = queryBuilder.eq('categorie', filters.categorie);
        }
        
        if (filters.sous_categorie) {
            queryBuilder = queryBuilder.eq('sous_categorie', filters.sous_categorie);
        }
        
        queryBuilder = queryBuilder.order('nom');
        
        const { data, error } = await queryBuilder;
        
        if (error) throw error;
        return data || [];
        
    } catch (error) {
        console.error('❌ Erreur searchProducts:', error);
        return [];
    }
}

// Récupérer les catégories uniques
function getCategories() {
    const categories = [...new Set(productsCache.map(p => p.categorie))];
    return categories.filter(c => c).sort();
}

// Récupérer les sous-catégories uniques
function getSubCategories() {
    const subCategories = [...new Set(productsCache.map(p => p.sous_categorie))];
    return subCategories.filter(c => c).sort();
}

// Récupérer les références d'un produit
function getProductReferences(productId) {
    return referencesCache.filter(r => r.produit_id === productId);
}

// Récupérer les caractéristiques d'une référence
function getReferenceSpecs(referenceId) {
    return specsCache.filter(s => s.reference_id === referenceId);
}

// Récupérer les statistiques
function getStats() {
    return {
        totalProducts: productsCache.length,
        totalReferences: referencesCache.length,
        totalSpecs: specsCache.length,
        categories: getCategories().length,
        suppliers: [...new Set(referencesCache.map(r => r.fournisseur_nom).filter(Boolean))].length
    };
}

// ===============================================
// FONCTIONS UTILITAIRES
// ===============================================

// Formater le prix
function formatPrice(price) {
    if (!price) return 'Prix sur demande';
    return new Intl.NumberFormat('fr-FR', {
        style: 'currency',
        currency: 'EUR',
        minimumFractionDigits: 2
    }).format(price);
}

// Formater la disponibilité
function formatAvailability(stock, delai) {
    if (stock) {
        return `<span class="availability-badge available">✅ En stock</span>`;
    } else if (delai) {
        return `<span class="availability-badge limited">⏳ ${delai} jours</span>`;
    } else {
        return `<span class="availability-badge out-of-stock">❌ Non disponible</span>`;
    }
}

// Afficher message de statut
function showStatus(message, type = 'info') {
    // Supprimer les anciens messages
    const existing = document.querySelectorAll('.status-message');
    existing.forEach(el => el.remove());
    
    // Créer nouveau message
    const div = document.createElement('div');
    div.className = `status-message status-${type}`;
    div.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 12px 20px;
        border-radius: 8px;
        color: white;
        font-weight: 600;
        z-index: 10000;
        animation: slideIn 0.3s ease-out;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    `;
    
    // Couleurs selon le type
    const colors = {
        success: '#10b981',
        error: '#ef4444',
        warning: '#f59e0b',
        info: '#3b82f6'
    };
    div.style.background = colors[type] || colors.info;
    
    div.textContent = message;
    document.body.appendChild(div);
    
    // Animation CSS
    const style = document.createElement('style');
    style.textContent = `
        @keyframes slideIn {
            from { transform: translateX(400px); opacity: 0; }
            to { transform: translateX(0); opacity: 1; }
        }
    `;
    document.head.appendChild(style);
    
    // Auto-suppression après 3 secondes
    setTimeout(() => {
        div.style.animation = 'slideIn 0.3s ease-out reverse';
        setTimeout(() => div.remove(), 300);
    }, 3000);
}

// Créer le badge de catégorie
function createCategoryBadge(category, subCategory) {
    const sub = subCategory ? ` • ${subCategory}` : '';
    return `<span class="product-category-badge">${category}${sub}</span>`;
}

// Tronquer le texte
function truncateText(text, maxLength = 100) {
    if (!text || text.length <= maxLength) return text;
    return text.substring(0, maxLength) + '...';
}

// ===============================================
// MISE À JOUR DES STATS DASHBOARD
// ===============================================

function updateDashboardStats() {
    const stats = getStats();
    
    // Mettre à jour les compteurs si présents
    updateCounter('statsProducts', stats.totalProducts);
    updateCounter('statsReferences', stats.totalReferences);
    updateCounter('statsSuppliers', stats.suppliers);
    updateCounter('statsCategories', stats.categories);
}

// Animation compteur
function updateCounter(elementId, targetValue) {
    const element = document.getElementById(elementId);
    if (!element) return;
    
    let current = parseInt(element.textContent) || 0;
    const increment = Math.ceil(targetValue / 30);
    
    const timer = setInterval(() => {
        current += increment;
        if (current >= targetValue) {
            current = targetValue;
            clearInterval(timer);
        }
        element.textContent = current;
    }, 30);
}

// ===============================================
// EXPORT DES FONCTIONS
// ===============================================

window.ChemSpotDB = {
    // Données
    getProducts: () => productsCache,
    getReferences: () => referencesCache,
    getSpecs: () => specsCache,
    
    // Fonctions principales
    getAllProductsWithReferences,
    getProductById,
    getProductByCAS,
    searchProducts,
    getProductReferences,
    getReferenceSpecs,
    
    // Utilitaires
    getCategories,
    getSubCategories,
    getStats,
    formatPrice,
    formatAvailability,
    showStatus,
    createCategoryBadge,
    truncateText,
    
    // Direct access
    supabase: () => supabase
};

console.log('✅ ChemSpotDB initialisé');
