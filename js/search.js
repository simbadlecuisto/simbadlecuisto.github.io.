// ========================================
// SEARCH.JS - SYSTÈME DE RECHERCHE CHEM SPOT
// ========================================

// Variables de recherche
let searchIndex = [];
let currentSearchTerm = '';
let searchFilters = {};
let searchHistory = [];

// Suggestions de recherche
const searchSuggestions = [
    "Paracétamol", "Ibuprofène", "Aspirine", "Lactose", "Stéarate de magnésium",
    "Cellulose microcristalline", "Dioxyde de titane", "Gélatine", "Amidon",
    "Sorbitol", "Mannitol", "Acide citrique", "Hydroxypropylcellulose",
    "Hydroxypropylméthylcellulose", "Polyéthylène glycol", "Polysorbate 80",
    "Acide stéarique", "Talc", "Carboxyméthylcellulose", "Povidone",
    "Croscarmellose", "Sodium lauryl sulfate", "Benzoate de sodium",
    "Acide sorbique", "Propylparaben", "Méthylparaben", "BHT", "BHA"
];

// Catégories de produits
const productCategories = {
    'api': 'Principes Actifs',
    'excipient': 'Excipients',
    'colorant': 'Colorants',
    'arome': 'Arômes',
    'conservateur': 'Conservateurs',
    'antioxydant': 'Antioxydants',
    'edulcorant': 'Édulcorants'
};

// Initialisation du système de recherche
document.addEventListener('DOMContentLoaded', function() {
    initializeSearch();
    loadSearchHistory();
});

function initializeSearch() {
    buildSearchIndex();
    setupSearchEventListeners();
    setupSearchTabs();
}

// Construction de l'index de recherche
function buildSearchIndex() {
    searchIndex = [];
    
    // Index des produits
    if (window.products) {
        window.products.forEach(product => {
            searchIndex.push({
                id: product.id,
                type: 'product',
                title: product.name,
                category: product.category,
                keywords: [
                    product.name.toLowerCase(),
                    product.cas.toLowerCase(),
                    product.formula.toLowerCase(),
                    product.supplier.toLowerCase(),
                    product.origin.toLowerCase(),
                    productCategories[product.category]?.toLowerCase() || '',
                ].join(' '),
                data: product
            });
        });
    }
    
    // Index des fournisseurs
    if (window.suppliers) {
        window.suppliers.forEach(supplier => {
            searchIndex.push({
                id: supplier.name,
                type: 'supplier',
                title: supplier.name,
                category: 'supplier',
                keywords: [
                    supplier.name.toLowerCase(),
                    supplier.country.toLowerCase(),
                    supplier.specialties.join(' ').toLowerCase()
                ].join(' '),
                data: supplier
            });
        });
    }
    
    console.log('Index de recherche construit:', searchIndex.length, 'éléments');
}

// Configuration des écouteurs d'événements de recherche
function setupSearchEventListeners() {
    // Recherche principale (page d'accueil)
    const mainSearchInput = document.getElementById('searchInput');
    if (mainSearchInput) {
        setupSearchInput(mainSearchInput, 'searchSuggestions');
    }
    
    // Recherche catalogue
    const catalogSearchInput = document.getElementById('catalogSearchInput');
    if (catalogSearchInput) {
        setupSearchInput(catalogSearchInput, 'catalogSearchSuggestions');
    }
}

// Configuration d'un champ de recherche
function setupSearchInput(input, suggestionsId) {
    let searchTimeout;
    
    input.addEventListener('input', function() {
        clearTimeout(searchTimeout);
        searchTimeout = setTimeout(() => {
            handleSearchInput(this.value, suggestionsId);
        }, 300);
    });
    
    input.addEventListener('focus', function() {
        if (this.value.length > 1) {
            showSuggestions(this.value, suggestionsId);
        }
    });
    
    input.addEventListener('blur', function() {
        setTimeout(() => hideSuggestions(suggestionsId), 200);
    });
    
    input.addEventListener('keydown', function(e) {
        if (e.key === 'Enter') {
            e.preventDefault();
            hideSuggestions(suggestionsId);
            performSearch(this.value);
        }
    });
}

