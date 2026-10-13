// Sidebar interactive behaviors: mobile drawer toggle & active state enhancement
document.addEventListener('DOMContentLoaded', function () {
    const sidebar = document.getElementById('sidebar');
    const toggleBtn = document.getElementById('sidebar-toggle');
    const closeBtn = document.getElementById('sidebar-close');
    const overlay = document.getElementById('sidebar-overlay');

    if (sidebar) {
        function openSidebar() {
            sidebar.classList.add('open');
            if (overlay) overlay.classList.add('active');
            if (toggleBtn) {
                toggleBtn.setAttribute('aria-expanded', 'true');
            }
            // Move focus into the drawer (close button)
            if (closeBtn) {
                closeBtn.focus();
            }
        }

        function closeSidebar(returnFocus = true) {
            sidebar.classList.remove('open');
            if (overlay) overlay.classList.remove('active');
            if (toggleBtn) {
                toggleBtn.setAttribute('aria-expanded', 'false');
                if (returnFocus) {
                    toggleBtn.focus();
                }
            }
        }

        if (toggleBtn) {
            toggleBtn.addEventListener('click', function () {
                if (sidebar.classList.contains('open')) {
                    closeSidebar(true);
                } else {
                    openSidebar();
                }
            });
        }

        if (closeBtn) {
            closeBtn.addEventListener('click', function () {
                closeSidebar(true);
            });
        }

        if (overlay) {
            overlay.addEventListener('click', function () {
                closeSidebar(true);
            });
        }

        // Close sidebar on Escape key and return focus to hamburger button
        document.addEventListener('keydown', function (e) {
            if (e.key === 'Escape' && sidebar.classList.contains('open')) {
                closeSidebar(true);
            }
        });
    }

    // Enhance active state matching based on current pathname
    const currentPath = window.location.pathname;
    const links = document.querySelectorAll('.sidebar-link');
    links.forEach(function (link) {
        const href = link.getAttribute('href');
        if (href && !href.startsWith('http') && href !== '#') {
            // Check exact match or prefix match for subpaths (except root '/')
            if (currentPath === href || (href !== '/' && currentPath.startsWith(href))) {
                link.classList.add('active');
                link.setAttribute('aria-current', 'page');
            }
        }
    });
});
