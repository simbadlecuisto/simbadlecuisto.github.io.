// ========================================
// AUTH.JS - SYSTÈME D'AUTHENTIFICATION CHEM SPOT
// ========================================

// Variables d'authentification
let currentUser = null;
let authToken = null;

// Configuration API
const AUTH_CONFIG = {
    baseUrl: '/api/auth',
    tokenKey: 'chemspot_token',
    userKey: 'chemspot_user'
};

// Initialisation du système d'auth
document.addEventListener('DOMContentLoaded', function() {
    initializeAuth();
    setupAuthEventListeners();
});

function initializeAuth() {
    // Vérifier si l'utilisateur est déjà connecté
    checkExistingAuth();
    updateUIBasedOnAuth();
}

function setupAuthEventListeners() {
    // Empêcher la soumission par défaut des formulaires
    document.addEventListener('submit', function(e) {
        if (e.target.matches('#loginForm, #registerForm, #demoForm, #supplierForm, #contactForm')) {
            e.preventDefault();
            handleFormSubmission(e.target);
        }
    });
}

// Vérification de l'authentification existante
function checkExistingAuth() {
    const token = localStorage.getItem(AUTH_CONFIG.tokenKey);
    const userData = localStorage.getItem(AUTH_CONFIG.userKey);
    
    if (token && userData) {
        try {
            authToken = token;
            currentUser = JSON.parse(userData);
            console.log('Utilisateur connecté:', currentUser.email);
        } catch (error) {
            console.error('Erreur lors de la lecture des données utilisateur:', error);
            clearAuthData();
        }
    }
}

// Mise à jour de l'interface selon l'état d'authentification
function updateUIBasedOnAuth() {
    const headerActions = document.querySelector('.header-actions');
    if (!headerActions) return;

    if (currentUser) {
        // Utilisateur connecté
        headerActions.innerHTML = `
            <div class="user-menu">
                <button class="btn btn-outline btn-sm" onclick="toggleUserDropdown()">
                    <i class="fas fa-user"></i> ${currentUser.firstName || currentUser.email}
                    <i class="fas fa-chevron-down"></i>
                </button>
                <div class="user-dropdown" id="userDropdown">
                    <a href="compte.html"><i class="fas fa-user-cog"></i> Mon compte</a>
                    <a href="#" onclick="viewOrders()"><i class="fas fa-shopping-cart"></i> Mes commandes</a>
                    <a href="#" onclick="viewQuotes()"><i class="fas fa-file-invoice"></i> Mes devis</a>
                    <div class="dropdown-divider"></div>
                    <a href="#" onclick="logout()"><i class="fas fa-sign-out-alt"></i> Déconnexion</a>
                </div>
            </div>
        `;
    } else {
        // Utilisateur non connecté
        headerActions.innerHTML = `
            <button class="btn btn-outline btn-sm" onclick="openModal('loginModal')">
                <i class="fas fa-sign-in-alt"></i> Connexion
            </button>
            <button class="btn btn-primary btn-sm" onclick="openModal('registerModal')">
                <i class="fas fa-user-plus"></i> Inscription
            </button>
        `;
    }
}

// Gestion de la soumission des formulaires
function handleFormSubmission(form) {
    const formId = form.id || form.getAttribute('onsubmit')?.match(/handle(\w+)/)?.[1];
    
    switch (formId) {
        case 'loginForm':
        case 'Login':
            handleLogin(form);
            break;
        case 'registerForm':
        case 'Register':
            handleRegister(form);
            break;
        case 'demoForm':
        case 'Demo':
            handleDemo(form);
            break;
        case 'supplierForm':
        case 'SupplierApplication':
            handleSupplierApplication(form);
            break;
        case 'contactForm':
        case 'ContactForm':
            handleContactForm(form);
            break;
        case 'appointmentForm':
        case 'Appointment':
            handleAppointment(form);
            break;
        default:
            console.warn('Formulaire non reconnu:', formId);
    }
}

// Gestion de la connexion
function handleLogin(form) {
    const formData = new FormData(form);
    const email = formData.get('email') || form.querySelector('input[type="email"]').value;
    const password = formData.get('password') || form.querySelector('input[type="password"]').value;
    
    if (!email || !password) {
        showNotification('Veuillez remplir tous les champs', 'warning');
        return;
    }
    
    showNotification('Connexion en cours...', 'info');
    
    // Simulation d'appel API
    simulateAuthRequest({
        endpoint: '/login',
        data: { email, password },
        successCallback: (response) => {
            handleLoginSuccess(response);
            closeModal('loginModal');
        },
        errorCallback: (error) => {
            showNotification(error.message || 'Erreur de connexion', 'error');
        }
    });
}

