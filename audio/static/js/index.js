// index.js

document.addEventListener("DOMContentLoaded", () => {
  console.log("Sound Remover - Index page loaded ✅");

  // เล็กๆ น้อยๆ: ทำให้ปุ่ม CTA สั่นเบาๆ เมื่อ hover
  const ctaButton = document.querySelector(".cta-btn");
  if (ctaButton) {
    ctaButton.addEventListener("mouseenter", () => {
      ctaButton.classList.add("animate__animated", "animate__pulse");
    });
    ctaButton.addEventListener("mouseleave", () => {
      ctaButton.classList.remove("animate__animated", "animate__pulse");
    });
  }
  
});

