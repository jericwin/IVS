import os

target_dirs = ['templates/buyer', 'templates']
search_text1 = '<a href="/buyer/dashboard">Overview</a>'
search_text2 = '<a href="/buyer/dashboard" style="color: var(--accent);">Overview</a>'

for target_dir in target_dirs:
    for root, _, files in os.walk(target_dir):
        # Prevent walking into subdirectories if we only want 'templates' root level for profile/addresses
        if target_dir == 'templates' and root != 'templates':
            continue
            
        for f in files:
            if f.endswith('.html'):
                filepath = os.path.join(root, f)
                with open(filepath, 'r', encoding='utf-8') as file:
                    content = file.read()
                    
                new_content = content.replace(search_text1, '').replace(search_text2, '')
                
                # Also remove any empty lines left by the replacement
                # Optional: just let it be, or do a regex replacement
                # Using simple string replace is safer. Let's just remove the exact string.
                
                if new_content != content:
                    with open(filepath, 'w', encoding='utf-8') as file:
                        file.write(new_content)
                    print(f'Updated {filepath}')
