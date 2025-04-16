// 캡차 새로고침 및 검증
document.addEventListener("DOMContentLoaded", () => {
    const captchaImage = document.getElementById("captcha-image");
    const refreshButton = document.getElementById("refresh-captcha");
    const captchaInput = document.getElementById("captcha-input");
    const captchaForm = document.getElementById("captcha-form");

    // 캡차 새로고침
    refreshButton.addEventListener("click", () => {
        captchaImage.src = `/captcha?${new Date().getTime()}`; // 새 캡차 요청
    });

    // 폼 제출 시 캡차 검증
    captchaForm.addEventListener("submit", (e) => {
        const userInput = captchaInput.value.trim();
        if (!userInput) {
            e.preventDefault();
            alert("캡차를 입력하세요!");
        }
    });
});
