const ICONS = {
  home: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m3 9 9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/></svg>`,
  stream: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="23 7 16 12 23 17 23 7"/><rect x="1" y="5" width="15" height="14" rx="2" ry="2"/></svg>`,
  animal: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22c7 0 10-4 10-8 0-2-1-3.5-2-5-1-2-2-3-4-3-1-1-2-2-4-2s-3 1-4 2c-2 0-3 1-4 3-1 1.5-2 3-2 5 0 4 3 8 10 8z"/><path d="M15 12c0 1.66-1.34 3-3 3s-3-1.34-3-3 1.34-3 3-3 3 1.34 3 3z"/></svg>`,
  fire: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M8.5 14.5A2.5 2.5 0 0 0 11 17h2a2.5 2.5 0 0 0 0-5H7"/><path d="M15 7c0-1.5-1-2.5-2-3 0 1-1 2-3 2.5S7 10 9 11.5c.8.7 1 2 .5 2.5"/><path d="M22 8c0 6-4 10-10 10S2 14 2 8c0-2.5 1-4.5 2.5-6C5 4 7 5 8 7c.5-2 1-4 3-5 0 2 1 4 3 4.5C16 7 18 5 18 2c2 1.5 4 4 4 6z"/></svg>`,
  weapon: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 12h13M13 8l4 4-4 4M19 12h2"/><path d="M7 9V7a1 1 0 0 1 1-1h2"/><path d="M7 15v2a1 1 0 0 0 1 1h2"/></svg>`,
  logs: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/><polyline points="10 9 9 9 8 9"/></svg>`,
  shield: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>`,
  chevrons: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="11 17 6 12 11 7"/><polyline points="18 17 13 12 18 7"/></svg>`,
  bell: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"/><path d="M13.73 21a2 2 0 0 1-3.46 0"/></svg>`,
  user: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>`,
  activity: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/></svg>`,
  logo: `<svg viewBox="0 0 50 39" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M16.4992 2H37.5808L22.0816 24.9729H1L16.4992 2Z" fill="white"/><path d="M17.4224 27.102L11.4192 36H33.5008L49 13.0271H32.7024L23.2064 27.102H17.4224Z" fill="white"/></svg>`,
};

const NAV_ITEMS = [
  { href: '/',               icon: 'home',   label: 'Dashboard',         tooltip: 'Dashboard' },
  { href: '/detect/threats', icon: 'shield', label: 'Animal & Weapon',   tooltip: 'Animal & Weapon',  notif: null },
  { href: '/detect/fire',    icon: 'fire',   label: 'Fire Detection',     tooltip: 'Fire Detection',    notif: null },
  { href: '/logs',           icon: 'logs',   label: 'Event Logs',         tooltip: 'Event Logs' },
];

function buildSidebar(activePath) {
  const navHTML = NAV_ITEMS.map(item => {
    const isActive = (activePath === item.href) || (item.href !== '/' && activePath.startsWith(item.href));
    const badge = item.notif ? `<span class="nav-badge">${item.notif}</span>` : '';
    return `
      <a href="${item.href}" class="nav-item${isActive ? ' active' : ''}" data-tooltip="${item.tooltip}">
        <span class="nav-icon">${ICONS[item.icon]}</span>
        <span class="nav-label">${item.label}</span>
        ${badge}
      </a>`;
  }).join('');

  return `
    <div class="sidebar-brand" href="/">
      <div class="brand-logo">${ICONS.logo}</div>
      <div class="brand-text">
        <span class="brand-name">ApexGuard AI</span>
        <span class="brand-sub">Surveillance</span>
      </div>
    </div>

    <nav class="sidebar-nav">
      <div class="nav-section-label">Navigation</div>
      ${navHTML}
    </nav>

    <div class="sidebar-status">
      <div class="status-chip">
        <span class="pulse-dot"></span>
        <div class="status-chip-text">
          System Online
          <strong>All Services Active</strong>
        </div>
      </div>
    </div>

    <button id="sidebar-toggle" onclick="toggleSidebar()">
      <span class="toggle-icon">${ICONS.chevrons}</span>
      <span id="toggle-label">Collapse</span>
    </button>
  `;
}

function toggleSidebar() {
  const sidebar = document.getElementById('sidebar');
  const body = document.body;
  const collapsed = sidebar.classList.toggle('collapsed');
  body.classList.toggle('sidebar-collapsed', collapsed);
  localStorage.setItem('sidebarCollapsed', collapsed ? '1' : '0');
}

function startClock() {
  const el = document.getElementById('header-clock');
  if (!el) return;
  const tick = () => {
    el.textContent = new Date().toLocaleTimeString('en-IN', { hour12: false });
  };
  tick();
  setInterval(tick, 1000);
}

function initSidebar(activePath) {
  const sidebar = document.getElementById('sidebar');
  if (!sidebar) return;
  sidebar.innerHTML = buildSidebar(activePath);

  if (localStorage.getItem('sidebarCollapsed') === '1') {
    sidebar.classList.add('collapsed');
    document.body.classList.add('sidebar-collapsed');
  }
  startClock();
}
