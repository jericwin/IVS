import os

base_dir = r"c:\Users\Windows 10 Pro\Documents\IVS\templates"
files_to_update = [
    "index.html",
    "login.html",
    "signup.html",
    "profile.html",
    "addresses.html",
    "buyer/dashboard.html",
    "buyer/marketplace.html",
    "buyer/purchases.html",
    "buyer/settings.html",
    "buyer/checkout.html",
    "buyer/asset-detail.html"
]

include_stmt = "{% include 'chatbot.html' %}"

for filepath_relative in files_to_update:
    filepath = os.path.join(base_dir, filepath_relative)
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            
        if include_stmt not in content:
            new_content = content.replace("</body>", f"  {include_stmt}\n</body>")
            if new_content != content:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                print(f"Injected into {filepath_relative}")
            else:
                print(f"Could not find </body> in {filepath_relative}")
        else:
            print(f"Skipped {filepath_relative} (already updated)")
    else:
        print(f"File not found: {filepath}")
