import sys
import os
import importlib
from script.abstract_converter import AbstractConverter
from Database.taxDBsqlite import TaxDBsqlite



def import_converters(package: str, directory: str):
    """
    Dynamically import all modules in a directory.
    Args:
        package (str): The Python package name (e.g., "converters").
        directory (str): The directory path where the modules are located.
    """
    #print(f"Contents of the directory: {os.listdir(directory)}")
    for filename in os.listdir(directory):
        if filename.endswith(".py") and filename != "__init__.py":
            module_name = f"{package}.{filename[:-3]}"
            try:
                module = importlib.import_module(module_name)
                #print(f"Imported: {module_name}")

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
    """
    Execute in the terminal:
        1.Change to the utils directory:
        2.Run the script using Python:
        python -m script.main path_to_file
        
        Example:
        python -m script.main script/input_samples/ground_truth.txt
    """
    current_dir = os.path.dirname(__file__)
    converters_dir = os.path.join(current_dir, "converters")
    import_converters("script.converters", converters_dir)

    database_path = sys.argv[2]
    taxdb = TaxDBsqlite(database_path)

    converters = get_all_converters(taxdb)

    file = sys.argv[1]
    # file = input("Enter the full file path:")
    # file = ("script/input_samples/mappingresult.sam")
    # file = ("script/input_samples/ground_truth.txt")
    # file = ("script/input_samples/kraken_in.report")
    # file = ("script/input_samples/classification_output.tre")

    for converter in converters:
        if converter.can_convert(file):
            #try:
            result = converter.convert(file)
            #print(result)
#             except Exception as e:
#                 print(f"Error converting {file}: {e}")
            break
    else:
        print(f"No suitable conversion found for {file}.")


if __name__ == "__main__":
    main()
