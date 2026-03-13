/**
 * ChemistrySpot — supply-map.js
 * Global supply chain map widget for index.html
 * Leaflet.js + CartoDB dark tiles + Supabase data
 */

(function () {
    'use strict';
    console.log('[supply-map] script loaded');

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
        1: "#00d4aa",   // Faible
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
        loadData();
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
            renderMarkers(activeExcipient);
            renderHhiPanel(activeExcipient);
        } catch (err) {
            console.error('[supply-map] loadData error:', err);
            showEmptyState("Erreur chargement données : " + err.message);
        } finally {
            showMapLoading(false);
        }
    }

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
        renderMarkers(excipient);
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
            const color    = RISK_COLORS[risk.risk_level] || '#8892a4';
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

            circle.addTo(markersLayer);
        });
    }

    function buildPopup(country, risk, excipientFilter) {
        const riskColor = RISK_COLORS[risk.risk_level] || '#8892a4';
        const riskLabel = risk.risk_label || RISK_LABELS[risk.risk_level] || '—';

        const excItems = country.excipients
            .sort((a, b) => b.value - a.value)
            .map(e => `
                <div style="display:flex;justify-content:space-between;padding:.2rem 0;border-bottom:1px solid rgba(255,255,255,.06);font-size:.78rem;">
                    <span style="color:#c0cfe0;">${e.nom}</span>
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
                <strong style="font-size:.95rem;color:#e8f4f8;">${country.name}</strong>
                <span style="background:${riskColor}22;color:${riskColor};border:1px solid ${riskColor}55;border-radius:12px;padding:.15rem .55rem;font-size:.7rem;font-weight:700;margin-left:.5rem;">${riskLabel}</span>
            </div>
            <div style="display:flex;gap:.35rem;flex-wrap:wrap;margin-bottom:.55rem;">
                ${sanctionsHtml}${restrictHtml}
            </div>
            <div style="font-size:.72rem;color:#8892a4;margin-bottom:.4rem;text-transform:uppercase;letter-spacing:.05em;">Parts de marché</div>
            ${excItems}
            ${factorsHtml}
            ${risk.notes ? `<div style="margin-top:.5rem;font-size:.73rem;color:#8892a4;line-height:1.4;">${risk.notes}</div>` : ''}
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
            <div style="font-size:.7rem;text-transform:uppercase;letter-spacing:.07em;color:#8892a4;margin-bottom:.5rem;">Indice HHI par excipient</div>
            ${excipients.map(e => {
                const h = computeHHI(e);
                if (h == null) return '';
                const { color, label } = hhiMeta(h);
                return `<div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:.3rem;font-size:.78rem;">
                    <span style="color:#c0cfe0;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;max-width:160px;" title="${e}">${e.split(' ')[0]}</span>
                    <span style="font-family:monospace;color:${color};font-weight:700;margin-left:.5rem;">${h.toLocaleString()}</span>
                    <span style="background:${color}22;color:${color};border-radius:8px;padding:.05rem .4rem;font-size:.65rem;margin-left:.3rem;">${label}</span>
                </div>`;
            }).join('')}
            <div style="margin-top:.6rem;font-size:.67rem;color:#555e70;border-top:1px solid rgba(255,255,255,.06);padding-top:.5rem;">
                HHI &lt;1500 : compétitif · 1500–2500 : modéré · &gt;2500 : 🚨 concentration
            </div>`;
        } else {
            const hhi = computeHHI(excipient);
            if (hhi == null) { panel.innerHTML = ''; return; }
            const { color, label, alert } = hhiMeta(hhi);
            panel.innerHTML = `
            <div style="font-size:.7rem;text-transform:uppercase;letter-spacing:.07em;color:#8892a4;margin-bottom:.4rem;">Indice HHI — Concentration</div>
            <div style="display:flex;align-items:center;gap:.6rem;flex-wrap:wrap;">
                <span style="font-size:1.6rem;font-weight:800;font-family:monospace;color:${color};">${hhi.toLocaleString()}</span>
                <span style="background:${color}22;color:${color};border:1px solid ${color}55;border-radius:12px;padding:.2rem .65rem;font-size:.75rem;font-weight:700;">${label}</span>
                ${alert ? `<span style="background:#ef444415;color:#ef4444;border:1px solid #ef444440;border-radius:12px;padding:.2rem .65rem;font-size:.72rem;font-weight:700;">🚨 Risque concentration</span>` : ''}
            </div>
            <div style="font-size:.72rem;color:#8892a4;margin-top:.4rem;">HHI &lt;1500 compétitif · 1500–2500 modéré · &gt;2500 concentration élevée</div>`;
        }
    }

    function hhiMeta(hhi) {
        if (hhi < HHI_COMPETITIVE) return { color: '#00d4aa', label: 'Compétitif',  alert: false };
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
        if (map) map.innerHTML = `<div style="display:flex;align-items:center;justify-content:center;height:100%;color:#8892a4;font-size:.85rem;text-align:center;padding:2rem;">${msg}</div>`;
        const hhi = document.getElementById('supplyHhiPanel');
        if (hhi) hhi.innerHTML = '';
    }

    // ── INIT TRIGGER ─────────────────────────────────────────────────────────
    function setupLazyInit() {
        const section = document.getElementById('supplyMapSection');
        console.log('[supply-map] setupLazyInit, section found:', !!section);
        if (!section) { initSupplyMap(); return; }

        if ('IntersectionObserver' in window) {
            const observer = new IntersectionObserver(function (entries) {
                if (entries[0].isIntersecting) {
                    console.log('[supply-map] section intersecting, init map');
                    initSupplyMap();
                    observer.disconnect();
                }
            }, { threshold: 0 });  // fire as soon as 1px is visible
            observer.observe(section);
        } else {
            initSupplyMap();
        }

        // Hard fallback: init after 3s regardless (catches cases where
        // the section is off-screen and IntersectionObserver never fires
        // during the initial visit)
        setTimeout(function () { initSupplyMap(); }, 3000);
    }

    // ── BOOT ─────────────────────────────────────────────────────────────────
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', setupLazyInit);
    } else {
        setupLazyInit();
    }

})();
