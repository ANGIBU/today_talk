// 프로필 사진 미리보기
document.addEventListener("DOMContentLoaded", () => {
    const profileImageInput = document.getElementById("profile-image-input");
    const profileImagePreview = document.getElementById("profile-image-preview");

    profileImageInput.addEventListener("change", (e) => {
        const file = e.target.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = (event) => {
                profileImagePreview.src = event.target.result;
            };
            reader.readAsDataURL(file);
        }
    });
});
