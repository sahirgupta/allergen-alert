document.addEventListener("DOMContentLoaded", function () {
    const imageInput = document.getElementById("imageInput");
    const previewImage = document.getElementById("previewImage");
    const imagePreview = document.getElementById("imagePreview");
    const analyzeForm = document.getElementById("analyzeForm");
    const loadingIndicator = document.getElementById("loadingIndicator");
    const responseContainer = document.getElementById("responseContainer");

    imageInput.addEventListener("change", function () {
        const file = this.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = function (event) {
                previewImage.setAttribute("src", event.target.result);
                imagePreview.style.display = "block";
            };
            reader.readAsDataURL(file);
        } else {
            imagePreview.style.display = "none";
        }
    });

    analyzeForm.addEventListener("submit", function (event) {
        loadingIndicator.style.display = "block";
        responseContainer.style.display = "none";
    });

    // Resize the canvas to fill browser window dynamically
    window.addEventListener("resize", resizeCanvas);
    function resizeCanvas() {
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
    }
    resizeCanvas();

});
