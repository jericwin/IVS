import os, glob, re

buyer_templates = glob.glob('templates/buyer/*.html')
for tpl in buyer_templates:
    with open(tpl, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Remove Settings link
    new_content = re.sub(r'\s*<a href=\"/buyer/settings\">Settings</a>', '', content)
    
    if new_content != content:
        with open(tpl, 'w', encoding='utf-8') as f:
            f.write(new_content)
            print(f'Updated {tpl}')
