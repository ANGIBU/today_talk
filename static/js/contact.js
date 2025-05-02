// 문의 폼 검증 및 메시지 처리
document.addEventListener("DOMContentLoaded", () => {
    const contactForm = document.getElementById("contact-form");
    const subjectInput = document.getElementById("subject");
    const messageInput = document.getElementById("message");

    contactForm.addEventListener("submit", (e) => {
        if (!subjectInput.value.trim() || !messageInput.value.trim()) {
            e.preventDefault();
            alert("제목과 메시지를 모두 입력하세요!");
        }
    });
});
