---
title: Connect
nav:
  order: 3
  tooltip: Email, address, and location
---

# {% include icon.html icon="fa-regular fa-envelope" %}Contact


{%
  include button.html
  type="email"
  text="Randi K Johnson"
  link="randi.johnson@cuanschutz.edu"
%}

{%
  include button.html
  type="phone"
  text="(303) 724-3078"
  link="+1-303-724-3078"
%}

{% include section.html %}

## 🧬 Affiliations and Training Programs 

{% capture col1 %}

{%
  include figure.html
  image="images/phd_epi_csph.jpg"
  caption="[PhD - Epidemiology at the Colorado School of Public Health](https://coloradosph.cuanschutz.edu/education/degrees-and-programs/doctor-of-philosophy/phd-in-epidemiology)"
%}

{%
  include figure.html
  image="images/barbara.jpg"
  caption="[Barbara Davis Center for Diabetes](https://medschool.cuanschutz.edu/barbara-davis-center-for-diabetes)"
%}

{% endcapture %}

{% capture col2 %}

{%
  include figure.html
  image="images/biomedical.jpg"
  caption="[Department of Biomedical Informatics, CU School of Medicine](https://medschool.cuanschutz.edu/dbmi) "
%}

{%
  include figure.html
  image="images/personalmedicine.jpg"
  caption="[Colorado Center for Personalized Medicine](https://medschool.cuanschutz.edu/ccpm) "
%}

{% endcapture %}

{% capture col3 %}

{%
  include figure.html
  image="images/hgeneprg.jpg"
  caption="[Human Medical Genetics and Genomics Training Program](https://www.cuanschutz.edu/graduate-programs/human-medical-genetics-and-genomics/home)"
%}

{%
  include figure.html
  image="images/epi_csph.png"
  caption="[Department of Epidemiology, Colorado School of Public Health](https://coloradosph.cuanschutz.edu/education/departments/epidemiology)"
%}

{% endcapture %}

{% include cols.html col1=col1 col2=col2 col3=col3 %}

{% include section.html dark=true %}

## 👩 Join Us

{% capture col1 %}
Staff and Postdoctoral Fellows: Open postings available on [CU Careers](https://www.cu.edu/cu-careers/anschutz-medical-campus)
{% endcapture %}

{% capture col2 %}
- PhD Students: Through affiliated training programs
- MPH, Undergraduate, and Other Students: Open postings on [Handshake](https://app.joinhandshake.com/login)
{% endcapture %}

{% capture col3 %}
Or email [Randi Johnson](mailto:randi.johnson@cuanschutz.edu)
{% endcapture %}

{% include cols.html col1=col1 col2=col2 col3=col3 %}
