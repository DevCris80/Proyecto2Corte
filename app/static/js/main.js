/* ── Toast system ── */
function showToast(msg, type) {
  type = type || 'success';
  var container = document.getElementById('toast-container');
  if (!container) return;
  var el = document.createElement('div');
  el.className = 'toast toast-' + type;
  el.textContent = msg;
  container.appendChild(el);
  requestAnimationFrame(function () {
    el.classList.add('toast-visible');
  });
  setTimeout(function () {
    el.classList.remove('toast-visible');
    el.addEventListener('transitionend', function () { el.remove(); });
  }, 5000);
}

document.addEventListener('DOMContentLoaded', function () {
  /* ── Read toast from query params ── */
  var params = new URLSearchParams(window.location.search);
  var msg = params.get('toast');
  if (msg) {
    showToast(msg, params.get('toast_type') || 'success');
    /* clean URL without reload */
    params.delete('toast');
    params.delete('toast_type');
    var qs = params.toString();
    var url = window.location.pathname + (qs ? '?' + qs : '');
    history.replaceState(null, '', url);
  }

  /* ── Confirm dialogs ── */
  document.querySelectorAll('[data-confirm]').forEach(function (el) {
    el.addEventListener('submit', function (e) {
      if (!confirm(el.getAttribute('data-confirm') || '¿Estás seguro?')) {
        e.preventDefault();
      }
    });
  });

  document.querySelectorAll('[data-confirm]').forEach(function (el) {
    if (el.tagName === 'BUTTON' || el.tagName === 'A') {
      el.addEventListener('click', function (e) {
        if (!confirm(el.getAttribute('data-confirm') || '¿Estás seguro?')) {
          e.preventDefault();
        }
      });
    }
  });

  /* ── Modal overlay click-to-close ── */
  document.querySelectorAll('.modal-overlay').forEach(function (overlay) {
    overlay.addEventListener('click', function (e) {
      if (e.target === overlay) {
        var id = overlay.getAttribute('data-modal');
        if (id) window.closeModal(id);
      }
    });
  });

  /* ── Escape key closes modal ── */
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') {
      document.querySelectorAll('.modal-overlay.modal-open').forEach(function (m) {
        var id = m.getAttribute('data-modal');
        if (id) window.closeModal(id);
      });
    }
  });

  /* ── Scroll-reveal animation ── */
  var revealElements = document.querySelectorAll('.reveal');
  if (revealElements.length) {
    var observer = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add('visible');
        }
      });
    }, { threshold: 0.1, rootMargin: '0px 0px -40px 0px' });

    revealElements.forEach(function (el) {
      observer.observe(el);
    });
  }

  /* ── Sortable table columns (event delegation) ── */
});

/* ── Preload images for modals in the background ── */
window.addEventListener('load', function () {
  setTimeout(function () {
    document.querySelectorAll('.clickable-row').forEach(function (row) {
      var raw = row.getAttribute('data-detail');
      if (raw) {
        try {
          var data = JSON.parse(raw);
          if (data.imagen_url) {
            var img = new Image();
            img.src = data.imagen_url;
          }
        } catch (e) {}
      }
    });
  }, 500); // 500ms delay to avoid blocking initial page render
});

/* ── Sidebar toggle ── */
var sidebarToggle = document.getElementById('sidebarToggle');
var sidebar = document.getElementById('sidebar');
if (sidebarToggle && sidebar) {
  sidebarToggle.addEventListener('click', function () {
    sidebar.classList.toggle('collapsed');
    try { localStorage.setItem('sidebar-collapsed', sidebar.classList.contains('collapsed')); } catch(e) {}
  });
  try {
    if (localStorage.getItem('sidebar-collapsed') === 'true') {
      sidebar.classList.add('collapsed');
    }
  } catch(e) {}
}

/* ── Modal controls ── */
window.openModal = function (id) {
  var modal = document.getElementById(id);
  if (modal) {
    modal.classList.add('modal-open');
    document.body.style.overflow = 'hidden';
  }
};

