// Theme Toggle JavaScript - Final Fixed Version

document.addEventListener('DOMContentLoaded', function () {
    initThemeToggle();
});

function initThemeToggle() {
    const themeToggle = document.getElementById('theme-toggle');
    const mobileThemeToggle = document.getElementById('mobile-theme-toggle');

    // Use localStorage or system preference
    let currentTheme = localStorage.getItem('theme') ||
        (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');

    applyTheme(currentTheme);

    function applyTheme(theme) {
        if (theme === 'dark') {
            document.documentElement.classList.add('dark');
        } else {
            document.documentElement.classList.remove('dark');
        }

        // Desktop icons
        const sunIcon = document.getElementById('sun-icon');
        const moonIcon = document.getElementById('moon-icon');

        if (sunIcon && moonIcon) {
            sunIcon.classList.toggle('opacity-100', theme === 'dark');
            sunIcon.classList.toggle('opacity-0', theme !== 'dark');
            moonIcon.classList.toggle('opacity-0', theme === 'dark');
            moonIcon.classList.toggle('opacity-100', theme !== 'dark');
        }

        // Mobile icons
        if (mobileThemeToggle) {
            const mobileSunIcon = mobileThemeToggle.querySelector('svg:first-child');
            const mobileMoonIcon = mobileThemeToggle.querySelector('svg:last-child');

            if (mobileSunIcon && mobileMoonIcon) {
                mobileSunIcon.classList.toggle('hidden', theme !== 'dark');
                mobileSunIcon.classList.toggle('block', theme === 'dark');
                mobileMoonIcon.classList.toggle('hidden', theme === 'dark');
                mobileMoonIcon.classList.toggle('block', theme !== 'dark');
            }
        }
    }

    function toggleTheme() {
        currentTheme = currentTheme === 'dark' ? 'light' : 'dark';
        localStorage.setItem('theme', currentTheme);
        applyTheme(currentTheme);
    }

    if (themeToggle) themeToggle.addEventListener('click', toggleTheme);
    if (mobileThemeToggle) mobileThemeToggle.addEventListener('click', toggleTheme);

    // Listen for system preference change if no saved theme
    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
    mediaQuery.addEventListener('change', (e) => {
        if (!localStorage.getItem('theme')) {
            const systemTheme = e.matches ? 'dark' : 'light';
            currentTheme = systemTheme;
            applyTheme(systemTheme);
        }
    });

    // Expose applyTheme globally so chatbot can use it
    window.applyTheme = applyTheme;
}
