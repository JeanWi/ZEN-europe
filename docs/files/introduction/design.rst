.. _design.design:

###########################
Design Ideas
###########################

ZEN-europe generates the input data of a European, sector-coupled energy system
model for `ZEN-garden <https://zen-garden.readthedocs.io/en/latest/>`_. It is
built on `ZEN-creator <https://zen-creator.readthedocs.io/en/latest/>`_, which
provides the generic building blocks (model, elements, attributes, datasets,
settings, scenarios). ZEN-europe implements these building blocks for a European
sector-coupled energy system to model the transition to a low-carbon economy.


The two packages
================

.. list-table::
   :header-rows: 1
   :widths: 20 40 40

   * -
     - ZEN-creator
     - ZEN-europe
   * - Role
     - Generic library. Knows the structure of a ZEN-garden input folder, but
       no data.
     - Project. Knows Europe: its nodes, sectors, technologies, carriers and
       data sources.
   * - Contains
     - Abstract classes (``Element``, ``Dataset``, ``DatasetCollection``,
       ``SettingsCategory``, ``Sector``), the ``Model``, validation,
       scenario handling and the writer.
     - Concrete subclasses of these classes, the settings categories, the
       default ``zen_europe_config.yaml`` and the command line interface.
   * - Reused by
     - Any project that builds ZEN-garden input data.
     - Users who want the base European dataset, or a variant of it.

A new project (for example a national model) can reuse ZEN-creator in the
same way, and can import individual elements or datasets from ZEN-europe.


Core ideas
==========

The design of ZEN-europe follows the ideas of ZEN-creator, which are described
together with a comparison to manual scripts and Snakemake in the
`ZEN-creator documentation
<https://zen-creator.readthedocs.io/en/latest/files/quick_start/design.html>`_.
In short:

- every carrier and technology is a class, and every attribute has one
  ``_set_<attribute>()`` method that decides where its value comes from
- every data source is a ``Dataset`` of its own, and sources are combined in a
  ``DatasetCollection``
- every value carries its source or assumption, written to ``sources.md``
- attributes that depend on other attributes are built on demand
- datasets are loaded once per process
- all choices are typed settings, and variants are sparse patches of them
- the model is validated before it is written

ZEN-europe adds the following on top:

- **Cached downloads.** Sources that are downloaded from an API (Eurostat,
  ENTSO-E, World Bank, ECB, ...) are stored as files in the raw data folder
  and only downloaded again when the matching ``cache.overwrite_*`` setting
  is set.
- **Parallel variants.** ``zen-europe --all`` generates every variant of
  ``models.yaml``, each in its own process (see :ref:`execution.execution`).
- **Common schemas.** Sources that report the same kind of data, such as the
  technology cost databases, return the same format, so that one collection
  combines them without source-specific code.
- **Conventions.** The rules for adding elements, datasets and settings are
  described in :ref:`extending.extending`.
