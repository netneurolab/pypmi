# -*- coding: utf-8 -*-
"""Common utility functions for the `pypmi` package."""

import os
from typing import List, Tuple
from pathlib import Path


def _get_cred(user: str = None,
                        password: str = None) -> Tuple[str, str]:
    """
    Get PPMI authentication from environmental variables if not supplied.

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
    user, password : str
        Authentication for PPMI database
    """
    var = env = None

    # try and find user in environmental variable "$PPMI_USER"
    if user is None:
        try:
            user = os.environ['PPMI_USER']
        except KeyError:
            var, env = 'user', 'PPMI_USER'

    # try and find password in environmental variable "$PPMI_PASSWORD"
    if password is None:
        try:
            password = os.environ['PPMI_PASSWORD']
        except KeyError:
            var, env = 'password', 'PPMI_PASSWORD'

    if var is not None or env is not None:
        raise ValueError('No `{0}` ID supplied and cannot find {0} in '
                         'local environment. Either supply `{0}` keyword '
                         'argument directly or set environmental variable '
                         '${1}.'.format(var, env))

    return user, password


def _get_data_dir(path: str = None) -> str:
    """
    Get `path` to PPMI data directory, searching environment if necessary.

    Will optionally check whether supplied `fnames` are present at `path`

    Parameters
    ----------
    path : str, optional
        Filepath to directory containing PPMI data files. If not specified this
        function will, in order, look (1) for an environmental variable
        $PPMI_PATH and (2) in the current directory. Default: None


    Returns
    -------
    path : str
        Filepath to directory containing PPMI data files

    Raises
    ------
    FileNotFoundError
    """
    # try and find directory in environmental variable "$PPMI_PATH"
    print(path, os.environ['PPMI_PATH'])
    if path is None:
        try:
            path = Path(os.environ['PPMI_PATH']).resolve()
        except KeyError:
            path = Path.cwd().resolve()
    else:
        path = Path(path).resolve()

    return path


def _check_data_exist(path, fname, datetoken=None):
    # check data existence:
    path = _get_data_dir(path)
    if datetoken is not None:
        fname = fname.format(DATETOKEN=datetoken)
        return (path / fname).is_file()
    else:
        fname = fname.format(DATETOKEN="*")
        return any(path.glob(fname))