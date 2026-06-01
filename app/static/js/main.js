document.addEventListener('DOMContentLoaded', function () {

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
  formEliminar.action = '/' + tipo + '/' + id + '/delete';
  formEliminar.setAttribute('data-confirm', '¿Eliminar ' + (data.titulo || 'este registro') + '?');

  window.openModal('modal-detalle');
});
