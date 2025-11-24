# Paper Database Index

医学論文管理システムへようこそ

---

## 📊 Quick Stats

```dataview
TABLE
  length(rows) as "Papers"
FROM "Papers"
GROUP BY file.folder
```

**総論文数**:
```dataview
TABLE length(rows.file.name) as "Total"
FROM "Papers"
```

---

## 🔍 Browse by Perspective

### Study Type Perspective
研究デザインから論文を探す

```dataview
TABLE rows.file.link as "Papers", length(rows) as "Count"
FROM "Papers"
WHERE perspectives.study_type
GROUP BY perspectives.study_type
SORT length(rows) DESC
```

### Disease Perspective
疾患・病態から論文を探す

```dataview
TABLE rows.file.link as "Papers", length(rows) as "Count"
FROM "Papers"
WHERE perspectives.disease AND perspectives.disease != "not_applicable"
GROUP BY perspectives.disease
SORT length(rows) DESC
```

### Method Perspective
測定・評価方法から論文を探す

```dataview
TABLE rows.file.link as "Papers", length(rows) as "Count"
FROM "Papers"
WHERE perspectives.method AND perspectives.method != "not_applicable"
GROUP BY perspectives.method
SORT length(rows) DESC
```

### Analysis Perspective
解析手法から論文を探す

```dataview
TABLE rows.file.link as "Papers", length(rows) as "Count"
FROM "Papers"
WHERE perspectives.analysis AND perspectives.analysis != "not_applicable"
GROUP BY perspectives.analysis
SORT length(rows) DESC
```

---

## 📚 Recent Papers

最近追加された論文（10件）

```dataview
TABLE title, authors, year, perspectives.study_type as "Study Type"
FROM "Papers"
SORT date_added DESC
LIMIT 10
```

---

## ⭐ Priority Papers

優先度が高い論文

```dataview
TABLE title, authors, year, read_status
FROM "Papers"
WHERE priority = "high"
SORT date_added DESC
```

---

## 📖 Reading Status

### Unread
```dataview
TABLE title, authors, year
FROM "Papers"
WHERE read_status = "unread"
SORT year DESC
```

### Reading
```dataview
TABLE title, authors, year
FROM "Papers"
WHERE read_status = "reading"
```

### Read
```dataview
TABLE title, authors, year
FROM "Papers"
WHERE read_status = "read"
SORT date_modified DESC
LIMIT 10
```

---

## 🏷️ Browse MOCs

### By Study Type
- [[rct_view|RCT]]
- [[systematic_review_view|Systematic Review]]
- [[meta_analysis_view|Meta-Analysis]]
- [[observational_study_view|Observational Study]]

### By Disease/Condition
- [[stroke_view|Stroke]]
- [[parkinson_view|Parkinson's Disease]]
- [[fracture_view|Fracture]]

### By Method
- [[gait_analysis_view|Gait Analysis]]
- [[motion_capture_view|Motion Capture]]
- [[emg_view|EMG]]

---

## 📅 By Year

```dataview
TABLE rows.file.link as "Papers", length(rows) as "Count"
FROM "Papers"
WHERE year
GROUP BY year
SORT year DESC
```

---

## 🔗 Useful Links

- [[MOC/README|MOC一覧]]
- [[Groups/README|タググループ一覧]]

---

**Last Updated**: <%+ tp.date.now("YYYY-MM-DD HH:mm") %>
