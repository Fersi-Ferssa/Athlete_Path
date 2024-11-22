document.addEventListener("DOMContentLoaded", function() {
    var navbar = document.getElementById("mainNav");

    window.addEventListener("scroll", function() {
        if (window.scrollY > 50) {
            navbar.classList.add("navbar-scrolled");
        } else {
            navbar.classList.remove("navbar-scrolled");
        }
    });
});

// SECONDARY VECTOR (ALL MEDALS)
document.addEventListener("DOMContentLoaded", function() {
    var banner = document.querySelector(".vector-banner");

    if (banner) {
        window.addEventListener("scroll", function() {
            if (window.scrollY > 50) {
                banner.classList.add("navbar-scrolled");
            } else {
                banner.classList.remove("navbar-scrolled");
            }
        });
    }
});
