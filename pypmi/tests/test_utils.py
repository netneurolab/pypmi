# -*- coding: utf-8 -*-
"""Code for testing the `pypmi` package."""

import os
import pytest

from pypmi import utils


def test_get_authentication():
    """Test that we can retrieve the authentication."""
    # confirm fetching from environment works
    try:
        assert utils._get_authentication() is not None
    except AssertionError:
        pass
    # confirm providing only one input still fetches both (from environ)
    try:
        assert utils._get_authentication(user='user') != ('user', None)
        assert utils._get_authentication(password='pass') != (None, 'pass')
    except AssertionError:
        pass
    # confirm giving both inputs simply returns inputs, as provided
    assert utils._get_authentication('user', 'pass') == ('user', 'pass')


def test_get_data_dir(studydata):
    """Test that we can retrieve the data directory."""
    ppmi_path = os.environ.get('PPMI_PATH')
    if ppmi_path is not None:
        del os.environ['PPMI_PATH']

    # no path and $PPMI_PATH not set returns current directory
    assert os.getcwd() == utils._get_data_dir()
    # setting $PPMI_PATH uses that instead of the current directory
    os.environ['PPMI_PATH'] = str(studydata)
    assert str(studydata) == utils._get_data_dir()
    # providing path returns path
    assert studydata == utils._get_data_dir(studydata)
    # providing filename that exists at path provides path
    assert studydata == utils._get_data_dir(studydata,
                                            ['AV-133_Image_Metadata.csv'])
    # providing filename that does not exist at path raises error
    with pytest.raises(FileNotFoundError):
        utils._get_data_dir(studydata, fnames=['notafile.csv'])

    if ppmi_path is not None:
        os.environ['PPMI_PATH'] = ppmi_path
