// ===============================
// JavaScript Portfolio Firda
// ===============================

document.addEventListener("DOMContentLoaded", function () {
    const navLinks = document.querySelectorAll("nav a[href^='#']");
    const sections = document.querySelectorAll("section");

    // Smooth scroll saat klik menu navbar
    navLinks.forEach(function (link) {
        link.addEventListener("click", function (e) {
            e.preventDefault();

            const targetId = this.getAttribute("href");
            const targetSection = document.querySelector(targetId);

            if (targetSection) {
                targetSection.scrollIntoView({
                    behavior: "smooth"
                });
            }
        });
    });

    // Animasi sederhana saat section terlihat
    const observer = new IntersectionObserver(function (entries) {
        entries.forEach(function (entry) {
            if (entry.isIntersecting) {
                entry.target.classList.add("show-section");
            }
        });
    }, {
        threshold: 0.2
    });

    sections.forEach(function (section) {
        section.classList.add("hidden-section");
        observer.observe(section);
    });

    // Navbar active saat scroll
    window.addEventListener("scroll", function () {
        let current = "";

        sections.forEach(function (section) {
            const sectionTop = section.offsetTop - 120;

            if (window.scrollY >= sectionTop) {
                current = section.getAttribute("id");
            }
        });

        navLinks.forEach(function (link) {
            link.classList.remove("active-link");

            if (link.getAttribute("href") === "#" + current) {
                link.classList.add("active-link");
            }
        });
    });
});

// ===============================
// Hidden admin login trigger
// ===============================

const adminSecret = document.getElementById("admin-secret");

if (adminSecret) {
    let clickCount = 0;
    let timer;

    adminSecret.addEventListener("click", function () {
        clickCount++;

        clearTimeout(timer);

        timer = setTimeout(function () {
            clickCount = 0;
        }, 1500);

        if (clickCount === 5) {
            const loginUrl = adminSecret.getAttribute("data-login-url");
            window.location.href = loginUrl;
        }
    });
}