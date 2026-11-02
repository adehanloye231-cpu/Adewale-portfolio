// =======================================================
// PORTFOLIO WEBSITE JAVASCRIPT
// Developed by Adehanloye Adewale
// =======================================================



// =======================================================
// MOBILE MENU
// =======================================================

const menuBtn = document.querySelector(".menu-btn");
const navbar = document.querySelector(".navbar");

if (menuBtn && navbar) {

    menuBtn.addEventListener("click", () => {

        navbar.classList.toggle("active");

        if (navbar.classList.contains("active")) {

            menuBtn.innerHTML = '<i class="fas fa-times"></i>';

        } else {

            menuBtn.innerHTML = '<i class="fas fa-bars"></i>';

        }

    });

    document.querySelectorAll(".navbar a").forEach(link => {

        link.addEventListener("click", () => {

            navbar.classList.remove("active");

            menuBtn.innerHTML = '<i class="fas fa-bars"></i>';

        });

    });

}



// =======================================================
// STICKY HEADER
// =======================================================

const header = document.querySelector(".header");

window.addEventListener("scroll", () => {

    if (!header) return;

    if (window.scrollY > 60) {

        header.classList.add("sticky");

    } else {

        header.classList.remove("sticky");

    }

});



// =======================================================
// ACTIVE NAVIGATION
// =======================================================

const sections = document.querySelectorAll("section[id]");
const navLinks = document.querySelectorAll(".navbar a");

window.addEventListener("scroll", () => {

    let current = "";

    sections.forEach(section => {

        const sectionTop = section.offsetTop - 180;
        const sectionHeight = section.offsetHeight;

        if (

            window.scrollY >= sectionTop &&
            window.scrollY < sectionTop + sectionHeight

        ) {

            current = section.getAttribute("id");

        }

    });

    navLinks.forEach(link => {

        link.classList.remove("active");

        if (link.getAttribute("href") === "#" + current) {

            link.classList.add("active");

        }

    });

});



// =======================================================
// SMOOTH SCROLL
// =======================================================

document.querySelectorAll('a[href^="#"]').forEach(link => {

    link.addEventListener("click", function (e) {

        const href = this.getAttribute("href");

        if (!href || href === "#") {
            return;
        }

        const target = document.querySelector(href);

        if (target) {

            e.preventDefault();

            const headerHeight = document.querySelector(".header")
                ? document.querySelector(".header").offsetHeight
                : 0;
            const targetPosition = target.getBoundingClientRect().top + window.pageYOffset - headerHeight;

            window.scrollTo({
                top: targetPosition,
                behavior: "smooth"
            });

        }

    });

});




// =======================================================
// HERO TYPING EFFECT
// =======================================================

const typing = document.getElementById("typing");

const heroText = "HI, I'M  ADEWALE";

let index = 0;

let deleting = false;

const typingSpeed = 100;

const deletingSpeed = 50;

const waitTime = 5000;



function typeEffect() {

    if (!typing) return;



    if (!deleting) {

        typing.textContent = heroText.substring(0, index);

        index++;

        if (index > heroText.length) {

            deleting = true;

            setTimeout(typeEffect, waitTime);

            return;

        }

        setTimeout(typeEffect, typingSpeed);

    }

    else {

        typing.textContent = heroText.substring(0, index);

        index--;

        if (index < 0) {

            deleting = false;

            index = 0;

            setTimeout(typeEffect, 800);

            return;

        }

        setTimeout(typeEffect, deletingSpeed);

    }

}



window.addEventListener("load", typeEffect);




// =======================================================
// SCROLL REVEAL ANIMATION
// =======================================================

const revealElements = document.querySelectorAll(
".about-content, .about-img, .service-box, .resume-box, .portfolio-box, .skill, .hero-image, .hero-text"
);

revealElements.forEach(item => {

    item.style.opacity = "0";
    item.style.transform = "translateY(70px)";
    item.style.transition = "all .8s ease";

});

function revealAnimation() {

    revealElements.forEach(item => {

        const top = item.getBoundingClientRect().top;

        if (top < window.innerHeight - 120) {

            item.style.opacity = "1";
            item.style.transform = "translateY(0)";

        }

    });

}

window.addEventListener("scroll", revealAnimation);
window.addEventListener("load", revealAnimation);




// =======================================================
// HERO IMAGE: COMBINED FLOATING + PARALLAX EFFECT
// =======================================================

const heroImage = document.querySelector(".hero-image");

