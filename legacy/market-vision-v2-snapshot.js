// MARKET VISION v2 — árbol jerárquico Índice → Sector → ETF → Empresa
// ================================================================
let mvCurrentTf = 'd1';
let mvHierarchy = null;

async function loadHierarchy() {
  if (mvHierarchy) return;
  try {
    const r = await fetch('data/hierarchy.json');
    if (!r.ok) throw new Error('HTTP ' + r.status);
    mvHierarchy = await r.json();
  } catch(e) {
    console.error('Market Vision: no se pudo cargar hierarchy.json', e);
  }
}

function mvGetPct(sym) {
  const v = flowAllData[sym]?.changes?.[mvCurrentTf];
  return v != null ? Number(v) : null;
}

function mvPctSpan(v) {
  if (v == null || isNaN(v)) return '<span class="mv2-pct mv2-flat">—</span>';
  const cls = Math.abs(v) < 0.05 ? 'mv2-flat' : v > 0 ? 'mv2-pos' : 'mv2-neg';
  return `<span class="mv2-pct ${cls}">${v > 0 ? '+' : ''}${v.toFixed(2)}%</span>`;
}

// Connector string for tree lines. cont = parent's continuation prefix.
function mvConn(cont, isLast) {
  return {
    conn: cont + (isLast ? '└── ' : '├── '),
    cont: cont + (isLast ? '    ' : '│   ')
  };
}

// Company chips row, aligned via prefix span
function mvCoListHTML(etfSym, childCont) {
  const cos = MOCK_COMPANIES.filter(c => c.etfs.includes(etfSym)).slice(0, 8);
  if (!cos.length) return '';
  const items = cos.map(co => {
    const v = getCoVar(co, mvCurrentTf);
    const n = v != null ? Number(v) : null;
    const cls = n == null ? 'mv2-flat' : n > 0 ? 'mv2-pos' : n < 0 ? 'mv2-neg' : 'mv2-flat';
    return `<span class="mv2-co" data-ticker="${co.ticker}" data-name="${co.name.replace(/"/g, '&quot;')}">` +
      `<span class="mv2-co-tick">${co.ticker}</span>` +
      `<span class="mv2-co-pct ${cls}">${n != null ? fmtPct(n) : '—'}</span>` +
    `</span>`;
  }).join('');
  return `<div class="mv2-row mv2-no-click">` +
    `<span class="mv2-pre">${childCont}</span>` +
    `<span class="mv2-toggle"> </span>` +
    `<div class="mv2-colist">${items}</div>` +
  `</div>`;
}

// ETF node (→ SMH) — expandable to companies
function mvRenderEtf(sym, cont, isLast) {
  const { conn, cont: cc } = mvConn(cont, isLast);
  const pct = mvGetPct(sym);
  const name = ETF_SHORT_NAMES[sym] || sym;
  const hasCos = MOCK_COMPANIES.some(c => c.etfs.includes(sym));
  const nid = 'mv2_etf_' + sym;
  return `<div class="mv2-node${hasCos ? '' : ' mv2-leaf'}" data-nid="${nid}">` +
    `<div class="mv2-row">` +
      `<span class="mv2-pre">${conn}→ </span>` +
      `<span class="mv2-toggle">▶</span>` +
      `<span class="mv2-label mv2-label-etf">${name}</span>` +
      `<span class="mv2-sym" data-open-etf="${sym}">${sym}</span>` +
      mvPctSpan(pct) +
    `</div>` +
    (hasCos ? `<div class="mv2-children">${mvCoListHTML(sym, cc)}</div>` : '') +
  `</div>`;
}

// Subsector node (→ Semiconductores) — expandable to ETFs
function mvRenderSubsector(subId, etfSyms, cont, isLast) {
  const sub = (mvHierarchy.subsectors || []).find(s => s.id === subId);
  if (!sub) return '';
  const { conn, cont: cc } = mvConn(cont, isLast);
  const vals = etfSyms.map(s => mvGetPct(s)).filter(v => v != null);
  const avg = vals.length ? vals.reduce((a, b) => a + b) / vals.length : null;
  const nid = 'mv2_sub_' + subId;
  const etfsHTML = etfSyms.map((s, i) => mvRenderEtf(s, cc, i === etfSyms.length - 1)).join('');
  return `<div class="mv2-node" data-nid="${nid}">` +
    `<div class="mv2-row">` +
      `<span class="mv2-pre">${conn}→ </span>` +
      `<span class="mv2-toggle">▶</span>` +
      `<span class="mv2-label mv2-label-sub">${sub.name}</span>` +
      mvPctSpan(avg) +
    `</div>` +
    `<div class="mv2-children">${etfsHTML}</div>` +
  `</div>`;
}

