## v1.1
*(2020-10-18)*


## v1.04
*(2020-07-17)*

### Applicatie
- changelog toegevoegd

### Datamodel
- tabel `ooa_rubriek` toegevoegd aan datamodel (bevat rubriekstatussen van alle aanmeldprocessen voor het betreffende collegejaar)

### Moedertabel
- velden toegevoegd aan moedertabel op basis van rubriekstatussen (`ooa_rubriek`):
    * `vvr_van_csa_naar_isa` is `True` als rubriekstatus is `X` in `CSA_I_VVR` anders `False`
    * `vvr_van_isa_naar_csa` is `True` als rubriekstatus is `F12` in `MVV/VVR BMS20` anders `False`
- herberekening toegepast op `betaalvorm`:
    1. betaalvorm verwijderen indien inschrijfregel is ingetrokken
    2. indien bij een student een betaalvorm aanwezig is, deze doorkopiëren naar andere inschrijfregels bij de student (indien aanwezig)

### Zeef
- actiefcode toegevoegd aan zeef **basis** omdat inschrijvingstatus in sommige gevallen op `i` blijft staan, nadat een inschrijfregel is teruggezet naar status verzoek.
- uitzondering toegevoegd op uitsluiten van studenten met isa vvr proces in zeef **basis**:

    > `(isa_vvr_proces == False or vvr_van_isa_naar_csa == True)`

- uitzondering toegevoegd om studenten die zijn doorgezet naar isa uit te sluiten in zeef **basis**:

    > `vvr_van_csa_naar_isa == False`

- criterium toegevoegd bij `om_csa` in zeef **mailing**:

    > `(factuur == True or vvr_van_isa_naar_csa == True)`

- criterium toegevoegd bij overige bakjes in zeef **mailings**:

    > `vvr_van_isa_naar_csa == False`

### Debugger
- velden `vvr_van_csa_naar_isa` en `vvr_van_isa_naar_csa` toegevoegd bij **kenmerken**
- veld `actiefcode` toegevoegd bij **inschrijfregel**
- tabel toegevoegd waarin aangegeven staat in welke bakje(s) de student is terechtgekomen; dit is niet direct uit de mailhistorie af te leiden omdat daar alleen records worden toegevoegd indien de vorige gelijksoortige mail meer dan twee weken geleden verstuurd is
- niet voorkomend studentnummer leidt niet langer tot een error message
