import re
with open('templates/profile.html', 'r', encoding='utf-8') as f:
    content = f.read()

# We need to wrap all <section class="profile-section"> tags that are direct children of <main class="main-content">
# with a <div style="flex: 1; display: flex; flex-direction: column; gap: 40px;">
# Let's find the position of the first <section class="profile-section">
# and the position of </main>

match = re.search(r'<section\s+class=["\']profile-section["\']', content)
if match:
    start_idx = match.start()
    
    # We will insert the div start before the <section>
    content = content[:start_idx] + '      <div style="flex: 1; display: flex; flex-direction: column; gap: 40px;">\n        ' + content[start_idx:]
    
    # We will insert the div end before </main>
    main_end_idx = content.rfind('</main>')
    if main_end_idx != -1:
        content = content[:main_end_idx] + '      </div>\n    ' + content[main_end_idx:]
        
    with open('templates/profile.html', 'w', encoding='utf-8') as f:
        f.write(content)
    print('Updated layout successfully')
else:
    print('Could not find profile-section')
