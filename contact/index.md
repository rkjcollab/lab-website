---
title: Connect
nav:
  order: 3
  tooltip: Email, address, and location
---

# {% include icon.html icon="fa-regular fa-envelope" %}Contact

Want to connect with us!!

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
{%
  include button.html
  type="address"
  tooltip="Our location on Google Maps for easy navigation"
  link="https://www.google.com/maps/dir//1890+N+Revere+Ct,+Aurora,+CO+80045/@39.745443,-104.9242938,12z/data=!4m8!4m7!1m0!1m5!1m1!1s0x876c633a9c45be13:0x85f675e778fce18c!2m2!1d-104.8418929!2d39.7454721?entry=ttu&g_ep=EgoyMDI1MDYxNS4wIKXMDSoASAFQAw%3D%3D"
%}

{% include section.html %}

{% capture col1 %}

{%
  include figure.html
  image="images/photo.jpg"
  caption="Lorem ipsum"
%}

{% endcapture %}

{% capture col2 %}

{%
  include figure.html
  image="images/photo.jpg"
  caption="Lorem ipsum"
%}

{% endcapture %}

{% include cols.html col1=col1 col2=col2 %}

{% include section.html dark=true %}

{% capture col1 %}
Lorem ipsum dolor sit amet  
consectetur adipiscing elit  
sed do eiusmod tempor
{% endcapture %}

{% capture col2 %}
Lorem ipsum dolor sit amet  
consectetur adipiscing elit  
sed do eiusmod tempor
{% endcapture %}

{% capture col3 %}
Lorem ipsum dolor sit amet  
consectetur adipiscing elit  
sed do eiusmod tempor
{% endcapture %}

{% include cols.html col1=col1 col2=col2 col3=col3 %}
