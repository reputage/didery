Setup
=====

First we need to install all the projects dependencies. 1. Node.js and
NPM ``bash     sudo apt update     sudo apt install nodejs npm``

2. NPM Install

   .. code:: bash

       cd /didery/src/didery/static/
       npm install

3. Minify JavaScript Code

   .. code:: bash

       npm run webpack

Running the server
==================

1. Start the server with this command

   .. code:: bash

       didery

   For more options see the
   `docs </docs/getting_started/getting_started.rst>`__

2. Navigate to Didery's frontend

   ::

       localhost:8080/
