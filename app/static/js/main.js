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
