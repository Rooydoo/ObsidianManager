---
paper_id: <% tp.file.title %>
title: "<% tp.system.prompt("Title") %>"
authors:
  - <% tp.system.prompt("Authors (comma separated)") %>
year: <% tp.system.prompt("Year") %>
journal: "<% tp.system.prompt("Journal") %>"
volume: "<% tp.system.prompt("Volume") %>"
issue: "<% tp.system.prompt("Issue") %>"
pages: "<% tp.system.prompt("Pages") %>"
doi: "<% tp.system.prompt("DOI") %>"
pmid: "<% tp.system.prompt("PMID") %>"

pdf_path: ""

study_type: "<% tp.system.prompt("Study Type") %>"
study_design: "<% tp.system.prompt("Study Design") %>"
sample_size: <% tp.system.prompt("Sample Size") %>
study_population: "<% tp.system.prompt("Study Population") %>"

perspectives:
  study_type: ""
  disease: ""
  method: ""
  analysis: ""
  population: ""

keywords: []

language: "en"
date_added: <% tp.date.now("YYYY-MM-DD") %>
date_modified: <% tp.date.now("YYYY-MM-DD") %>
read_status: "unread"
priority: "medium"
tags: []
---

# <% tp.frontmatter.title %>

## 📊 Study Overview

**研究タイプ**: <% tp.frontmatter.study_type %> / <% tp.frontmatter.study_design %>
**対象**: <% tp.frontmatter.study_population %> (n=<% tp.frontmatter.sample_size %>)
**著者**: <% tp.frontmatter.authors %>
**掲載誌**: <% tp.frontmatter.journal %> (<% tp.frontmatter.year %>)

---

## 📝 Summary（要約）

### 目的


### 方法


### 結果


### 結論


---

## 📄 Abstract（原文）

<details>
<summary>クリックで展開</summary>


</details>

---

## 🔍 Key Findings

### 主要な知見
1.
2.
3.

### 限界・課題
-
-

---

## 🔗 Related Information

### Perspectives
- **Disease**: [[]]
- **Method**: [[]]
- **Analysis**: [[]]

### Related Papers


---

## 📎 Resources

### PDF


### Links
- DOI: [<% tp.frontmatter.doi %>](https://doi.org/<% tp.frontmatter.doi %>)
- PubMed: [PMID: <% tp.frontmatter.pmid %>](https://pubmed.ncbi.nlm.nih.gov/<% tp.frontmatter.pmid %>/)

---

## 💡 Personal Notes

### 読んだ日:

### メモ
- [ ]

### 疑問点


### 引用候補


---

## 🔄 Update History

- <% tp.date.now("YYYY-MM-DD") %>: 初回作成
