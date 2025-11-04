===================
Framework Utilities
===================

Supporting systems for advanced usage and development tooling.

.. currentmodule:: osprey

Core Components
===============

.. autosummary::
   :toctree: _autosummary

   models.get_model
   models.get_chat_completion

.. currentmodule:: osprey.utils

.. autosummary::
   :toctree: _autosummary

   logger.get_logger
   logger.ComponentLogger
   streaming.get_streamer
   streaming.StreamWriter

Model Factory
=============

Multi-provider LLM model management for structured generation and direct completions.

.. currentmodule:: osprey.models

.. autofunction:: get_model

.. autofunction:: get_chat_completion

Developer Tools
===============

Component logging and streaming utilities for framework development.

Logging System
--------------

.. currentmodule:: osprey.utils.logger

.. autofunction:: get_logger

.. autoclass:: ComponentLogger
   :members:
   :show-inheritance:

Streaming System
----------------

.. currentmodule:: osprey.utils.streaming

.. autofunction:: get_streamer

.. autoclass:: StreamWriter
   :members:
   :show-inheritance:

.. seealso::

   :doc:`../../developer-guides/01_understanding-the-framework/04_orchestrator-first-philosophy`
       Development utilities integration patterns and configuration conventions