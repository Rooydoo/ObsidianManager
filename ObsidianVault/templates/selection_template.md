# Paper Selection: <% tp.system.prompt("Project name") %>

**Created**: <% tp.date.now("YYYY-MM-DD") %>
**Purpose**: <% tp.system.prompt("Selection purpose") %>

---

## Selection Criteria

<!-- 選択基準を記載 -->
-
-

---

## Selected Papers

<!-- チェックボックスで選択 -->
<!-- [x] をつけた論文がエクスポートされます -->

### Category 1

- [ ] [[]]
- [ ] [[]]

### Category 2

- [ ] [[]]
- [ ] [[]]

---

## Export Command

```bash
python scripts/export_selected.py \
  ObsidianVault/<% tp.file.title %>.md \
  exports/<project_name>/
```

---

## Notes

<!-- メモ -->

---

**Last updated**: <% tp.date.now("YYYY-MM-DD HH:mm") %>
