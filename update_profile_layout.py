with open('templates/profile.html', 'r', encoding='utf-8') as f:
    content = f.read()

# I will wrap the two sections.
# Find the start of the first section:
start_idx = content.find('<!-- Main Content Area -->')
if start_idx != -1:
    wrapper_start = '<!-- Main Content Area -->\n      <div style="flex: 1; display: flex; flex-direction: column; gap: 40px;">\n'
    content = content[:start_idx] + wrapper_start + content[start_idx + len('<!-- Main Content Area -->'):]
    
    # Find </main> and put </div> before it
    main_end_idx = content.rfind('</main>')
    if main_end_idx != -1:
        content = content[:main_end_idx] + '      </div>\n    ' + content[main_end_idx:]
        
    with open('templates/profile.html', 'w', encoding='utf-8') as f:
        f.write(content)
    print('Updated layout in profile.html')
else:
    print('Could not find marker')
