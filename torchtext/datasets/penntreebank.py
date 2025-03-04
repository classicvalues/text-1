import os
from typing import Union, Tuple

from torchtext._internal.module_utils import is_module_available
from torchtext.data.datasets_utils import (
    _wrap_split_argument,
    _create_dataset_directory,
)

if is_module_available("torchdata"):
    from torchdata.datapipes.iter import FileOpener, HttpReader, IterableWrapper


URL = {
    "train": "https://raw.githubusercontent.com/wojzaremba/lstm/master/data/ptb.train.txt",
    "test": "https://raw.githubusercontent.com/wojzaremba/lstm/master/data/ptb.test.txt",
    "valid": "https://raw.githubusercontent.com/wojzaremba/lstm/master/data/ptb.valid.txt",
}

MD5 = {
    "train": "f26c4b92c5fdc7b3f8c7cdcb991d8420",
    "valid": "aa0affc06ff7c36e977d7cd49e3839bf",
    "test": "8b80168b89c18661a38ef683c0dc3721",
}

NUM_LINES = {
    "train": 42068,
    "valid": 3370,
    "test": 3761,
}

DATASET_NAME = "PennTreebank"


@_create_dataset_directory(dataset_name=DATASET_NAME)
@_wrap_split_argument(("train", "valid", "test"))
def PennTreebank(root, split: Union[Tuple[str], str]):
    """PennTreebank Dataset

    For additional details refer to https://catalog.ldc.upenn.edu/docs/LDC95T7/cl93.html

    Number of lines per split:
        - train: 42068
        - valid: 3370
        - test: 3761

    Args:
        root: Directory where the datasets are saved. Default: os.path.expanduser('~/.torchtext/cache')
        split: split or splits to be returned. Can be a string or tuple of strings. Default: (`train`, `valid`, `test`)

    :returns: DataPipe that yields text from the Treebank corpus
    :rtype: str
    """
    if not is_module_available("torchdata"):
        raise ModuleNotFoundError(
            "Package `torchdata` not found. Please install following instructions at `https://github.com/pytorch/data`"
        )

    url_dp = IterableWrapper([URL[split]])
    cache_dp = url_dp.on_disk_cache(
        filepath_fn=lambda x: os.path.join(root, os.path.basename(x)),
        hash_dict={os.path.join(root, os.path.basename(URL[split])): MD5[split]},
        hash_type="md5",
    )
    cache_dp = HttpReader(cache_dp).end_caching(mode="wb", same_filepath_fn=True)

    # TODO: read in text mode with utf-8 encoding, see: https://github.com/pytorch/pytorch/issues/72713
    data_dp = FileOpener(cache_dp, mode="b")
    # remove single leading and trailing space from the dataset
    return data_dp.readlines(return_path=False, decode=True).map(lambda t: t.strip())
