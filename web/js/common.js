/**
 * Common JavaScript functions for SQL E-commerce Connector Web UI
 */

const API_URL = 'http://localhost:8000';
const ADMIN_URL = 'http://localhost:8001';

/**
 * Check if user is authenticated
 */
function checkAuth() {
    const token = localStorage.getItem('token');
    if (!token) {
        window.location.href = 'login.html';
        return false;
    }
    return true;
}

/**
 * Logout user
 */
function logout() {
    localStorage.removeItem('token');
    localStorage.removeItem('username');
    window.location.href = 'login.html';
}

/**
 * Get authorization headers
 */
function getHeaders() {
    return {
        'Authorization': `Bearer ${localStorage.getItem('token')}`,
        'Content-Type': 'application/json'
    };
}

/**
 * Fetch data from API with error handling
 */
async function fetchAPI(endpoint, options = {}) {
    try {
        const url = endpoint.startsWith('http') ? endpoint : `${API_URL}${endpoint}`;
        const response = await fetch(url, {
            ...options,
            headers: {
                ...getHeaders(),
                ...options.headers
            }
        });

        if (response.status === 401) {
            logout();
            return null;
        }

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'API request failed');
        }

        return await response.json();
    } catch (error) {
        console.error('API Error:', error);
        showToast(error.message, 'danger');
        throw error;
    }
}

/**
 * Show toast notification
 */
function showToast(message, type = 'info') {
    const toastContainer = document.getElementById('toast-container') || createToastContainer();

    const toastId = 'toast-' + Date.now();
    const toast = document.createElement('div');
    toast.className = 'toast show';
    toast.setAttribute('role', 'alert');
    toast.id = toastId;

    const bgClass = {
        'success': 'bg-success',
        'danger': 'bg-danger',
        'warning': 'bg-warning',
        'info': 'bg-info'
    }[type] || 'bg-info';

    const icon = {
        'success': 'bi-check-circle',
        'danger': 'bi-exclamation-circle',
        'warning': 'bi-exclamation-triangle',
        'info': 'bi-info-circle'
    }[type] || 'bi-info-circle';

    toast.innerHTML = `
        <div class="toast-header ${bgClass} text-white">
            <i class="bi ${icon} me-2"></i>
            <strong class="me-auto">Notification</strong>
            <button type="button" class="btn-close btn-close-white" data-bs-dismiss="toast"></button>
        </div>
        <div class="toast-body">
            ${message}
        </div>
    `;

    toastContainer.appendChild(toast);

    // Auto remove after 5 seconds
    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => toast.remove(), 300);
    }, 5000);
}

/**
 * Create toast container if it doesn't exist
 */
function createToastContainer() {
    const container = document.createElement('div');
    container.id = 'toast-container';
    container.className = 'toast-container position-fixed top-0 end-0 p-3';
    container.style.zIndex = '9999';
    document.body.appendChild(container);
    return container;
}

/**
 * Show loading overlay
 */
function showLoading(message = 'Loading...') {
    let overlay = document.getElementById('loading-overlay');
    if (!overlay) {
        overlay = document.createElement('div');
        overlay.id = 'loading-overlay';
        overlay.className = 'loading-overlay';
        document.body.appendChild(overlay);
    }

    overlay.innerHTML = `
        <div class="loading-spinner">
            <div class="spinner-border text-primary" style="width: 3rem; height: 3rem;" role="status">
                <span class="visually-hidden">Loading...</span>
            </div>
            <p class="mt-3 fw-bold">${message}</p>
        </div>
    `;
    overlay.style.display = 'flex';
}

/**
 * Hide loading overlay
 */
function hideLoading() {
    const overlay = document.getElementById('loading-overlay');
    if (overlay) {
        overlay.style.display = 'none';
    }
}

/**
 * Format date to locale string
 */
function formatDate(dateString) {
    if (!dateString) return '-';
    const date = new Date(dateString);
    return date.toLocaleString();
}

/**
 * Format platform type with icon
 */
function formatPlatformType(type) {
    const icons = {
        'shopify': '<i class="bi bi-shop text-success"></i> Shopify',
        'woocommerce': '<i class="bi bi-cart text-primary"></i> WooCommerce'
    };
    return icons[type] || type;
}

/**
 * Format database type with icon
 */
function formatDatabaseType(type) {
    const icons = {
        'postgresql': '<i class="bi bi-database text-info"></i> PostgreSQL',
        'mysql': '<i class="bi bi-database text-warning"></i> MySQL',
        'mssql': '<i class="bi bi-database text-danger"></i> MS SQL',
        'sqlite': '<i class="bi bi-database text-secondary"></i> SQLite'
    };
    return icons[type] || type;
}

/**
 * Format sync direction
 */
function formatSyncDirection(direction) {
    const formats = {
        'to_platform': '<i class="bi bi-arrow-up"></i> To Platform',
        'from_platform': '<i class="bi bi-arrow-down"></i> From Platform',
        'bidirectional': '<i class="bi bi-arrow-left-right"></i> Bidirectional'
    };
    return formats[direction] || direction;
}

/**
 * Format status badge
 */
function formatStatus(status) {
    const badges = {
        'active': '<span class="badge bg-success">Active</span>',
        'inactive': '<span class="badge bg-secondary">Inactive</span>',
        'error': '<span class="badge bg-danger">Error</span>',
        'completed': '<span class="badge bg-success">Completed</span>',
        'running': '<span class="badge bg-primary">Running</span>',
        'failed': '<span class="badge bg-danger">Failed</span>'
    };
    return badges[status] || `<span class="badge bg-secondary">${status}</span>`;
}

/**
 * Confirm dialog
 */
function confirmDialog(message) {
    return confirm(message);
}

/**
 * Get URL parameter
 */
function getURLParameter(name) {
    const urlParams = new URLSearchParams(window.location.search);
    return urlParams.get(name);
}

/**
 * Copy to clipboard
 */
function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        showToast('Copied to clipboard!', 'success');
    }).catch(() => {
        showToast('Failed to copy', 'danger');
    });
}

/**
 * Download JSON data
 */
function downloadJSON(data, filename) {
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}

/**
 * Initialize tooltips
 */
function initTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

/**
 * Initialize on page load
 */
document.addEventListener('DOMContentLoaded', function() {
    initTooltips();
});
