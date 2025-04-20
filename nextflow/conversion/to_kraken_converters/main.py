"""
Main script to run conversion layer. This converts all tool outputs to kraken2 report format.
Imports all specified converters from converters folder.
Instantiates all converters with an instance of the internal taxonomy database.
Tries to convert all given outputs by iterating over the converters.
"""
import sys
import os
import importlib
from to_kraken_converters.abstract_converter import AbstractConverter
from Database.taxDBsqlite import TaxDBsqlite


def import_converters(package: str, directory: str):
    """
    Dynamically import all modules from directory.
    Makes them addressable as subclasses of AbstractConverter.
    Args:
        package (str): The Python package name (e.g., "converters").
        directory (str): The directory path where the modules are located.
    """
    for filename in os.listdir(directory):
        if filename.endswith(".py") and filename != "__init__.py":
            module_name = f"{package}.{filename[:-3]}"
            try:
                importlib.import_module(module_name)

            except Exception as e:
                print(f"Error importing {module_name}: {e}")


def get_all_converters(taxdb):
    """
    Instantiate all subclasses of AbstractConverter with the TaxDB.
    """
    converters = []
    for subclass in AbstractConverter.__subclasses__():
        converters.append(subclass(taxdb))
    return converters


def main():
    current_dir = os.path.dirname(__file__)
    converters_dir = os.path.join(current_dir, "converters")
    import_converters("to_kraken_converters.converters", converters_dir)

    database_path = sys.argv[2]
    taxdb = TaxDBsqlite(database_path)

    converters = get_all_converters(taxdb)

    file = sys.argv[1]
    output_file = sys.argv[3]

    for converter in converters:
        if converter.can_convert(file):
            try:
                converter.convert(file, output_file)
            except Exception as e:
                raise e
            break
    else:
        print(f"No suitable conversion found for {file}.")


if __name__ == "__main__":
    main()
