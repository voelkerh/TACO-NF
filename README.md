## TODO

# Create ReadMe
TODO add README with how2build app container - appcontainer bauen und
Von Frau Voelker das app container definitionsfile geben lassen, bauen pfad dann absolut param zu https://zenodo.org/ (wenn pipeline rework done)
create params.dashContainer (siehe line 9 @workflowNew.nf)


# Todo DatenBank.py

store dir -> gucke https://www.nextflow.io/docs/latest/reference/process.html#storedir
prozess 1 -> dmps runterladen wenn nicht vorhanden (Kein Input, läuft immer) entpackt sie. Gibt 3 dumps aus
prozess 2 -> Nimmt 3 dmps (OUTPUT Channle von P1 als input für P2) verwendet dabei store dir
        rufe die datenbank auf mit create zeil 158
           liest die ganzen dmps ein und erstellt die sqlite db (mit sotre dir, damit wenn bereits vorhanden übersprungen wird)