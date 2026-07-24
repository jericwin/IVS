import os

target_dir = 'templates/seller'
search_text1 = '<a href="/seller/sales">My Sales</a>'
search_text2 = '<a href="/seller/sales" style="color: var(--accent);">My Sales</a>'

replace_text1 = '<a href="/seller/sales" style="display: flex; align-items: center;">My Sales {% if pending_orders_count and pending_orders_count > 0 %}<span style="background: var(--accent); color: var(--bg-primary); padding: 2px 6px; border-radius: 10px; font-size: 0.7rem; margin-left: 5px;">{{ pending_orders_count }}</span>{% endif %}</a>'
replace_text2 = '<a href="/seller/sales" style="color: var(--accent); display: flex; align-items: center;">My Sales {% if pending_orders_count and pending_orders_count > 0 %}<span style="background: var(--accent); color: var(--bg-primary); padding: 2px 6px; border-radius: 10px; font-size: 0.7rem; margin-left: 5px;">{{ pending_orders_count }}</span>{% endif %}</a>'

for root, _, files in os.walk(target_dir):
    for f in files:
        if f.endswith('.html'):
            filepath = os.path.join(root, f)
            with open(filepath, 'r', encoding='utf-8') as file:
                content = file.read()
                
            new_content = content.replace(search_text1, replace_text1).replace(search_text2, replace_text2)
            
            if new_content != content:
                with open(filepath, 'w', encoding='utf-8') as file:
                    file.write(new_content)
                print(f'Updated {filepath}')