// Sector node (● Tecnología) — expandable to ETFs/subsectors
function mvRenderSector(sid, cont, isLast) {
  const meta = SECTOR_META[sid];
  if (!meta) return '';
  const { conn, cont: cc } = mvConn(cont, isLast);
  const sectorPct = computeSectorChange(sid, mvCurrentTf);
  const nid = 'mv2_s_' + sid;
  const etfs = ETF_BY_SECTOR[sid] || [];
  const subMap = {};
  const directEtfs = [];
  etfs.forEach(sym => {
    const subId = (mvHierarchy.etf_to_subsector || {})[sym];
    subId ? (subMap[subId] = subMap[subId] || []).push(sym) : directEtfs.push(sym);
  });
  const items = [
    ...directEtfs.map(sym => ({ t: 'etf', sym })),
    ...Object.entries(subMap).map(([sid2, syms]) => ({ t: 'sub', sid2, syms }))
  ];
  const childHTML = items.map((item, i) => {
    const last = i === items.length - 1;
    return item.t === 'etf' ? mvRenderEtf(item.sym, cc, last) : mvRenderSubsector(item.sid2, item.syms, cc, last);
  }).join('');
  return `<div class="mv2-node" data-nid="${nid}">` +
    `<div class="mv2-row">` +
      `<span class="mv2-pre">${conn}</span>` +
      `<span class="mv2-toggle">▶</span>` +
      `<span class="mv2-dot" style="background:${meta.color}"></span>` +
      `<span class="mv2-label mv2-label-sector">${meta.name}</span>` +
      mvPctSpan(sectorPct) +
    `</div>` +
    `<div class="mv2-children">${childHTML}</div>` +
  `</div>`;
}

// Key index (S&P 500, Nasdaq 100, R2K) — expandable to companies
function mvRenderKeyIndex(node, cont, isLast) {
  const { conn, cont: cc } = mvConn(cont, isLast);
  const pct = node.proxy_etf ? mvGetPct(node.proxy_etf) : null;
  const nid = 'mv2_ki_' + node.id;
  const symHTML = node.proxy_etf ? `<span class="mv2-sym" data-open-etf="${node.proxy_etf}">${node.proxy_etf}</span>` : '';
  const hasCos = node.proxy_etf ? MOCK_COMPANIES.some(c => c.etfs.includes(node.proxy_etf)) : false;
  return `<div class="mv2-node${hasCos ? '' : ' mv2-leaf'}" data-nid="${nid}">` +
    `<div class="mv2-row">` +
      `<span class="mv2-pre">${conn}→ </span>` +
      `<span class="mv2-toggle">▶</span>` +
      `<span class="mv2-label mv2-label-subidx">${node.name}</span>` +
      symHTML +
      mvPctSpan(pct) +
    `</div>` +
    (hasCos ? `<div class="mv2-children">${mvCoListHTML(node.proxy_etf, cc)}</div>` : '') +
  `</div>`;
}

// MSCI World / MSCI EM — expandable to Índices + Sectores groups
function mvRenderChildIndex(node, cont, isLast, startOpen) {
  const { conn, cont: cc } = mvConn(cont, isLast);
  const pct = node.proxy_etf ? mvGetPct(node.proxy_etf) : null;
  const nid = 'mv2_ci_' + node.id;
  const symHTML = node.proxy_etf ? `<span class="mv2-sym" data-open-etf="${node.proxy_etf}">${node.proxy_etf}</span>` : '';
  const keyIndices = (node.key_indices || []).map(kid => mvHierarchy.indices.find(i => i.id === kid)).filter(Boolean);
  const sectors = node.sectors_applicable || [];
  const hasIdx = keyIndices.length > 0;
  const hasSec = sectors.length > 0;
  const hasChildren = hasIdx || hasSec;
  let body = '';
  if (hasIdx) {
    const { conn: gc, cont: gCont } = mvConn(cc, !hasSec);
    body += `<div class="mv2-row mv2-no-click">` +
      `<span class="mv2-pre">${gc}</span>` +
      `<span class="mv2-toggle"> </span>` +
      `<span class="mv2-label mv2-label-group">Índices</span>` +
    `</div>`;
    body += keyIndices.map((ki, i) => mvRenderKeyIndex(ki, gCont, i === keyIndices.length - 1)).join('');
  }
  if (hasSec) {
    const { conn: gc, cont: gCont } = mvConn(cc, true);
    body += `<div class="mv2-row mv2-no-click">` +
      `<span class="mv2-pre">${gc}</span>` +
      `<span class="mv2-toggle"> </span>` +
      `<span class="mv2-label mv2-label-group">Sectores</span>` +
    `</div>`;
    body += sectors.map((sid, i) => mvRenderSector(sid, gCont, i === sectors.length - 1)).join('');
  }
  return `<div class="mv2-node${startOpen ? ' mv2-open' : ''}${hasChildren ? '' : ' mv2-leaf'}" data-nid="${nid}">` +
    `<div class="mv2-row${hasChildren ? '' : ' mv2-no-click'}">` +
      `<span class="mv2-pre">${conn}</span>` +
      `<span class="mv2-toggle">${hasChildren ? (startOpen ? '▼' : '▶') : ' '}</span>` +
      `<span class="mv2-label mv2-label-index">${node.short_name || node.name}</span>` +
      symHTML +
      mvPctSpan(pct) +
    `</div>` +
    (hasChildren ? `<div class="mv2-children">${body}</div>` : '') +
  `</div>`;
}

