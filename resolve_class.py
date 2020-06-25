import argparse
import time

from utils.meta_utils import read_meta, add_meta
from utils.std_utils import read_data, write_std

from utils.curate_utils import df_filter_invalid_smi, df_filter_replicates
from utils.curate_utils import get_keep_indices, __version__
from utils.curate_utils import ask_for_filter, process_filter_input, filters

def resolve_class(path, filter_fn=None):

    # Read meta and extra necessary elements
    meta = read_meta(path)
    meta_path = meta.get('meta_path')
    std_data_path = meta.get('std_data_path')
    std_smiles_col = meta.get('std_smiles_col')
    std_key_col = meta.get('std_key_col')

    # Read standardized data and remove invalid smiles
    std_data = read_data(std_data_path)
    resolved_data = df_filter_invalid_smi(std_data, std_smiles_col)

    # Then, process filter function and extract indices to keep
    filter_fn = process_filter_input(filter_fn, filters)
    idx_keep_dict = get_keep_indices(resolved_data, std_key_col, filter_fn)

    # Filter replicates and write data to curated data path
    resolved_data = df_filter_replicates(resolved_data, idx_keep_dict)
    resolved_data_path = write_std(resolved_data, path, prefix='resolved_')

    resolved_meta = {'resolved_data_path': resolved_data_path,
                    'resolved_indices': idx_keep_dict,
                    'resolved_rows': int(resolved_data.shape[0]),
                    'resolution_function': filter_fn.__name__,
                    'resolved_version': __version__,
                    'resolved_utc_fix': int(time.time())}

    add_meta(meta_path, resolved_meta)  # Update metadata

    print("Curated df will be written to:", resolved_data_path)
    print("Updated metadata at:", meta_path)

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('path', type=str,
                        help='path to directory with data to curate')
    parser.add_argument('--filter_fn', '-f', type=str, default=None,
                        choices=list(filters.keys()),
                        help='specify a filter function for curation')
    args = parser.parse_args()

    resolve_class(args.path, args.filter_fn)
