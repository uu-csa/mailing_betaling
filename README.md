# Mailing Betaling
**Applicatie voor de betaalmail selecties van CSa**
- - -
*L.C. Vriend*

Deze [Python](https://www.python.org/) applicatie selecteert en groepeert de studenten die een betaalmail moeten ontvangen tijdens de inschrijfcampagne. Hieronder staat een korte uitleg over de werking van de tool.

## Brongegevens
De brondata komt uit de OSIRIS query database. Deze wordt geraadpleegd mbv [osiris_query](https://github.com/uu-csa/osiris_query).

> Deze tool maakt gebruik van [pyodbc](https://github.com/mkleehammer/pyodbc/wiki) om verbinding te maken met de ODBC driver. Omdat op UU-computers een 32-bit versie geïnstalleerd is van deze driver, moet een 32-bit virtuele omgeving gebruikt worden.

De SQL en resulterende tabellen worden opgeslagen in en geraadpleegd vanuit de folders van [osiris_query](https://github.com/uu-csa/osiris_query). Het betreft de volgende tabellen:

| Tabel                               | afkorting |
| ----------------------------------- | --------- |
| **Inschrijfregels**                 |           |
| OSIRIS.OST_STUDENT_INSCHRIJFHIST    | s_sih     |
| OSIRIS.OST_STUDENT_OPLEIDING        | s_opl     |
| OSIRIS.OST_STUDENT_INSCHR_STOPLICHT | s_stop    |
| **Persoonsgegevens**                |           |
| OSIRIS.OST_STUDENT                  | s_stud    |
| OSIRIS.OST_STUDENT_ADRES            | s_adr     |
| **Aanmeldprocessen**                |           |
| OSIRIS.OST_STUDENT_IO_IN_AANVRAAG   | s_ooa_aan |
| **Financiële gegevens**             |           |
| OSIRIS.OST_STUDENT_VRIJ_VELD        | s_vrij    |
| OSIRIS.OST_SGROEP_STUDENT           | s_grp     |
| OSIRIS.OST_SGROEP                   | r_grp     |

Alleen gegevens die gekoppeld kunnen worden aan openstaande inschrijfverzoeken voor het gedefinieerde collegejaar worden gebruikt.

## Moedertabel
De brongegevens worden mbv [pandas](https://pandas.pydata.org/) samengevoegd tot een moedertabel. Deze dient als basis voor de rest van de selecties.

> De parameters die gebruikt worden om het moederbestand te genereren, zijn terug te vinden (en te bewerken) in [`parameters.ini`](https://github.com/uu-csa/mailing_betaling/blob/master/parameters.ini).

## Zeef
De moedertabel wordt vervolgens door de zeef gehaald. Deze bestaat uit drie opeenvolgende selecties:

1. **De basisselectie** : in deze stap worden alle studenten verwijderd die geen mail dienen te ontvangen. Het gaat hier (1) om studenten die op een andere manier aan de collegegeldverplichting (zullen gaan) voldoen, en (2) om studenten die systeemtechnisch nog niet aan de betalingsverplichting kunnen voldoen (bv. geen geverifieerde indentiteit of het te betalen collegegeldbedrag is nog niet bepaald).
1. **De selectie per soort inschrijving** : in deze stap worden de studenten verwijderd die binnen het inschrijfproces (nog) niet in een fase beland zijn waarin ze voor een betaalmail in aanmerking komen. Het gaat hier om studenten die nog niet geselecteerd/geplaatst/toegelaten zijn of studenten die nog niet aan de matchingsverplichting voldaan hebben.
1. **De selectie per betaalmail** : op dit punt houden we alleen nog de studenten over die een betaalmail moeten ontvangen. In deze stap wordt bepaald wie welke betaal moet krijgen.

> De criteria voor deze selecties zijn terug te vinden (en te bewerken) in [`queries.ini`](https://github.com/uu-csa/mailing_betaling/blob/master/queries.ini). De queries zijn opgesteld volgens [deze grammatica](https://pandas.pydata.org/pandas-docs/stable/user_guide/indexing.html#indexing-query).

## Mailhistorie
De mailhistorie wordt bijgehouden in `mailhistorie.pkl` in de folder `output`.

> Deze kan maar één keer per dag bijgewerkt worden. Deze beperking is ingebouwd om te voorkomen dat er verwarring ontstaat over welke studenten wel/niet een e-mail hebben ontvangen.

Deze tabel wordt gebruikt om bij te houden welke studenten wanneer welke mail heeft ontvangen. Alleen als een student nooit of langer dan 14 dagen geleden een bepaald type mail heeft ontvangen, komt zij in aanmerking om gemaild te worden.

## Dashboard
De output wordt weergegeven in het Dashboard Betaalmail. Dit is een app gebouwd met [Flask](http://flask.pocoo.org/). Het dashboard wordt automatisch gestart in de webbrowser nadat de queries zijn afgerond.

> Op de achtergrond draait een lokale server die de webapplicatie aan de browser serveert. Om de applicatie af te sluiten moet niet alleen de browser/tab worden afgesloten maar ook de server.
>
>De makkelijkste manier om dit te bewerkstelligen is via de knop `[x]` op het Dashboard. Deze sluit niet alleen de browser/tab af, maar ook de server.

### Output
In het dashboard kun je per betaalmail een Excel-bestand downloaden met daarin alle studentnummers die de mail moeten ontvangen. Het is echter ook mogelijk om studenten per batch van 500 direct naar het klembord te kopiëren. Voor de kleinere selecties is het direct kopiëren naar OSIRIS doorgaans efficiënter dan het inlezen van Excel-bestanden.

### Issues
Daarnaast geeft het Dashboard weer of er issues zijn opgetreden bij bepaalde studenten. Het gaat hier dan om:

1. Studenten die wel door de tweede zeef zijn gekomen maar uiteindelijk niet zijn ingedeeld bij een bepaalde betaalmail.
1. Studenten die bij de derde zeef aan meer dan één betaalmail zijn toegewezen.

In deze gevallen wordt de student buiten de selecties gehouden en zal handmatig bepaald moeten worden wat er in dat geval moet gebeuren.

- - -

## Afhankelijkheden

Dit script maakt gebruik van verschillende Python packages. Als deze afhankelijkheden niet in de Python omgeving geïnstalleerd zijn, werkt het script niet. Het gaat om de volgende afhankelijkheden:

- python=3.7
- pandas=0.24.*
- pyodbc=4.0.*
- ipykernel
- xlrd
- openpyxl
- flask=1.0.*

Deze zijn terug te vinden in [`environment.yml`](https://github.com/uu-csa/mailing_betaling/blob/master/environment.yml).

## Installatie
Deze afhankelijkheden moeten [vanwege de ODBC-driver](https://github.com/uu-csa/mailing_betaling#brongegevens) in een 32bit virtuele omgeving geïnstalleerd worden. Bij gebruik van de [Anaconda](https://www.anaconda.com/distribution/) distributie van Python, is de virtuele omgeving met de volgende commando's in de command prompt te installeren:

> `set CONDA_FORCE_32BIT=1`  
> `conda env create -f environment.yml`

## Applicatie
Ervanuitgaande dat de virtuele omgeving geïnstalleerd is volgens bovenstaande instructies, kun je de applicatie starten met `run_app.bat`.
