"""Fix duplicate lang-toggle buttons in index.html header"""

PATH = "index.html"

with open(PATH, "r", encoding="utf-8") as f:
    html = f.read()

# The broken section: first lang-toggle is correct, then 3 duplicate fragments follow
old = """      </button>
        <span class=\"lang-vi\">🇻🇳 VI</span>
        <span class=\"lang-en\" style=\"display:none;\">🇬🇧 EN</span>
      </button>
        <span class=\"lang-vi\">🇻🇳 VI</span>
        <span class=\"lang-en\" style=\"display:none;\">🇬🇧 EN</span>
      </button>
        <span class=\"lang-vi\">🇻🇳 VI</span>
        <span class=\"lang-en\" style=\"display:none;\">🇬🇧 EN</span>
      </button>
      <button class=\"theme-toggle\""""

new = """      </button>
      <button class=\"theme-toggle\""""

count = html.count(old)
if count == 1:
    html = html.replace(old, new, 1)
    with open(PATH, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"✅ Removed {count} block of duplicate lang-toggle fragments (found 3 duplicates)")
else:
    print(f"⚠️ Found {count} occurrences of duplicate lang-toggle block")
    # fallback: count occurrences of the fragment
    fragment = '<span class="lang-en" style="display:none;">🇬🇧 EN</span>\n      </button>'
    c = html.count(fragment)
    print(f"  Total </button> closures after lang-en spans: {c}")
