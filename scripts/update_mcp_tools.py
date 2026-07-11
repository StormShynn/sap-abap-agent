"""Update index.html with 5 new MCP tools: sap_find_where_used, sap_execute_query, sap_run_unit_tests, sap_get_system_info, sap_analyze_dump"""

import re

PATH = "index.html"

with open(PATH, "r", encoding="utf-8") as f:
    html = f.read()

# 1. Add 5 rows to tools table (after sap_activate row, before </tbody>)
table_rows = """            <tr>
              <td>sap_activate</td>
              <td>Activate object (transport local)</td>
              <td><code>profile</code>, <code>objectUri</code>, <code>objectType</code></td>
            </tr>
            <tr>
              <td>sap_find_where_used</td>
              <td>Tìm nơi sử dụng object ABAP (where-used)</td>
              <td><code>profile</code>, <code>objectName</code>, <code>objectType</code></td>
            </tr>
            <tr>
              <td>sap_execute_query</td>
              <td>Truy vấn dữ liệu bảng / CDS view</td>
              <td><code>profile</code>, <code>tableName</code>, <code>objectType</code>, <code>top</code></td>
            </tr>
            <tr>
              <td>sap_run_unit_tests</td>
              <td>Chạy ABAP Unit tests</td>
              <td><code>profile</code>, <code>objectUri</code>, <code>objectType</code></td>
            </tr>
            <tr>
              <td>sap_get_system_info</td>
              <td>Lấy thông tin hệ thống SAP (version, profile...)</td>
              <td><code>profile</code></td>
            </tr>
            <tr>
              <td>sap_analyze_dump</td>
              <td>Phân tích ST22 runtime dump</td>
              <td><code>profile</code>, <code>dumpId</code>, <code>top</code></td>
            </tr>"""

old_table_end = """              <td>sap_activate</td>
              <td>Activate object (transport local)</td>
              <td><code>profile</code>, <code>objectUri</code>, <code>objectType</code></td>
            </tr>
          </tbody>
        </table>"""

new_table_end = table_rows + """
          </tbody>
        </table>"""

count = html.count(old_table_end)
if count == 1:
    html = html.replace(old_table_end, new_table_end, 1)
    print(f"✅ Table rows updated (1 occurrence)")
else:
    print(f"⚠️ Found {count} occurrences of table end - check manually")
    exit(1)

# 2. Update "7 MCP tools" → "12 MCP tools"
old_count_text = """      <h3>7 MCP tools</h3>
      <p><code>sap_list_profiles</code>, <code>sap_ping</code>, <code>sap_list_packages</code>, <code>sap_search</code>, <code>sap_read_source</code>, <code>sap_syntax_check</code>, <code>sap_activate</code> — mỗi tool đều nhận tham số <code>profile</code> (để trống = active).</p>"""

new_count_text = """      <h3>12 MCP tools</h3>
      <p><code>sap_list_profiles</code>, <code>sap_ping</code>, <code>sap_list_packages</code>, <code>sap_search</code>, <code>sap_read_source</code>, <code>sap_syntax_check</code>, <code>sap_activate</code>, <code>sap_find_where_used</code>, <code>sap_execute_query</code>, <code>sap_run_unit_tests</code>, <code>sap_get_system_info</code>, <code>sap_analyze_dump</code> — mỗi tool đều nhận tham số <code>profile</code> (để trống = active).</p>"""

count = html.count(old_count_text)
if count == 1:
    html = html.replace(old_count_text, new_count_text, 1)
    print(f"✅ '7 MCP tools' updated to '12 MCP tools'")
else:
    print(f"⚠️ Found {count} occurrences of '7 MCP tools' text - check manually")
    exit(1)

# 3. Update ASCII art tree
old_ascii = """<span class=\"dir\">│              🖥️ SAP BTP / S/4HANA Cloud               │</span>
<span class=\"dir\">│                                                         │</span>
<span class=\"dir\">│  sap_list_profiles  sap_ping  sap_search               │</span>
<span class=\"dir\">│  sap_list_packages  sap_read_source  sap_syntax_check  │</span>
<span class=\"dir\">│  sap_activate                                          │</span>
<span class=\"dir\">└─────────────────────────────────────────────────────────┘</span>"""

new_ascii = """<span class=\"dir\">│              🖥️ SAP BTP / S/4HANA Cloud               │</span>
<span class=\"dir\">│                                                         │</span>
<span class=\"dir\">│  sap_list_profiles  sap_ping  sap_search               │</span>
<span class=\"dir\">│  sap_list_packages  sap_read_source  sap_syntax_check  │</span>
<span class=\"dir\">│  sap_activate  sap_find_where_used                     │</span>
<span class=\"dir\">│  sap_execute_query  sap_run_unit_tests                 │</span>
<span class=\"dir\">│  sap_get_system_info  sap_analyze_dump                 │</span>
<span class=\"dir\">└─────────────────────────────────────────────────────────┘</span>"""

count = html.count(old_ascii)
if count == 1:
    html = html.replace(old_ascii, new_ascii, 1)
    print(f"✅ ASCII art updated")
else:
    print(f"⚠️ Found {count} occurrences of ASCII art - check manually")
    exit(1)

# 4. Add translation entries for new tools
old_trans = """    'Activate object (transport local)': 'Activate object (local transport)',"""

new_trans = """    'Activate object (transport local)': 'Activate object (local transport)',
    'Tìm nơi sử dụng object ABAP (where-used)': 'Find where-used for ABAP objects',
    'Truy vấn dữ liệu bảng / CDS view': 'Query table / CDS view data',
    'Chạy ABAP Unit tests': 'Run ABAP Unit tests',
    'Lấy thông tin hệ thống SAP (version, profile...)': 'Get SAP system info (version, profile...)',
    'Phân tích ST22 runtime dump': 'Analyze ST22 runtime dump',"""

count = html.count(old_trans)
if count == 1:
    html = html.replace(old_trans, new_trans, 1)
    print(f"✅ Translation entries added")
else:
    print(f"⚠️ Found {count} occurrences of translation section - check manually")
    exit(1)

with open(PATH, "w", encoding="utf-8") as f:
    f.write(html)

print(f"\n🎉 All updates applied successfully!")
