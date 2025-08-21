// DOM Elements
const sidebarToggle = document.getElementById('sidebarToggle');
const sidebar = document.querySelector('.sidebar');
const menuItems = document.querySelectorAll('.menu-item a');

// Sidebar Toggle Functionality
function toggleSidebar() {
    sidebar.classList.toggle('collapsed');
    
    // Update toggle button icon
    const icon = sidebarToggle.querySelector('i');
    if (sidebar.classList.contains('collapsed')) {
        icon.className = 'fas fa-chevron-right';
        icon.title = 'Sidebar\'ı genişlet';
    } else {
        icon.className = 'fas fa-bars';
        icon.title = 'Sidebar\'ı daralt';
    }
    
    // Save state to localStorage
    localStorage.setItem('sidebarCollapsed', sidebar.classList.contains('collapsed'));
}

// Initialize sidebar state from localStorage
document.addEventListener('DOMContentLoaded', () => {
    const isCollapsed = localStorage.getItem('sidebarCollapsed') === 'true';
    if (isCollapsed) {
        sidebar.classList.add('collapsed');
        const icon = sidebarToggle.querySelector('i');
        icon.className = 'fas fa-chevron-right';
        icon.title = 'Sidebar\'ı genişlet';
    }
});

// Add click event listener
if (sidebarToggle) {
    sidebarToggle.addEventListener('click', toggleSidebar);
}

// Menu Item Click Handler
menuItems.forEach(item => {
    item.addEventListener('click', (e) => {
        // Remove active class from all menu items
        menuItems.forEach(menuItem => {
            menuItem.parentElement.classList.remove('active');
        });
        
        // Add active class to clicked item
        item.parentElement.classList.add('active');
        
        // Update breadcrumb
        const breadcrumb = document.querySelector('.breadcrumb span');
        const menuText = item.querySelector('span').textContent;
        breadcrumb.textContent = menuText;
        
        // Prevent default link behavior for demo
        e.preventDefault();
    });
});

// Search Functionality
const searchInput = document.querySelector('.search-box input');
searchInput.addEventListener('input', (e) => {
    const searchTerm = e.target.value.toLowerCase();
    
    // You can implement search functionality here
    console.log('Searching for:', searchTerm);
});

// Notification Click Handler
const notificationBtn = document.querySelector('.notification-btn');
notificationBtn.addEventListener('click', () => {
    // You can implement notification dropdown here
    alert('Bildirimler: 3 yeni mesaj');
});

// Profile Click Handler
const profileBtn = document.querySelector('.profile-btn');
profileBtn.addEventListener('click', () => {
    // You can implement profile dropdown here
    alert('Profil menüsü açılacak');
});

// Add smooth scrolling to content area
const content = document.querySelector('.content');
content.addEventListener('scroll', (e) => {
    // You can add scroll-based animations here
});

// Add loading animation
document.addEventListener('DOMContentLoaded', () => {
    // Add fade-in animation to stat cards
    const statCards = document.querySelectorAll('.stat-card');
    statCards.forEach((card, index) => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';
        
        setTimeout(() => {
            card.style.transition = 'all 0.6s ease';
            card.style.opacity = '1';
            card.style.transform = 'translateY(0)';
        }, index * 100);
    });
});

// Add hover effects for better UX
document.querySelectorAll('.stat-card').forEach(card => {
    card.addEventListener('mouseenter', () => {
        card.style.transform = 'translateY(-8px) scale(1.02)';
    });
    
    card.addEventListener('mouseleave', () => {
        card.style.transform = 'translateY(0) scale(1)';
    });
});

// Keyboard shortcuts
document.addEventListener('keydown', (e) => {
    // Ctrl/Cmd + B to toggle sidebar
    if ((e.ctrlKey || e.metaKey) && e.key === 'b') {
        e.preventDefault();
        toggleSidebar();
    }
    
    // Escape to close sidebar on mobile
    if (e.key === 'Escape' && window.innerWidth <= 768) {
        sidebar.classList.remove('active');
    }
});

// Responsive sidebar behavior
function handleResize() {
    if (window.innerWidth <= 768) {
        sidebar.classList.remove('collapsed');
        sidebar.classList.remove('active');
    }
}

window.addEventListener('resize', handleResize);

// Add click outside to close sidebar on mobile
document.addEventListener('click', (e) => {
    if (window.innerWidth <= 768) {
        if (!sidebar.contains(e.target) && !sidebarToggle.contains(e.target)) {
            sidebar.classList.remove('active');
        }
    }
});

// Add some sample data updates (for demo purposes)
setInterval(() => {
    const statNumbers = document.querySelectorAll('.stat-number');
    statNumbers.forEach(stat => {
        const currentValue = parseInt(stat.textContent.replace(/,/g, ''));
        const newValue = currentValue + Math.floor(Math.random() * 10);
        stat.textContent = newValue.toLocaleString();
    });
}, 5000);

// Add theme toggle functionality (optional)
function toggleTheme() {
    document.body.classList.toggle('dark-theme');
}

// Export functions for potential use in other scripts
window.dashboardFunctions = {
    toggleSidebar: toggleSidebar,
    toggleTheme: toggleTheme,
    updateStats: (data) => {
        // Function to update statistics with real data
        console.log('Updating stats with:', data);
    }
};
