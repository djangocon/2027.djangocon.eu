// Site behaviour: theme switch, desktop dropdowns, mobile menu.
//
// Deliberately dependency-free — Bootstrap's JS is still bundled for any
// legacy markup, but nothing here needs it.

(function () {
  'use strict';

  var THEME_KEY = 'djceu-theme';

  // ---------------------------------------------------------------------------
  // Theme switch
  // ---------------------------------------------------------------------------
  // The initial theme is applied by the inline script in base.html (before
  // paint). This only handles later changes.

  function currentTheme() {
    return document.documentElement.getAttribute('data-theme') === 'light'
      ? 'light'
      : 'dark';
  }

  function applyTheme(theme) {
    document.documentElement.setAttribute('data-theme', theme);
    try {
      localStorage.setItem(THEME_KEY, theme);
    } catch (e) {
      // Private mode or blocked storage: the theme still applies for this page.
    }
    document.querySelectorAll('[data-theme-toggle]').forEach(function (btn) {
      btn.setAttribute(
        'aria-label',
        theme === 'dark' ? 'Switch to light theme' : 'Switch to dark theme',
      );
    });
  }

  function initTheme() {
    applyTheme(currentTheme());

    document.querySelectorAll('[data-theme-toggle]').forEach(function (btn) {
      btn.addEventListener('click', function () {
        applyTheme(currentTheme() === 'dark' ? 'light' : 'dark');
      });
    });

    // Follow the OS only while the visitor has not made an explicit choice.
    var stored = null;
    try {
      stored = localStorage.getItem(THEME_KEY);
    } catch (e) {
      /* ignore */
    }
    if (!stored && window.matchMedia) {
      var mq = window.matchMedia('(prefers-color-scheme: light)');
      var onChange = function (e) {
        document.documentElement.setAttribute(
          'data-theme',
          e.matches ? 'light' : 'dark',
        );
      };
      if (mq.addEventListener) {
        mq.addEventListener('change', onChange);
      }
    }
  }

  // ---------------------------------------------------------------------------
  // Desktop dropdowns
  // ---------------------------------------------------------------------------
  // Open on click (and on hover via CSS). Only one open at a time.

  function initDropdowns() {
    var toggles = document.querySelectorAll('.site-nav__toggle');

    function closeAll(except) {
      toggles.forEach(function (t) {
        if (t !== except) {
          t.setAttribute('aria-expanded', 'false');
          t.parentElement.classList.remove('is-open');
        }
      });
    }

    toggles.forEach(function (toggle) {
      toggle.addEventListener('click', function (e) {
        e.preventDefault();
        var isOpen = toggle.getAttribute('aria-expanded') === 'true';
        closeAll(toggle);
        toggle.setAttribute('aria-expanded', isOpen ? 'false' : 'true');
        toggle.parentElement.classList.toggle('is-open', !isOpen);
      });
    });

    document.addEventListener('click', function (e) {
      if (!e.target.closest('.site-nav__item--has-menu')) {
        closeAll(null);
      }
    });

    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape') {
        closeAll(null);
      }
    });
  }

  // ---------------------------------------------------------------------------
  // Mobile menu
  // ---------------------------------------------------------------------------

  function initMobileNav() {
    var burger = document.querySelector('.site-header__burger');
    var panel = document.getElementById('mobile-nav');
    if (!burger || !panel) return;

    burger.addEventListener('click', function () {
      var isOpen = burger.getAttribute('aria-expanded') === 'true';
      burger.setAttribute('aria-expanded', isOpen ? 'false' : 'true');
      burger.setAttribute('aria-label', isOpen ? 'Open menu' : 'Close menu');
      burger.classList.toggle('is-open', !isOpen);
      panel.hidden = isOpen;
      // Stop the page scrolling behind the open panel. The class goes on <html>
      // as well as <body> — <body> alone does not hold on iOS Safari.
      document.documentElement.classList.toggle('has-mobile-nav', !isOpen);
      document.body.classList.toggle('has-mobile-nav', !isOpen);
    });

    // Accordion inside the mobile panel.
    panel.querySelectorAll('.mobile-nav__toggle').forEach(function (toggle) {
      toggle.addEventListener('click', function () {
        var submenu = toggle.nextElementSibling;
        var isOpen = toggle.getAttribute('aria-expanded') === 'true';
        toggle.setAttribute('aria-expanded', isOpen ? 'false' : 'true');
        if (submenu) submenu.hidden = isOpen;
      });
    });
  }

  // ---------------------------------------------------------------------------
  // Sticky header shadow — only once the page has scrolled off the top.
  // ---------------------------------------------------------------------------

  function initHeaderScroll() {
    var header = document.querySelector('.site-header');
    if (!header) return;

    var ticking = false;
    function update() {
      header.classList.toggle('is-scrolled', window.scrollY > 8);
      ticking = false;
    }
    window.addEventListener(
      'scroll',
      function () {
        if (!ticking) {
          window.requestAnimationFrame(update);
          ticking = true;
        }
      },
      { passive: true },
    );
    update();
  }

  function init() {
    initTheme();
    initDropdowns();
    initMobileNav();
    initHeaderScroll();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