// Gestion de l'inscription
function handleRegister(form) {
    const formData = new FormData(form);
    const data = {
        company: formData.get('company') || form.querySelector('input[placeholder*="entreprise"], input[placeholder*="Laboratoire"]').value,
        email: formData.get('email') || form.querySelector('input[type="email"]').value,
        password: formData.get('password') || form.querySelector('input[type="password"]').value,
        phone: formData.get('phone') || form.querySelector('input[type="tel"]').value,
        type: formData.get('type') || 'buyer'
    };
    
    if (!data.company || !data.email || !data.password) {
        showNotification('Veuillez remplir tous les champs obligatoires', 'warning');
        return;
    }
    
    if (!isValidEmail(data.email)) {
        showNotification('Veuillez saisir un email valide', 'warning');
        return;
    }
    
    if (data.password.length < 6) {
        showNotification('Le mot de passe doit contenir au moins 6 caractères', 'warning');
        return;
    }
    
    showNotification('Création du compte en cours...', 'info');
    
    simulateAuthRequest({
        endpoint: '/register',
        data,
        successCallback: (response) => {
            handleRegisterSuccess(response);
            closeModal('registerModal');
        },
        errorCallback: (error) => {
            showNotification(error.message || 'Erreur lors de la création du compte', 'error');
        }
    });
}

// Gestion de la demande de démo
function handleDemo(form) {
    const formData = new FormData(form);
    const data = {
        name: formData.get('name') || form.querySelector('input[placeholder*="nom"], input[placeholder*="Nom"]').value,
        company: formData.get('company') || form.querySelector('input[placeholder*="entreprise"], input[placeholder*="Entreprise"]').value,
        email: formData.get('email') || form.querySelector('input[type="email"]').value,
        phone: formData.get('phone') || form.querySelector('input[type="tel"]').value,
        position: formData.get('position') || form.querySelector('input[placeholder*="poste"], input[placeholder*="Poste"]').value,
        needs: formData.get('needs') || form.querySelector('textarea').value
    };
    
    if (!data.name || !data.company || !data.email) {
        showNotification('Veuillez remplir tous les champs obligatoires', 'warning');
        return;
    }
    
    if (!isValidEmail(data.email)) {
        showNotification('Veuillez saisir un email valide', 'warning');
        return;
    }
    
    showNotification('Demande de démo en cours d\'envoi...', 'info');
    
    simulateRequest({
        endpoint: '/demo-request',
        data,
        successCallback: () => {
            showNotification('Demande de démo enregistrée ! Notre équipe vous contactera sous 24h.', 'success');
            closeModal('demoModal');
            form.reset();
        },
        errorCallback: (error) => {
            showNotification('Erreur lors de l\'envoi de la demande', 'error');
        }
    });
}

// Gestion de la candidature fournisseur
function handleSupplierApplication(form) {
    const formData = new FormData(form);
    
    // Récupération des spécialités sélectionnées
    const specialties = Array.from(form.querySelectorAll('input[type="checkbox"]:checked'))
        .map(checkbox => checkbox.value);
    
    // Récupération des certifications
    const certifications = Array.from(form.querySelectorAll('input[name="certifications"]:checked'))
        .map(checkbox => checkbox.value);
    
    const data = {
        company: formData.get('company') || form.querySelector('input[placeholder*="entreprise"]').value,
        country: formData.get('country') || form.querySelector('select').value,
        specialties,
        certifications,
        email: formData.get('email') || form.querySelector('input[type="email"]').value
    };
    
    if (!data.company || !data.country || !data.email || specialties.length === 0) {
        showNotification('Veuillez remplir tous les champs obligatoires', 'warning');
        return;
    }
    
    showNotification('Candidature en cours d\'envoi...', 'info');
    
    simulateRequest({
        endpoint: '/supplier-application',
        data,
        successCallback: () => {
            showNotification('Candidature envoyée avec succès ! Notre équipe d\'audit vous contactera sous 48h.', 'success');
            closeModal('supplierModal');
            form.reset();
        },
        errorCallback: (error) => {
            showNotification('Erreur lors de l\'envoi de la candidature', 'error');
        }
    });
}

