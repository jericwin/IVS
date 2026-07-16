document.addEventListener('DOMContentLoaded', () => {
    const themeToggles = document.querySelectorAll('.theme-switch input');
    const currentTheme = localStorage.getItem('theme');
    
    // On load, check the theme and apply
    if (currentTheme === 'light') {
        document.body.classList.add('light-theme');
        themeToggles.forEach(toggle => {
            toggle.checked = true;
        });
    } else {
        document.body.classList.remove('light-theme');
        themeToggles.forEach(toggle => {
            toggle.checked = false;
        });
    }
    
    // Add event listeners to all toggles on the page
    themeToggles.forEach(toggle => {
        toggle.addEventListener('change', function() {
            if (this.checked) {
                document.body.classList.add('light-theme');
                localStorage.setItem('theme', 'light');
                // Sync any other toggles on the same page
                themeToggles.forEach(t => t.checked = true);
            } else {
                document.body.classList.remove('light-theme');
                localStorage.setItem('theme', 'dark');
                // Sync any other toggles on the same page
                themeToggles.forEach(t => t.checked = false);
            }
        });
    });
});
