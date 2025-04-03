.. goit-pythonweb-hw-12 documentation master file, created by
   sphinx-quickstart on Thu Apr  3 21:19:54 2025.

You can adapt this file completely to your liking, but it should at least
contain the root `toctree` directive.

goit-pythonweb-hw-12 documentation
===================================

Add your content using ``reStructuredText`` syntax. See the
`reStructuredText <https://www.sphinx-doc.org/en/master/usage/restructuredtext/index.html>`_
documentation for details.

.. toctree::
   :maxdepth: 2
   :caption: Contents:


REST API main
===================
.. automodule:: main
  :members:
  :undoc-members:
  :show-inheritance:


REST API Config
===================
.. automodule:: src.conf.config
  :members:
  :undoc-members:
  :show-inheritance:


REST API Database
====================
.. automodule:: src.database.db
  :members:
  :undoc-members:
  :show-inheritance:


REST API Models
====================================
.. automodule:: src.entity.models
  :members:
  :undoc-members:
  :show-inheritance:


REST router Contacts
=================================
.. automodule:: src.routes.contacts
  :members:
  :undoc-members:
  :show-inheritance:


REST router Auth
==============================
.. automodule:: src.routes.auth
  :members:
  :undoc-members:
  :show-inheritance:


REST router Users
================================
.. automodule:: src.routes.users
  :members:
  :undoc-members:
  :show-inheritance:


REST repository Base
========================================
.. automodule:: src.repositories.base
  :members:
  :undoc-members:
  :show-inheritance:


REST repository Contacts
========================================
.. automodule:: src.repositories.contacts_repository
  :members:
  :undoc-members:
  :show-inheritance:


REST repository Users password reset
======================================
.. automodule:: src.repositories.password_reset_repository
  :members:
  :undoc-members:
  :show-inheritance:


REST repository User refresh token
========================================
.. automodule:: src.repositories.refresh_token_repository
  :members:
  :undoc-members:
  :show-inheritance:


REST repository Users
======================================
.. automodule:: src.repositories.user_repository
  :members:
  :undoc-members:
  :show-inheritance:



REST Service Auth
=======================================
.. automodule:: src.services.auth
  :members:
  :undoc-members:
  :show-inheritance:


REST Service Contacts
=======================================
.. automodule:: src.services.contacts
  :members:
  :undoc-members:
  :show-inheritance:


REST Service Email
=======================================
.. automodule:: src.services.email
  :members:
  :undoc-members:
  :show-inheritance:


REST Service Users
====================================
.. automodule:: src.services.user
  :members:
  :undoc-members:
  :show-inheritance:


REST Password reset
==========================================
.. automodule:: src.services.password_reset
  :members:
  :undoc-members:
  :show-inheritance:


REST Upload file service
==========================================
.. automodule:: src.services.upload_file_service
  :members:
  :undoc-members:
  :show-inheritance:


.. _orm_declarative_metadata:

ORM Declarative Metadata
========================

SQLAlchemy підтримує декларативне створення моделей з використанням базових класів.
Докладніше читайте у [документації SQLAlchemy](https://docs.sqlalchemy.org/en/20/orm/mapping_styles.html#orm-declarative-mapping).



Indices and tables
====================

* :ref:genindex
* :ref:modindex
* :ref:searcharch`