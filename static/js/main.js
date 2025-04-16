document.addEventListener('DOMContentLoaded', () => {
    initializeNavigation();
    initializeDarkMode();
    initializeSideMenu();
    initializeClickOutside();
    initializeBurgerHover();
    initializeTooltips();
    initializeReplyButtons();
});

function initializeNavigation() {
    const currentUrl = window.location.pathname;
    document.querySelectorAll('.nav a').forEach(link => {
        if (link.getAttribute('href') === currentUrl) {
            link.classList.add('active');
        }
    });
}

function initializeDarkMode() {
    const darkModeToggle = document.querySelector('.darkmode__input');
    const darkModeText = document.querySelector('.mode-text');
    
    if (!darkModeToggle || !darkModeText) return;

    const savedTheme = localStorage.getItem('theme');
    const updateTheme = (isDark) => {
        document.body.setAttribute('data-theme', isDark ? 'dark' : 'light');
        darkModeText.textContent = isDark ? '라이트모드' : '다크모드';
        localStorage.setItem('theme', isDark ? 'dark' : 'light');
        
        document.body.style.transition = 'background 0.4s ease';
        setTimeout(() => {
            document.body.style.transition = '';
        }, 400);
    };

    if (savedTheme === 'dark') {
        darkModeToggle.checked = true;
        updateTheme(true);
    }

    darkModeToggle.addEventListener('change', () => {
        updateTheme(darkModeToggle.checked);
    });
}

function initializeReplyButtons() {
    document.querySelectorAll('.btn-reply').forEach(button => {
        button.addEventListener('click', (event) => {
            const commentId = event.target.getAttribute('data-comment-id');
            showReplyForm(commentId);
        });
    });
}

function showReplyForm(commentId) {
    const replyForm = document.getElementById(`reply-form-${commentId}`);
    const allReplyForms = document.getElementsByClassName("reply-form");
    
    // 다른 모든 답글 폼을 숨김
    for (let form of allReplyForms) {
        if (form.id !== `reply-form-${commentId}`) {
            form.style.display = "none";
        }
    }
    
    // 선택된 답글 폼 표시 토글
    replyForm.style.display = replyForm.style.display === "none" ? "block" : "none";
}

function initializeBurgerHover() {
    const burger = document.getElementById('burger');
    if (!burger) return;

    burger.addEventListener('mouseenter', () => {
        burger.classList.add('burger-hover');
    });

    burger.addEventListener('mouseleave', () => {
        burger.classList.remove('burger-hover');
    });
}

function initializeSideMenu() {
    const burger = document.getElementById('burger');
    const sidemenu = document.querySelector('.sidemenu');

    if (!burger || !sidemenu) return;

    sidemenu.style.left = `-${sidemenu.offsetWidth}px`;

    burger.addEventListener('click', () => {
        const isOpen = sidemenu.style.left === '0px';
        sidemenu.style.left = isOpen ? `-${sidemenu.offsetWidth}px` : '0px';
    });
}

function initializeClickOutside() {
    document.addEventListener('click', (event) => {
        const sidemenu = document.querySelector('.sidemenu');
        const burger = document.getElementById('burger');
        
        if (!sidemenu || !burger) return;

        if (sidemenu.style.left === '0px' && 
            !sidemenu.contains(event.target) && 
            !burger.contains(event.target)) {
            sidemenu.style.left = `-${sidemenu.offsetWidth}px`;
            closeActiveSubmenu();
        }
    });
}

let activeSubmenu = null;
let activeArrow = null;

function closeActiveSubmenu() {
    if (activeSubmenu) {
        activeSubmenu.classList.remove('open');
        if (activeArrow) {
            activeArrow.style.transform = 'rotate(0deg)';
            activeArrow.textContent = '▶';
        }
        activeSubmenu = null; 
        activeArrow = null;
    }
}

function toggleSubmenu(menuId) {
    const submenu = document.getElementById(`${menuId}-submenu`);
    const arrow = submenu.parentElement.querySelector('.sidemenu__arrow');
    
    if (activeSubmenu && activeSubmenu !== submenu) {
        closeActiveSubmenu();
    }
    
    const isOpen = submenu.classList.contains('open');
    
    if (!isOpen) {
        submenu.classList.add('open');
        arrow.style.transform = 'rotate(90deg)';
        arrow.textContent = '▶'; 
        activeSubmenu = submenu;
        activeArrow = arrow;
    } else {
        closeActiveSubmenu();
    }
}

function initializeTooltips() {
    document.querySelectorAll('[data-tooltip]').forEach(element => {
        element.addEventListener('mouseenter', () => {
            const tooltip = document.createElement('span');
            tooltip.className = 'tooltip';
            tooltip.textContent = element.dataset.tooltip;
            element.appendChild(tooltip);
        });

        element.addEventListener('mouseleave', () => {
            const tooltip = element.querySelector('.tooltip');
            if (tooltip) tooltip.remove();
        });
    });
}