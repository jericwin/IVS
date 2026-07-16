import os
import glob

# HTML snippet to insert
profile_link = '<a href="/profile" class="auth-btn" style="display: block; width: 100%; text-align: center; margin-top: 0; margin-bottom: 8px; padding: 10px; font-size: 0.75rem; text-decoration: none; box-sizing: border-box; background: transparent; border: 1px solid var(--accent); color: var(--accent) !important;">My Profile</a>'

logout_link = '<a href="/logout" class="auth-btn" style="display: block; width: 100%; text-align: center; margin-top: 0; padding: 10px; font-size: 0.75rem; text-decoration: none; box-sizing: border-box; color: white !important;">Logout</a>'
logout_link_alternative = '<a href="/login" class="auth-btn" style="display: block; width: 100%; text-align: center; margin-top: 0; padding: 10px; font-size: 0.75rem; text-decoration: none; box-sizing: border-box; color: white !important;">Logout</a>'

template_dir = r"c:\Users\Windows 10 Pro\Documents\IVS\templates"

for root, _, files in os.walk(template_dir):
    for file in files:
        if file.endswith(".html"):
            path = os.path.join(root, file)
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
            
            # Skip if already inserted
            if 'href="/profile"' in content:
                continue

            # Replace either variation of the logout link
            if logout_link in content:
                new_content = content.replace(logout_link, f"{profile_link}\n          {logout_link}")
                with open(path, "w", encoding="utf-8") as f:
                    f.write(new_content)
                print(f"Updated {path}")
            elif logout_link_alternative in content:
                new_content = content.replace(logout_link_alternative, f"{profile_link}\n          {logout_link_alternative}")
                with open(path, "w", encoding="utf-8") as f:
                    f.write(new_content)
                print(f"Updated {path}")
