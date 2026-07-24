import os, glob

template_dir = r'c:\Users\Windows 10 Pro\Documents\IVS\templates\seller'
files = glob.glob(os.path.join(template_dir, '*.html'))

for file in files:
    with open(file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    content = content.replace('<div class="avatar">S</div>', '<div class="avatar">{{ current_user.first_name[0] if current_user.first_name else \'S\' }}</div>')
    content = content.replace('<span style="font-size: 0.9rem; font-weight: 500;">Seller Account</span>', '<span style="font-size: 0.9rem; font-weight: 500;">{{ current_user.first_name }}</span>')
    content = content.replace('<p style="font-weight: 600; font-size: 0.9rem; margin: 4px 0 0 0; color: var(--text-primary);">Seller Account</p>', '<p style="font-weight: 600; font-size: 0.9rem; margin: 4px 0 0 0; color: var(--text-primary);">{{ current_user.first_name }}</p>')
    
    with open(file, 'w', encoding='utf-8') as f:
        f.write(content)
print('Updated seller templates')
