===================
Framework Utilities
===================

Supporting systems for advanced usage and development tooling.

Model Factory
=============

Multi-provider LLM model management for structured generation and direct completions.

.. currentmodule:: framework.models

.. autofunction:: get_model
   :no-index:

.. autofunction:: get_chat_completion
   :no-index:

Developer Tools
===============

Component logging and streaming utilities for framework development.

Logging System
--------------

.. currentmodule:: configs.logger

.. autofunction:: get_logger
   :no-index:

.. autoclass:: ComponentLogger
   :members:
   :show-inheritance:
   :no-index:

Streaming System
----------------

.. currentmodule:: configs.streaming

.. autofunction:: get_streamer
   :no-index:

.. autoclass:: StreamWriter
   :members:
   :show-inheritance:
   :no-index:

.. seealso::

   :doc:`../../developer-guides/01_understanding-the-framework/04_orchestrator-first-philosophy`
       Development utilities integration patterns and configuration conventions