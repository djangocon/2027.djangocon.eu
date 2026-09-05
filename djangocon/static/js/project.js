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

// popup js
function openPopup() {
  document.getElementById('popup').style.display = 'block';
  document.getElementById('overlay').style.display = 'block';
}

function closePopup() {
  document.getElementById('popup').style.display = 'none';
  document.getElementById('overlay').style.display = 'none';
}
