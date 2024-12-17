# -*- coding: utf-8 -*-
"""Code for testing the `pypmi` package."""

import os
import pytest
import requests
from pathlib import Path

from pypmi import fetchers

def test_get_download_params():
    """Test that we can retrieve the authorization key."""

    # confirm we can retrieve authorization key effectively
    session = fetchers._get_auth_session()
    assert isinstance(session, requests.sessions.Session)

    # confirm bad user/password returns NO authorization
    with pytest.raises(ValueError):
        fetchers._get_auth_session('baduser', 'badpass')


def test_fetchable_studydata():
    """Test that we can retrieve the list of available datasets."""
    # 113 datasets available, should get a list of them
    dsets = fetchers.fetchable_studydata()
    assert isinstance(dsets, list) and len(dsets) == 538


@pytest.mark.parametrize(('datasets', 'expected'), [
    (['Code List'], 1),
    (['Current Biospecimen Analysis Results', 'Data Dictionary'], 2)
])
def test_fetch_studydata(datadir, datasets, expected):
    """Test that we can download datasets."""
    out = fetchers.fetch_studydata(
        datasets, 
        path=datadir, 
        overwrite=True, 
        verbose=False
    )
    assert len(out) == expected


def test_fetchable_genetics():
    """Test that we can retrieve the list of available datasets."""
    dsets = fetchers.fetchable_genetics()
    assert isinstance(dsets, list) and len(dsets) == 237


@pytest.mark.parametrize(('datasets', 'expected'), [
    (['Project 272: PPMI Isogenic iPSCs Whole Genome Sequencing'], 1),
    ([
        'Project 272: PPMI Isogenic iPSCs Whole Genome Sequencing',
        'Project 193: Whole Genome Sequencing of iPSC lines'
    ], 2)
])
def test_fetch_genetics(datadir, datasets, expected):
    """Test that we can download datasets."""
    out = fetchers.fetch_genetics(
        datasets,
        path=datadir,
        overwrite=True,
        verbose=False
    )
    assert len(out) == expected
    assert all([f.is_file() for f in out])
