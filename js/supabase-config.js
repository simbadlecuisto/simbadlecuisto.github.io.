const SUPABASE_URL = 'https://jkaffpgqbyhuihvyvtld.supabase.co';
const SUPABASE_ANON_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImprYWZmcGdxYnlodWlodnl2dGxkIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTE2NTgzOTQsImV4cCI6MjA2NzIzNDM5NH0.OIjoz6uoPV25Nraral4YN_gz7q6COBW3dAVIYhBy1pI';

let supabaseClient;  // ✅ UN SEUL NOM
let excipients = [];

// Initialisation
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
        
        supabaseClient = window.supabase.createClient(SUPABASE_URL, SUPABASE_ANON_KEY);  // ✅
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

async function loadExcipients() {
    try {
        console.log('📊 Chargement des excipients...');
        
        const { data, error } = await supabaseClient  // ✅
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

// ... RESTE DU CODE (continue comme avant mais remplace 'supabase' par 'supabaseClient')
