// 배경 초기화
document.addEventListener('DOMContentLoaded', () => {
    // 초기 별 생성
    createStars();
    
    // 반응형 대응
    window.addEventListener('resize', () => {
        updateStarsOnResize();
    });
});

// 별들 생성 함수
function createStars() {
    const nightSky = document.querySelector('.night-sky');
    if (!nightSky) return;

    const numberOfStars = 100; // 별의 수 설정
    const maxHeight = window.innerHeight * 0.6; // 화면 높이의 60%로 제한
    
    // 각 별들을 시간차를 두고 생성
    for (let i = 0; i < numberOfStars; i++) {
        setTimeout(() => {
            createSingleStar(nightSky, maxHeight);
        }, Math.random() * 3000); // 0~3초 사이에 랜덤하게 생성
    }
}

// 개별 별 생성 함수
function createSingleStar(nightSky, maxHeight) {
    const star = document.createElement('div');
    star.className = 'twinkling-star';
    
    // 초기 위치 설정 (화면 높이의 60% 이내로 제한)
    const x = Math.random() * window.innerWidth;
    const y = Math.random() * maxHeight;
    
    star.style.left = `${x}px`;
    star.style.top = `${y}px`;
    
    nightSky.appendChild(star);

    // DOM에 추가된 후 약간의 지연을 두고 페이드 인 시작
    setTimeout(() => {
        star.style.transition = 'opacity 0.5s ease-in-out';
        star.style.opacity = '1';
        
        // 페이드 인 완료 후 반복 애니메이션 시작
        setTimeout(() => {
            startStarAnimation(star, maxHeight);
        }, 500);
    }, 50);
}

// 별의 반복 애니메이션 시작
function startStarAnimation(star, maxHeight) {
    setInterval(() => {
        // 페이드 아웃
        star.style.opacity = '0';
        
        // 완전히 사라진 후 새 위치로 이동 (높이 제한 유지)
        setTimeout(() => {
            const newX = Math.random() * window.innerWidth;
            const newY = Math.random() * maxHeight; // 화면 높이의 60% 이내로 제한
            
            star.style.left = `${newX}px`;
            star.style.top = `${newY}px`;
            
            // 새 위치에서 페이드 인
            setTimeout(() => {
                star.style.opacity = '1';
            }, 50);
        }, 500);
    }, 4000); // 4초마다 반복
}

// 화면 크기 변경 시 별들의 위치 업데이트 (높이 제한 유지)
function updateStarsOnResize() {
    const maxHeight = window.innerHeight * 0.6; // 화면 높이의 60%로 제한
    const stars = document.querySelectorAll('.twinkling-star');
    
    stars.forEach(star => {
        const x = Math.random() * window.innerWidth;
        const y = Math.random() * maxHeight;
        
        star.style.left = `${x}px`;
        star.style.top = `${y}px`;
    });
}

// 다크 모드 토글 시 별 스타일 조정 함수 추가
function adjustStarsForDarkMode() {
    const stars = document.querySelectorAll('.twinkling-star');
    const isDarkMode = document.body.classList.contains('dark-mode');
    
    stars.forEach(star => {
        star.style.opacity = isDarkMode ? '1' : '0';
    });
}

// 다크 모드 관련 이벤트 리스너
document.addEventListener('DOMContentLoaded', () => {
    const darkModeToggle = document.querySelector('.darkmode__input');
    const body = document.body;
    const nightCover = document.querySelector('.night-cover');

    // 현재 다크 모드 상태 로드
    const isDarkMode = localStorage.getItem('darkMode') === 'enabled';
    
    // 초기 다크 모드 설정
    if (isDarkMode) {
        body.classList.add('dark-mode');
        darkModeToggle.checked = true;
    }

    // 다크 모드 토글 이벤트 리스너
    darkModeToggle.addEventListener('change', () => {
        if (darkModeToggle.checked) {
            body.classList.add('dark-mode');
            localStorage.setItem('darkMode', 'enabled');
            
            // 다크 모드 토글 이벤트 디스패치
            const event = new Event('darkModeToggled');
            document.dispatchEvent(event);
        } else {
            body.classList.remove('dark-mode');
            localStorage.removeItem('darkMode');
            
            // 라이트 모드 토글 이벤트 디스패치
            const event = new Event('lightModeToggled');
            document.dispatchEvent(event);
        }
    });

    // 다크 모드 토글 이벤트 리스너 추가
    document.addEventListener('darkModeToggled', adjustStarsForDarkMode);
});

