## 📝 Mô tả

<!-- Mô tả ngắn gọn về Pull Request này: tính năng gì, fix bug gì, thay đổi docs gì -->

## 🆕 Loại thay đổi

- [ ] ✨ **feat**: Tính năng mới (skill/agent mới)
- [ ] 🐛 **fix**: Sửa lỗi
- [ ] 📖 **docs**: Documentation (README, index.html)
- [ ] 🔧 **refactor**: Cải thiện code/skill không thay đổi chức năng
- [ ] 🌐 **i18n**: Translations
- [ ] ⚙️ **chore**: Cấu hình, CI, dependencies

## ✅ Checklist

### Kiểm tra chung

- [ ] Tôi đã đọc [`CONTRIBUTING.md`](https://github.com/StormShynn/sap-abap-agent/blob/main/CONTRIBUTING.md)
- [ ] Tôi đã dùng [`SKILL_TEMPLATE.md`](https://github.com/StormShynn/sap-abap-agent/blob/main/SKILL_TEMPLATE.md) nếu thêm skill/agent mới
- [ ] YAML frontmatter đúng format (`---` delimiter)
- [ ] Code/skill hoạt động (đã test với Claude Code)

### Nếu thêm skill mới

- [ ] `skills/<tên>/SKILL.md` được tạo
- [ ] `skills/sap-ask-consultant/SKILL.md` đã được cập nhật routing

### Nếu thêm agent mới

- [ ] `agents/<tên>.md` được tạo
- [ ] `reference/modules/<tên>/SKILL.md` được tạo (knowledge base)
- [ ] `skills/sap-ask-consultant/SKILL.md` đã được cập nhật keyword matrix + coupling
- [ ] `.claude-plugin/plugin.json` version đã bump

### Cập nhật documentation

- [ ] `README.md` đã cập nhật
- [ ] `index.html` đã cập nhật (table, sidebar, routing examples)
- [ ] `index.html` translations (VI + EN) đã thêm

### Kiểm tra an toàn

- [ ] Không có file chứa đường dẫn tuyệt đối cá nhân
- [ ] Không có file chứa thông tin nhạy cảm (credentials, tenant URLs thật)
- [ ] `.gitignore` đã cập nhật nếu có file tạm mới

## 📸 Screenshots (nếu có)

<!-- Nếu thay đổi UI (index.html), chụp màn hình trước/sau -->

## 🔗 Related issues

<!-- Link đến issue liên quan: Closes #123, Fixes #456 -->
