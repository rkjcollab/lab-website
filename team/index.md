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

{% include list.html data="members" component="portrait" filter="group == 'staff'" %}

---

## 🎓 Students

{% include list.html data="members" component="portrait" filter="group == 'student'" %}

---

## 🧑‍🎓 Alumni

{% include list.html data="members" component="portrait" filter="group == 'alumni'" %}

