// theme toggle (light/dark). Initial value is set synchronously in
// base.html's <head> to avoid a flash; this just handles the click.
document.addEventListener('DOMContentLoaded', function () {
  var toggles = document.querySelectorAll('.theme-toggle');
  if (!toggles.length) return;

  var sync = function () {
    var isDark = document.documentElement.getAttribute('data-theme') === 'dark';
    toggles.forEach(function (btn) {
      btn.setAttribute('aria-pressed', String(isDark));
    });
  };

  toggles.forEach(function (btn) {
    btn.addEventListener('click', function () {
      var next = document.documentElement.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
      document.documentElement.setAttribute('data-theme', next);
      localStorage.setItem('theme', next);
      sync();
    });
  });

  sync();
});

// Hero parallax fallback. The motion itself is defined in _homepage.scss as
// scroll-driven animations; browsers without `animation-timeline: scroll()`
// (Firefox at the time of writing) get the same curves here through the
// --hero-p custom property, which the stylesheet reads via calc().
document.addEventListener('DOMContentLoaded', function () {
  var hero = document.querySelector('.hero-section');
  if (!hero) return;
  if (window.CSS && CSS.supports && CSS.supports('animation-timeline', 'scroll()')) return;
  if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;

  var RANGE = 0.7; // must match animation-range (70vh) in _homepage.scss
  var ticking = false;

  var update = function () {
    ticking = false;
    var range = window.innerHeight * RANGE || 1;
    var p = Math.min(1, Math.max(0, window.scrollY / range));
    hero.style.setProperty('--hero-p', p.toFixed(4));
  };

  var onScroll = function () {
    if (!ticking) {
      ticking = true;
      window.requestAnimationFrame(update);
    }
  };

  window.addEventListener('scroll', onScroll, { passive: true });
  window.addEventListener('resize', onScroll);
  update();
});
