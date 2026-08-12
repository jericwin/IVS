import os

def fix_file(fpath):
    with open(fpath, 'r', encoding='utf-8') as f:
        txt = f.read()
    
    # We want to replace 'object-fit: cover;">' with 'object-fit: cover; z-index: 10;">' for var-image-preview
    # Only if it doesn't already have z-index: 10
    if 'z-index: 10' not in txt:
        txt = txt.replace('object-fit: cover;">', 'object-fit: cover; z-index: 10;">')
        with open(fpath, 'w', encoding='utf-8') as f:
            f.write(txt)
        print(f"Fixed {fpath}")
    else:
        print(f"Already fixed {fpath}")

base = 'c:/Users/Windows 10 Pro/Documents/IVS/templates/seller/'
fix_file(os.path.join(base, 'add-asset.html'))
fix_file(os.path.join(base, 'edit-asset.html'))
