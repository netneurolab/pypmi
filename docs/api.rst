.. _ref_api:

Reference API
=============

This is the primary reference of ``pypmi``. Please refer to the :ref:`user
guide <usage>` for more information on how to best implement these functions in
your own workflows.

.. _ref_fetchers:

:mod:`pypmi.fetchers` - Dataset fetchers
------------------------------------------------------

.. automodule:: pypmi.fetchers
   :no-members:
   :no-inherited-members:

.. currentmodule:: pypmi.fetchers

Functions for listing and downloading datasets from the PPMI database:

.. autosummary::
   :template: function.rst
   :toctree:  generated/

   pypmi.fetchers.fetchable_studydata
   pypmi.fetchers.fetchable_genetics
   pypmi.fetchers.fetch_studydata
   pypmi.fetchers.fetch_genetics