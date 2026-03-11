// ═══════════════════════════════════════════════════════════════
// ChemistrySpot — auth.js v2
// Auth Supabase réelle (Connexion / Inscription / Déconnexion)
// À charger dans toutes les pages après supabase-js CDN.
// Crée son propre client auth (partage la session localStorage).
// ═══════════════════════════════════════════════════════════════

(function () {
    'use strict';

    const SUPABASE_URL = 'https://jkaffpgqbyhuihvyvtld.supabase.co';
    const ANON_KEY     = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImprYWZmcGdxYnlodWlodnl2dGxkIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTE2NTgzOTQsImV4cCI6MjA2NzIzNDM5NH0.OIjoz6uoPV25Nraral4YN_gz7q6COBW3dAVIYhBy1pI';

    let authClient = null;

    // ── Global modal helpers (no-op override if already defined) ─────
    if (!window.openModal)  window.openModal  = id => { const el = document.getElementById(id); if (el) el.classList.add('open');    };
    if (!window.closeModal) window.closeModal = id => { const el = document.getElementById(id); if (el) el.classList.remove('open'); };

    // ── Inject login + register modals ────────────────────────────────
    function injectAuthModals() {
        if (document.getElementById('loginModal')) return;

        document.body.insertAdjacentHTML('beforeend', `
            <div id="loginModal" class="modal" role="dialog" aria-modal="true" aria-labelledby="auth-login-title">
                <div class="modal-box" style="max-width:400px;">
                    <button class="modal-close" data-close="loginModal" aria-label="Fermer">&times;</button>
                    <div class="modal-title" id="auth-login-title">
                        <i class="fas fa-sign-in-alt"></i> Connexion
                    </div>
                    <form id="loginAuthForm">
                        <div class="form-group">
                            <label class="form-label" for="auth-email">Email</label>
                            <input id="auth-email" type="email" class="form-input" required
                                autocomplete="email" placeholder="jean.dupont@labo.com">
                        </div>
                        <div class="form-group">
                            <label class="form-label" for="auth-password">Mot de passe</label>
                            <input id="auth-password" type="password" class="form-input" required
                                autocomplete="current-password" placeholder="••••••••">
                        </div>
                        <div id="loginAuthError" style="display:none;margin-bottom:.75rem;" role="alert"></div>
                        <button type="submit" id="loginAuthBtn" class="btn btn-primary w-full">
                            <i class="fas fa-sign-in-alt"></i> Se connecter
                        </button>
                        <p style="text-align:center;margin-top:.75rem;font-size:.82rem;color:var(--text-muted);">
                            Pas encore de compte ?
                            <a href="#" data-switch-to="registerModal" style="color:var(--primary);">S'inscrire</a>
                        </p>
                    </form>
                </div>
            </div>

            <div id="registerModal" class="modal" role="dialog" aria-modal="true" aria-labelledby="auth-register-title">
                <div class="modal-box" style="max-width:400px;">
                    <button class="modal-close" data-close="registerModal" aria-label="Fermer">&times;</button>
                    <div class="modal-title" id="auth-register-title">
                        <i class="fas fa-user-plus"></i> Inscription
                    </div>
                    <form id="registerAuthForm">
                        <div class="form-group">
                            <label class="form-label" for="auth-reg-entreprise">Entreprise *</label>
                            <input id="auth-reg-entreprise" type="text" class="form-input" required
                                autocomplete="organization" placeholder="Laboratoire ABC">
                        </div>
                        <div class="form-group">
                            <label class="form-label" for="auth-reg-email">Email professionnel *</label>
                            <input id="auth-reg-email" type="email" class="form-input" required
                                autocomplete="email" placeholder="jean.dupont@labo.com">
                        </div>
                        <div class="form-group">
                            <label class="form-label" for="auth-reg-password">Mot de passe *</label>
                            <input id="auth-reg-password" type="password" class="form-input" required
                                autocomplete="new-password" placeholder="Minimum 6 caractères" minlength="6">
                        </div>
                        <div id="registerAuthError"   style="display:none;margin-bottom:.75rem;" role="alert"></div>
                        <div id="registerAuthSuccess" style="display:none;margin-bottom:.75rem;" role="status"></div>
                        <button type="submit" id="registerAuthBtn" class="btn btn-primary w-full">
                            <i class="fas fa-user-plus"></i> Créer mon compte
                        </button>
                        <p style="text-align:center;margin-top:.75rem;font-size:.82rem;color:var(--text-muted);">
                            Déjà un compte ?
                            <a href="#" data-switch-to="loginModal" style="color:var(--primary);">Se connecter</a>
                        </p>
                    </form>
                </div>
            </div>
        `);

        // Event delegation — no global onclick needed in injected HTML
        document.addEventListener('click', function (e) {
            const closeBtn   = e.target.closest('[data-close]');
            const switchLink = e.target.closest('[data-switch-to]');

            if (closeBtn) {
                window.closeModal(closeBtn.dataset.close);
                return;
            }
            if (switchLink) {
                e.preventDefault();
                const from = switchLink.closest('.modal')?.id;
                const to   = switchLink.dataset.switchTo;
                if (from) window.closeModal(from);
                setTimeout(() => window.openModal(to), 150);
                return;
            }
            if (e.target.matches('#loginModal, #registerModal')) {
                e.target.classList.remove('open');
            }
        });

        document.getElementById('loginAuthForm').addEventListener('submit',    handleSignIn);
        document.getElementById('registerAuthForm').addEventListener('submit', handleSignUp);
    }

    // ── Update header auth section ────────────────────────────────────
    function updateAuthUI(user) {
        const div = document.querySelector('.header-actions');
        if (!div) return;

        if (user) {
            const meta    = user.user_metadata || {};
            const name    = meta.entreprise || user.email.split('@')[0];
            const display = escapeHtml(name.length > 16 ? name.slice(0, 16) + '…' : name);
            div.innerHTML = `
                <span style="font-size:.82rem;color:var(--text-muted);display:flex;align-items:center;gap:.4rem;white-space:nowrap;">
                    <i class="fas fa-user-circle" style="color:var(--primary);font-size:1rem;"></i>
                    ${display}
                </span>
                <button class="btn btn-ghost btn-sm" id="signOutBtn">
                    <i class="fas fa-sign-out-alt"></i> Déconnexion
                </button>
            `;
            document.getElementById('signOutBtn').addEventListener('click', handleSignOut);
        } else {
            div.innerHTML = `
                <button class="btn btn-ghost btn-sm" id="openLoginBtn">
                    <i class="fas fa-sign-in-alt"></i> Connexion
                </button>
                <button class="btn btn-primary btn-sm" id="openRegisterBtn">
                    <i class="fas fa-user-plus"></i> Inscription
                </button>
            `;
            document.getElementById('openLoginBtn').addEventListener('click',    () => window.openModal('loginModal'));
            document.getElementById('openRegisterBtn').addEventListener('click', () => window.openModal('registerModal'));
        }
    }

    // ── Sign in ───────────────────────────────────────────────────────
    async function handleSignIn(e) {
        e.preventDefault();
        const email    = document.getElementById('auth-email').value.trim();
        const password = document.getElementById('auth-password').value;
        const errDiv   = document.getElementById('loginAuthError');
        const btn      = document.getElementById('loginAuthBtn');

        errDiv.style.display = 'none';
        btn.disabled = true;
        btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Connexion…';

        try {
            const { error } = await authClient.auth.signInWithPassword({ email, password });
            if (error) throw error;
            window.closeModal('loginModal');
            document.getElementById('loginAuthForm').reset();
            showAuthStatus('✅ Connecté — bienvenue !', 'success');
        } catch (err) {
            errDiv.style.display = 'block';
            errDiv.innerHTML = errorHtml(getAuthErrorFr(err.message));
        } finally {
            btn.disabled = false;
            btn.innerHTML = '<i class="fas fa-sign-in-alt"></i> Se connecter';
        }
    }

    // ── Sign up ───────────────────────────────────────────────────────
    async function handleSignUp(e) {
        e.preventDefault();
        const email      = document.getElementById('auth-reg-email').value.trim();
        const password   = document.getElementById('auth-reg-password').value;
        const entreprise = document.getElementById('auth-reg-entreprise').value.trim();
        const errDiv     = document.getElementById('registerAuthError');
        const succDiv    = document.getElementById('registerAuthSuccess');
        const btn        = document.getElementById('registerAuthBtn');

        errDiv.style.display  = 'none';
        succDiv.style.display = 'none';
        btn.disabled = true;
        btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Création…';

        try {
            const { error } = await authClient.auth.signUp({
                email, password,
                options: { data: { entreprise } }
            });
            if (error) throw error;
            succDiv.style.display = 'block';
            succDiv.innerHTML = `<div class="status-bar status-success"><i class="fas fa-envelope"></i> Compte créé ! Vérifiez votre boîte mail pour confirmer votre adresse.</div>`;
            document.getElementById('registerAuthForm').reset();
            btn.innerHTML = '<i class="fas fa-check"></i> Confirmation envoyée';
        } catch (err) {
            errDiv.style.display = 'block';
            errDiv.innerHTML = errorHtml(getAuthErrorFr(err.message));
            btn.disabled = false;
            btn.innerHTML = '<i class="fas fa-user-plus"></i> Créer mon compte';
        }
    }

    // ── Sign out ──────────────────────────────────────────────────────
    async function handleSignOut() {
        try {
            await authClient.auth.signOut();
            showAuthStatus('👋 Déconnecté avec succès', 'info');
        } catch (err) {
            console.error('Erreur déconnexion:', err);
        }
    }

    // ── Helpers ───────────────────────────────────────────────────────
    function getAuthErrorFr(msg) {
        if (!msg) return 'Une erreur est survenue.';
        if (msg.includes('Invalid login credentials'))          return 'Email ou mot de passe incorrect.';
        if (msg.includes('Email not confirmed'))                return 'Email non confirmé — vérifiez votre boîte mail.';
        if (msg.includes('User already registered'))            return 'Un compte existe déjà avec cet email.';
        if (msg.includes('Password should be'))                 return 'Mot de passe trop court (minimum 6 caractères).';
        if (msg.includes('rate limit') || msg.includes('too many')) return 'Trop de tentatives — réessayez dans quelques minutes.';
        return 'Une erreur est survenue. Réessayez ou contactez-nous.';
    }

    function errorHtml(text) {
        return `<div class="status-bar status-danger"><i class="fas fa-exclamation-circle"></i> ${escapeHtml(text)}</div>`;
    }

    function escapeHtml(str) {
        return String(str)
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;');
    }

    function showAuthStatus(msg, type) {
        if (typeof window.showStatus === 'function') { window.showStatus(msg, type); return; }
        const colors = { success: '#22c55e', error: '#ef4444', info: '#4fc3f7', warning: '#f0b429' };
        const toast = Object.assign(document.createElement('div'), {
            textContent: msg,
        });
        Object.assign(toast.style, {
            position: 'fixed', top: '20px', right: '20px',
            padding: '12px 20px', borderRadius: '8px',
            color: '#fff', fontWeight: '600', zIndex: '10000',
            fontFamily: 'Inter, sans-serif', fontSize: '.88rem',
            background: colors[type] || colors.info,
            boxShadow: '0 4px 12px rgba(0,0,0,.3)',
            transition: 'opacity .3s ease',
        });
        document.body.appendChild(toast);
        setTimeout(() => { toast.style.opacity = '0'; setTimeout(() => toast.remove(), 300); }, 3000);
    }

    // ── Keyboard: Escape closes modals ────────────────────────────────
    document.addEventListener('keydown', e => {
        if (e.key === 'Escape') {
            ['loginModal', 'registerModal'].forEach(id => window.closeModal(id));
        }
    });

    // ── Init ──────────────────────────────────────────────────────────
    async function initAuth() {
        let attempts = 0;
        while (typeof window.supabase === 'undefined' && attempts < 30) {
            await new Promise(r => setTimeout(r, 200));
            attempts++;
        }
        if (typeof window.supabase === 'undefined') {
            console.warn('[auth.js] Supabase JS not available');
            return;
        }

        authClient = window.supabase.createClient(SUPABASE_URL, ANON_KEY);

        injectAuthModals();

        // Auth state change (fires immediately with current session from localStorage)
        authClient.auth.onAuthStateChange((_event, session) => {
            updateAuthUI(session?.user || null);
        });

        // Fast init from cached session
        const { data: { session } } = await authClient.auth.getSession();
        updateAuthUI(session?.user || null);
    }

    document.addEventListener('DOMContentLoaded', initAuth);

    // Public API
    window.ChemSpotAuth = {
        signIn:  (email, pw)       => authClient?.auth.signInWithPassword({ email, password: pw }),
        signUp:  (email, pw, meta) => authClient?.auth.signUp({ email, password: pw, options: { data: meta } }),
        signOut: ()                => authClient?.auth.signOut(),
        getUser: async ()          => {
            if (!authClient) return null;
            const { data: { session } } = await authClient.auth.getSession();
            return session?.user || null;
        },
        isAuthenticated: async () => !!(await window.ChemSpotAuth.getUser()),
    };

})();
