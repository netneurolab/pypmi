# -*- coding: utf-8 -*-
"""Code for testing the `pypmi` package."""

import json
import os
import importlib.resources
import pytest
from pypmi.fetchers import fetch_studydata, fetchable_studydata

if getattr(importlib.resources, 'files', None) is not None:
    with open(importlib.resources.files("pypmi") / "data/studydata.json") as src:
        _STUDYDATA = json.load(src)
else:
    from pkg_resources import resource_filename
    with open(resource_filename('pypmi', 'data/studydata.json'), 'r') as src:
        _STUDYDATA = json.load(src)

@pytest.fixture(scope='session')
def datadir():
    """Return the path to the data directory."""
    if os.environ.get('PPMI_PATH') is None:
        path = os.path.join(os.environ['HOME'], 'pypmi-data')
        os.makedirs(path, exist_ok=True)
        os.environ['PPMI_PATH'] = path
    else:
        path = os.environ['PPMI_PATH']
    print(path)
    return path


# @pytest.fixture(scope='session')
# def studydata(datadir):
#     """Return the path to the studydata directory."""
#     # download data (don't overwrite if we already did it)
#     fetch_studydata('all', path=datadir, overwrite=False)

#     # has all the studydata we were supposed to fetch has been fetched?
#     fns = [_STUDYDATA.get(d)['name'] for d in fetchable_studydata()]
#     assert all(os.path.exists(os.path.join(datadir, f)) for f in fns)

#     return datadir
