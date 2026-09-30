(() => {
  const tabs = [...document.querySelectorAll('[data-floor]')];
  const panels = [...document.querySelectorAll('.floor-panel')];
  const notes = [...document.querySelectorAll('[data-floor-note]')];
  function selectFloor(tab) {
    tabs.forEach(item => { const active = item === tab; item.setAttribute('aria-selected', String(active)); item.tabIndex = active ? 0 : -1; });
    panels.forEach(panel => { panel.hidden = panel.id !== `plan-${tab.dataset.floor}`; panel.setAttribute('role', 'tabpanel'); });
    notes.forEach(note => { note.hidden = note.dataset.floorNote !== tab.dataset.floor; });
  }
  if (tabs.length) {
    document.querySelector('.plan-tabs').hidden = false;
    selectFloor(tabs[0]);
    tabs.forEach((tab, index) => {
      tab.addEventListener('click', () => selectFloor(tab));
      tab.addEventListener('keydown', event => {
        if (!['ArrowLeft', 'ArrowRight', 'ArrowUp', 'ArrowDown', 'Home', 'End'].includes(event.key)) return;
        event.preventDefault();
        let next = event.key === 'Home' ? 0 : event.key === 'End' ? tabs.length - 1 : (index + (['ArrowLeft', 'ArrowUp'].includes(event.key) ? -1 : 1) + tabs.length) % tabs.length;
        selectFloor(tabs[next]); tabs[next].focus();
      });
    });
  }

  const dialog = document.getElementById('image-dialog');
  const dialogImage = document.getElementById('dialog-image');
  const imageScroll = document.querySelector('.dialog-image-scroll');
  let scale = 100;
  function setScale(value) {
    scale = Math.max(100, Math.min(300, value));
    dialogImage.style.width = `${scale}%`;
    imageScroll.classList.toggle('is-zoomed', scale > 100);
    document.getElementById('zoom-level').value = `${scale}%`;
    document.getElementById('zoom-out').disabled = scale === 100;
    document.getElementById('zoom-in').disabled = scale === 300;
  }
  if (dialog && typeof dialog.showModal === 'function') {
    document.querySelectorAll('[data-zoom]').forEach(link => link.addEventListener('click', event => {
      if (event.ctrlKey || event.metaKey || event.shiftKey || event.altKey) return;
      event.preventDefault();
      const caption = link.dataset.caption || 'Drawing detail';
      document.getElementById('image-dialog-title').textContent = caption;
      document.getElementById('image-original').href = link.href;
      dialogImage.src = link.href;
      dialogImage.alt = link.querySelector('img')?.alt || caption;
      setScale(100);
      dialog.showModal();
      imageScroll.scrollTo(0, 0);
      document.getElementById('close-dialog').focus();
    }));
    document.getElementById('close-dialog').addEventListener('click', () => dialog.close());
    document.getElementById('zoom-in').addEventListener('click', () => setScale(scale + 50));
    document.getElementById('zoom-out').addEventListener('click', () => setScale(scale - 50));
    dialog.addEventListener('click', event => { if (event.target === dialog) { const r = dialog.getBoundingClientRect(); if (event.clientX < r.left || event.clientX > r.right || event.clientY < r.top || event.clientY > r.bottom) dialog.close(); } });
    dialog.addEventListener('close', () => { document.body.style.overflow = ''; });
    document.querySelectorAll('[data-zoom]').forEach(link => link.addEventListener('click', () => { if (dialog.open) document.body.style.overflow = 'hidden'; }));
  }

  const loadModel = document.getElementById('load-model');
  const modelContainer = document.getElementById('model-container');
  loadModel?.addEventListener('click', () => {
    if (!modelContainer.querySelector('iframe')) {
      const frame = document.createElement('iframe');
      frame.src = 'model/site-model-3d.html#yard';
      frame.title = 'Interactive schematic ADU model, Option F revision 2';
      frame.allowFullscreen = true;
      modelContainer.append(frame);
    }
    modelContainer.hidden = false;
    loadModel.disabled = true;
    loadModel.textContent = 'Model open below';
    document.getElementById('close-model').focus({ preventScroll: true });
    modelContainer.scrollIntoView({ block: 'start', behavior: matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth' });
  });
  document.getElementById('close-model')?.addEventListener('click', () => {
    modelContainer.hidden = true;
    modelContainer.querySelector('iframe')?.remove();
    loadModel.disabled = false;
    loadModel.textContent = 'Explore in 3D ↗';
    loadModel.focus();
  });
  document.querySelector('.walkthrough')?.addEventListener('toggle', event => {
    if (event.target.open) { const frame = event.target.querySelector('iframe[data-src]'); if (frame) { frame.src = frame.dataset.src; delete frame.dataset.src; } }
  });

  const navLinks = [...document.querySelectorAll('.section-nav a')];
  if ('IntersectionObserver' in window) {
    const observer = new IntersectionObserver(entries => {
      entries.forEach(entry => { if (entry.isIntersecting) navLinks.forEach(link => { if (link.hash === `#${entry.target.id}`) link.setAttribute('aria-current', 'location'); else link.removeAttribute('aria-current'); }); });
    }, { rootMargin: '-15% 0px -65% 0px', threshold: 0 });
    navLinks.forEach(link => { const target = document.querySelector(link.hash); if (target) observer.observe(target); });
  }
  const aliases = { summary: 'overview', 'floor-plans': 'plans', interiors: 'explore', model: 'explore', inspiration: 'files', site: 'decisions' };
  const originalHash = location.hash.slice(1);
  if (aliases[originalHash]) { history.replaceState(null, '', `#${aliases[originalHash]}`); document.getElementById(aliases[originalHash])?.scrollIntoView(); }
})();