if (heroImage) {

    let floatOffset = 0;
    let parallaxX = 0;
    let parallaxY = 0;

    setInterval(() => {
        floatOffset = floatOffset === 0 ? -15 : 0;
        updateHeroTransform();
    }, 2500);

    document.addEventListener("mousemove", (e) => {
        parallaxX = (window.innerWidth / 2 - e.clientX) / 45;
        parallaxY = (window.innerHeight / 2 - e.clientY) / 45;
        updateHeroTransform();
    });

    function updateHeroTransform() {
        heroImage.style.transform = `translate(${parallaxX}px, ${parallaxY + floatOffset}px)`;
        heroImage.style.transition = "transform 2.5s ease";
    }

}




// =======================================================
// SKILL BAR ANIMATION
// =======================================================

const skillSections = document.querySelectorAll(".skill");
const skillAnimated = new WeakSet();

function animateSkillBars() {
    skillSections.forEach(skill => {
        if (skillAnimated.has(skill)) return;
        const top = skill.getBoundingClientRect().top;
        if (top < window.innerHeight - 80) {
            const bar = skill.querySelector(".progress");
            if (bar) {
                const classes = bar.getAttribute("class");
                let widthVal = "";
                if (classes.includes("html")) widthVal = "95%";
                else if (classes.includes("css")) widthVal = "90%";
                else if (classes.includes("js")) widthVal = "85%";
                else if (classes.includes("python")) widthVal = "80%";
                bar.style.width = "0";
                bar.style.transition = "width 2s ease";
                setTimeout(() => {
                    bar.style.width = widthVal;
                }, 100);
                skillAnimated.add(skill);
            }
        }
    });
}

window.addEventListener("scroll", animateSkillBars);
window.addEventListener("load", animateSkillBars);





// =======================================================
// BUTTON RIPPLE EFFECT
// =======================================================

const buttons = document.querySelectorAll(".btn");

buttons.forEach(button => {

    button.addEventListener("click", function (e) {

        const existingRipple = button.querySelector(".ripple");
        if (existingRipple) {
            existingRipple.remove();
        }

        const circle = document.createElement("span");

        const diameter = Math.max(button.clientWidth, button.clientHeight);

        const radius = diameter / 2;

        circle.style.width = circle.style.height = `${diameter}px`;

        circle.style.left = `${e.clientX - button.getBoundingClientRect().left - radius}px`;

        circle.style.top = `${e.clientY - button.getBoundingClientRect().top - radius}px`;

        circle.classList.add("ripple");

        button.appendChild(circle);

        setTimeout(() => {
            if (circle.parentNode) {
                circle.remove();
            }
        }, 700);

    });

});



// =======================================================
// CONTACT FORM - WITH BACKEND API
// =======================================================

const contactForm = document.querySelector(".contact form");

