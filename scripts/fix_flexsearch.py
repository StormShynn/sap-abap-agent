"""
Fix index.html:
1. Replace sections.forEach with Object.keys().forEach (sections is now an object)
2. Remove duplicate FlexSearch JS blocks (keep only the newest one)
3. Update deploy_enhance_index.py to use correct iteration pattern
"""
import re

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# === 1. Fix all sections.forEach → Object.keys(sections).forEach ===
# Pattern 1: sections.forEach(function(item) { index.add(item); });
content = content.replace(
    'sections.forEach(function(item) {',
    'Object.keys(sections).forEach(function(_sk) { var item = sections[_sk];'
)

# Pattern 2: sections.forEach(function(section) {
# Only fix the ones inside the FlexSearch script (after the marker)
# The one at line 3028 is for sidebar tracking and uses querySelectorAll result
# Let me check... actually the one at line 3028 is for active sidebar tracking
# and iterates over document.querySelectorAll('section[id]') - that returns a NodeList
# which IS iterable. So that one is correct. The ones inside the FlexSearch script
# are the ones that need fixing.

# Since sections.forEach only appears 4 times total and 3 are in FlexSearch,
# let me be more targeted. Find the chunks that need fixing.

# === 2. Remove duplicate FlexSearch blocks ===
# Count how many flexsearch scripts exist
count = content.count('flexsearch.bundle.min.js')
print(f"Found {count} FlexSearch CDN script tags")

# Find all script blocks after the first flexsearch
# Strategy: find the marker comment or the flexsearch script tag
# and remove duplicates

# Find all positions of the flexsearch CDN tags
import re
cdn_positions = [m.start() for m in re.finditer(r'<script src="https://cdn\.jsdelivr\.net/npm/flexsearch@', content)]
print(f"FlexSearch CDN at positions: {cdn_positions}")

# Keep only the first CDN tag, remove subsequent duplicates
for i in range(len(cdn_positions) - 1, 0, -1):
    pos = cdn_positions[i]
    # Find the end of this script tag
    end_pos = content.index('</script>', pos) + len('</script>')
    # Remove until the next CDN tag or end
    content = content[:pos] + content[end_pos:]

# Count again
final_cdn = content.count('flexsearch.bundle.min.js')
print(f"After dedup: {final_cdn} FlexSearch CDN tags")

# === 3. Remove duplicate initSearch() blocks ===
# Find all (function() { ... })(); blocks containing initSearch
# Strategy: count how many have the marker
init_count = content.count('function initSearch()')
print(f"Found {init_count} initSearch() functions")

if init_count > 1:
    # Find the LAST initSearch block (it's the newest)
    last_init = content.rfind('function initSearch()')
    first_init = content.find('function initSearch()')
    
    # Remove all initSearch blocks EXCEPT the last one
    # Find where the first block starts...
    # Actually, each block is wrapped in (function() { 'use strict'; ... })();
    # Let me find the wrapper structure
    
    # Simpler approach: find the last (function() block and keep only that
    # Each block starts with (function() { and ends with })();
    blocks = []
    search_start = 0
    while True:
        block_start = content.find('(function() {', search_start)
        if block_start == -1:
            break
        block_end = content.find('})();', block_start)
        if block_end == -1:
            break
        block_end += 5  # len of '})();'
        blocks.append((block_start, block_end))
        search_start = block_end
    
    print(f"Found {len(blocks)} IIFE blocks")
    
    if len(blocks) > 1:
        # Keep only the LAST IIFE block
        last_block = blocks[-1]
        # Remove all blocks except the last one
        for i in range(len(blocks) - 2, -1, -1):
            start, end = blocks[i]
            content = content[:start] + content[end:]
        
        print(f"Removed {len(blocks) - 1} duplicate IIFE blocks")

# === 4. Write back ===
with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ index.html fixed!")
print(f"Final file size: {len(content)} chars")

# === 5. Also fix the deploy_enhance_index.py to use correct pattern ===
with open('scripts/deploy_enhance_index.py', 'r', encoding='utf-8') as f:
    py_content = f.read()

# Fix the flexsearch_js to use object iteration
old_iter = 'sections.forEach(function(item) {\n      index.add(item);\n    });'
new_iter = '''Object.keys(sections).forEach(function(_sk) {\n        var item = sections[_sk];\n        index.add(item);\n      });'''

if old_iter in py_content:
    py_content = py_content.replace(old_iter, new_iter)
    with open('scripts/deploy_enhance_index.py', 'w', encoding='utf-8') as f:
        f.write(py_content)
    print("✅ deploy_enhance_index.py fixed!")
else:
    print("⚠️ deploy_enhance_index.py: old pattern not found, may already be fixed")
