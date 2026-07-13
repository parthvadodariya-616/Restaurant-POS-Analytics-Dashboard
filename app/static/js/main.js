document.addEventListener('DOMContentLoaded', () => {
    
    // ---- THEME SWITCHER LOGIC ----
    const htmlElement = document.documentElement;

    const applyTheme = (theme) => {
        htmlElement.classList.toggle('dark', theme === 'dark');
        const darkIcon = document.getElementById('theme-icon-dark');
        const lightIcon = document.getElementById('theme-icon-light');
        if (darkIcon && lightIcon) {
            darkIcon.classList.toggle('hidden', theme !== 'dark');
            lightIcon.classList.toggle('hidden', theme === 'dark');
        }
    };

    const savedTheme = localStorage.getItem('theme') || (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');
    applyTheme(savedTheme);

    // ---- DASHBOARD & CART LOGIC ----
    const menuGrid = document.getElementById('menu-grid');
    if (!menuGrid) return; // Exit if not on the dashboard page

    // --- Element Selectors ---
    const cartItemsTableBody = document.querySelector('#cart-items');
    const cartSubtotalEl = document.getElementById('cart-subtotal');
    const cartGstEl = document.getElementById('cart-gst');
    const cartTotalEl = document.getElementById('cart-total');
    const checkoutBtn = document.getElementById('checkout-btn');
    const clearCartBtn = document.getElementById('clear-cart-btn');
    const orderTypeButtons = document.querySelectorAll('.order-type');
    
    // --- Custom Modal Elements ---
    const customerModal = document.getElementById('customer-modal');
    const customerForm = document.getElementById('customer-form');
    const cancelModalBtn = document.getElementById('cancel-modal-btn');
    const customerPhoneInput = document.getElementById('customer-phone');
    const phoneError = document.getElementById('phone-error');
    const submitOrderBtn = document.getElementById('submit-order-btn');

    // --- State Variables ---
    let cart = [];
    let orderType = 'Dine-In';
    const GST_RATE = 0.05;

    // --- Event Listeners ---
    orderTypeButtons.forEach(button => {
        button.addEventListener('click', () => {
            orderTypeButtons.forEach(btn => btn.classList.replace('bg-blue-600', 'bg-gray-600'));
            button.classList.replace('bg-gray-600', 'bg-blue-600');
            orderType = button.dataset.type;
        });
    });

    if (clearCartBtn) clearCartBtn.addEventListener('click', clearCart);
    
    if (checkoutBtn) {
        checkoutBtn.addEventListener('click', () => {
            if (cart.length > 0) customerModal.classList.remove('hidden');
        });
    }

    if (cancelModalBtn) {
        cancelModalBtn.addEventListener('click', () => customerModal.classList.add('hidden'));
    }

    if (customerPhoneInput) {
        customerPhoneInput.addEventListener('input', () => {
            const phone = customerPhoneInput.value.replace(/\D/g, '');
            customerPhoneInput.value = phone;
            if (phone.length === 10) {
                phoneError.classList.add('hidden');
                submitOrderBtn.disabled = false;
            } else {
                phoneError.classList.remove('hidden');
                submitOrderBtn.disabled = true;
            }
        });
    }

    if (customerForm) {
        customerForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const formData = new FormData(customerForm);
            const name = formData.get('name');
            const phone = formData.get('phone');
            
            try {
                const response = await fetch('/api/order', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ cart, name, phone, orderType })
                });

                const result = await response.json();
                if (!response.ok) throw new Error(result.error || 'An unknown server error occurred.');
                
                if (result.success) {
                    window.location.href = `/payment?order_id=${result.order_id}&total=${result.total}`;
                } else {
                    alert('Error placing order: ' + (result.error || 'Unknown error'));
                }
            } catch (error) {
                console.error('Checkout error:', error);
                alert('An error occurred: ' + error.message);
            }
        });
    }

    // --- Core Functions ---
    function updateCartUI() {
        if (!cartItemsTableBody) return;
        checkoutBtn.disabled = cart.length === 0;
        if (cart.length === 0) {
            cartItemsTableBody.innerHTML = '<tr><td colspan="3" class="text-center text-slate-400 h-[72px] px-4 py-2">Your cart is empty.</td></tr>';
            cartSubtotalEl.textContent = '₹0.00';
            cartGstEl.textContent = '₹0.00';
            cartTotalEl.textContent = '₹0.00';
        } else {
            cartItemsTableBody.innerHTML = '';
            let subtotal = 0;
            cart.forEach(item => {
                const row = document.createElement('tr');
                row.className = 'border-t border-slate-700';
                row.innerHTML = `<td class="h-[72px] px-4 py-2 text-slate-400">${item.name}</td><td class="h-[72px] px-4 py-2 text-slate-400">${item.quantity}</td><td class="h-[72px] px-4 py-2 text-slate-400 text-right">₹${(item.price * item.quantity).toFixed(2)}</td>`;
                cartItemsTableBody.appendChild(row);
                subtotal += item.price * item.quantity;
            });
            const gst = subtotal * GST_RATE;
            cartSubtotalEl.textContent = `₹${subtotal.toFixed(2)}`;
            cartGstEl.textContent = `₹${gst.toFixed(2)}`;
            cartTotalEl.textContent = `₹${(subtotal + gst).toFixed(2)}`;
        }
    }

    function addToCart(item) {
        const existingItem = cart.find(cartItem => cartItem.id === item.id);
        if (existingItem) existingItem.quantity++;
        else cart.push({ ...item, quantity: 1 });
        updateCartUI();
    }

    function clearCart() {
        cart = [];
        updateCartUI();
    }

    async function fetchMenu() {
        menuGrid.innerHTML = '<p class="col-span-full text-center text-gray-600 dark:text-gray-400">Loading menu...</p>';
        try {
            const response = await fetch('/api/menu');
            if (!response.ok) throw new Error(`Network error`);
            const menuItems = await response.json();
            
            menuGrid.innerHTML = '';
            
            menuItems.forEach(item => {
                const menuItemEl = document.createElement('div');
                menuItemEl.className = 'flex flex-col gap-3 pb-3 cursor-pointer group';
                menuItemEl.innerHTML = `
                    <div class="w-full bg-center bg-no-repeat aspect-square bg-cover rounded-lg shadow-lg transform group-hover:scale-105 transition-transform duration-300" 
                         style="background-image: url('${item.image_path}');"></div>
                    <div>
                        <p class="font-medium text-gray-800 dark:text-gray-50">${item.name}</p>
                        <p class="text-sm text-gray-600 dark:text-gray-400">₹${item.price.toFixed(2)}</p>
                    </div>`;
                menuItemEl.addEventListener('click', () => addToCart(item));
                menuGrid.appendChild(menuItemEl);
            });
        } catch (error) {
            menuGrid.innerHTML = '<p class="col-span-full text-center text-red-400">Failed to load menu.</p>';
        }
    }

    // --- Initializations ---
    fetchMenu();
    updateCartUI();
});
