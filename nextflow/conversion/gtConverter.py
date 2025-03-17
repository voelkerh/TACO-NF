import os
import sys
from taxDBsqlite import TaxDBsqlite


def fetch_taxonomic_info(taxid, taxdb):
    name = taxdb.get_name_from_taxonomic_data(taxid)
    parent_taxid = taxdb.get_parent_taxid_from_taxonomic_data(taxid)
    rank = taxdb.get_full_rank_from_taxonomic_data(taxid)
    rank_code = taxdb.get_rank_code_from_full_rank(rank)
    return name, parent_taxid, rank_code

def convert_to_kraken(input_file, output_dir, dbfilename):
    taxdb = TaxDBsqlite(dbfilename)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    numreads = 0
    
    with open(input_file, 'r') as infile:
        header = infile.readline().strip()
        for line in infile:
            try:
                tax_id, read_number, genbank_accession = line.strip().split(',')
                numreads += int(read_number)
            except ValueError as e:
                print(f"Error processing line: {line.strip()} - {e}")
                continue

    with open(input_file, 'r') as infile:
        header = infile.readline().strip()
        output_file = open(os.path.join(output_dir, f"converted.report"), 'w')

        for line in infile:
            try:
                tax_id, read_number, genbank_accession = line.strip().split(',')
                tax_id = int(tax_id)
                read_number = int(read_number)
            except ValueError as e:
                print(f"Error processing line: {line.strip()} - {e}")
                continue
            
            name, parent_taxid, rank_code = fetch_taxonomic_info(tax_id, taxdb)
            tax_ids = []
            old_taxid = tax_id
            perc_reads = read_number/numreads
            res = []
            level = 0
            while parent_taxid != tax_id and parent_taxid != 1:
                if tax_id in tax_ids:
                    continue
                print(f"{parent_taxid} - {tax_id}")
                tax_id = parent_taxid
                name, parent_taxid, rank_code = fetch_taxonomic_info(tax_id, taxdb)
                res += [(f"{perc_reads}\t{read_number}\t0\t{rank_code}\t{tax_id}\t", name + "\n", level)]
                level -= 1
            res.reverse() 
            output_file.write("".join([x[0] + (x[2]-level)*"    "+x[1] for x in res]))
            name, parent_taxid, rank_code = fetch_taxonomic_info(old_taxid, taxdb)
            output_file.write(f"{perc_reads}\t{read_number}\t{read_number}\t{rank_code}\t{tax_id}\t" + (-1*level+1)*"    " + f"{name}\n")
        output_file.close()                

if __name__ == '__main__':
    input_file = sys.argv[1]
    output_dir = sys.argv[2]
    dbfile = sys.argv[3]
    convert_to_kraken(input_file, output_dir, dbfile)

