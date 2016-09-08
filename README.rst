Trackmac
-----------

|PyPI Latest Version|

Trackmac is a command line tool built for OS X users to track their time spent
on every application.It can also track the websites you visited through
Chrome or Safari(will add support for more browers soon) every day.

Screenshot here

.. image:: https://raw.githubusercontent.com/MacLeek/trackmac/master/screen.gif


Quick start
-----------

Installation
~~~~~~~~~~~~

Install **trackmac** using pip:

.. code:: bash

  $ pip install trackmac

or

.. code:: bash

  $ git clone https://github.com/MacLeek/trackmac && cd trackmac && python setup.py install


Note:

If you are using virtual environment, you should use `$VIRTUAL_ENV/bin/tm`
instead of `tm` or simply add it to your environment PATH.

Usage
~~~~~

First, create sqlite database and add .plist to keep trackmac run at startup

.. code:: bash

  $ tm setup

With this command, a dbfile will be created under ~/Library/Application Support/com.macleek.github.trackmac/
and com.macleek.github.trackmac.plist will be added to ~/Library/LaunchAgents/

Now the trackmac will automatically start in the background.

Let's see what we can get via

.. code:: bash

  $ tm list

  	        2016 Sep 07 - 2016 Sep 08
	        ─────────────────────────────
	         终端     01m 29s  █████████████████████ 70.6%
	Google Chrome         34s  ████████ 27.0%
	      PyCharm         03s  █ 2.4%

Web sites tracking

.. code:: bash

  $ tm list web

  	                               2016 Sep 07 - 2016 Sep 08
	                             ─────────────────────────────
	               https://github.com/     55m 35s  ██████████████████████████ 88.3%
	https://raw.githubusercontent.com/     02m 18s  █ 3.7%
	           https://www.google.com/     01m 13s  █ 1.9%
	  http://docutils.sourceforge.net/     01m 02s   1.6%
	         http://stackoverflow.com/         20s   0.5%
	     https://news.ycombinator.com/         15s   0.4%
	             https://www.v2ex.com/         15s   0.4%


To see the data of yesterday, current week or current month, simply add -d, -w or -m respectively.

.. code:: bash

  $ tm list -m

	          2016 Sep 01 - 2016 Sep 08
	        ─────────────────────────────
	Google Chrome     03m 09s  ████████████████████ 65.2%
	         终端     01m 38s  ██████████ 33.8%
	      PyCharm         03s   1.0%

Full options here

+------------------------+------------------------------------+--------------------------------+
|:kbd:`-f, --from TEXT`  |The date from when the report should start.Format:%Y-%m-%d           |
+------------------------+------------------------------------+--------------------------------+
|:kbd:`-t, --to TEXT`    |The date at which the report should stop (inclusive).Format:%Y-%m-%d |
+------------------------+------------------------------------+--------------------------------+
|:kbd:`-w, --week`       |Reports application usage for current week.                          |
+------------------------+------------------------------------+--------------------------------+
|:kbd:`-m, --month`      |Reports application usage for current month                          |
+------------------------+------------------------------------+--------------------------------+
|:kbd:`-d, --day`        |Reports application usage for yesterday.                             |
+------------------------+------------------------------------+--------------------------------+
|:kbd:`-n, --num INT`    |Reports application usage for the provided days.                     |
+------------------------+------------------------------------+--------------------------------+
|:kbd:`-T, --tags`       |Reports application usage group by tags                              |
+------------------------+------------------------------------+--------------------------------+
|:kbd:`-O, --output PATH`|Output json data to the specified file                               |
+------------------------+------------------------------------+--------------------------------+
|:kbd:`--help`           |Show this message and exit.                                          |
+------------------------+------------------------------------+--------------------------------+

If you do not want to track for some applications,just type

.. code:: bash

  $ tm block QQ
  Successfully blocked QQ.

and to remove from block list:

.. code:: bash

  $ tm block -d QQ
  Successfully unblocked QQ.

Trackmac also provides tag command for you which make it more clear to see which aspect your time actually being spent.

.. code:: bash

  $ tm tag -a Playing QQ
  $ tm tag -a Developing PyCharm
  $ tm tag -a Studying Google\ Chrome
  $ tm list -T

  	       2016 Sep 07 - 2016 Sep 08
	     ─────────────────────────────
	  Studying     37m 16s  ██████████████████████████ 88.1%
	    Others     04m 56s  ███ 11.7%
	Developing         03s   0.1%
	   Playing         03s   0.1%


If you want the tracking data to for other uses,
the following command will write the top 20 records
of track data of the current week to data.json in current folder.

.. code:: bash

  $ tm list -w -n 20 -O data.json

.. code-block:: javascript

  [
      {
          "duration":2525,
          "app_name":"Google Chrome"
      },
      {
          "duration":317,
          "app_name":"终端"
      },
      {
          "duration":3,
          "app_name":"PyCharm"
      },
      {
          "duration":3,
          "app_name":"QQ"
      }
  ]


Manually start or stop trackmac,

.. code:: bash

  $ tm start
  trackmac daemon unloaded.
  $ tm stop
  trackmac daemon loaded.


To list all available commands, use

.. code:: bash

  $ tm help

For a specific command help, use like

.. code:: bash

  $ tm help list


Uninstallation
~~~~~~~~~~~~
.. code:: bash

  $ tm drop
  $ pip uninstall trackmac


Known Issues
-----------

When tracking web sites, python rocketship icon will appear in the dock.
This has something to do with using ScripingBridge to track websites.

Possible solutions:
http://stackoverflow.com/questions/30768087/restricted-folder-files-in-os-x-el-capitan


License
-------
MIT

.. |PyPI Latest Version| image:: https://img.shields.io/pypi/v/trackmac.svg