const state = {
    fraudChart: null,
    page: document.body.dataset.page
};

document.addEventListener('DOMContentLoaded', () => {
    initDarkMode();
    if (state.page === 'dashboard') {
        initDashboard();
    }
    if (state.page === 'admin') {
        initAdmin();
    }
    const searchInput = document.getElementById('search-input');
    const filterStatus = document.getElementById('filter-status');

    if (searchInput) {
        searchInput.addEventListener('input', debounce(loadTransactions, 400));
    }
    if (filterStatus) {
        filterStatus.addEventListener('change', loadTransactions);
    }
});

function initDarkMode() {
    const toggle = document.getElementById('dark-mode-toggle');
    const current = localStorage.getItem('theme');
    if (current === 'dark') {
        document.body.classList.add('dark-mode');
    }
    if (toggle) {
        toggle.addEventListener('click', () => {
            document.body.classList.toggle('dark-mode');
            const theme = document.body.classList.contains('dark-mode') ? 'dark' : 'light';
            localStorage.setItem('theme', theme);
        });
    }
}

async function initDashboard() {
    showLoader();
    await loadAnalytics();
    await loadTransactions();
    hideLoader();
}

async function initAdmin() {
    showLoader();
    await loadAnalytics();
    await loadUsers();
    hideLoader();
}

async function loadAnalytics() {
    try {
        const response = await fetch('/api/analytics');
        const data = await response.json();
        document.getElementById('total-transactions').textContent = data.total_transactions;
        document.getElementById('fraud-count').textContent = data.fraud_count;
        document.getElementById('safe-count').textContent = data.safe_count;
        document.getElementById('average-probability').textContent = `${data.average_probability}%`;
        updateRecentPredictions(data.recent_transactions);
        renderFraudChart(data);
    } catch (error) {
        console.error('Analytics load failed:', error);
    }
}

function updateRecentPredictions(transactions) {
    const list = document.getElementById('recent-predictions');
    if (!list) return;
    list.innerHTML = '';
    transactions.forEach(tx => {
        const item = document.createElement('li');
        item.className = 'list-group-item d-flex justify-content-between align-items-center';
        item.innerHTML = `<span>${tx.created_at}</span><span class="badge bg-${tx.prediction === 1 ? 'danger' : 'success'}">${tx.prediction === 1 ? 'Fraud' : 'Safe'}</span>`;
        list.appendChild(item);
    });
}

function renderFraudChart(data) {
    const ctx = document.getElementById('fraudChart');
    if (!ctx) return;
    const chartData = {
        labels: ['Safe', 'Fraud'],
        datasets: [{
            data: [data.safe_count, data.fraud_count],
            backgroundColor: ['#0d6efd', '#dc3545'],
            borderWidth: 0,
            hoverOffset: 6
        }]
    };
    if (state.fraudChart) {
        state.fraudChart.data = chartData;
        state.fraudChart.update();
        return;
    }
    state.fraudChart = new Chart(ctx, {
        type: 'doughnut',
        data: chartData,
        options: {
            plugins: {
                legend: { position: 'bottom' }
            }
        }
    });
}

async function loadTransactions() {
    const query = new URLSearchParams();
    const searchInput = document.getElementById('search-input');
    const filterStatus = document.getElementById('filter-status');
    if (searchInput && searchInput.value.trim()) {
        query.append('q', searchInput.value.trim());
    }
    if (filterStatus && filterStatus.value) {
        query.append('status', filterStatus.value);
    }
    const url = `/api/transactions?${query.toString()}`;
    try {
        const response = await fetch(url);
        const data = await response.json();
        renderTransactions(data.transactions || []);
    } catch (error) {
        console.error('Transaction load failed:', error);
    }
}

function renderTransactions(transactions) {
    const tableBody = document.getElementById('transaction-body');
    if (!tableBody) return;
    tableBody.innerHTML = '';
    transactions.forEach(tx => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${tx.created_at}</td>
            <td><span class="badge bg-${tx.prediction === 1 ? 'danger' : 'success'}">${tx.status}</span></td>
            <td>${(tx.probability * 100).toFixed(2)}%</td>
            <td>${tx.email}</td>
            <td>${tx.source || 'live'}</td>
        `;
        tableBody.appendChild(row);
    });
}

async function loadUsers() {
    const tableBody = document.getElementById('user-body');
    const userCount = document.getElementById('user-count');
    if (!tableBody || !userCount) return;
    try {
        const response = await fetch('/api/users');
        const data = await response.json();
        const users = data.users || [];
        userCount.textContent = users.length;
        tableBody.innerHTML = '';
        users.forEach(user => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${user.name}</td>
                <td>${user.email}</td>
                <td>${user.role}</td>
                <td>${user.created_at}</td>
            `;
            tableBody.appendChild(row);
        });
    } catch (error) {
        console.error('User load failed:', error);
    }
}

function showLoader() {
    const loader = document.getElementById('loader');
    if (loader) loader.classList.add('active');
}

function hideLoader() {
    const loader = document.getElementById('loader');
    if (loader) loader.classList.remove('active');
}

function debounce(fn, delay) {
    let timer;
    return (...args) => {
        clearTimeout(timer);
        timer = setTimeout(() => fn(...args), delay);
    };
}
