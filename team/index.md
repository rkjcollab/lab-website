---
title: Team
nav:
  order: 2
  tooltip: About our team
---

# {% include icon.html icon="fa-solid fa-users" %} Team

Welcome to our team page! Meet the amazing people that make up our lab — including staff, students, and alumni.

---

## 🧑‍💼 Staff

{% assign staff = site.members | where: "group", "staff" %}
{% assign role_order_staff = "principal-investigator,staff-researcher,bioinformatics-analyst" | split: "," %}

{% for role in role_order_staff %}
  {% for member in staff %}
    {% if member.role == role %}
      {% include portrait.html lookup=member.slug %}
    {% endif %}
  {% endfor %}
{% endfor %}

---

## 🎓 Students

{% assign students = site.members | where: "group", "student" %}
{% assign role_order_students = "postdoc,phd,grad" | split: "," %}

{% for role in role_order_students %}
  {% for member in students %}
    {% if member.role == role %}
      {% include portrait.html lookup=member.slug %}
    {% endif %}
  {% endfor %}
{% endfor %}

---

## 🧑‍🎓 Alumni

{% assign alumni = site.members | where: "group", "alumni" %}
{% assign role_order_alumni = "research-sevices-proffesional,postdoc,phd,grad" | split: "," %}

{% for role in role_order_alumni %}
  {% for member in alumni %}
    {% if member.role == role %}
      {% include portrait.html lookup=member.slug %}
    {% endif %}
  {% endfor %}
{% endfor %}
