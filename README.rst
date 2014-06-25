==================
Summary
==================

pyspectator_tornado is a web-monitoring tool ported on Tornado with pyspectator as a main monitoring module.
It's able to collect and display general information about workstation, cpu, memory, disk devices and network.


==================
Screenshots
==================

.. image:: http://uzumaxy.tk/static/img/projects/pyspectator_tornado_01_thumb.png
    :target: http://uzumaxy.tk/static/img/projects/pyspectator_tornado_01.png
    :alt: General information

.. image:: http://uzumaxy.tk/static/img/projects/pyspectator_tornado_02_thumb.png
    :target: http://uzumaxy.tk/static/img/projects/pyspectator_tornado_02.png
    :alt: CPU

.. image:: http://uzumaxy.tk/static/img/projects/pyspectator_tornado_03_thumb.png
    :target: http://uzumaxy.tk/static/img/projects/pyspectator_tornado_03.png
    :alt: Disk devices

.. image:: http://uzumaxy.tk/static/img/projects/pyspectator_tornado_04_thumb.png
    :target: http://uzumaxy.tk/static/img/projects/pyspectator_tornado_04.png
    :alt: Network


==================
Requirements
==================

- OS: Linux, Windows, FreeBSD, Solaris
- Python version: 3.X
- Packages: pyspectator, tornado


==================
How to install
==================

Run as root user:

.. code-block:: bash

    pip install pyspectator_tornado


==================
How to use
==================

To start working with pyspectator_tornado system you must execute file "start.py" in a root directory of project.

Most simple method, where pyspectator_tornado will be binded on port "8888" and available by address: "localhost:8888":

.. code-block:: bash

    python start.py


If you want use simple address "localhost" or
port "8888" is busy by another application, you specify custom port, for example:

.. code-block:: bash

    python start.py --port=80
    # now pyspectator_tornado is available by address "localhost"


Also you can bind site with some domain name:

.. code-block:: bash

    python start.py --port=80 --address=your-domain-name.com
    # now pyspectator_tornado is available by next addresses:
    # "localhost" and "your-domain-name.com"