window.closeModal = function (id) {
  var modal = document.getElementById(id);
  if (modal) {
    modal.classList.remove('modal-open');
    document.body.style.overflow = '';
  }
};

/* ── Sortable table columns ── */
document.addEventListener('click', function (e) {
  var th = e.target.closest('th.sortable');
  if (!th) return;
  var table = th.closest('.data-table');
  if (!table) return;
  var col = parseInt(th.getAttribute('data-col'));
  var tbody = table.querySelector('tbody');
  if (!tbody) return;
  var rows = Array.from(tbody.querySelectorAll('tr'));
  var isAsc = th.classList.contains('sort-asc');
  table.querySelectorAll('thead th.sortable').forEach(function (h) {
    h.classList.remove('sort-asc', 'sort-desc');
  });
  rows.sort(function (a, b) {
    var aCell = a.children[col];
    var bCell = b.children[col];
    if (!aCell || !bCell) return 0;
    var aRaw = aCell.textContent.trim();
    var bRaw = bCell.textContent.trim();
    var aClean = aRaw.replace(/[$,\s]|d[ií]as?|%/g, '').trim();
    var bClean = bRaw.replace(/[$,\s]|d[ií]as?|%/g, '').trim();
    var aNum = parseFloat(aClean);
    var bNum = parseFloat(bClean);

    var dateRegex = /^\d{4}-\d{2}-\d{2}/;
    if (dateRegex.test(aRaw) && dateRegex.test(bRaw)) {
      return isAsc ? bRaw.localeCompare(aRaw) : aRaw.localeCompare(bRaw);
    }

    var isNumA = aClean !== '' && !isNaN(Number(aClean));
    var isNumB = bClean !== '' && !isNaN(Number(bClean));
    if (isNumA && isNumB) {
      return isAsc ? bNum - aNum : aNum - bNum;
    }
    return isAsc ? bRaw.localeCompare(aRaw) : aRaw.localeCompare(bRaw);
  });
  rows.forEach(function (row) { tbody.appendChild(row); });
  th.classList.add(isAsc ? 'sort-desc' : 'sort-asc');
});

/* ── Detail row click (ignore clicks on actions) ── */
document.addEventListener('click', function (e) {
  if (e.target.closest('.actions-cell')) return;
  var row = e.target.closest('.clickable-row');
  if (!row) return;

  var raw = row.getAttribute('data-detail');
  if (!raw) return;

  var data, tipo;
  try {
    data = JSON.parse(raw);
    tipo = row.getAttribute('data-type') || '';
  } catch (err) {
    return;
  }

  var titulo = document.getElementById('detalle-titulo');
  var imagenCol = document.getElementById('detalle-imagen-col');
  var imagen = document.getElementById('detalle-imagen');
  var campos = document.getElementById('detalle-campos');
  var btnEditar = document.getElementById('detalle-btn-editar');
  var btnProductos = document.getElementById('detalle-btn-productos');
  var formEliminar = document.getElementById('detalle-form-eliminar');
  var id = row.getAttribute('data-id') || '';

  titulo.textContent = data.titulo || 'Detalle';

  if (data.imagen_url) {
    imagen.src = data.imagen_url;
    imagenCol.style.display = '';
  } else {
    imagenCol.style.display = 'none';
  }

  var html = '';
  if (data.campos) {
    data.campos.forEach(function (f) {
      html += '<div class="detail-field">';
      html += '  <span class="detail-field-label">' + (f.label || '') + '</span>';
      html += '  <span class="detail-field-value">' + (f.valor || '') + '</span>';
      html += '</div>';
    });
  }
  campos.innerHTML = html;

  btnEditar.href = '/' + tipo + '/' + id + '/editar';
  if (data.proveedor_id) {
    btnProductos.href = '/productos?id_proveedor=' + encodeURIComponent(data.proveedor_id);
    btnProductos.style.display = '';
  } else {
    btnProductos.style.display = 'none';
  }
  formEliminar.action = '/' + tipo + '/' + id + '/delete';
  formEliminar.setAttribute('data-confirm', '¿Eliminar ' + (data.titulo || 'este registro') + '?');

  window.openModal('modal-detalle');
});
