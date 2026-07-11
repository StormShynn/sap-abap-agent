"""
Script to enhance index.html with:
1. FlexSearch CDN + search index builder
2. Search bar UI + CSS
3. Anchor highlight (CSS :target)
4. Mobile improvements
"""
import re

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# === 1. FlexSearch CDN before </head> ===
search_cdn = '''  <script src="https://cdn.jsdelivr.net/npm/flexsearch@0.7.43/dist/flexsearch.bundle.min.js"></script>
'''
content = content.replace('</head>', search_cdn + '</head>')

# === 2. CSS additions before </style> ===
css_additions = '''
    /* ===== SEARCH BAR ===== */
    .search-container {
      position: relative;
      max-width: 320px;
      width: 100%;
    }
    .search-container .search-icon {
      position: absolute;
      left: 12px;
      top: 50%;
      transform: translateY(-50%);
      font-size: 14px;
      color: var(--text-dim);
      pointer-events: none;
      z-index: 1;
    }
    #searchInput {
      width: 100%;
      padding: 7px 12px 7px 34px;
      background: var(--bg-code);
      border: 1px solid var(--border);
      border-radius: 20px;
      color: var(--text);
      font-size: 13px;
      font-family: var(--font);
      outline: none;
      transition: all .25s;
    }
    #searchInput:focus {
      border-color: var(--accent);
      box-shadow: 0 0 0 3px var(--accent-glow);
    }
    #searchInput::placeholder {
      color: var(--text-dim);
      opacity: .7;
    }
    #searchResults {
      position: absolute;
      top: calc(100% + 6px);
      right: 0;
      width: 420px;
      max-height: 360px;
      overflow-y: auto;
      background: var(--bg-card);
      border: 1px solid var(--border);
      border-radius: var(--radius-sm);
      box-shadow: 0 8px 24px rgba(0,0,0,.4);
      display: none;
      z-index: 300;
    }
    #searchResults.open { display: block; }
    #searchResults .sr-item {
      padding: 10px 14px;
      border-bottom: 1px solid var(--border);
      cursor: pointer;
      transition: background .15s;
    }
    #searchResults .sr-item:last-child { border-bottom: none; }
    #searchResults .sr-item:hover { background: var(--bg-code); }
    #searchResults .sr-item .sr-title {
      font-size: 13px;
      font-weight: 600;
      color: var(--text-bright);
    }
    #searchResults .sr-item .sr-section {
      font-size: 11px;
      color: var(--text-dim);
      margin-top: 2px;
    }
    #searchResults .sr-item mark {
      background: rgba(88,166,255,.25);
      color: var(--accent);
      border-radius: 2px;
      padding: 0 2px;
    }
    #searchResults .sr-empty {
      padding: 20px;
      text-align: center;
      color: var(--text-dim);
      font-size: 13px;
    }
    #searchResults .sr-count {
      padding: 6px 14px;
      font-size: 11px;
      color: var(--text-dim);
      background: var(--bg);
      border-bottom: 1px solid var(--border);
      text-align: right;
    }

    /* ===== ANCHOR HIGHLIGHT ===== */
    :target {
      animation: highlightTarget 2s ease;
    }
    @keyframes highlightTarget {
      0% { background-color: rgba(88,166,255,.15); border-radius: 8px; }
      100% { background-color: transparent; }
    }

    /* ===== SKELETON LOADING ===== */
    .skeleton {
      background: linear-gradient(90deg, var(--bg-code) 25%, var(--border) 50%, var(--bg-code) 75%);
      background-size: 200% 100%;
      animation: shimmer 1.5s ease infinite;
      border-radius: var(--radius-sm);
    }
    @keyframes shimmer {
      0% { background-position: 200% 0; }
      100% { background-position: -200% 0; }
    }

    /* ===== MOBILE TOUCH IMPROVEMENTS ===== */
    @media (max-width: 860px) {
      .search-container { max-width: 100%; }
      #searchResults { width: calc(100vw - 40px); right: 0; }
      .top-header { gap: 6px; }
      .sidebar a.nav-link { padding: 10px 12px; min-height: 44px; }
      .sidebar-toggle { padding: 10px 12px; min-width: 44px; min-height: 44px; }
      .lang-toggle, .theme-toggle { min-width: 44px; min-height: 44px; }
      table td:first-child { white-space: normal; word-break: break-all; }
      pre { font-size: 12px; padding: 14px 14px; }
    }
    @media (max-width: 480px) {
      .header-version { display: none; }
      .search-container { max-width: 100%; }
      #searchResults { width: calc(100vw - 40px); }
      section h2 { font-size: 20px; }
      .hero h1 { font-size: 1.6rem; }
      .btn { min-height: 44px; }
    }
'''
content = content.replace('  </style>', css_additions + '  </style>')

# === 3. Search bar HTML in header ===
search_bar_html = '''      <div class="search-container">
        <span class="search-icon">🔍</span>
        <input type="text" id="searchInput" placeholder="Tìm kiếm..." autocomplete="off">
        <div id="searchResults"></div>
      </div>
      <button class="lang-toggle" id="langToggle" aria-label="Switch language">
        <span class="lang-vi">🇻🇳 VI</span>
        <span class="lang-en" style="display:none;">🇬🇧 EN</span>
      </button>'''

content = # Only inject search bar if not already present (idempotent)
if 'searchInput' not in content:
    content = content.replace(
        '<button class="lang-toggle" id="langToggle" aria-label="Switch language">',
        search_bar_html
    )
else:
    print("  [skip] Search bar already exists, skipping injection")

