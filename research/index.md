---
layout: default
title: Research
nav:
  order: 1
  tooltip: Published works, Software, datasets, and more
---

# {% include icon.html icon="fa-solid fa-microscope" %} Research

---

{% include section.html %}

## 🛠 Current Projects

<div class="citation-container">
  {% include list.html component="project-row" data="projects" filter="group == 'featured'" %}
</div>

{% include section.html %}

## 📁 Past Projects

<div class="citation-container small">
  {% include list.html component="project-row" data="projects" filter="!group" style="small" %}
</div>

{% include section.html %}

## 📚 Publications

{% include search-box.html %}
{% include search-info.html %}
{% include list.html data="citations" component="citation" style="rich" %}

{% include section.html %}
