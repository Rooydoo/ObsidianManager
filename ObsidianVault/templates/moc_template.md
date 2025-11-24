# <% tp.file.title %> View

> <% tp.system.prompt("Perspective type (study_type/disease/method/analysis/population)") %>: <% tp.system.prompt("Tag value") %>

## Papers in this category

```dataview
TABLE title, authors, year, study_type
FROM "Papers"
WHERE perspectives.<% tp.system.prompt("meta_tag") %> = "<% tp.system.prompt("tag_value") %>"
SORT year DESC
```

## Statistics

**Total Papers**:
```dataview
TABLE length(rows) as "Count"
FROM "Papers"
WHERE perspectives.<meta_tag> = "<tag_value>"
```

## By Year

```dataview
TABLE rows.title as "Papers", length(rows) as "Count"
FROM "Papers"
WHERE perspectives.<meta_tag> = "<tag_value>"
GROUP BY year
SORT year DESC
```

## By Study Type

```dataview
TABLE rows.title as "Papers", length(rows) as "Count"
FROM "Papers"
WHERE perspectives.<meta_tag> = "<tag_value>"
GROUP BY perspectives.study_type
SORT length(rows) DESC
```

---

## Related Perspectives

<!-- 関連する他のperspectiveへのリンク -->

---

## Notes

<!-- このMOCに関するメモ -->

---

**Last updated**: <% tp.date.now("YYYY-MM-DD HH:mm") %>
