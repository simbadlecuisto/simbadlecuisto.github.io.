// ===============================================
// SUPABASE CONFIG - CHEMISTRYSPOT V3
// Simplifié pour table excipients uniquement
// ===============================================

const SUPABASE_URL = 'https://jkaffpgqbyhuihvyvtld.supabase.co';
const SUPABASE_ANON_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImprYWZmcGdxYnlodWlodnl2dGxkIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTE2NTgzOTQsImV4cCI6MjA2NzIzNDM5NH0.OIjoz6uoPV25Nraral4YN_gz7q6COBW3dAVIYhBy1pI';

let supabaseClient;
let excipients = [];

// Initialisation Supabase
document.addEventListener('DOMContentLoaded', async () => {
    try {
        console.log('🔄 Initialisation Supabase...');
        
        if (typeof window.supabase === 'undefined') {
            console.log('⏳ Attente du chargement de Supabase...');
            await new Promise(resolve => setTimeout(resolve, 1000));
            if (typeof window.supabase === 'undefined') {
                throw new Error('Supabase non chargé');
            }
        }
        
        supabaseClient = window.supabase.createClient(SUPABASE_URL, SUPABASE_ANON_KEY);
        console.log('✅ Client Supabase créé');
        
        await loadExcipients();
        
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

async function loadExcipients() {
    try {
        console.log('📊 Chargement des excipients...');
        
        const { data, error } = await supabaseClient
            .from('excipients')
            .select('*')
            .order('nom_commun');
        
        if (error) throw error;
        excipients = data || [];
        console.log(`✅ ${excipients.length} excipients chargés`);
        return true;
        
    } catch (error) {
        console.error('❌ Erreur chargement excipients:', error);
        return false;
    }
}

// ===============================================
// FONCTIONS D'ACCÈS AUX DONNÉES
// ===============================================

async function getAllExcipients() {
    try {
        const { data, error } = await supabaseClient
            .from('excipients')
            .select('*')
            .order('nom_commun');
        
        if (error) throw error;
        return data || [];
        
    } catch (error) {
        console.error('❌ Erreur getAllExcipients:', error);
        return [];
    }
}

async function getExcipientById(id) {
    try {
        const { data, error } = await supabaseClient
            .from('excipients')
            .select('*')
            .eq('id', id)
            .single();
        
        if (error) throw error;
        return data;
        
    } catch (error) {
        console.error('❌ Erreur getExcipientById:', error);
        return null;
    }
}

async function getExcipientByCAS(casNumber) {
    try {
        const { data, error } = await supabaseClient
            .from('excipients')
            .select('*')
            .eq('cas_number', casNumber)
            .single();
        
        if (error) throw error;
        return data;
        
    } catch (error) {
        console.error('❌ Erreur getExcipientByCAS:', error);
        return null;
    }
}

async function searchExcipients(query) {
    try {
        const { data, error } = await supabaseClient
            .from('excipients')
            .select('*')
            .or(`nom_commun.ilike.%${query}%,nom_chimique.ilike.%${query}%,cas_number.ilike.%${query}%`)
            .order('nom_commun');
        
        if (error) throw error;
        return data || [];
        
    } catch (error) {
        console.error('❌ Erreur searchExcipients:', error);
        return [];
    }
}

// Statistiques
function getStats() {
    return {
        totalProducts: excipients.length,
        totalReferences: 0,
        totalSpecs: 0,
        categories: 0,
        suppliers: 0
    };
}

// ===============================================
// FONCTIONS UTILITAIRES
// ===============================================

function showStatus(message, type = 'info') {
    const existing = document.querySelectorAll('.status-message');
    existing.forEach(el => el.remove());
    
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
    
    const colors = {
        success: '#10b981',
        error: '#ef4444',
        warning: '#f59e0b',
        info: '#3b82f6'
    };
    div.style.background = colors[type] || colors.info;
    
    div.textContent = message;
    document.body.appendChild(div);
    
    const style = document.createElement('style');
    style.textContent = `
        @keyframes slideIn {
            from { transform: translateX(400px); opacity: 0; }
            to { transform: translateX(0); opacity: 1; }
        }
    `;
    document.head.appendChild(style);
    
    setTimeout(() => {
        div.style.animation = 'slideIn 0.3s ease-out reverse';
        setTimeout(() => div.remove(), 300);
    }, 3000);
}

function updateDashboardStats() {
    const stats = getStats();
    updateCounter('statsProducts', stats.totalProducts);
}

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
    getProducts: () => excipients,
    getAllExcipients,
    getExcipientById,
    getExcipientByCAS,
    searchExcipients,
    getStats,
    showStatus,
    supabase: () => supabaseClient
};

console.log('✅ ChemSpotDB initialisé');
