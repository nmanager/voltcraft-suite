// VoltCraft - Interactive Core Client Engine
(function() {
  'use strict';

  // 1. Theme Management
  const themeToggle = document.getElementById('themeToggle');
  const currentTheme = localStorage.getItem('voltcraft_theme') || 'dark';
  document.documentElement.setAttribute('data-theme', currentTheme);
  updateThemeIcon(currentTheme);

  if (themeToggle) {
    themeToggle.addEventListener('click', () => {
      const active = document.documentElement.getAttribute('data-theme');
      const next = active === 'dark' ? 'light' : 'dark';
      document.documentElement.setAttribute('data-theme', next);
      localStorage.setItem('voltcraft_theme', next);
      updateThemeIcon(next);
    });
  }

  function updateThemeIcon(theme) {
    if (!themeToggle) return;
    themeToggle.textContent = theme === 'dark' ? '☀️' : '🌙';
  }

  // 2. Unit Formatter Utility
  window.formatUnit = function(value, unit) {
    if (isNaN(value) || !isFinite(value)) return "—";
    if (unit === 'Ω') {
      if (value >= 1e6) return (value / 1e6).toFixed(2) + " MΩ";
      if (value >= 1e3) return (value / 1e3).toFixed(2) + " kΩ";
      return value.toFixed(2) + " Ω";
    }
    if (unit === 'W') {
      if (value < 1) return (value * 1000).toFixed(1) + " mW";
      return value.toFixed(2) + " W";
    }
    if (unit === 'Hz') {
      if (value >= 1e6) return (value / 1e6).toFixed(2) + " MHz";
      if (value >= 1e3) return (value / 1e3).toFixed(2) + " kHz";
      return value.toFixed(1) + " Hz";
    }
    return value.toLocaleString('en-US', { maximumFractionDigits: 2 }) + " " + unit;
  };

  // 3. Live Ohm's Law Calculator (Home Widget)
  const vInput = document.getElementById('quick_v');
  const vSlider = document.getElementById('quick_v_slider');
  const iInput = document.getElementById('quick_i');
  const iSlider = document.getElementById('quick_i_slider');
  const outR = document.getElementById('quick_out_r');
  const outP = document.getElementById('quick_out_p');

  function calculateQuickOhms() {
    if (!vInput || !iInput) return;
    const v = parseFloat(vInput.value) || 0;
    const i = parseFloat(iInput.value) || 0;

    if (i <= 0) {
      if (outR) outR.textContent = "∞ Ω";
      if (outP) outP.textContent = "0 W";
      return;
    }

    const r = v / i;
    const p = v * i;

    if (outR) outR.textContent = window.formatUnit(r, 'Ω');
    if (outP) outP.textContent = window.formatUnit(p, 'W');
  }

  if (vInput && vSlider && iInput && iSlider) {
    vInput.addEventListener('input', (e) => {
      vSlider.value = e.target.value;
      calculateQuickOhms();
    });
    vSlider.addEventListener('input', (e) => {
      vInput.value = e.target.value;
      calculateQuickOhms();
    });
    iInput.addEventListener('input', (e) => {
      iSlider.value = e.target.value;
      calculateQuickOhms();
    });
    iSlider.addEventListener('input', (e) => {
      iInput.value = e.target.value;
      calculateQuickOhms();
    });
    calculateQuickOhms();
  }

  // 4. Live Search & Filtering
  const searchInput = document.getElementById('calcSearch');
  const filterChips = document.querySelectorAll('.chip');
  const cards = document.querySelectorAll('.calc-card');

  let currentCategory = 'all';

  function filterCards() {
    const query = (searchInput ? searchInput.value : '').toLowerCase().trim();
    cards.forEach(card => {
      const title = (card.getAttribute('data-title') || '').toLowerCase();
      const cat = (card.getAttribute('data-category') || '').toLowerCase();
      const desc = (card.getAttribute('data-desc') || '').toLowerCase();

      const matchesCat = (currentCategory === 'all') || (cat === currentCategory);
      const matchesQuery = !query || title.includes(query) || desc.includes(query) || cat.includes(query);

      card.style.display = (matchesCat && matchesQuery) ? 'flex' : 'none';
    });
  }

  if (searchInput) {
    searchInput.addEventListener('input', filterCards);
  }

  filterChips.forEach(chip => {
    chip.addEventListener('click', () => {
      filterChips.forEach(c => c.classList.remove('active'));
      chip.classList.add('active');
      currentCategory = (chip.getAttribute('data-category') || 'all').toLowerCase();
      filterCards();
    });
  });

  // 5. Copy Result Helper
  window.copyResult = function(val, btnId) {
    navigator.clipboard.writeText(val).then(() => {
      const btn = document.getElementById(btnId);
      if (btn) {
        const orig = btn.innerHTML;
        btn.innerHTML = "✓ Copied!";
        setTimeout(() => btn.innerHTML = orig, 1800);
      }
    });
  };

  // 6. Pro Export Hook
  window.triggerProExport = function() {
    alert("⚡ VoltCraft Pro: Calculation export generates a certified PDF/CSV report with schematic diagrams and BOM recommendations. Available via Pro subscription!");
  };

})();