if (contactForm) {

    const success = document.createElement("div");
    success.className = "success-message";
    contactForm.appendChild(success);

    const submitBtn = contactForm.querySelector(".btn");

    contactForm.addEventListener("submit", async function (e) {

        e.preventDefault();

        const inputs = contactForm.querySelectorAll("input, textarea");
        const nameInput = contactForm.querySelector('input[name="name"]');
        const emailInput = contactForm.querySelector('input[name="email"]');
        const subjectInput = contactForm.querySelector('input[name="subject"]');
        const messageInput = contactForm.querySelector('textarea[name="message"]');

        let valid = true;
        const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

        inputs.forEach(input => {

            if (input.value.trim() === "") {

                input.style.border = "2px solid #ff4444";
                valid = false;

            } else if (input.type === "email" && !emailPattern.test(input.value.trim())) {

                input.style.border = "2px solid #ff4444";
                valid = false;

            } else {

                input.style.border = "2px solid #19f59c";

            }

        });

        if (!valid) {

            success.innerHTML = "❌ Please fill in all fields correctly.";
            success.style.color = "#ff4444";
            success.style.marginTop = "20px";
            success.style.fontWeight = "600";
            success.style.textAlign = "center";
            return;

        }

        const originalBtnText = submitBtn ? submitBtn.innerHTML : "";
        if (submitBtn) {
            submitBtn.disabled = true;
            submitBtn.style.opacity = "0.6";
            submitBtn.style.cursor = "not-allowed";
            submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Sending...';
        }

        const payload = {
            name: nameInput ? nameInput.value.trim() : "",
            email: emailInput ? emailInput.value.trim() : "",
            subject: subjectInput ? subjectInput.value.trim() : "",
            message: messageInput ? messageInput.value.trim() : ""
        };

        try {

            const response = await fetch("/api/contact", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify(payload)
            });

            const result = await response.json();

            if (result.success) {

                success.innerHTML = result.message;
                success.style.color = "#19f59c";
                success.style.marginTop = "20px";
                success.style.fontWeight = "600";
                success.style.textAlign = "center";

                contactForm.reset();

                setTimeout(() => {

                    success.innerHTML = "";

                    inputs.forEach(input => {
                        input.style.border = "";
                    });

                }, 7000);

            } else {

                success.innerHTML = result.message || "❌ Failed to send message. Please try again.";
                success.style.color = "#ff4444";
                success.style.marginTop = "20px";
                success.style.fontWeight = "600";
                success.style.textAlign = "center";

            }

        } catch (err) {

            console.error("Contact API error:", err);
            success.innerHTML = "❌ Could not send message. Please check your internet connection or email directly at adehanloyemail@gmail.com";
            success.style.color = "#ff4444";
            success.style.marginTop = "20px";
            success.style.fontWeight = "600";
            success.style.textAlign = "center";

            setTimeout(() => {
                success.innerHTML = "";
            }, 7000);

        } finally {

            if (submitBtn) {
                submitBtn.disabled = false;
                submitBtn.style.opacity = "1";
                submitBtn.style.cursor = "pointer";
                submitBtn.innerHTML = originalBtnText;
            }

        }

    });

    const formInputs = contactForm.querySelectorAll("input, textarea");
    formInputs.forEach(input => {
        input.addEventListener("input", () => {
            if (input.value.trim() !== "") {
                if (input.type === "email") {
                    const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
                    input.style.border = emailPattern.test(input.value.trim())
                        ? "2px solid #19f59c"
                        : "2px solid #ffaa00";
                } else {
                    input.style.border = "2px solid #19f59c";
                }
            } else {
                input.style.border = "";
            }
        });
        input.addEventListener("focus", () => {
            input.style.transition = "border-color 0.3s ease, box-shadow 0.3s ease";
        });
    });

}





// =======================================================
// BACK TO TOP BUTTON
// =======================================================

const topButton = document.createElement("button");

topButton.className = "top-btn";

topButton.innerHTML = '<i class="fas fa-arrow-up"></i>';

topButton.setAttribute("aria-label", "Back to top");

document.body.appendChild(topButton);

window.addEventListener("scroll", () => {

    if (window.scrollY > 400) {

        topButton.classList.add("show");

    } else {

        topButton.classList.remove("show");

    }

});

topButton.addEventListener("click", () => {

    window.scrollTo({

        top: 0,

        behavior: "smooth"

    });

});





// =======================================================
// SCROLL PROGRESS BAR
// =======================================================

const progressBar = document.createElement("div");

progressBar.className = "scroll-progress";

document.body.appendChild(progressBar);

window.addEventListener("scroll", () => {

    const scroll = document.documentElement.scrollTop;

    const height = document.documentElement.scrollHeight -
        document.documentElement.clientHeight;

    const progress = (scroll / height) * 100;

    progressBar.style.width = progress + "%";

});





// =======================================================
// CUSTOM CURSOR
// =======================================================

const cursor = document.createElement("div");

cursor.className = "cursor";

document.body.appendChild(cursor);

document.addEventListener("mousemove", (e) => {

    cursor.style.left = e.clientX + "px";

    cursor.style.top = e.clientY + "px";

});

document.querySelectorAll("a, .btn, .portfolio-box, .service-box, .resume-box, .menu-btn, input, textarea, button").forEach(item => {

    item.addEventListener("mouseenter", () => {

        cursor.classList.add("grow");

    });

    item.addEventListener("mouseleave", () => {

        cursor.classList.remove("grow");

    });

});





// =======================================================
// PAGE FADE IN
// =======================================================

document.body.style.opacity = "0";

window.addEventListener("load", () => {

    document.body.style.transition = "opacity .8s";

    document.body.style.opacity = "1";

});





// =======================================================
// COPYRIGHT YEAR AUTO-UPDATE
// =======================================================

const footerParagraph = document.querySelector("footer p");
if (footerParagraph) {
    footerParagraph.innerHTML = `© ${new Date().getFullYear()} All Rights Reserved.`;
}





// =======================================================
// CONSOLE MESSAGE
// =======================================================

console.log("%cPortfolio Developed By Adehanloye Adewale",
"color:#19f59c;font-size:18px;font-weight:bold;");
