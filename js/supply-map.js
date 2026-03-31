/**
 * ChemistrySpot — supply-map.js
 * Global supply chain map widget for index.html
 * Leaflet.js + CartoDB dark tiles + Supabase data
 */

console.log('[supply-map] script loaded');
// No IIFE / no 'use strict' — avoids cross-script let scoping edge cases

    // ── CONFIG ───────────────────────────────────────────────────────────────
    const EXCIPIENTS = [
        "Tous",
        "Cellulose Microcristalline",
        "Mannitol",
        "Lactose",
        "Hypromellose (HPMC)",
        "Stéarate de Magnésium",
    ];

    const RISK_COLORS = {
        1: "#e8a0b4",   // Faible
        2: "#4fc3f7",   // Faible-Modéré
        3: "#f0b429",   // Modéré
        4: "#fb923c",   // Élevé
        5: "#ef4444",   // Critique
    };

    const RISK_LABELS = {
        1: "Faible",
        2: "Faible-Modéré",
        3: "Modéré",
        4: "Élevé",
        5: "Critique",
    };

    // HHI thresholds (Herfindahl-Hirschman Index, 0-10000)
    const HHI_COMPETITIVE   = 1500;   // < 1500: marché concurrentiel
    const HHI_MODERATE      = 2500;   // 1500-2500: concentration modérée
    // > 2500: concentration élevée, alerte rouge

    // ── STATE ────────────────────────────────────────────────────────────────
    let mapInstance     = null;
    let markersLayer    = null;
    let allTradeData    = [];
    let allRiskData     = {};   // iso3 → risk record
    let activeExcipient = "Tous";
    let mapInitialized  = false;

    // Supplier layer state
    let suppliersLayer  = null;   // L.markerClusterGroup
    let allSuppliersData = [];    // [{id, name, country, latitude, longitude, excipient_names}]
    let activeMapView   = 'exportateurs'; // 'exportateurs' | 'fournisseurs' | 'les-deux'

    let activeRiskFilter   = 0;     // 0 = all, 1-5 = specific risk level
    let activeCountryFilter = '';   // empty = all countries
    let activeSearchQuery  = '';    // empty = no filter

    // ── INIT ─────────────────────────────────────────────────────────────────
    function initSupplyMap() {
        if (mapInitialized) return;
        mapInitialized = true;
        console.log('[supply-map] initSupplyMap called');

        const mapEl = document.getElementById('supplyMap');
        if (!mapEl) { console.error('[supply-map] #supplyMap not found'); return; }

        // Map
        mapInstance = L.map('supplyMap', {
            center:          [25, 15],
            zoom:            2,
            minZoom:         1,
            maxZoom:         7,
            zoomControl:     true,
            attributionControl: true,
        });

        // Dark tile layer (CartoDB Dark Matter)
        L.tileLayer(
            'https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png',
            {
                attribution: '&copy; <a href="https://carto.com/">CARTO</a> &copy; OSM contributors',
                subdomains: 'abcd',
                maxZoom: 19,
            }
        ).addTo(mapInstance);

        markersLayer = L.layerGroup().addTo(mapInstance);

        // Force reflow — 500ms to let the grid/flex layout fully settle
        setTimeout(function () { mapInstance.invalidateSize(); }, 500);

        // Load data then render
        loadData().then(function() {
            loadSuppliers().then(function() {
                renderLayerToggle();
            });
        });
    }

    // ── DATA FETCH ───────────────────────────────────────────────────────────

    // supabaseClient is assigned async in supabase-config.js DOMContentLoaded.
    // Poll until it's ready (max 8s) before querying.
    function waitForClient(maxMs) {
        maxMs = maxMs || 8000;
        return new Promise(function (resolve, reject) {
            if (typeof supabaseClient !== 'undefined' && supabaseClient) {
                return resolve(supabaseClient);
            }
            var elapsed = 0;
            var interval = setInterval(function () {
                elapsed += 100;
                if (typeof supabaseClient !== 'undefined' && supabaseClient) {
                    clearInterval(interval);
                    resolve(supabaseClient);
                } else if (elapsed >= maxMs) {
                    clearInterval(interval);
                    reject(new Error('Supabase client non disponible après ' + maxMs + 'ms'));
                }
            }, 100);
        });
    }

    async function loadData() {
        showMapLoading(true);
        console.log('[supply-map] loadData called');
        try {
            const client = await waitForClient();
            console.log('[supply-map] Supabase client ready, querying...');
            const [tradeRes, riskRes] = await Promise.all([
                client.from('supply_chain_data').select('*').order('rank_in_excipient'),
                client.from('geopolitical_risks').select('*'),
            ]);

            allTradeData = tradeRes.data || [];
            (riskRes.data || []).forEach(r => { allRiskData[r.country_iso3] = r; });
            console.log('[supply-map] data loaded:', allTradeData.length, 'trade rows,', Object.keys(allRiskData).length, 'risk countries');

            if (allTradeData.length === 0) {
                showEmptyState("Aucune donnée supply chain disponible. Exécutez scripts/fetch_comtrade.py.");
                return;
            }

            renderFilters();
            populateCountryDropdown();
            initSearchBar();
            renderMarkers(activeExcipient);
            renderHhiPanel(activeExcipient);
        } catch (err) {
            console.error('[supply-map] loadData error:', err);
            showEmptyState("Erreur chargement données : " + err.message);
        } finally {
            showMapLoading(false);
        }
    }

    // ── SUPPLIER DATA FETCH ───────────────────────────────────────────────────
    async function loadSuppliers() {
        try {
            const client = await waitForClient(5000);

            const [suppRes, linksRes, excRes] = await Promise.all([
                client.from('suppliers')
                    .select('id, name, country, latitude, longitude')
                    .not('latitude', 'is', null)
                    .not('longitude', 'is', null),
                client.from('excipient_suppliers')
                    .select('supplier_id, excipient_id'),
                client.from('excipients')
                    .select('id, nom_commun'),
            ]);

            const suppliers = suppRes.data || [];
            const links     = linksRes.data || [];
            const excipients = excRes.data || [];

            const excipientMap = {};
            excipients.forEach(function(e) { excipientMap[e.id] = e.nom_commun; });

            const supplierExcipients = {};
            links.forEach(function(l) {
                if (!supplierExcipients[l.supplier_id]) supplierExcipients[l.supplier_id] = [];
                if (excipientMap[l.excipient_id]) {
                    supplierExcipients[l.supplier_id].push(excipientMap[l.excipient_id]);
                }
            });

            allSuppliersData = suppliers.map(function(s) {
                return Object.assign({}, s, { excipient_names: supplierExcipients[s.id] || [] });
            });

            console.log('[supply-map] suppliers loaded:', allSuppliersData.length, 'with coordinates');

            // Update country count badge
            const countEl = document.getElementById('smapCountryCount');
            if (countEl && allSuppliersData.length > 0) {
                const countries = new Set(allSuppliersData.map(function(s) { return s.country; }));
                countEl.textContent = countries.size + ' pays';
            }
        } catch (err) {
            console.warn('[supply-map] loadSuppliers error (non-fatal):', err.message);
        }
    }

    // ── SUPPLIER MARKERS ─────────────────────────────────────────────────────
    function renderSupplierMarkers() {
        if (suppliersLayer) {
            mapInstance.removeLayer(suppliersLayer);
            suppliersLayer = null;
        }
        if (!allSuppliersData.length || typeof L.markerClusterGroup !== 'function') return;

        suppliersLayer = L.markerClusterGroup({
            maxClusterRadius: 40,
            iconCreateFunction: function(cluster) {
                var count = cluster.getChildCount();
                return L.divIcon({
                    html: '<div class="smap-cluster">' + count + '</div>',
                    className: '',
                    iconSize: [32, 32],
                });
            },
        });

        allSuppliersData.forEach(function(sup) {
            var lat = parseFloat(sup.latitude);
            var lng = parseFloat(sup.longitude);
            if (isNaN(lat) || isNaN(lng)) return;

            var icon = L.divIcon({
                html: '<div class="smap-pin"></div>',
                className: '',
                iconSize: [12, 12],
                iconAnchor: [6, 6],
            });

            var excipientList = sup.excipient_names.length > 0
                ? sup.excipient_names.slice(0, 5).map(function(n) {
                    return '<span class="smap-tag">' + n + '</span>';
                  }).join(' ')
                : '<span style="color:#7a5060;">Aucun excipient listé</span>';

            var popup = L.popup({ className: 'smap-popup', maxWidth: 260 }).setContent(
                '<div style="font-weight:600;color:#e8a0b4;margin-bottom:.35rem;">' + sup.name + '</div>'
                + '<div style="font-size:.78rem;color:#b8909a;margin-bottom:.5rem;">📍 ' + sup.country + '</div>'
                + '<div style="font-size:.72rem;color:#7a5060;margin-bottom:.3rem;text-transform:uppercase;letter-spacing:.05em;">Excipients fournis</div>'
                + '<div style="font-size:.76rem;line-height:1.6;">' + excipientList + '</div>'
            );

            var marker = L.marker([lat, lng], { icon: icon }).bindPopup(popup);
            suppliersLayer.addLayer(marker);
        });

        mapInstance.addLayer(suppliersLayer);
    }

    // ── LAYER TOGGLE ─────────────────────────────────────────────────────────
    function renderLayerToggle() {
        var existing = document.getElementById('smapLayerToggle');
        if (existing) existing.remove();

        var bar = document.createElement('div');
        bar.id = 'smapLayerToggle';
        bar.style.cssText = 'position:absolute;top:10px;right:10px;z-index:1000;display:flex;gap:4px;background:rgba(10,14,26,.85);border:1px solid rgba(232,160,180,.2);border-radius:6px;padding:4px;backdrop-filter:blur(4px);';

        var views = [
            { id: 'exportateurs', label: 'Exportateurs' },
            { id: 'fournisseurs', label: 'Fournisseurs' },
            { id: 'les-deux',     label: 'Les deux' },
        ];

        views.forEach(function(v) {
            var btn = document.createElement('button');
            btn.textContent = v.label;
            btn.dataset.view = v.id;
            btn.style.cssText = 'font-size:.72rem;padding:4px 9px;border:none;border-radius:4px;cursor:pointer;transition:all .15s;font-family:inherit;'
                + (activeMapView === v.id
                    ? 'background:#e8a0b4;color:#0a0e1a;font-weight:700;'
                    : 'background:transparent;color:#b8909a;');
            btn.onclick = function() { window._supplyMapView(v.id); };
            bar.appendChild(btn);
        });

        var mapEl = document.getElementById('supplyMap');
        if (mapEl) mapEl.appendChild(bar);
    }

    window._supplyMapView = function(view) {
        activeMapView = view;

        // Update button styles
        document.querySelectorAll('[data-view]').forEach(function(btn) {
            var isActive = btn.dataset.view === view;
            btn.style.background = isActive ? 'rgba(232,160,180,.12)' : 'transparent';
            btn.style.color = isActive ? '#e8a0b4' : '#b8909a';
            btn.style.fontWeight = isActive ? '700' : '400';
            btn.style.borderColor = isActive ? 'rgba(232,160,180,.3)' : 'rgba(255,255,255,.1)';
        });

        if (view === 'exportateurs') {
            applyFilters();
            if (suppliersLayer) mapInstance.removeLayer(suppliersLayer);
        } else if (view === 'fournisseurs') {
            markersLayer.clearLayers();
            if (suppliersLayer) mapInstance.removeLayer(suppliersLayer);
            renderFilteredSuppliers();
        } else { // les-deux
            applyFilters();
            renderFilteredSuppliers();
        }
    };

    // ── FILTERS ──────────────────────────────────────────────────────────────
    function renderFilters() {
        const bar = document.getElementById('supplyMapFilters');
        if (!bar) return;

        // Only show excipients that have data
        const available = ["Tous", ...new Set(allTradeData.map(d => d.excipient_nom))];

        bar.innerHTML = available.map(name =>
            `<button class="smap-filter-btn ${name === activeExcipient ? 'active' : ''}"
                     onclick="window._supplyMapFilter('${name.replace(/'/g, "\\'")}')"
                     title="${name}">
                ${name === "Tous" ? "Tous" : name.split(' ')[0]}
            </button>`
        ).join('');
    }

    window._supplyMapFilter = function (excipient) {
        activeExcipient = excipient;
        document.querySelectorAll('.smap-filter-btn').forEach(btn => {
            btn.classList.toggle('active', btn.title === excipient);
        });
        applyFilters();
        renderHhiPanel(excipient);
    };

    // ── MARKERS ──────────────────────────────────────────────────────────────
    function renderMarkers(excipientFilter) {
        markersLayer.clearLayers();

        const data = excipientFilter === "Tous"
            ? allTradeData
            : allTradeData.filter(d => d.excipient_nom === excipientFilter);

        // Aggregate by country when showing "Tous" (sum values)
        const byCountry = {};
        data.forEach(d => {
            if (!d.lat || !d.lng) return;
            const key = d.country_iso3;
            if (!byCountry[key]) {
                byCountry[key] = {
                    iso3:         d.country_iso3,
                    name:         d.country_name,
                    lat:          parseFloat(d.lat),
                    lng:          parseFloat(d.lng),
                    total_value:  0,
                    excipients:   [],
                };
            }
            byCountry[key].total_value  += d.export_value_usd || 0;
            byCountry[key].excipients.push({
                nom:   d.excipient_nom,
                share: d.market_share_pct,
                rank:  d.rank_in_excipient,
                value: d.export_value_usd,
            });
        });

        const allValues = Object.values(byCountry).map(c => c.total_value);
        const maxValue  = Math.max(...allValues, 1);

        Object.values(byCountry).forEach(country => {
            const risk     = allRiskData[country.iso3] || { risk_level: 1, risk_label: 'Inconnu' };
            const color    = RISK_COLORS[risk.risk_level] || '#b8909a';
            const radius   = 8 + (country.total_value / maxValue) * 28;

            const circle = L.circleMarker([country.lat, country.lng], {
                radius:      radius,
                fillColor:   color,
                color:       color,
                weight:      1.5,
                opacity:     0.9,
                fillOpacity: 0.45,
            });

            circle.bindPopup(buildPopup(country, risk, excipientFilter), {
                maxWidth: 300,
                className: 'smap-popup',
            });

            circle.on('click', function() {
                showCountrySuppliers(country.name, country.iso3);
            });

            circle.addTo(markersLayer);
        });
    }

    function buildPopup(country, risk, excipientFilter) {
        const riskColor = RISK_COLORS[risk.risk_level] || '#b8909a';
        const riskLabel = risk.risk_label || RISK_LABELS[risk.risk_level] || '—';

        const excItems = country.excipients
            .sort((a, b) => b.value - a.value)
            .map(e => `
                <div style="display:flex;justify-content:space-between;padding:.2rem 0;border-bottom:1px solid rgba(255,255,255,.06);font-size:.78rem;">
                    <span style="color:#f0d4dc;">${e.nom}</span>
                    <span style="font-family:monospace;color:${riskColor};">${e.share != null ? e.share.toFixed(1) + '%' : '—'}</span>
                </div>`)
            .join('');

        const factorsHtml = (risk.risk_factors || []).length
            ? `<div style="margin-top:.5rem;font-size:.73rem;color:#f0b429;">
                ⚠ ${risk.risk_factors.slice(0, 3).join(' · ')}
               </div>`
            : '';

        const sanctionsHtml = risk.sanctions_active
            ? `<span style="background:#ef444422;color:#ef4444;border:1px solid #ef444455;border-radius:10px;padding:.1rem .5rem;font-size:.68rem;font-weight:700;">🚫 SANCTIONS</span>`
            : '';
        const restrictHtml = risk.export_restrictions
            ? `<span style="background:#f0b42922;color:#f0b429;border:1px solid #f0b42955;border-radius:10px;padding:.1rem .5rem;font-size:.68rem;font-weight:700;">⚠ RESTRICTIONS EXPORT</span>`
            : '';

        return `
        <div style="font-family:-apple-system,BlinkMacSystemFont,'Inter',sans-serif;padding:.25rem;">
            <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:.6rem;">
                <strong style="font-size:.95rem;color:#f5e6ea;">${country.name}</strong>
                <span style="background:${riskColor}22;color:${riskColor};border:1px solid ${riskColor}55;border-radius:12px;padding:.15rem .55rem;font-size:.7rem;font-weight:700;margin-left:.5rem;">${riskLabel}</span>
            </div>
            <div style="display:flex;gap:.35rem;flex-wrap:wrap;margin-bottom:.55rem;">
                ${sanctionsHtml}${restrictHtml}
            </div>
            <div style="font-size:.72rem;color:#b8909a;margin-bottom:.4rem;text-transform:uppercase;letter-spacing:.05em;">Parts de marché</div>
            ${excItems}
            ${factorsHtml}
            ${risk.notes ? `<div style="margin-top:.5rem;font-size:.73rem;color:#b8909a;line-height:1.4;">${risk.notes}</div>` : ''}
        </div>`;
    }

    // ── HHI PANEL ────────────────────────────────────────────────────────────
    function computeHHI(excipient) {
        const data = excipient === "Tous" ? [] :
            allTradeData.filter(d => d.excipient_nom === excipient);
        if (!data.length) return null;
        const hhi = data.reduce((sum, d) => sum + Math.pow(d.market_share_pct || 0, 2), 0);
        return Math.round(hhi);
    }

    function renderHhiPanel(excipient) {
        const panel = document.getElementById('supplyHhiPanel');
        if (!panel) return;

        if (excipient === "Tous") {
            // Show mini HHI for each excipient
            const excipients = [...new Set(allTradeData.map(d => d.excipient_nom))];
            panel.innerHTML = `
            <div style="font-size:.7rem;text-transform:uppercase;letter-spacing:.07em;color:#b8909a;margin-bottom:.5rem;">Indice HHI par excipient</div>
            ${excipients.map(e => {
                const h = computeHHI(e);
                if (h == null) return '';
                const { color, label } = hhiMeta(h);
                return `<div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:.3rem;font-size:.78rem;">
                    <span style="color:#f0d4dc;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;max-width:160px;" title="${e}">${e.split(' ')[0]}</span>
                    <span style="font-family:monospace;color:${color};font-weight:700;margin-left:.5rem;">${h.toLocaleString()}</span>
                    <span style="background:${color}22;color:${color};border-radius:8px;padding:.05rem .4rem;font-size:.65rem;margin-left:.3rem;">${label}</span>
                </div>`;
            }).join('')}
            <div style="margin-top:.6rem;font-size:.67rem;color:#7a5060;border-top:1px solid rgba(255,255,255,.06);padding-top:.5rem;">
                HHI &lt;1500 : compétitif · 1500–2500 : modéré · &gt;2500 : 🚨 concentration
            </div>`;
        } else {
            const hhi = computeHHI(excipient);
            if (hhi == null) { panel.innerHTML = ''; return; }
            const { color, label, alert } = hhiMeta(hhi);
            panel.innerHTML = `
            <div style="font-size:.7rem;text-transform:uppercase;letter-spacing:.07em;color:#b8909a;margin-bottom:.4rem;">Indice HHI — Concentration</div>
            <div style="display:flex;align-items:center;gap:.6rem;flex-wrap:wrap;">
                <span style="font-size:1.6rem;font-weight:800;font-family:monospace;color:${color};">${hhi.toLocaleString()}</span>
                <span style="background:${color}22;color:${color};border:1px solid ${color}55;border-radius:12px;padding:.2rem .65rem;font-size:.75rem;font-weight:700;">${label}</span>
                ${alert ? `<span style="background:#ef444415;color:#ef4444;border:1px solid #ef444440;border-radius:12px;padding:.2rem .65rem;font-size:.72rem;font-weight:700;">🚨 Risque concentration</span>` : ''}
            </div>
            <div style="font-size:.72rem;color:#b8909a;margin-top:.4rem;">HHI &lt;1500 compétitif · 1500–2500 modéré · &gt;2500 concentration élevée</div>`;
        }
    }

    function hhiMeta(hhi) {
        if (hhi < HHI_COMPETITIVE) return { color: '#e8a0b4', label: 'Compétitif',  alert: false };
        if (hhi < HHI_MODERATE)    return { color: '#f0b429', label: 'Modéré',       alert: false };
        return                              { color: '#ef4444', label: 'Concentré',   alert: true  };
    }

    // ── UI HELPERS ───────────────────────────────────────────────────────────
    function showMapLoading(show) {
        const el = document.getElementById('supplyMapLoading');
        if (el) el.style.display = show ? 'flex' : 'none';
    }

    function showEmptyState(msg) {
        const map = document.getElementById('supplyMap');
        if (map) map.innerHTML = `<div style="display:flex;align-items:center;justify-content:center;height:100%;color:#b8909a;font-size:.85rem;text-align:center;padding:2rem;">${msg}</div>`;
        const hhi = document.getElementById('supplyHhiPanel');
        if (hhi) hhi.innerHTML = '';
    }

    // ── COUNTRY SUPPLIER PANEL ───────────────────────────────────────────────

    async function showCountrySuppliers(countryName, countryIso3) {
        const panel = document.getElementById('gazettePanel');
        if (!panel) return;

        // Save gazette HTML on first click so it can be restored on close
        if (!window._gazetteHTML) {
            window._gazetteHTML = panel.innerHTML;
        }

        // Show loading state
        panel.innerHTML = '<div class="sup-panel-loading">Chargement des fournisseurs…</div>';

        try {
            const client = await waitForClient();

            // Step 1: Get suppliers in this country
            const { data: suppliers, error: suppErr } = await client
                .from('suppliers')
                .select('id, name, country, website, contact_email')
                .eq('country', countryName)
                .order('name');

            if (suppErr) throw suppErr;

            if (!suppliers || suppliers.length === 0) {
                panel.innerHTML = '<div class="gazette-placeholder"><div style="font-size:.8rem;color:#7a5060;text-align:center;padding:2rem;">Aucun fournisseur référencé pour ' + countryName + '</div></div>';
                return;
            }

            // Step 2: Get excipient relationships for these supplier IDs
            const supplierIds = suppliers.map(function(s) { return s.id; });
            const { data: relations, error: relErr } = await client
                .from('excipient_suppliers')
                .select('supplier_id, excipients(nom_commun)')
                .in('supplier_id', supplierIds);

            if (relErr) throw relErr;

            // Build map: supplierId → [excipient names]
            var supplierMap = {};
            (relations || []).forEach(function(r) {
                var sid = r.supplier_id;
                if (!supplierMap[sid]) supplierMap[sid] = [];
                if (r.excipients && r.excipients.nom_commun) {
                    supplierMap[sid].push(r.excipients.nom_commun);
                }
            });

            // Render supplier cards
            var cardsHtml = suppliers.map(function(sup) {
                var excipients = supplierMap[sup.id] || [];
                var excText = excipients.length > 0
                    ? excipients.join(' · ')
                    : '<em style="color:#444c5c;">—</em>';
                var linkHtml = sup.website
                    ? '<a href="' + sup.website + '" class="sup-card-link" target="_blank" rel="noopener">Site web ↗</a>'
                    : '';
                return '<div class="sup-card">'
                    + '<div class="sup-card-name">' + sup.name + '</div>'
                    + '<div class="sup-card-excipients">' + excText + '</div>'
                    + linkHtml
                    + '</div>';
            }).join('');

            panel.innerHTML = '<div class="sup-panel">'
                + '<div class="sup-panel-header">'
                + '<button class="sup-panel-close" onclick="closeSupplierPanel()">&#10005;</button>'
                + '<div class="sup-panel-title">Fournisseurs \u2014 ' + countryName + '</div>'
                + '<div class="sup-panel-count">' + suppliers.length + ' fournisseur' + (suppliers.length > 1 ? 's' : '') + '</div>'
                + '</div>'
                + '<div class="sup-panel-body">' + cardsHtml + '</div>'
                + '<div class="sup-panel-footer">'
                + '<a href="fournisseurs.html" class="sup-panel-all">Voir tous les fournisseurs \u2192</a>'
                + '</div>'
                + '</div>';

        } catch (err) {
            console.error('[supply-map] showCountrySuppliers error:', err);
            panel.innerHTML = '<div class="gazette-placeholder"><div style="font-size:.8rem;color:#7a5060;text-align:center;padding:2rem;">Erreur chargement : ' + err.message + '</div></div>';
        }
    }

    window.closeSupplierPanel = function() {
        var panel = document.getElementById('gazettePanel');
        if (panel && window._gazetteHTML) {
            panel.innerHTML = window._gazetteHTML;
            window._gazetteHTML = null; // allow re-saving on next click
        }
    };

    // ── FILTER LOGIC ─────────────────────────────────────────────────────────

    function applyFilters() {
        // Filter trade data
        var tradeFiltered = allTradeData.filter(function(d) {
            // Excipient filter
            if (activeExcipient !== 'Tous' && d.excipient_nom !== activeExcipient) return false;
            // Country filter (by iso3 or name)
            if (activeCountryFilter && d.country_iso3 !== activeCountryFilter) return false;
            // Search query (country name)
            if (activeSearchQuery) {
                var q = activeSearchQuery.toLowerCase();
                if (d.country_name && !d.country_name.toLowerCase().includes(q)) return false;
            }
            // Risk filter
            if (activeRiskFilter > 0) {
                var risk = allRiskData[d.country_iso3];
                if (!risk || risk.risk_level !== activeRiskFilter) return false;
            }
            return true;
        });

        // Re-render markers with filtered data (temporarily override allTradeData)
        var savedAll = allTradeData;
        allTradeData = tradeFiltered;
        renderMarkers(activeExcipient === 'Tous' ? 'Tous' : activeExcipient);
        allTradeData = savedAll;

        // Filter suppliers
        if (activeMapView === 'fournisseurs' || activeMapView === 'les-deux') {
            renderFilteredSuppliers();
        }
    }

    function renderFilteredSuppliers() {
        if (suppliersLayer) {
            mapInstance.removeLayer(suppliersLayer);
            suppliersLayer = null;
        }
        if (!allSuppliersData.length || typeof L.markerClusterGroup !== 'function') return;

        var filtered = allSuppliersData.filter(function(s) {
            if (activeCountryFilter) {
                // match by country name substring (suppliers table uses country name, not iso3)
                var riskEntry = Object.values(allRiskData).find(function(r) { return r.country_iso3 === activeCountryFilter; });
                if (riskEntry && s.country !== riskEntry.country_name) return false;
            }
            if (activeSearchQuery) {
                var q = activeSearchQuery.toLowerCase();
                var matchName = s.name && s.name.toLowerCase().includes(q);
                var matchCountry = s.country && s.country.toLowerCase().includes(q);
                var matchExcipient = s.excipient_names && s.excipient_names.some(function(e) { return e.toLowerCase().includes(q); });
                if (!matchName && !matchCountry && !matchExcipient) return false;
            }
            return true;
        });

        suppliersLayer = L.markerClusterGroup({
            maxClusterRadius: 40,
            iconCreateFunction: function(cluster) {
                var count = cluster.getChildCount();
                return L.divIcon({
                    html: '<div class="smap-cluster">' + count + '</div>',
                    className: '',
                    iconSize: [32, 32],
                });
            },
        });

        filtered.forEach(function(sup) {
            var lat = parseFloat(sup.latitude);
            var lng = parseFloat(sup.longitude);
            if (isNaN(lat) || isNaN(lng)) return;

            var icon = L.divIcon({
                html: '<div class="smap-pin"></div>',
                className: '',
                iconSize: [12, 12],
                iconAnchor: [6, 6],
            });

            var marker = L.marker([lat, lng], { icon: icon });
            marker.on('click', function() {
                if (typeof showSupplierDetail === 'function') showSupplierDetail(sup);
            });
            suppliersLayer.addLayer(marker);
        });

        mapInstance.addLayer(suppliersLayer);
    }

    function populateCountryDropdown() {
        var select = document.getElementById('smapCountryFilter');
        if (!select) return;

        var countries = [];
        var seen = {};
        allTradeData.forEach(function(d) {
            if (d.country_iso3 && !seen[d.country_iso3]) {
                seen[d.country_iso3] = true;
                countries.push({ iso3: d.country_iso3, name: d.country_name || d.country_iso3 });
            }
        });
        countries.sort(function(a, b) { return a.name.localeCompare(b.name); });

        countries.forEach(function(c) {
            var opt = document.createElement('option');
            opt.value = c.iso3;
            opt.textContent = c.name;
            select.appendChild(opt);
        });

        select.addEventListener('change', function() {
            activeCountryFilter = this.value;
            applyFilters();
        });
    }

    function initSearchBar() {
        var input = document.getElementById('smapSearch');
        if (!input) return;

        var debounceTimer = null;
        input.addEventListener('input', function() {
            clearTimeout(debounceTimer);
            var val = this.value.trim();
            debounceTimer = setTimeout(function() {
                activeSearchQuery = val;
                applyFilters();
            }, 250);
        });
    }

    function hexToRgb(hex) {
        var r = parseInt(hex.slice(1,3),16);
        var g = parseInt(hex.slice(3,5),16);
        var b = parseInt(hex.slice(5,7),16);
        return r + ',' + g + ',' + b;
    }

    window._smapRiskFilter = function(level) {
        activeRiskFilter = level;

        // Update button active styles
        document.querySelectorAll('[data-risk]').forEach(function(btn) {
            var btnLevel = parseInt(btn.dataset.risk, 10);
            var isActive = btnLevel === level;
            var riskColors = { 0: '#e8a0b4', 1: '#e8a0b4', 2: '#4fc3f7', 3: '#f0b429', 4: '#fb923c', 5: '#ef4444' };
            var col = riskColors[btnLevel] || '#b8909a';
            btn.style.background = isActive ? 'rgba(' + hexToRgb(col) + ',.15)' : 'transparent';
            btn.style.color = isActive ? col : '#b8909a';
            btn.style.borderColor = isActive ? 'rgba(' + hexToRgb(col) + ',.5)' : 'rgba(255,255,255,.1)';
        });

        applyFilters();
    };

    // ── BOOT — called explicitly from index.html inline script ───────────────
    // window.supplyMapInit() is called by the inline <script> after all deps load
