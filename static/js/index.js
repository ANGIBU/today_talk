// Index page initialization
document.addEventListener('DOMContentLoaded', () => {
    initializePageAnimations();
});

// Initialize page animations
function initializePageAnimations() {
    // 페이지 로드 시 부드러운 등장 효과
    const homeContainer = document.querySelector('.home-container');
    if (homeContainer) {
        homeContainer.style.opacity = '0';
        setTimeout(() => {
            homeContainer.style.opacity = '1';
            homeContainer.style.transition = 'opacity 1s ease-in-out';
        }, 100);
    }
}