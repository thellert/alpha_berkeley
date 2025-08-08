===============
Data Management
===============

Data orchestration framework for integrating heterogeneous data sources into agent workflows with provider discovery, concurrent retrieval, and LLM-optimized formatting.

.. note::
   For implementation guides and examples, see :doc:`../../../developer-guides/05_production-systems/02_data-source-integration`.

.. currentmodule:: framework.data_management

Core Components
===============

.. autosummary::
   :toctree: _autosummary
   
   DataSourceManager
   DataRetrievalResult
   DataSourceProvider
   DataSourceContext
   DataSourceRequest
   DataSourceRequester
   get_data_source_manager
   create_data_source_request

Management Classes
==================

.. autoclass:: DataSourceManager
   :members:
   :show-inheritance:

.. autoclass:: DataRetrievalResult
   :members:
   :show-inheritance:

Provider Interfaces
===================

.. autoclass:: DataSourceProvider
   :members:
   :show-inheritance:

.. autoclass:: DataSourceContext
   :members:
   :show-inheritance:

Request Models
==============

.. autoclass:: DataSourceRequest
   :members:
   :show-inheritance:

.. autoclass:: DataSourceRequester
   :members:
   :show-inheritance:

Utility Functions
=================

.. autofunction:: get_data_source_manager

.. autofunction:: create_data_source_request

.. seealso::

   :doc:`../../../developer-guides/05_production-systems/02_data-source-integration`
       Complete implementation guide and examples
   
   :class:`framework.services.memory_storage.UserMemoryProvider`
       Example core data source provider implementation