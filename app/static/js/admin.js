document.addEventListener('DOMContentLoaded', function() {
    const menuTableBody = document.getElementById('menu-table-body');
    const uploadForm = document.getElementById('uploadCsvForm');
    const csvMessageEl = document.getElementById('csv-message');

    async function fetchAdminMenu() {
        if (!menuTableBody) return;
        try {
            const response = await fetch('/api/admin/menu');
            if (!response.ok) throw new Error('Failed to fetch menu. Are you logged in?');
            
            const items = await response.json();
            menuTableBody.innerHTML = '';
            
            items.forEach(item => {
                const row = document.createElement('tr');
                row.className = 'border-b border-slate-700';
                row.innerHTML = `<td class="p-3">${item.name}</td><td class="p-3">${item.category}</td><td class="p-3">₹${item.price.toFixed(2)}</td><td class="p-3">${item.is_available ? '<span class="text-green-400 font-semibold">Yes</span>' : '<span class="text-red-400 font-semibold">No</span>'}</td>`;
                menuTableBody.appendChild(row);
            });
        } catch (error) {
            menuTableBody.innerHTML = `<tr><td colspan="4" class="text-center text-red-400 p-4">${error.message}</td></tr>`;
        }
    }

    if (uploadForm) {
        uploadForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            const formData = new FormData(this);
            csvMessageEl.textContent = 'Uploading...';
            csvMessageEl.className = 'mt-4 text-sm text-sky-400';
            
            try {
                const response = await fetch('/api/admin/menu/upload', {
                    method: 'POST',
                    body: formData,
                });
                const result = await response.json();
                if (response.ok) {
                    csvMessageEl.textContent = 'Menu imported successfully!';
                    csvMessageEl.className = 'mt-4 text-sm text-green-400';
                    fetchAdminMenu();
                } else {
                    throw new Error(result.error || 'Upload failed');
                }
            } catch (error) {
                csvMessageEl.textContent = `Error: ${error.message}`;
                csvMessageEl.className = 'mt-4 text-sm text-red-400';
            }
        });
    }

    fetchAdminMenu();
});
