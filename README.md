# Mailing Betaling
---

Script om de selectie te maken op de betaalmail.
Het script maakt gebruik van [osiris_query](https://github.com/uu-csa/osiris_query).

1. Mailhistorie wordt bijgehouden in `mailhistorie.pkl` in de folder `output`
1. Indien bestand niet bestaat, wordt deze aangemaakt.
1. Indien datum van vandaag niet aanwezig is in bestand, dan query op de OSQP voor vti.
1. Vervolgens worden de studenten geselecteerd en gecategoriseerd die voor een mail in aanmerking komen.
1. Dit werkt als volgt:
    a. Basisselectie
    b. Selectie per soort inschrijving
    c. Selectie per soort betaalmail

De output wordt weergegeven in Dashboard Betaalmail. Hier kun je per betaalmail:

1. een excel met studentnummers downloaden, of;
2. per batch van 500 studenten naar je klembord kopiëren.
