// Main JavaScript for E-click Django Project

document.addEventListener('DOMContentLoaded', function() {
    
    // Navbar functionality
    initNavbar();
    
    // Reveal animations
    initRevealAnimations();
    
    // Solutions tabs
    initSolutionsTabs();
    
    // Scroll to top
    initScrollToTop();
    
    // Contact form
    initContactForm();
    
    // Mobile menu
    initMobileMenu();
    
    // Image loading
    initImageLoading();
});

// Navbar scroll effects
function initNavbar() {
    const navbar = document.getElementById('navbar');
    const navbarLine = document.getElementById('navbar-line');
    
    if (!navbar) return;
    
    let isScrolled = false;
    
    function handleScroll() {
        const shouldBeScrolled = window.scrollY > 20;
        
        if (isScrolled !== shouldBeScrolled) {
            isScrolled = shouldBeScrolled;
            
            if (isScrolled) {
                navbar.classList.remove('py-6', 'bg-transparent');
                navbar.classList.add('py-3', 'backdrop-blur-lg', 'bg-white/80', 'dark:bg-gray-900/80', 'shadow-lg');
                if (navbarLine) navbarLine.classList.add('opacity-100');
            } else {
                navbar.classList.remove('py-3', 'backdrop-blur-lg', 'bg-white/80', 'dark:bg-gray-900/80', 'shadow-lg');
                navbar.classList.add('py-6', 'bg-transparent');
                if (navbarLine) navbarLine.classList.remove('opacity-100');
            }
        }
        
        // Update active nav links
        updateActiveNavLink();
    }
    
    function updateActiveNavLink() {
        const sections = document.querySelectorAll('section[id]');
        const navLinks = document.querySelectorAll('.nav-link');
        
        let activeSection = 'home';
        
        sections.forEach(section => {
            const rect = section.getBoundingClientRect();
            if (rect.top <= 100 && rect.bottom >= 100) {
                activeSection = section.id;
            }
        });
        
        navLinks.forEach(link => {
            const indicator = link.querySelector('.nav-indicator');
            if (link.dataset.section === activeSection) {
                link.classList.add('text-red-600', 'dark:text-red-400');
                link.classList.remove('text-gray-600', 'dark:text-gray-300');
                if (indicator) indicator.classList.add('opacity-100');
            } else {
                link.classList.remove('text-red-600', 'dark:text-red-400');
                link.classList.add('text-gray-600', 'dark:text-gray-300');
                if (indicator) indicator.classList.remove('opacity-100');
            }
        });
    }
    
    // Throttle scroll events
    let ticking = false;
    window.addEventListener('scroll', () => {
        if (!ticking) {
            requestAnimationFrame(() => {
                handleScroll();
                ticking = false;
            });
            ticking = true;
        }
    }, { passive: true });
    
    // Smooth scroll for nav links
    document.querySelectorAll('a[href^="#"]').forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const targetId = this.getAttribute('href').substring(1);
            const target = document.getElementById(targetId);
            
            if (target) {
                const offsetTop = target.offsetTop - 80;
                window.scrollTo({
                    top: offsetTop,
                    behavior: 'smooth'
                });
            }
        });
    });
}

// Reveal animations on scroll
function initRevealAnimations() {
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('revealed');
                
                // Stagger child animations
                const children = entry.target.querySelectorAll('.reveal-element');
                children.forEach((child, index) => {
                    setTimeout(() => {
                        child.classList.add('revealed');
                    }, index * 100);
                });
                
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);
    
    document.querySelectorAll('.reveal-element').forEach(el => {
        observer.observe(el);
    });
}

// Solutions tabs functionality
function initSolutionsTabs() {
    const triggers = document.querySelectorAll('.tab-trigger');
    const contents = document.querySelectorAll('.tab-content');
    
    triggers.forEach(trigger => {
        trigger.addEventListener('click', () => {
            const targetId = trigger.dataset.target;
            
            // Update active trigger
            triggers.forEach(t => {
                t.classList.remove('active', 'text-red-600', 'dark:text-red-400', 'border-b-2', 'border-red-600', 'dark:border-red-400');
                t.classList.add('text-gray-600', 'dark:text-gray-400');
            });
            
            trigger.classList.add('active', 'text-red-600', 'dark:text-red-400', 'border-b-2', 'border-red-600', 'dark:border-red-400');
            trigger.classList.remove('text-gray-600', 'dark:text-gray-400');
            
            // Update active content
            contents.forEach(content => {
                content.classList.add('hidden');
            });
            
            const targetContent = document.getElementById(targetId);
            if (targetContent) {
                targetContent.classList.remove('hidden');
            }
        });
    });
}

// Scroll to top functionality
function initScrollToTop() {
    const scrollToTopBtn = document.getElementById('scroll-to-top');
    
    if (!scrollToTopBtn) return;
    
    function toggleScrollToTop() {
        if (window.scrollY > 500) {
            scrollToTopBtn.classList.remove('opacity-0', 'translate-y-10', 'pointer-events-none');
            scrollToTopBtn.classList.add('opacity-100', 'translate-y-0');
        } else {
            scrollToTopBtn.classList.add('opacity-0', 'translate-y-10', 'pointer-events-none');
            scrollToTopBtn.classList.remove('opacity-100', 'translate-y-0');
        }
    }
    
    window.addEventListener('scroll', toggleScrollToTop, { passive: true });
    
    scrollToTopBtn.addEventListener('click', () => {
        window.scrollTo({
            top: 0,
            behavior: 'smooth'
        });
    });
}