// Gestion de la saisie dans le champ de recherche
function handleSearchInput(query, suggestionsId) {
    if (query.length > 1) {
        showSuggestions(query, suggestionsId);
    } else {
        hideSuggestions(suggestionsId);
    }
}

// Affichage des suggestions
function showSuggestions(query, suggestionsId) {
    const suggestionsContainer = document.getElementById(suggestionsId);
    if (!suggestionsContainer) return;
    
    const filteredSuggestions = getFilteredSuggestions(query);
    
    if (filteredSuggestions.length > 0) {
        suggestionsContainer.innerHTML = filteredSuggestions
            .slice(0, 8)
            .map(suggestion => createSuggestionHTML(suggestion, query))
            .join('');
        suggestionsContainer.style.display = 'block';
    } else {
        hideSuggestions(suggestionsId);
    }
}

// Filtrage des suggestions
function getFilteredSuggestions(query) {
    const normalizedQuery = query.toLowerCase().trim();
    const suggestions = [];
    
    // Suggestions directes
    const directMatches = searchSuggestions.filter(item => 
        item.toLowerCase().includes(normalizedQuery)
    );
    
    // Recherche dans l'index
    const indexMatches = searchIndex
        .filter(item => item.keywords.includes(normalizedQuery))
        .map(item => item.title);
    
    // Combiner et dédoublonner
    const combined = [...new Set([...directMatches, ...indexMatches])];
    
    // Trier par pertinence (correspondance exacte en premier)
    return combined.sort((a, b) => {
        const aExact = a.toLowerCase().startsWith(normalizedQuery);
        const bExact = b.toLowerCase().startsWith(normalizedQuery);
        
        if (aExact && !bExact) return -1;
        if (!aExact && bExact) return 1;
        return a.length - b.length;
    });
}

// Création du HTML d'une suggestion
function createSuggestionHTML(suggestion, query) {
    const highlighted = highlightMatch(suggestion, query);
    return `
        <div class="suggestion-item" onclick="selectSuggestion('${suggestion.replace(/'/g, "\\'")}')">
            <i class="fas fa-search"></i>
            <span>${highlighted}</span>
        </div>
    `;
}

// Mise en surbrillance des correspondances
function highlightMatch(text, query) {
    const regex = new RegExp(`(${escapeRegex(query)})`, 'gi');
    return text.replace(regex, '<mark>$1</mark>');
}

function escapeRegex(string) {
    return string.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}

// Masquage des suggestions
function hideSuggestions(suggestionsId) {
    const suggestionsContainer = document.getElementById(suggestionsId);
    if (suggestionsContainer) {
        suggestionsContainer.style.display = 'none';
    }
}

// Sélection d'une suggestion
function selectSuggestion(suggestion) {
    const activeInput = document.activeElement.closest('.search-input-container')?.querySelector('input') ||
                       document.getElementById('searchInput') ||
                       document.getElementById('catalogSearchInput');
    
    if (activeInput) {
        activeInput.value = suggestion;
        hideSuggestions('searchSuggestions');
        hideSuggestions('catalogSearchSuggestions');
        performSearch(suggestion);
    }
}

// Recherche principale
function performSearch(query = null) {
    const searchTerm = query || getCurrentSearchTerm();
    
    if (!searchTerm.trim()) {
        showNotification('Veuillez saisir un terme de recherche', 'warning');
        return;
    }
    
    currentSearchTerm = searchTerm;
    addToSearchHistory(searchTerm);
    
    showNotification(`Recherche de "${searchTerm}" en cours...`, 'info');
    
    // Recherche dans l'index
    const results = searchInIndex(searchTerm);
    
    // Affichage des résultats
    setTimeout(() =>
