# -*- coding: utf-8 -*-
"""Functions for fetching/downloading data from the PPMI database."""

from io import BytesIO
from pathlib import Path
import json
import shutil
import os
import importlib.resources
import re
from typing import Dict, List
import zipfile
from datetime import datetime

import requests
from tqdm import tqdm

from .utils import _get_cred, _get_data_dir


if getattr(importlib.resources, 'files', None) is not None:
    with open(importlib.resources.files("pypmi") / "data/studydata.json") as src:
        _STUDYDATA = json.load(src)
    with open(importlib.resources.files("pypmi") / "data/genetics.json") as src:
        _GENETICS = json.load(src)
else:
    from pkg_resources import resource_filename
    with open(resource_filename('pypmi', 'data/studydata.json'), 'r') as src:
        _STUDYDATA = json.load(src)
    with open(resource_filename('pypmi', 'data/genetics.json'), 'r') as src:
        _GENETICS = json.load(src)


def _get_auth_session(
        user: str = None, password: str = None) -> Dict[str, str]:
    """
    Return credentials for downloading raw study data from the PPMI.

    Parameters
    ----------
    user : str, optional
        Email for user authentication to the LONI IDA database. If not supplied
        will look for $PPMI_USER variable in environment. Default: None
    password : str, optional
        Password for user authentication to the LONI IDA database. If not
        supplied will look for $PPMI_PASSWORD variable in environment. Default:
        None

    Returns
    -------
    params : dict
        With keys 'userId' and 'authKey', ready to be supplied to a GET call
    """
    user, password = _get_cred(user, password)

    s = requests.Session()
    r = s.post(
        "https://ida.loni.usc.edu/explore/jsp/common/login.jsp",
        data=dict(userEmail=user, userPassword=password),
    )
    if "Invalid password" in r.text:
        raise ValueError(
            'Could not authenticate user and password from PPMI database.'
            'Please make sure that URL is appropriately formed and try again.'
        )
    else:
        print('Authenticated')

    return s


def _download_data(info: Dict[str, Dict[str, str]],
                   type: str,
                   path: str = None,
                   user: str = None,
                   password: str = None,
                   overwrite: bool = False,
                   verbose: bool = True) -> List[str]:
    """
    Download dataset(s) listed in `info` from `url`.

    Parameters
    ----------
    info : dict
        Dataset information to download. Each key must have a value that is
        a dictionary containing keys 'id' (specifying the file ID of the
        dataset in the PPMI database) and 'name' (specifying the file name of
        the dataset in the PPMI database).
    type : str
        Type of data being downloaded; this is used to determine the URL to
        which the request is made. Currently only 'studydata' and 'genetics'
        are supported.
    path : str, optional
        Filepath where downloaded data should be saved. If data files already
        exist at `path` they will be overwritten unless `overwrite=False`. If
        not specified will look for an environmental variable $PPMI_PATH and,
        if not set, use the current directory. Default: None
    user : str, optional
        Email for user authentication to the LONI IDA database. If not supplied
        will look for $PPMI_USER variable in environment. Default: None
    password : str, optional
        Password for user authentication to the LONI IDA database. If not
        supplied will look for $PPMI_PASSWORD variable in environment. Default:
        None
    overwrite : bool, optional
        Whether to overwrite existing PPMI data files at `path` if they already
        exist. Default: False
    verbose : bool, optional
        Whether to print progress bar as download occurs. Default: True

    Returns
    -------
    downloaded : list
        Filepath(s) to downloaded datasets
    """
    path = _get_data_dir(path)

    # check provided credentials; if none were supplied, look for creds in
    # user environmental variables
    if verbose:
        print('Fetching authentication key for data download...')
    user, password = _get_cred(user, password)

    # gets numerical file IDs from relevant JSON file; if the file is already
    # downloaded we store the filename to return to the user
    downloaded = []
    if verbose:
        print('Requesting {} datasets for download...'.format(len(info)))

    files_to_download = []
    for dset, file_info in info.items():
        if file_info is None:
            raise ValueError('Provided dataset {} not available. Please see '
                             'available_datasets() for valid entries.'
                             .format(dset))

        file_id = file_info.get('id', None)
        file_name = path / file_info.get('filename', '').format(DATETOKEN=datetime.now().strftime("%d%b%Y"))

        # if we don't want to overwrite existing data make sure that file
        # does not exist before appending it to request parameters
        if not file_name.is_file() or overwrite:
            files_to_download.append((file_id, file_name))
        else:
            downloaded.append(file_name)

    # if we already downloaded all then there is no reason to make requests!
    if len(files_to_download) == 0:
        return downloaded

    session = _get_auth_session(user=user, password=password)
    # access the page to update the session
    if type == 'studydata':
        session.get(
            "https://ida.loni.usc.edu/pages/access/studyData.jsp?project=PPMI"
        )
    elif type == 'genetics':
        r_genetics = session.get(
            "https://ida.loni.usc.edu/pages/access/geneticData.jsp?project=PPMI"
        )

        fileurl_match = re.search(r' \"/(.+)/\" +', r_genetics.text)
        fileurl_string = fileurl_match.group(1) if fileurl_match else None
    else:
        raise ValueError('Invalid data type requested for download.')

    print(f"{files_to_download = }")
    if type == 'studydata':
        for fid, fname in files_to_download:
            print(fid)
            fileurl_resp = session.post(
                "https://ida.loni.usc.edu/pages/ajax/getStudyData",
                data=dict(fileId=fid)
            )
            fileurl_match = re.search(r'<path name=\"(.+)\"/>', fileurl_resp.text)
            fileurl_string = fileurl_match.group(1) if fileurl_match else None
            if fileurl_string is None:
                raise ValueError('Could not find download URL for file ID {}.'
                                    .format(fid))
            fileurl = f"https://ida.loni.usc.edu/download/files/study/{fileurl_string}"
            if verbose:
                print('Downloading {}...'.format(fname))
            with session.get(fileurl, stream=True) as r:
                with open(fname, 'wb') as f:
                    shutil.copyfileobj(r.raw, f)
            downloaded.append(fname)
    elif type == 'genetics':
        for fid, fname in files_to_download:
            print(fid)
            fileurl = f"https://ida.loni.usc.edu/download/files/genetic/{fileurl_string}/{fid}"
            if verbose:
                print('Downloading {}...'.format(fname))
            with session.get(fileurl, stream=True) as r:
                with open(fname, 'wb') as f:
                    shutil.copyfileobj(r.raw, f)
            downloaded.append(fname)
    else:
        raise ValueError('Invalid data type requested for download.')
    return downloaded


