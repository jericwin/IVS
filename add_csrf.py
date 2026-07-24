import os
import re

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
csrf_input = '\n        <input type="hidden" name="csrf_token" value="{{ csrf_token() }}"/>'

for root, _, files in os.walk(template_dir):
    for file in files:
        if file.endswith('.html'):
            filepath = os.path.join(root, file)
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Simple regex to find <form ...> that doesn't already have a csrf token right after
            # Actually, just replace <form ...> with <form ...>\n<input ... csrf>
            if '<form' in content and 'csrf_token' not in content:
                new_content = re.sub(r'(<form[^>]*>)', r'\1' + csrf_input, content, flags=re.IGNORECASE)
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                print(f"Added CSRF to {filepath}")