# === 4. FlexSearch JS before </body> ===
flexsearch_js = '''<script>
(function() {
  'use strict';

  var searchInput = document.getElementById('searchInput');
  var searchResults = document.getElementById('searchResults');
  if (!searchInput || !searchResults) return;

  var sections = {};

  // Collect all sections with ids
  document.querySelectorAll('section[id]').forEach(function(section) {
    var id = section.id;
    var titleEl = section.querySelector('h2') || section.querySelector('h1');
    var title = '';
    if (titleEl) {
      var icon = titleEl.querySelector('.section-icon');
      var iconText = icon ? icon.textContent + ' ' : '';
      var titleText = titleEl.textContent.replace(icon ? icon.textContent : '', '').trim();
      title = iconText + titleText;
    }
    // Get text content from paragraphs and lists
    var textContent = '';
    section.querySelectorAll('p, li, td, th').forEach(function(el) {
      textContent += el.textContent + ' ';
    });
    textContent = textContent.trim();

    if (id && title) {
      sections[id] = {
        id: id,
        title: title,
        text: textContent.substring(0, 500)
      };
    }
  });

  // Build FlexSearch index (load from CDN)
  function initSearch() {
    if (typeof FlexSearch === 'undefined') {
      setTimeout(initSearch, 200);
      return;
    }

    var index = new FlexSearch.Document({
      document: {
        id: 'id',
        index: [{
          field: 'title',
          tokenize: 'forward',
          cache: true
        }, {
          field: 'text',
          tokenize: 'forward',
          cache: true
        }]
      },
      tokenize: 'forward'
    });

    Object.keys(sections).forEach(function(_sk) {
        var item = sections[_sk];
        index.add(item);
      });

    // Search handler
    searchInput.addEventListener('input', function() {
      var query = this.value.trim();
      if (query.length < 1) {
        searchResults.classList.remove('open');
        return;
      }

      var raw = index.search(query, { limit: 8, suggest: true });
      var results = [];
      var seen = {};

      raw.forEach(function(fieldResult) {
        (fieldResult.result || []).forEach(function(id) {
          if (!seen[id] && results.length < 8) {
            seen[id] = true;
            var section = sections[id];
            if (section) {
              results.push(section);
            }
          }
        });
      });

      renderResults(results, query);
    });

    // Close on click outside
    document.addEventListener('click', function(e) {
      if (!searchInput.contains(e.target) && !searchResults.contains(e.target)) {
        searchResults.classList.remove('open');
      }
    });

    // Navigate with keyboard
    searchInput.addEventListener('keydown', function(e) {
      var items = searchResults.querySelectorAll('.sr-item');
      var activeItem = searchResults.querySelector('.sr-item.active');
      var activeIdx = -1;
      if (activeItem) {
        activeIdx = Array.prototype.indexOf.call(items, activeItem);
      }

      if (e.key === 'ArrowDown') {
        e.preventDefault();
        var nextIdx = activeIdx + 1;
        if (nextIdx < items.length) {
          if (activeItem) activeItem.classList.remove('active');
          items[nextIdx].classList.add('active');
        }
      } else if (e.key === 'ArrowUp') {
        e.preventDefault();
        var prevIdx = activeIdx - 1;
        if (prevIdx >= 0) {
          if (activeItem) activeItem.classList.remove('active');
          items[prevIdx].classList.add('active');
        }
      } else if (e.key === 'Enter') {
        e.preventDefault();
        if (activeItem) {
          activeItem.click();
        } else if (items.length > 0) {
          items[0].click();
        }
      } else if (e.key === 'Escape') {
        searchResults.classList.remove('open');
        searchInput.blur();
      }
    });

    function renderResults(results, query) {
      searchResults.innerHTML = '';

      if (results.length === 0) {
        searchResults.innerHTML = '<div class="sr-empty">Không tìm thấy kết quả cho "<strong>' + escapeHtml(query) + '</strong>"</div>';
        searchResults.classList.add('open');
        return;
      }

      var html = '<div class="sr-count">' + results.length + ' kết quả</div>';

      results.forEach(function(section) {
        var title = highlightMatch(section.title, query);
        var snippet = highlightMatch(section.text.substring(0, 100), query);
        html += '<div class="sr-item" data-id="' + section.id + '">' +
          '<div class="sr-title">' + title + '</div>' +
          '<div class="sr-section">' + snippet + '...</div>' +
          '</div>';
      });

      searchResults.innerHTML = html;
      searchResults.classList.add('open');

      // Click handler
      searchResults.querySelectorAll('.sr-item').forEach(function(item) {
        item.addEventListener('click', function() {
          var id = this.dataset.id;
          searchResults.classList.remove('open');
          searchInput.value = '';
          var target = document.getElementById(id);
          if (target) {
            target.scrollIntoView({ behavior: 'smooth', block: 'start' });
          }
        });
      });
    }

    function highlightMatch(text, query) {
      if (!query || !text) return text || '';
      var escaped = query.replace(/[.*+?^${}()|[\\]\\\\]/g, '\\\\$&');
      var regex = new RegExp('(' + escaped + ')', 'gi');
      return text.replace(regex, '<mark>$1</mark>');
    }

    function escapeHtml(text) {
      var div = document.createElement('div');
      div.textContent = text;
      return div.innerHTML;
    }
  }

  initSearch();
})();
</script>
'''

content = content.replace('</body>', flexsearch_js + '\n</body>')

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ index.html enhanced successfully!")
print("Changes made:")
print("  1. FlexSearch CDN added before </head>")
print("  2. Search bar CSS + anchor highlight + skeleton + mobile improvements added")
print("  3. Search bar HTML added in header")
print("  4. FlexSearch JS initialization added before </body>")
print("File size:", len(content), "chars")
