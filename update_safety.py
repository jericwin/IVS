import os, glob

dirs = [r'c:\Users\Windows 10 Pro\Documents\IVS\templates\seller', r'c:\Users\Windows 10 Pro\Documents\IVS\templates\buyer']
for d in dirs:
    files = glob.glob(os.path.join(d, '*.html'))
    for file in files:
        with open(file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        content = content.replace('{{ current_user.first_name[0] }}', '{{ current_user.first_name[0] if current_user.first_name else \'U\' }}')
        
        with open(file, 'w', encoding='utf-8') as f:
            f.write(content)
print('Updated all templates for safety')