def fetchable_studydata() -> List[str]:
    """
    List study data available to download from the PPMI.

    Returns
    -------
    available : list
        List of available data files

    See Also
    --------
    pypmi.fetch_studydata
    """
    return list(_STUDYDATA.keys())


def fetchable_genetics() -> List[str]:
    """
    List genetics data available to download from the PPMI.

    Returns
    -------
    available : list
        List of available data files

    See Also
    --------
    pypmi.fetch_genetics
    """
    return list(_GENETICS.keys())


def fetch_studydata(datasets: str,
                    path: str = None,
                    user: str = None,
                    password: str = None,
                    overwrite: bool = False,
                    verbose: bool = True) -> List[str]:
    """
    Download specified study data `datasets` from the PPMI database.

    Parameters
    ----------
    *datasets : str
        Datasets to download. Can provide as many as desired, but they should
        be listed in :py:func:`pypmi.fetchable_studydata`. Alternatively, if
        any of the provided values are 'all', then all available datasets will
        be fetched.
    path : str, optional
        Filepath where downloaded data should be saved. If data files already
        exist at `path` they will be overwritten unless `overwrite=False`. If
        not supplied the current directory is used. Default: None
    user : str, optional
        Email for user authentication to the LONI IDA database. If not supplied
        will look for $PPMI_USER variable in environment. Default: None
    password : str, optional
        Password for user authentication to the LONI IDA database. If not
        supplied will look for $PPMI_PASSWORD variable in environment. Default:
        None
    overwrite : bool, optional
        Whether to overwrite existing PPMI data files at `path` if they already
        exist. Default: False
    verbose : bool, optional
        Whether to print progress bar as download occurs. Default: True

    Returns
    -------
    downloaded : list
        Filepath(s) to downloaded datasets

    See Also
    --------
    pypmi.fetchable_studydata
    """
    # take subset of available study data based on requested `datasets`
    if isinstance(datasets, str) and datasets=='all':
        datasets = fetchable_studydata()

    # filter the dictionary of available datasets to only include those
    # requested by the user
    # print(datasets)
    info = {dset: _STUDYDATA.get(dset) for dset in datasets}
    # print(info)
    return _download_data(info, "studydata", path=path, user=user, password=password,
                          overwrite=overwrite, verbose=verbose)


def fetch_genetics(datasets: str,
                   path: str = None,
                   user: str = None,
                   password: str = None,
                   overwrite: bool = False,
                   verbose: bool = True) -> List[str]:
    """
    Download specified genetics data `datasets` from the PPMI database.

    Parameters
    ----------
    *datasets : str
        Datasets to download. Can provide as many as desired, but they should
        be listed in :py:func:`pypmi.fetchable_genetics`. Alternatively, if any
        of the provided values are 'all', then all available datasets will be
        fetched.
    path : str, optional
        Filepath where downloaded data should be saved. If data files already
        exist at `path` they will be overwritten unless `overwrite=False`. If
        not supplied the current directory is used. Default: None
    user : str, optional
        Email for user authentication to the LONI IDA database. If not supplied
        will look for $PPMI_USER variable in environment. Default: None
    password : str, optional
        Password for user authentication to the LONI IDA database. If not
        supplied will look for $PPMI_PASSWORD variable in environment. Default:
        None
    overwrite : bool, optional
        Whether to overwrite existing PPMI data files at `path` if they already
        exist. Default: False
    verbose : bool, optional
        Whether to print progress bar as download occurs. Default: True

    Returns
    -------
    downloaded : list
        Filepath(s) to downloaded datasets

    See Also
    --------
    pypmi.fetchable_genetics
    """
    url = "https://utilities.loni.usc.edu/download/genetic"
    datasets = list(datasets)

    # take subset of available genetics data based on requested `datasets`
    if isinstance(datasets, str) and datasets=='all':
        datasets = fetchable_studydata()

    # check for project designations in requested data
    # for project in fetchable_genetics(projects=True):
    #     if project in datasets:
    #         datasets.remove(project)
    #         datasets += [f for f in _GENETICS.keys() if project in f.lower()]

    info = {dset: _GENETICS.get(dset) for dset in datasets}

    return _download_data(info, "genetics", path=path, user=user, password=password,
                          overwrite=overwrite, verbose=verbose)
