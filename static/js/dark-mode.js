// 다크 모드 토글
document.addEventListener("DOMContentLoaded", () => {
    const darkModeToggle = document.getElementById("dark-mode-toggle");

    // 저장된 모드 상태 불러오기
    const currentMode = localStorage.getItem("darkMode");
    if (currentMode === "enabled") {
        document.body.classList.add("dark-mode");
        darkModeToggle.checked = true; // 체크박스 상태 업데이트
    }

    // 다크 모드 전환
    darkModeToggle.addEventListener("change", () => {
        document.body.classList.toggle("dark-mode");
        if (document.body.classList.contains("dark-mode")) {
            localStorage.setItem("darkMode", "enabled");
        } else {
            localStorage.setItem("darkMode", "disabled");
        }
    });
});