// Gestion du formulaire de contact
function handleContactForm(form) {
    const formData = new FormData(form);
    const data = {
        firstName: formData.get('firstName') || form.querySelector('input[placeholder*="prénom"], input[placeholder*="Prénom"]').value,
        lastName: formData.get('lastName') || form.querySelector('input[placeholder*="nom"], input[placeholder*="Nom"]').value,
        email: formData.get('email') || form.querySelector('input[type="email"]').value,
        phone: formData.get('phone') || form.querySelector('input[type="tel"]').value,
        company: formData.get('company') || form.querySelector('input[placeholder*="entreprise"], input[placeholder*="Entreprise"]').value,
        subject: formData.get('subject') || form.querySelector('select').value,
        message: formData.get('message') || form.querySelector('textarea').value
    };
    
    if (!data.firstName || !data.lastName || !data.email || !data.company || !data.subject || !data.message) {
        showNotification('Veuillez remplir tous les champs obligatoires', 'warning');
        return;
    }
    
    if (!isValidEmail(data.email)) {
        showNotification('Veuillez saisir un email valide', 'warning');
        return;
    }
    
    showNotification('Envoi du message en cours...', 'info');
    
    simulateRequest({
        endpoint: '/contact',
        data,
        successCallback: () => {
            showNotification('Message envoyé avec succès ! Nous vous répondrons sous 24h.', 'success');
            form.reset();
        },
        errorCallback: (error) => {
            showNotification('Erreur lors de l\'envoi du message', 'error');
        }
    });
}

// Gestion de la prise de rendez-vous
function handleAppointment(form) {
    const formData = new FormData(form);
    const data = {
        name: formData.get('name') || form.querySelector('input[placeholder*="nom"]').value,
        company: formData.get('company') || form.querySelector('input[placeholder*="entreprise"]').value,
        email: formData.get('email') || form.querySelector('input[type="email"]').value,
        type: formData.get('type') || form.querySelector('select').value,
        message: formData.get('message') || form.querySelector('textarea').value
    };
    
    if (!data.name || !data.company || !data.email || !data.type) {
        showNotification('Veuillez remplir tous les champs obligatoires', 'warning');
        return;
    }
    
    showNotification('Planification du rendez-vous...', 'info');
    
    simulateRequest({
        endpoint: '/appointment',
        data,
        successCallback: () => {
            showNotification('Rendez-vous planifié ! Vous recevrez un email de confirmation.', 'success');
            closeModal('demoModal');
            form.reset();
        }
    });
}

// Succès de connexion
function handleLoginSuccess(response) {
    authToken = response.token;
    currentUser = response.user;
    
    // Sauvegarder les données d'authentification
    localStorage.setItem(AUTH_CONFIG.tokenKey, authToken);
    localStorage.setItem(AUTH_CONFIG.userKey, JSON.stringify(currentUser));
    
    showNotification(`Bienvenue ${currentUser.firstName || currentUser.email} !`, 'success');
    updateUIBasedOnAuth();
    
    // Redirection si nécessaire
    if (currentUser.type === 'supplier') {
        setTimeout(() => {
            window.location.href = 'compte.html';
        }, 2000);
    }
}

// Succès d'inscription
function handleRegisterSuccess(response) {
    showNotification('Compte créé avec succès ! Un email de validation vous a été envoyé.', 'success');
    
    // Auto-connexion après inscription
    if (response.autoLogin) {
        setTimeout(() => {
            handleLoginSuccess(response);
        }, 1500);
    }
}

// Déconnexion
function logout() {
    showNotification('Déconnexion en cours...', 'info');
    
    setTimeout(() => {
        clearAuthData();
        updateUIBasedOnAuth();
        showNotification('Vous avez été déconnecté', 'success');
        
        // Redirection vers l'accueil
        if (window.location.pathname !== '/' && window.location.pathname !== '/index.html') {
            window.location.href = 'index.html';
        }
    }, 1000);
}

// Nettoyage des données d'authentification
function clearAuthData() {
    authToken = null;
    currentUser = null;
    localStorage.removeItem(AUTH_CONFIG.tokenKey);
    localStorage.removeItem(AUTH_CONFIG.userKey);
}

// Menu utilisateur
function toggleUserDropdown() {
    const dropdown = document.getElementById('userDropdown');
    if (dropdown) {
        dropdown.classList.toggle('show');
    }
}

// Fermer le dropdown si on clique ailleurs
document.addEventListener('click', function(e) {
    if (!e.target.closest('.user-menu')) {
        const dropdown = document.getElementById('userDropdown');
        if (dropdown) {
            dropdown.classList.remove('show');
        }
    }
});

