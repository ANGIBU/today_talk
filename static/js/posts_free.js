document.addEventListener("DOMContentLoaded", function () {
    const paginationButtons = document.querySelectorAll(".pagination a");
    
    paginationButtons.forEach(button => {
        button.addEventListener("click", function (event) {
            event.preventDefault();
            const pageUrl = this.getAttribute("href");
            
            fetch(pageUrl, {
                method: "GET",
                headers: {
                    "X-Requested-With": "XMLHttpRequest"
                }
            })
            .then(response => response.text())
            .then(html => {
                const parser = new DOMParser();
                const doc = parser.parseFromString(html, "text/html");
                const newContent = doc.querySelector(".post-list-wrapper").innerHTML;
                const newPagination = doc.querySelector(".pagination").innerHTML;
                
                document.querySelector(".post-list-wrapper").innerHTML = newContent;
                document.querySelector(".pagination").innerHTML = newPagination;
            })
            .catch(error => console.error("페이지네이션 로딩 오류:", error));
        });
    });
});