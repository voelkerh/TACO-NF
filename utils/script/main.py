import sys
import os
sys.path.append('/Users/arturmeshalkin/Documents/GitHub/htwpipe/utils')
import importlib
from script.abstract_converter import AbstractConverter
from Database.taxDBsqlite import TaxDBsqlite


def import_converters(package: str, directory: str):
    """
    Dynamisch alle Module in einem Verzeichnis importieren.
    Args:
        package (str): Der Python-Paketname (z. B. "converters").
        directory (str): Der Verzeichnispfad, in dem die Module liegen.
    """
    print(f"Inhalt des Verzeichnisses: {os.listdir(directory)}")
    for filename in os.listdir(directory):
        if filename.endswith(".py") and filename != "__init__.py":
            module_name = f"{package}.{filename[:-3]}"
            try:
                module = importlib.import_module(module_name)
                #print(f"Importiert: {module_name}")
            except Exception as e:
                print(f"Fehler beim Importieren von {module_name}: {e}")


def get_all_converters(taxdb):
    """
    Instanziiert alle Unterklassen von AbstractConverter mit der TaxDB.
    """
    converters = []
    for subclass in AbstractConverter.__subclasses__():
        converters.append(subclass(taxdb))
    return converters


def main():
    """
    Im Terminal ausführen:
    Ins Verzeichnis 'utils' wechseln
    python -m script.main path_der_datei
    Beispiel:
    python -m script.main input_samples/ground_truth.txt
    """    
    current_dir = os.path.dirname(__file__)
    converters_dir = os.path.join(current_dir, "converters")
    import_converters("script.converters", converters_dir)

    database_path = "Database/database.db"
    taxdb = TaxDBsqlite(database_path)
    
    converters = get_all_converters(taxdb)
    
    file = sys.argv[1]
    #file = input("Gib den Dateipfad ein: ")
    #file = ("script/input_samples/mappingresult.sam")
    #file = ("script/input_samples/ground_truth.txt")
    #file = ("script/input_samples/kraken_in.report")


    for converter in converters:
        if converter.can_convert(file):
            try:
                result = converter.convert(file)
                print(result)
            except Exception as e:
                print(f"Fehler bei der Konvertierung von {file}: {e}")
            break
    else:
        print(f"Keine passende Konvertierung für {file} gefunden.")

if __name__ == "__main__":
    main()
