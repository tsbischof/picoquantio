Usage
=====

Installation
------------

To install picoquantio, use pip:

.. code-block:: console

    $ pip install picoquantio

Examples
--------

You can let the loader detect the filetype automatically:

.. code-block:: python

    import picoquantio
    header, data = picoquantio.load('data.ht3')


Or using a specific loader:

.. code-block:: python

   import picoquantio
   header, data = picoquantio.load_cor('test.cor')

