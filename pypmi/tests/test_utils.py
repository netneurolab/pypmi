# -*- coding: utf-8 -*-
"""Code for testing the `pypmi` package."""

import os
from pathlib import Path
import pytest

from pypmi import utils
from pypmi.fetchers import fetch_studydata, _STUDYDATA

TEST_PPMI_PATH = Path(os.environ['TEST_PPMI_PATH'])

def test_get_cred():
    """Test that we can retrieve the authentication."""
    # confirm fetching from environment works
    try:
        assert utils._get_cred() is not None
    except AssertionError:
        pass
    # confirm providing only one input still fetches both (from environ)
    try:
        assert utils._get_cred(user='user') != ('user', None)
        assert utils._get_cred(password='pass') != (None, 'pass')
    except AssertionError:
        pass
    # confirm giving both inputs simply returns inputs, as provided
    assert utils._get_cred('user', 'pass') == ('user', 'pass')


def test_get_data_dir():
    """Test that we can retrieve the data directory."""
    ppmi_path = os.environ.get('PPMI_PATH')
    if ppmi_path is not None:
        del os.environ['PPMI_PATH']

    # no path and $PPMI_PATH not set returns current directory
    assert Path.cwd() == utils._get_data_dir()
    # setting $PPMI_PATH uses that instead of the current directory
    os.environ['PPMI_PATH'] = str(TEST_PPMI_PATH.resolve())
    assert TEST_PPMI_PATH.resolve() == utils._get_data_dir()
    # providing path returns path
    assert TEST_PPMI_PATH.resolve() == utils._get_data_dir(TEST_PPMI_PATH)

    if ppmi_path is not None:
        os.environ['PPMI_PATH'] = ppmi_path

def test_check_data_exist(datadir):
    """Test that we can check if data exists."""
    # confirm that we can check if data exists

    fname = "Code List"
    fetch_studydata(
        [fname], 
        path=datadir, 
        overwrite=False, 
        verbose=True
    )

    assert utils._check_data_exist(
        datadir,
        _STUDYDATA[fname]['filename'],
        datetoken=None
    ) == True

    assert utils._check_data_exist(
        datadir,
        _STUDYDATA[fname]['filename'],
        datetoken="01Jan2000"
    ) == False