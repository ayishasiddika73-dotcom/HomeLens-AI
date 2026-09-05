/* =========================================================
   HOMELENS AI - LUXURY JAVASCRIPT & UI INTERACTION SYSTEM
   ========================================================= */

document.addEventListener("DOMContentLoaded", function () {

    /* -----------------------------------------------------
       AUTO-UPDATE CURRENT YEAR IN FOOTER
       ----------------------------------------------------- */
    const yearElements = document.querySelectorAll(".current-year");
    yearElements.forEach(function (element) {
        element.textContent = new Date().getFullYear();
    });

    /* -----------------------------------------------------
       SMOOTH SCROLLING FOR ANCHOR LINKS
       ----------------------------------------------------- */
    const anchorLinks = document.querySelectorAll('a[href^="#"]');
    anchorLinks.forEach(function (link) {
        link.addEventListener("click", function (event) {
            const targetId = link.getAttribute("href");
            if (!targetId || targetId === "#") return;

            const target = document.querySelector(targetId);
            if (target) {
                event.preventDefault();
                target.scrollIntoView({
                    behavior: "smooth",
                    block: "start"
                });
            }
        });
    });

    /* -----------------------------------------------------
       FORM SUBMISSION LOADING STATE
       ----------------------------------------------------- */
    const forms = document.querySelectorAll("form");
    forms.forEach(function (form) {
        form.addEventListener("submit", function () {
            const submitBtn = form.querySelector('button[type="submit"], input[type="submit"], .submit, .search-button, .submit-button');
            if (!submitBtn) return;

            submitBtn.dataset.originalText = submitBtn.textContent || submitBtn.value;
            if (submitBtn.tagName === "INPUT") {
                submitBtn.value = "Estimating AI Price...";
            } else {
                submitBtn.innerHTML = `
                    <span style="display:inline-block; animation: spin 1s infinite linear;">✦</span> Processing AI Model...
                `;
            }
            submitBtn.disabled = true;
            submitBtn.style.opacity = "0.8";
            submitBtn.style.cursor = "wait";
        });
    });

    /* -----------------------------------------------------
       NUMBER INPUT CONSTRAINTS & VALIDATIONS
       ----------------------------------------------------- */
    const numberInputs = document.querySelectorAll('input[type="number"]');
    numberInputs.forEach(function (input) {
        input.addEventListener("input", function () {
            if (input.value !== "" && Number(input.value) < 0) {
                input.value = 0;
            }
        });
    });

    /* -----------------------------------------------------
       SEARCH BUDGET RANGE SYNC & VALIDATION
       ----------------------------------------------------- */
    const searchForms = document.querySelectorAll('form[action="/search"]');
    searchForms.forEach(function (form) {
        form.addEventListener("submit", function (event) {
            const minBudget = form.querySelector('[name="min_budget"]');
            const maxBudget = form.querySelector('[name="max_budget"]');

            if (minBudget && maxBudget) {
                const min = Number(minBudget.value);
                const max = Number(maxBudget.value);

                if (minBudget.value !== "" && maxBudget.value !== "" && max < min) {
                    event.preventDefault();
                    alert("Maximum budget must be greater than or equal to minimum budget.");
                    maxBudget.focus();
                    
                    // Reset button state if submission was cancelled
                    const submitBtn = form.querySelector('button[type="submit"], .search-button, .submit-button');
                    if (submitBtn) {
                        submitBtn.disabled = false;
                        submitBtn.style.opacity = "1";
                        submitBtn.style.cursor = "pointer";
                        submitBtn.textContent = submitBtn.dataset.originalText || "Search Properties";
                    }
                    return;
                }
            }
        });
    });

    /* -----------------------------------------------------
       SELLER VALUATION FORM VALIDATION
       ----------------------------------------------------- */
    const sellerForms = document.querySelectorAll('form[action="/valuate"]');
    sellerForms.forEach(function (form) {
        form.addEventListener("submit", function (event) {
            const area = form.querySelector('[name="area"]');
            const bhk = form.querySelector('[name="bhk"]');

            if (area && Number(area.value) <= 0) {
                event.preventDefault();
                alert("Please enter a valid built-up area in square feet.");
                area.focus();
                return;
            }

            if (bhk && Number(bhk.value) <= 0) {
                event.preventDefault();
                alert("Please select the number of bedrooms.");
                bhk.focus();
                return;
            }
        });
    });

    /* -----------------------------------------------------
       SCROLL REVEAL ANIMATIONS (INTERSECTION OBSERVER)
       ----------------------------------------------------- */
    const animatedElements = document.querySelectorAll(".card, .feature, .step, .property-card, .info-card, .process-card");
    if ("IntersectionObserver" in window) {
        const observer = new IntersectionObserver(
            function (entries) {
                entries.forEach(function (entry) {
                    if (entry.isIntersecting) {
                        entry.target.style.opacity = "1";
                        entry.target.style.transform = "translateY(0)";
                        observer.unobserve(entry.target);
                    }
                });
            },
            { threshold: 0.1 }
        );

        animatedElements.forEach(function (el) {
            el.style.opacity = "0";
            el.style.transform = "translateY(20px)";
            el.style.transition = "opacity 0.6s cubic-bezier(0.16, 1, 0.3, 1), transform 0.6s cubic-bezier(0.16, 1, 0.3, 1)";
            observer.observe(el);
        });
    }

    /* -----------------------------------------------------
       BACK TO TOP BUTTON
       ----------------------------------------------------- */
    const topBtn = document.createElement("button");
    topBtn.type = "button";
    topBtn.id = "backToTop";
    topBtn.innerHTML = "↑";
    topBtn.setAttribute("aria-label", "Back to top");
    topBtn.style.cssText = `
        position: fixed;
        bottom: 30px;
        right: 30px;
        width: 48px;
        height: 48px;
        border-radius: 50%;
        background: linear-gradient(135deg, #D4AF37 0%, #A88624 100%);
        color: #0B0F17;
        border: none;
        font-size: 20px;
        font-weight: 800;
        cursor: pointer;
        display: none;
        z-index: 999;
        box-shadow: 0 8px 25px rgba(212, 175, 55, 0.3);
        transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
    `;

    document.body.appendChild(topBtn);

    window.addEventListener("scroll", function () {
        if (window.scrollY > 400) {
            topBtn.style.display = "block";
        } else {
            topBtn.style.display = "none";
        }
    });

    topBtn.addEventListener("click", function () {
        window.scrollTo({ top: 0, behavior: "smooth" });
    });

    console.log("HomeLens AI luxury design system initialized.");
});