# -*- coding: utf-8 -*-
"""Code for testing the `pypmi` package."""

import pytest

from pypmi import fetchers


@pytest.mark.parametrize('url', [
    "https://utilities.loni.usc.edu/download/study",
    "https://utilities.loni.usc.edu/download/genetic"
])
def test_get_download_params(url):
    """Test that we can retrieve the authorization key."""
    # confirm we can retrieve authorization key effectively
    params = fetchers._get_download_params(url)
    assert isinstance(params, dict)
    try:
        assert all(f in params.keys() for f in ['authKey', 'userId'])
    except AssertionError:
        pass

    # confirm bad user/password returns NO authorization
    assert fetchers._get_download_params(url, 'baduser', 'badpass') is None

    # invalid URL raises error
    with pytest.raises(ValueError):
        fetchers._get_download_params('invalidurl')


def test_fetchable_studydata():
    """Test that we can retrieve the list of available datasets."""
    # 113 datasets available, should get a list of them
    dsets = fetchers.fetchable_studydata()
    assert isinstance(dsets, list) and len(dsets) == 113


@pytest.mark.parametrize(('datasets', 'expected'), [
    (['all'], 113),
    (['Code list', 'Clinical labs'], 2)
])
def test_fetch_studydata(studydata, datasets, expected):
    """Test that we can download datasets."""
    # ensure dataset download returns expected number of files
    out = fetchers.fetch_studydata(*datasets, path=studydata, verbose=False)
    assert len(out) == expected


def test_fetchable_genetics():
    """Test that we can retrieve the list of available datasets."""
    # 199 datasets available, should get a list of them
    dsets = fetchers.fetchable_genetics()
    assert isinstance(dsets, list) and len(dsets) == 199

    # requesting projects will return a shorter list
    projects = fetchers.fetchable_genetics(projects=True)
    assert isinstance(projects, list) and len(projects) == 7


@pytest.mark.parametrize(('datasets', 'expected'), [
    (['project 108'], 2)
])
def test_fetch_genetics(studydata, datasets, expected):
    """Test that we can download datasets."""
    out = fetchers.fetch_genetics(*datasets, path=studydata, verbose=False)
    assert len(out) == expected
