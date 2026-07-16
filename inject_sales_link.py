import os
import re

templates_dir = r"c:\Users\Windows 10 Pro\Documents\IVS\templates\seller"
files_to_update = [
    "dashboard.html",
    "listings.html",
    "analytics.html",
    "add-asset.html",
    "settings.html",
    "asset-detail.html"
]

target_link = '<a href="/seller/sales">My Sales</a>'
search_pattern = r'<a href="/seller/listings"[^>]*>My Listings</a>'

for filename in files_to_update:
    filepath = os.path.join(templates_dir, filename)
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            
        if "/seller/sales" not in content:
            # Find My Listings and insert My Sales after it
            new_content = re.sub(
                f'({search_pattern})', 
                r'\1\n      <a href="/seller/sales">My Sales</a>', 
                content
            )
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"Updated {filename}")
        else:
            print(f"Skipped {filename} (already updated)")
    else:
        print(f"File not found: {filepath}")
