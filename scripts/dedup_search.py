"""
Remove duplicate search bars from index.html.
The deploy_enhance_index.py was run multiple times, creating duplicate search bars.
This script keeps only the first occurrence and makes the deploy script idempotent.
"""
import re

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Count search bars
search_input_count = content.count('id="searchInput"')
print(f"Found {search_input_count} searchInput elements")

if search_input_count > 1:
    # Find all search-container divs
    # Pattern: <div class="search-container"> ... </div>
    # followed by lang-toggle button
    
    # Strategy: Find the FIRST search-container and keep it,
    # remove all subsequent search-containers
    
    first_pos = content.find('class="search-container"')
    last_pos = first_pos
    
    # Find the last occurrence
    for _ in range(search_input_count - 1):
        next_pos = content.find('class="search-container"', last_pos + 1)
        if next_pos == -1:
            break
        last_pos = next_pos
    
    # Remove all search containers except the first one
    # Process from last to first to keep positions valid
    positions = []
    pos = 0
    while True:
        pos = content.find('class="search-container"', pos)
        if pos == -1:
            break
        # Find the containing div start
        div_start = content.rfind('<div', 0, pos)
        # Find the matching </div>
        div_end = content.find('</div>', pos)
        if div_end != -1:
            div_end += 6  # len('</div>')
        positions.append((div_start, div_end))
        pos = div_end or (pos + 1)
    
    print(f"Found {len(positions)} search containers")
    
    # Keep only the first one, remove the rest (from last to first)
    for i in range(len(positions) - 1, 0, -1):
        start, end = positions[i]
        if start is not None and end is not None and end > start:
            # Also remove the following lang-toggle if it's a duplicate
            # Check what's after the </div>
            rest = content[end:end+80]
            # Remove this search container
            content = content[:start] + content[end:]
            print(f"  Removed duplicate search container #{i+1}")

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)

# Verify
final_count = content.count('id="searchInput"')
print(f"Final searchInput count: {final_count}")

# === Make deploy_enhance_index.py idempotent ===
with open('scripts/deploy_enhance_index.py', 'r', encoding='utf-8') as f:
    py_content = f.read()

# Add a check before injecting search bar HTML
old_search_inject = '''content.replace(
    '<button class="lang-toggle" id="langToggle" aria-label="Switch language">',
    search_bar_html
)'''

new_search_inject = '''# Only inject search bar if not already present (idempotent)
if 'searchInput' not in content:
    content = content.replace(
        '<button class="lang-toggle" id="langToggle" aria-label="Switch language">',
        search_bar_html
    )
else:
    print("  [skip] Search bar already exists, skipping injection")'''

if old_search_inject in py_content:
    py_content = py_content.replace(old_search_inject, new_search_inject)
    with open('scripts/deploy_enhance_index.py', 'w', encoding='utf-8') as f:
        f.write(py_content)
    print("✅ deploy_enhance_index.py now idempotent!")
else:
    print("⚠️ Pattern not found in deploy_enhance_index.py, may already be idempotent")

print("✅ Done!")
