
---
title: Research
nav:
  order: 1
  tooltip: Published works
---

# {% include icon.html icon="fa-solid fa-microscope" %}Research

Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.

{% include section.html %}

## Featured Projects

{% include list.html component="card" data="projects" filter="group == 'featured'" %}

{% include section.html %}

## More Projects

{% include list.html component="card" data="projects" filter="!group" style="small" %}

{% include section.html %}

## Highlighted Publication

{% include citation.html lookup="Open collaborative writing with Manubot" style="rich" %}

{% include section.html %}

## All Publications

{% include search-box.html %}

{% include search-info.html %}

{% include list.html data="citations" component="citation" style="rich" %}
