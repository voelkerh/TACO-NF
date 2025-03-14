# Dash - README

## Extension für phylogenetic tree

! Erweiterte Plotly-Version inkl phylogenetic tree in Ordner "local_plotly" ablegen.
Hier laden: [GitHub Plolty mit Extension](https://github.com/voelkerh/plotly.py)

## CSS Styleshee einbinden

Automatisch über "assets" Ordner: [CSS einbinden](https://dash.plotly.com/external-resources)

## Aufrufen mit Sample Files

- Die .txt Dateien enthalten die Baum-Serialisierung in Newick-Format.
- Die .report Dateien enthalten die Klassifikationen im kraken-Format.

Aufruf über die Kommandozeile nach Format: dash_tree_nextto_heatmap.py newick.txt gt.report kraken.report bowtie.report (Anzahl der reports ist beliebig, newick-Strings aktuell = 1)
In Repo läuft: python dash_tree_nextto_heatmap.py sample_files/newick_kraken.txt sample_files/groundtruthkraken.report sample_files/kraken.report sample_files/bowtiekraken.report

Output -> Visualisierung über localhost