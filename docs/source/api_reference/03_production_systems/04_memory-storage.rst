==============
Memory Storage
==============

User memory infrastructure with persistent storage, data source integration, and structured memory operations.

.. note::
   For implementation guides and examples, see :doc:`../../../developer-guides/05_production-systems/04_memory-storage-service`.

.. currentmodule:: framework.services.memory_storage

Core Components
===============

.. autosummary::
   :toctree: _autosummary
   
   MemoryStorageManager
   UserMemoryProvider
   MemoryContent
   get_memory_storage_manager

Storage Management
==================

.. autoclass:: MemoryStorageManager
   :members:
   :show-inheritance:

Data Source Integration
=======================

.. autoclass:: UserMemoryProvider
   :members:
   :show-inheritance:

Data Models
===========

.. autoclass:: MemoryContent
   :members:
   :show-inheritance:

Utility Functions
=================

.. autofunction:: get_memory_storage_manager

.. seealso::

   :doc:`../../../developer-guides/05_production-systems/04_memory-storage-service`
       Complete implementation guide and examples
   
   :class:`framework.data_management.DataSourceProvider`
       Base provider interface implemented by UserMemoryProvider