// Fonctions de simulation d'API
function simulateAuthRequest({ endpoint, data, successCallback, errorCallback }) {
    // Simulation d'un délai réseau
    setTimeout(() => {
        if (endpoint === '/login') {
            // Simulation de connexion
            if (data.email && data.password) {
                const userData = {
                    id: Math.random().toString(36).substr(2, 9),
                    email: data.email,
                    firstName: data.email.split('@')[0],
                    company: 'Laboratoire Demo',
                    type: 'buyer',
                    verified: true
                };
                
                successCallback({
                    token: 'demo_token_' + Date.now(),
                    user: userData
                });
            } else {
                errorCallback({ message: 'Email ou mot de passe incorrect' });
            }
        } else if (endpoint === '/register') {
            // Simulation d'inscription
            const userData = {
                id: Math.random().toString(36).substr(2, 9),
                email: data.email,
                firstName: data.company.split(' ')[0],
                company: data.company,
                type: data.type,
                verified: false
            };
            
            successCallback({
                user: userData,
                autoLogin: false
            });
        }
    }, 1500 + Math.random() * 1000);
}

function simulateRequest({ endpoint, data, successCallback, errorCallback }) {
    setTimeout(() => {
        // 95% de chance de succès
        if (Math.random() > 0.05) {
            successCallback({ success: true, data });
        } else {
            errorCallback({ message: 'Erreur de communication avec le serveur' });
        }
    }, 1000 + Math.random() * 2000);
}

// Fonctions utilitaires
function isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

function isValidPhone(phone) {
    const phoneRegex = /^[\+]?[\d\s\-\(\)]{10,}$/;
    return phoneRegex.test(phone);
}

// Fonctions pour les utilisateurs connectés
function viewOrders() {
    if (!currentUser) {
        showNotification('Veuillez vous connecter pour accéder à vos commandes', 'warning');
        openModal('loginModal');
        return;
    }
    
    showNotification('Redirection vers vos commandes...', 'info');
    // Redirection vers la page des commandes
    window.location.href = 'compte.html#commandes';
}

function viewQuotes() {
    if (!currentUser) {
        showNotification('Veuillez vous connecter pour accéder à vos devis', 'warning');
        openModal('loginModal');
        return;
    }
    
    showNotification('Redirection vers vos devis...', 'info');
    // Redirection vers la page des devis
    window.location.href = 'compte.html#devis';
}

// Vérification des permissions
function requireAuth(callback) {
    if (!currentUser) {
        showNotification('Veuillez vous connecter pour accéder à cette fonctionnalité', 'warning');
        openModal('loginModal');
        return false;
    }
    
    if (callback) {
        callback();
    }
    return true;
}

function requireSupplierAuth(callback) {
    if (!currentUser) {
        showNotification('Veuillez vous connecter', 'warning');
        openModal('loginModal');
        return false;
    }
    
    if (currentUser.type !== 'supplier') {
        showNotification('Accès réservé aux fournisseurs', 'warning');
        return false;
    }
    
    if (callback) {
        callback();
    }
    return true;
}

// Export des fonctions pour utilisation globale
window.ChemSpotAuth = {
    handleLogin,
    handleRegister,
    handleDemo,
    handleSupplierApplication,
    handleContactForm,
    handleAppointment,
    logout,
    toggleUserDropdown,
    viewOrders,
    viewQuotes,
    requireAuth,
    requireSupplierAuth,
    getCurrentUser: () => currentUser,
    isAuthenticated: () => !!currentUser
};

// Alias pour les gestionnaires de formulaires (rétrocompatibilité)
window.handleLogin = function(event) {
    if (event && event.preventDefault) event.preventDefault();
    const form = event ? event.target : document.querySelector('#loginModal form');
    handleLogin(form);
};

window.handleRegister = function(event) {
    if (event && event.preventDefault) event.preventDefault();
    const form = event ? event.target : document.querySelector('#registerModal form');
    handleRegister(form);
};

window.handleDemo = function(event) {
    if (event && event.preventDefault) event.preventDefault();
    const form = event ? event.target : document.querySelector('#demoModal form');
    handleDemo(form);
};

window.handleSupplierApplication = function(event) {
    if (event && event.preventDefault) event.preventDefault();
    const form = event ? event.target : document.querySelector('#supplierModal form');
    handleSupplierApplication(form);
};

window.handleContactForm = function(event) {
    if (event && event.preventDefault) event.preventDefault();
    const form = event ? event.target : document.querySelector('.contact-form');
    handleContactForm(form);
};

window.handleAppointment = function(event) {
    if (event && event.preventDefault) event.preventDefault();
    const form = event ? event.target : document.querySelector('#demoModal form');
    handleAppointment(form);
};
