import os
import re

template_dir = 'templates'

# Regex to match src="/static/uploads/{{ variable }}" or href="..."
pattern = re.compile(r'(src|href)="/static/uploads/\{\{\s*(.*?)\s*\}\}"')

def replace_html(match):
    attr = match.group(1)
    var = match.group(2)
    return f'{attr}="{{% if {var} and {var}.startswith(\'http\') %}}{{{{ {var} }}}}{{% else %}}/static/uploads/{{{{ {var} }}}}{{% endif %}}"'

for root, _, files in os.walk(template_dir):
    for file in files:
        if file.endswith('.html'):
            filepath = os.path.join(root, file)
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Replace HTML template tags
            new_content = pattern.sub(replace_html, content)
            
            # Replace JS 1
            new_content = new_content.replace(
                "img.src = '/static/uploads/' + images[idx];",
                "img.src = (images[idx] && images[idx].startsWith('http')) ? images[idx] : '/static/uploads/' + images[idx];"
            )
            
            # Replace JS 2
            new_content = new_content.replace(
                "document.getElementById('mainAssetImage').src = '/static/uploads/' + imageFilename;",
                "document.getElementById('mainAssetImage').src = (imageFilename && imageFilename.startsWith('http')) ? imageFilename : '/static/uploads/' + imageFilename;"
            )
            
            if new_content != content:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                print(f"Updated {filepath}")
