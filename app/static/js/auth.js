document.addEventListener('DOMContentLoaded', function () {
    const loginForm = document.getElementById('adminLoginForm');
    const errorEl = document.getElementById('login-error');

    if (!loginForm) return;

    loginForm.addEventListener('submit', async function (e) {
        e.preventDefault();
        errorEl.textContent = '';

        const formData = new FormData(loginForm);
        const data = Object.fromEntries(formData.entries());

        try {
            const response = await fetch('/auth/api/admin/login', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });

            const result = await response.json();

            if (response.ok && result.success) {
                window.location.href = result.redirect_url;
            } else {
                errorEl.textContent = result.message || 'Login failed. Please try again.';
            }
        } catch (error) {
            errorEl.textContent = 'A network error occurred. Please check your connection.';
            console.error('Login fetch error:', error);
        }
    });
});