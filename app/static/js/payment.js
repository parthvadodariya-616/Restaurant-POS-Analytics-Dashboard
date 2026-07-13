document.addEventListener('DOMContentLoaded', function () {
    const totalEl = document.getElementById('payment-total');
    const messageEl = document.getElementById('payment-message');
    const cardNumberInput = document.getElementById('cardnumber');
    const cardNameInput = document.getElementById('cardname');
    const expMonthInput = document.getElementById('expmonth');
    const expYearInput = document.getElementById('expyear');
    const expiryErrorEl = document.getElementById('expiry-error');
    const visaLogo = document.getElementById('visa-logo');
    const mastercardLogo = document.getElementById('mastercard-logo');
    const tabs = document.querySelectorAll('.payment-tab');
    const cardForm = document.getElementById('cardPaymentForm');
    const upiForm = document.getElementById('upiPaymentForm');

    const urlParams = new URLSearchParams(window.location.search);
    const orderId = urlParams.get('order_id');
    const total = urlParams.get('total');

    if (total) {
        totalEl.textContent = `₹${parseFloat(total).toFixed(2)}`;
    }

    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            tabs.forEach(t => {
                t.classList.remove('border-sky-500', 'text-sky-500');
                t.classList.add('border-transparent', 'text-slate-400');
            });
            tab.classList.add('border-sky-500', 'text-sky-500');
            tab.classList.remove('border-transparent', 'text-slate-400');
            
            cardForm.classList.toggle('hidden', tab.dataset.payment !== 'card');
            upiForm.classList.toggle('hidden', tab.dataset.payment !== 'upi');
        });
    });

    cardNumberInput.addEventListener('input', () => {
        let cleaned = cardNumberInput.value.replace(/\D/g, '');
        if (cleaned.length > 16) cleaned = cleaned.substring(0, 16);
        cardNumberInput.value = cleaned.replace(/(.{4})/g, '$1 ').trim();
        visaLogo.classList.toggle('hidden', !cleaned.startsWith('4'));
        mastercardLogo.classList.toggle('hidden', !cleaned.startsWith('5'));
    });

    cardNameInput.addEventListener('input', () => {
        cardNameInput.value = cardNameInput.value.toUpperCase();
    });

    const validateExpiry = () => {
        const month = parseInt(expMonthInput.value, 10);
        const year = parseInt(expYearInput.value, 10);
        if (!month || !year || expYearInput.value.length < 2) {
            expiryErrorEl.classList.add('hidden');
            return true;
        }
        const currentYear = new Date().getFullYear() % 100;
        const currentMonth = new Date().getMonth() + 1;
        if (year < currentYear || (year === currentYear && month < currentMonth)) {
            expiryErrorEl.textContent = 'Card is expired.';
            expiryErrorEl.classList.remove('hidden');
            return false;
        } else if (month < 1 || month > 12) {
            expiryErrorEl.textContent = 'Month must be 01-12.';
            expiryErrorEl.classList.remove('hidden');
            return false;
        } else {
            expiryErrorEl.classList.add('hidden');
            return true;
        }
    };
    expMonthInput.addEventListener('input', validateExpiry);
    expYearInput.addEventListener('input', validateExpiry);
    
    async function handlePayment(url, data) {
        messageEl.textContent = 'Processing payment...';
        messageEl.className = 'mt-4 text-center text-sky-400';
        try {
            const response = await fetch(url, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });
            const result = await response.json();
            if (!response.ok) throw new Error(result.message || 'Payment failed');
            
            messageEl.textContent = result.message;
            messageEl.className = 'mt-4 text-center text-green-400 font-bold';
            cardForm.style.display = 'none';
            upiForm.style.display = 'none';
            document.querySelector('.payment-tab').parentElement.style.display = 'none';

            // Create and append the "View Bill" button
            const billLink = document.createElement('a');
            billLink.href = result.bill_url;
            billLink.target = '_blank';
            billLink.className = 'mt-4 w-full block text-center bg-purple-600 hover:bg-purple-700 text-white font-bold py-3 px-4 rounded-lg transition-colors';
            billLink.textContent = 'View & Download Bill';
            messageEl.parentElement.appendChild(billLink);

            // Create and append the "Back to Dashboard" button
            const backButton = document.createElement('a');
            backButton.href = '/dashboard';
            backButton.className = 'mt-2 w-full block text-center bg-gray-600 hover:bg-gray-700 text-white font-bold py-3 px-4 rounded-lg transition-colors';
            backButton.textContent = 'New Order (Back to Dashboard)';
            messageEl.parentElement.appendChild(backButton);

        } catch (error) {
            messageEl.textContent = `Error: ${error.message}`;
            messageEl.className = 'mt-4 text-center text-red-400 font-semibold';
        }
    }

    if (cardForm) {
        cardForm.addEventListener('submit', async e => {
            e.preventDefault();
            if (!validateExpiry()) return;
            const data = Object.fromEntries(new FormData(cardForm).entries());
            data.cardnumber = data.cardnumber.replace(/\s/g, '');
            data.method = 'Card';
            handlePayment(`/api/order/${orderId}/pay`, data);
        });
    }

    if (upiForm) {
        upiForm.addEventListener('submit', async e => {
            e.preventDefault();
            const data = Object.fromEntries(new FormData(upiForm).entries());
            data.method = 'UPI';
            handlePayment(`/api/order/${orderId}/pay`, data);
        });
    }
});