// Contact form functionality
function initContactForm() {
    const form = document.getElementById('contact-form');
    const submitBtn = document.getElementById('submit-btn');
    const formContainer = document.getElementById('contact-form-container');
    const successMessage = document.getElementById('success-message');
    const errorMessage = document.getElementById('error-message');
    const sendAnotherBtn = document.getElementById('send-another');
    const tryAgainBtn = document.getElementById('try-again');

    if (!form) return;

    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        const captchaTokenEl = document.getElementById('captcha-token');
        const captchaErrorEl = document.getElementById('captcha-error');

        // Block submission if captcha not solved
        if (captchaTokenEl && !captchaTokenEl.value) {
            if (captchaErrorEl) { captchaErrorEl.classList.remove('hidden'); captchaErrorEl.textContent = 'Please verify you are not a robot.'; }
            return;
        }

        // Show loading state
        if (submitBtn) {
            submitBtn.disabled = true;
            submitBtn.innerHTML = `
                <svg class="w-5 h-5 animate-spin" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" class="opacity-25"></circle>
                    <path fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" class="opacity-75"></path>
                </svg>
                <span>Sending...</span>
            `;
        }

        try {
            const formData = new FormData(form);
            const response = await fetch(form.action, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            });

            const data = await response.json();

            if (data.success) {
                if (formContainer) formContainer.classList.add('hidden');
                if (successMessage) successMessage.classList.remove('hidden');
            } else if (data.captcha_error) {
                if (typeof window._captchaReset === 'function') window._captchaReset();
            } else {
                throw new Error(data.message || 'Form submission failed');
            }
        } catch (error) {
            console.error('Error:', error);
            if (formContainer) formContainer.classList.add('hidden');
            if (errorMessage) errorMessage.classList.remove('hidden');
        }
    });

    // Reset form handlers
    if (sendAnotherBtn) {
        sendAnotherBtn.addEventListener('click', resetForm);
    }

    if (tryAgainBtn) {
        tryAgainBtn.addEventListener('click', resetForm);
    }

    function resetForm() {
        form.reset();
        if (submitBtn) {
            submitBtn.disabled = false;
            submitBtn.innerHTML = `
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"></path>
                </svg>
                <span>Send Message</span>
            `;
        }

        if (formContainer) formContainer.classList.remove('hidden');
        if (successMessage) successMessage.classList.add('hidden');
        if (errorMessage) errorMessage.classList.add('hidden');
    }
}

// Mobile menu functionality
function initMobileMenu() {
    const mobileMenuToggle = document.getElementById('mobile-menu-toggle');
    const mobileMenu = document.getElementById('mobile-menu');
    const mobileMenuLines = document.querySelectorAll('.mobile-menu-line');
    const mobileNavLinks = document.querySelectorAll('.mobile-nav-link');
    
    if (!mobileMenuToggle || !mobileMenu) return;
    
    let isOpen = false;
    
    function toggleMobileMenu() {
        isOpen = !isOpen;
        
        if (isOpen) {
            mobileMenu.classList.remove('translate-x-full', 'opacity-0', 'pointer-events-none');
            mobileMenu.classList.add('translate-x-0', 'opacity-100');
            
            // Animate hamburger to X
            if (mobileMenuLines.length >= 3) {
                mobileMenuLines[0].style.transform = 'rotate(45deg) translateY(6px)';
                mobileMenuLines[1].style.opacity = '0';
                mobileMenuLines[2].style.transform = 'rotate(-45deg) translateY(-6px)';
            }
        } else {
            mobileMenu.classList.add('translate-x-full', 'opacity-0', 'pointer-events-none');
            mobileMenu.classList.remove('translate-x-0', 'opacity-100');
            
            // Reset hamburger
            if (mobileMenuLines.length >= 3) {
                mobileMenuLines[0].style.transform = '';
                mobileMenuLines[1].style.opacity = '';
                mobileMenuLines[2].style.transform = '';
            }
        }
    }
    
    mobileMenuToggle.addEventListener('click', toggleMobileMenu);
    
    // Close mobile menu when clicking nav links
    mobileNavLinks.forEach(link => {
        link.addEventListener('click', () => {
            if (isOpen) toggleMobileMenu();
        });
    });
    
    // Close mobile menu when clicking outside
    document.addEventListener('click', (e) => {
        if (isOpen && !mobileMenu.contains(e.target) && !mobileMenuToggle.contains(e.target)) {
            toggleMobileMenu();
        }
    });
}

// Image loading for company logos
function initImageLoading() {
    const companyLogos = document.querySelectorAll('.company-logo');
    
    companyLogos.forEach(img => {
        img.addEventListener('load', function() {
            this.style.opacity = '1';
            const fallback = this.parentElement.querySelector('.company-fallback');
            if (fallback) fallback.style.display = 'none';
        });
        
        img.addEventListener('error', function() {
            this.style.display = 'none';
            const fallback = this.parentElement.querySelector('.company-fallback');
            if (fallback) fallback.style.display = 'block';
        });
    });
}

// Simple AJAX utility for requests without CSRF
function simpleAjax(url, options = {}) {
    const defaultOptions = {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        ...options
    };
    
    // Remove any CSRF-related headers if they exist
    if (defaultOptions.headers['X-CSRFToken']) {
        delete defaultOptions.headers['X-CSRFToken'];
    }
    
    return fetch(url, defaultOptions);
}

// Helper function to create form data without CSRF
function createFormData(form) {
    const formData = new FormData(form);
    // Remove CSRF token if it exists
    formData.delete('csrfmiddlewaretoken');
    return formData;
}