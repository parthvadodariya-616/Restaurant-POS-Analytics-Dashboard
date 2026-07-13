document.addEventListener('DOMContentLoaded', function () {
    const rangeButtons = document.querySelectorAll('.range-btn');
    const exportBtn = document.getElementById('export-items-btn');

    let salesChart, orderTypeChart, paymentMethodChart, topItemsChart;
    let currentRange = '7d';

    async function loadDashboardData(range = '7d') {
        currentRange = range;

        const res = await fetch(`/api/analytics/dashboard?range=${range}`);
        const data = await res.json();

        // --- Update KPIs ---
        document.getElementById('kpi-total-sales').textContent = `₹${data.kpis.total_sales.toFixed(2)}`;
        document.getElementById('kpi-total-orders').textContent = data.kpis.total_orders;
        document.getElementById('kpi-avg-order').textContent = `₹${data.kpis.avg_order_value.toFixed(2)}`;

        // --- Sales Trends ---
        if (salesChart) salesChart.destroy();
        salesChart = new Chart(document.getElementById('salesChart'), {
            type: 'line',
            data: {
                labels: data.sales_trends.labels,
                datasets: [{
                    label: 'Total Sales (₹)',
                    data: data.sales_trends.data,
                    borderColor: '#38bdf8',
                    backgroundColor: 'rgba(56, 189, 248, 0.2)',
                    fill: true,
                    tension: 0.4
                }]
            }
        });

        // --- Order Type ---
        if (orderTypeChart) orderTypeChart.destroy();
        orderTypeChart = new Chart(document.getElementById('orderTypeChart'), {
            type: 'pie',
            data: {
                labels: data.order_type.labels,
                datasets: [{
                    data: data.order_type.values,
                    backgroundColor: ['#38bdf8', '#f87171', '#4ade80']
                }]
            }
        });

        // --- Payment Method ---
        if (paymentMethodChart) paymentMethodChart.destroy();
        paymentMethodChart = new Chart(document.getElementById('paymentMethodChart'), {
            type: 'doughnut',
            data: {
                labels: data.payment_methods.labels,
                datasets: [{
                    data: data.payment_methods.values,
                    backgroundColor: ['#fbbf24', '#60a5fa', '#f472b6']
                }]
            }
        });

        // --- Top Selling Items ---
        if (topItemsChart) topItemsChart.destroy();
        topItemsChart = new Chart(document.getElementById('topItemsChart'), {
            type: 'bar',
            data: {
                labels: data.top_items.labels,
                datasets: [{
                    label: 'Quantity Sold',
                    data: data.top_items.values,
                    backgroundColor: '#34d399'
                }]
            },
            options: { indexAxis: 'y' }
        });

        // --- All Items Table ---
        const tableBody = document.getElementById('all-items-table');
        tableBody.innerHTML = '';
        data.all_items.labels.forEach((itemName, index) => {
            const row = document.createElement('tr');
            row.innerHTML = `<td class="py-2">${itemName}</td><td class="py-2">${data.all_items.values[index]}</td>`;
            tableBody.appendChild(row);
        });

        // --- Active Button Style ---
        rangeButtons.forEach(btn => {
            if (btn.dataset.range === range) {
                btn.classList.add('bg-blue-500', 'text-white');
                btn.classList.remove('bg-gray-300', 'dark:bg-gray-700', 'dark:text-gray-200');
            } else {
                btn.classList.remove('bg-blue-500', 'text-white');
                btn.classList.add('bg-gray-300', 'dark:bg-gray-700', 'dark:text-gray-200');
            }
        });
    }

    // Button click events
    rangeButtons.forEach(btn => {
        btn.addEventListener('click', () => loadDashboardData(btn.dataset.range));
    });

    // Export CSV
    exportBtn.addEventListener('click', () => {
        window.location.href = `/api/analytics/items-sales/export?range=${currentRange}`;
    });

    // Load default
    loadDashboardData('7d');
});
