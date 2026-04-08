/**
 * api.js — Shared helper functions for all frontend pages
 * Optimized for Vercel + Aiven Cloud Deployment
 */

// Check if we are on localhost
const isLocal = window.location.hostname === "127.0.0.1" || window.location.hostname === "localhost";

// Localhost Only Configuration
const API_URL = "http://127.0.0.1:5000/api"; 


// Ensure credentials are included for local session cookies
async function apiFetch(path, options = {}) {
    try {
        const res = await fetch(API_URL + path, {
            headers: { 'Content-Type': 'application/json' },
            credentials: 'include', 
            ...options,
            body: options.body ? JSON.stringify(options.body) : undefined
        });

        // 1. Check if the response is empty before parsing
        const text = await res.text(); 
        if (!text) return {}; 

        // 2. Now try to parse the text as JSON
        const data = JSON.parse(text);
        
        if (!res.ok) {
            // Only show toast if we DIDN'T ask for a silent check
            if (!options.silent) showToast(data.error || 'Error', true);
            throw new Error(data.error);
        }
        return data;
    } catch (err) {
        throw err;
    }
}

// ── Convenience methods (Matches your index.html calls) ────────
const api = {
    get:    (path)         => apiFetch(path, { method: 'GET' }),
    post:   (path, body)   => apiFetch(path, { method: 'POST',   body }),
    put:    (path, body)   => apiFetch(path, { method: 'PUT',    body }),
    delete: (path)         => apiFetch(path, { method: 'DELETE' }),
};

// ── Toast notification ────────────────────────────────────────
function showToast(msg, isError = false) {
    const t = document.getElementById('toast');
    if (!t) return;
    t.textContent = msg;
    t.className   = 'show' + (isError ? ' error' : '');
    setTimeout(() => t.className = '', 3000);
}

// ── Modal helpers ─────────────────────────────────────────────
function openModal(id)  { 
    const el = document.getElementById(id);
    if(el) el.classList.add('show'); 
}
function closeModal(id) { 
    const el = document.getElementById(id);
    if(el) el.classList.remove('show'); 
}

// ── Status badge HTML ─────────────────────────────────────────
function statusBadge(status) {
    const map = {
        available:  'badge-green',
        occupied:   'badge-red',
        reserved:   'badge-amber',
        pending:    'badge-amber',
        preparing:  'badge-blue',
        served:     'badge-blue',
        completed:  'badge-green',
        cancelled:  'badge-red',
        paid:       'badge-green',
        cash:       'badge-muted',
        card:       'badge-blue',
        upi:        'badge-blue',
    };
    return `<span class="badge ${map[status] || 'badge-muted'}">${status}</span>`;
}

// ── Format currency (INR) ─────────────────────────────────────
function rupees(amount) {
    return '₹' + parseFloat(amount || 0).toFixed(2);
}

// ── Auth guard — redirect to login if not authenticated ────────
async function requireAuth() {
    try {
        const user = await api.get('/me');
        return user;
    } catch {
        // If this points to the wrong place, it creates a "Redirect Loop"
        window.location.href = '/index.html'; 
    }
}

// ── Build sidebar HTML ────────────────────────────────────────
function renderSidebar(activePage) {
    // Adjusted paths to work from inside the 'frontend/pages/' folder
    const pages = [
        { id: 'dashboard', icon: '📊', label: 'Dashboard',       href: 'dashboard.html' },
        { id: 'orders',    icon: '🧾', label: 'Orders',          href: 'orders.html' },
        { id: 'tables',    icon: '🪑', label: 'Tables',          href: 'tables.html' },
        { id: 'menu',      icon: '🍽️',  label: 'Menu Management',  href: 'menu.html' },
        { id: 'customers', icon: '👥', label: 'Customers',        href: 'customers.html' },
        { id: 'reports',   icon: '📈', label: 'Reports',          href: 'reports.html' },
    ];

    return `
    <aside class="sidebar">
        <div class="sidebar-logo">
            🍴 Test-E
            <span>Taste The Results</span>
        </div>
        <nav class="sidebar-nav">
            <div class="nav-section-label">Main Menu</div>
            ${pages.map(p => `
                <a href="${p.href}" class="nav-item ${activePage === p.id ? 'active' : ''}">
                    <span class="icon">${p.icon}</span> ${p.label}
                </a>
            `).join('')}
        </nav>
        <div class="sidebar-footer">
            <button class="btn btn-outline btn-full" onclick="logout()">🚪 Logout</button>
        </div>
    </aside>`;
}

async function logout() {
    try {
        await api.post('/logout');
    } catch (e) {
        console.log("Logout failed or session already cleared");
    }
    window.location.href = '/index.html';
}
