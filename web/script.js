// qscreen-filing-tool marketing site — minimal vanilla JS
// (no framework, no build, no npm install)

(function () {
  'use strict';

  // Footer year — set once on load so the page is fully static after first paint.
  const yr = document.getElementById('yr');
  if (yr) {
    yr.textContent = String(new Date().getFullYear());
  }

  // Smooth-scroll anchor links (with sticky-nav offset).
  document.querySelectorAll('a[href^="#"]').forEach((a) => {
    a.addEventListener('click', (e) => {
      const id = a.getAttribute('href');
      if (!id || id === '#') return;
      const target = document.querySelector(id);
      if (!target) return;
      e.preventDefault();
      const navH = document.querySelector('.nav')?.offsetHeight ?? 0;
      const top = target.getBoundingClientRect().top + window.scrollY - navH - 16;
      window.scrollTo({ top, behavior: 'smooth' });
    });
  });

  // Track outbound link clicks (analytics if added later; no-op today).
  document.querySelectorAll('a[href^="http"]').forEach((a) => {
    a.setAttribute('rel', 'noopener noreferrer');
  });
})();