function renderMV2() {
  const el = document.getElementById('mv2Container');
  if (!el) return;
  if (!mvHierarchy) {
    el.innerHTML = '<div style="padding:6px 0;font-family:var(--font-sans);font-size:12px;color:var(--text-dim)">Cargando jerarquía…</div>';
    loadHierarchy().then(() => { if (mvHierarchy) renderMV2(); });
    return;
  }
  const root = mvHierarchy.indices.find(i => i.id === 'msci_acwi');
  if (!root) return;
  const pct = root.proxy_etf ? mvGetPct(root.proxy_etf) : null;
  const symHTML = root.proxy_etf ? `<span class="mv2-sym" data-open-etf="${root.proxy_etf}">${root.proxy_etf}</span>` : '';
  const children = (root.children || []).map(cid => mvHierarchy.indices.find(i => i.id === cid)).filter(Boolean);
  const childrenHTML = children.map((child, i) =>
    mvRenderChildIndex(child, '', i === children.length - 1, child.id === 'msci_world')
  ).join('');
  el.innerHTML =
    `<div class="mv2-node mv2-open" data-nid="mv2_root">` +
      `<div class="mv2-row">` +
        `<span class="mv2-toggle">▼</span>` +
        `<span class="mv2-label mv2-label-index" style="font-size:14px;font-weight:800">${root.short_name || root.name}</span>` +
        symHTML +
        mvPctSpan(pct) +
      `</div>` +
      `<div class="mv2-children" style="display:block">${childrenHTML}</div>` +
    `</div>`;
}

function setupMV2() {
  const sel = document.getElementById('mv2TfSelector');
  if (sel) {
    sel.addEventListener('click', e => {
      const btn = e.target.closest('button[data-tf]');
      if (!btn) return;
      sel.querySelectorAll('button').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      mvCurrentTf = btn.dataset.tf;
      renderMV2();
    });
  }
  const el = document.getElementById('mv2Container');
  if (!el) return;
  el.addEventListener('click', e => {
    // ETF symbol → open modal
    const symEl = e.target.closest('[data-open-etf]');
    if (symEl) {
      e.stopPropagation();
      const sym = symEl.dataset.openEtf;
      if (sym && flowAllData[sym]) {
        const labelEl = symEl.closest('.mv2-node')?.querySelector('.mv2-label');
        openModal(sym, labelEl?.textContent || sym);
      }
      return;
    }
    // Company chip → open company modal
    const co = e.target.closest('.mv2-co[data-ticker]');
    if (co) {
      e.stopPropagation();
      openCompanyModal(co.dataset.ticker, co.dataset.name);
      return;
    }
    // Row click → toggle expand/collapse
    const row = e.target.closest('.mv2-row');
    if (!row || row.classList.contains('mv2-no-click')) return;
    const node = row.closest('.mv2-node');
    if (!node || node.classList.contains('mv2-leaf')) return;
    const ch = node.querySelector(':scope > .mv2-children');
    if (!ch) return;
    node.classList.toggle('mv2-open');
    const tog = row.querySelector('.mv2-toggle');
    if (tog) tog.textContent = node.classList.contains('mv2-open') ? '▼' : '▶';
  });
  loadHierarchy().then(() => renderMV2());
}

// ================================================================
// VIEW TABS
// ================================================================
function setupViewTabs() {
  document.querySelectorAll('.view-tab').forEach(tab => {
    tab.addEventListener('click', () => {
      document.querySelectorAll('.view-tab').forEach(t => t.classList.remove('active'));
      tab.classList.add('active');
      const view = tab.dataset.view;
      document.getElementById('companiesView').style.display = view === 'companies' ? '' : 'none';
      document.getElementById('etfsView').style.display = view === 'etfs' ? '' : 'none';
    });
  });
}