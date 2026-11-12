// Reveal elements as they scroll into view; pages add their own behaviour.
const io = new IntersectionObserver((entries) => {
  for (const e of entries) if (e.isIntersecting) { e.target.classList.add("in"); io.unobserve(e.target); }
}, { threshold: 0.15 });
document.querySelectorAll(".reveal").forEach((el) => io.observe(el));
// Close the Learn menu when clicking elsewhere.
document.addEventListener("click", (ev) => {
  document.querySelectorAll("details.menu[open]").forEach((d) => { if (!d.contains(ev.target)) d.open = false; });
});
