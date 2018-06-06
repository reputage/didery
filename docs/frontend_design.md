Didery Frontent Project Specification

2018/05/22

# 1. Overview
The  didery frontend provides an administrator interface for didery backend services.

### 1.1. File Structure
```
static/
|––– css/
|    '--- dashboard.css
|
|--- fonts/
|    '--- Raleway/
|         |--- OFL.txt
|         |--- Raleway-Black.ttf
|         |--- Raleway-BlackItalic.ttf
|         |--- Raleway-Bold.ttf
|         |--- Raleway-BoldItalic.ttf
|         |--- Raleway-ExtraBold.ttf
|         |--- Raleway-ExtraBoldItalic.ttf
|         |--- Raleway-ExtraLight.ttf
|         |--- Raleway-ExtraLightItalic.ttf
|         |--- Raleway-Italic.ttf
|         |--- Raleway-Light.ttf
|         |--- Raleway-LightItalic.ttf
|         |--- Raleway-Medium.ttf
|         |--- Raleway-MediumItalic.ttf
|         |--- Raleway-Regular.ttf
|         |--- Raleway-SemiBold.ttf
|         |--- Raleway-SemiBoldItalic.ttf
|         |--- Raleway-Thin.ttf
|         '--- Raleway-ThinItalic.ttf
|
|--- images/
|    |--- logo.png
|    '--- logo-extended.png
|
|--- (node_modules/)
|
|--- tests/
|    |--- (__javascript__/)
|    |--- __init__.py
|    |--- runt_tests.py
|    |--- test_components.py
|    |--- test_server.py
|    '--- tester.py
|
|--- transcrypt/
|    |--- (__javascript__/)
|    |--- components/
|    |    |--- (__javascript__/)
|    |    |--- __init__.py
|    |    |--- fields.py
|    |    |--- searcher.py
|    |    |--- tab.py
|    |    |--- tabledtab.py
|    |    |--- tables.py
|    |    '--- tabs.py
|    |
|    |--- __init__.py
|    |--- dashboard.py
|    |--- main.py
|    |--- router.py
|    '--- server.py
|
|--- __init__.py
|--- clean_tests.py
|--- favicon.ico
|--- main.html
|--- package.json
'--- package-lock.json
```

The didery frontend is located exclusively within the static folder (didery/src/didery/static/). On server launch, 
main.html is loaded into the browser. main.html imports javascript compiled from transcrypt files in the transcrypt 
folder. This compiled javascript uses Mithril.js to render the actual document. Frontend styling comes from the 
dashboard.css file in the css folder. Fonts used in the interface are saved in the fonts folder. Static images used on
the frontend are stored in the images folder. The package.json file contains Node.js scripts and dependencies. Once 
these dependencies are installed, they can be found in the node_modules folder. The tests folder contains transcrypt 
files that can be compiled into javascript unit tests. The clean_tests.py file is used to remove extra generated files.

### 1.2. Development Language and Environment
The main.html is written in HTML5. Styling uses CSS3. Dependencies are imported and managed using Node.js. Scripts are
also defined and run through Node.js. Components and general functionality is written using Transcrypt (Python). 
Transcrypt files are compiled into ES6 Javascript files. Mithril.js is used to create generated the rendered markup. 
Testing uses the ospec framework.

# 2. Components

### 2.1. Router
The router object simply sets up the url path for the user interface and then renders said interface.

### 2.2. Server
The server object makes needed HTTP calls for the frontend. For each call there is a class with a list to contain 
request data as well as functions to retrieve/refresh data (_refresh*) and parse data (_parseAll). Each separate call 
class is managed by the manager class. The manager class has no other purpose than to aggrigate all of the call classes
into one convenient class for ease of use. Helper functions are included for the server classes to clear data and handle
promises. 

### 2.3. Dashboard
The dashboard is stored in a manager class in the dashboard.py file. Upon instantiation, the manager initializes all of
the different tabs, initializes the search bar, sets up a jquery function for clicking tabs, and retrieves/refreshes tab
data. The dashboard manager has four member functions. The refresh function retrieves fresh data for each of the tabs.
The currentTab function returns the currently active tab. The searchAll function interfaces with the searcher object to 
search data on each of the tab pages. Finally the view function returns the Mithril.js generated HTML markup for the 
dashboard.

### 2.4. TabledTabs
Tabled tabs are basically content containers for a given tab. They setup the table for a tab, as well as the details and
copied boxes. Furthermore, tabled tabs show the number of found and visible entries in a given table (this display is 
found on the tab itself). Member functions set up the table for a given tab, copy details from a selected table row, 
return the number of table rows, return the entries label, clear copied details, and return Mithril.js generated HTML
markup for both the tab itself and its page content. The details box in a tabled tab lets one see the JSON associated
with a table row. The copied box allows one to copy the JSON data from a selected table row. Together the details and
copied boxes allow for the comparison of table rows. Specific tabled tabs are defined in the tabs.py file.


### 2.5. Tabs
Tabs are basically the menu navigation for the dashboard. They appear along the top of the dashboard and can be clicked
to display their associated content (tabled tab). Tabs store the visible name of the tab, the tab icon, the machine name
of the tab (DataTab), and whether or not the tab is currently active. All of the tabs member functions return Mithril.js
generated HTML markup.

### 2.6. Tables
Tables are the real powerhouses of the interface. They display data retrieved from the server and allow for the limited
manipulation of that data. The table class stores retrieved data, the display limit, and sort and filter settings.
Member functions stringify table data, limit displayed results, select row data, refresh table data, clear table data, 
create testing data, set table data, filter displayed results, sort displayed results, return a table field, create a
table row, and return a Mithril.js generated HTML markup for that table. Tables are made up of field objects. These 
fields setup the columns in the table and provide headers for those columns. Rows are created for each entry in a data
set stored in the table. Specific tables are defined in the tables.py file together with the base table class.

### 2.7. Fields
Fields set up the columns in a table. Field member functions format field titles, shorten field titles if necessary, and
return the Mithril.js generated HTML markup for that field. Specific fields are defined in the fields.py file together 
with the base field class.

### 2.8. Searcher
The searcher class provides functionality for the interfaces search bar. The searcher can be set to be case sensitive or
not. Member functions process the search query string, check primitives (such as strings), check data structures (such 
as dictionaries), and returns the result of a search.

# 3. Testing
Testing uses the ospec framework. Unit tests are written in Python. They are compiled into Javascript using Transcrypt.
Excess generated files are removed by the clean_tests.py file. To both compile and clean the frontend tests, an npm 
script can be run using the following commands:
```
$ cd didery/src/didery/static
$ npm run-script prep-tests
```
Once unit tests have been compiled, they can be run by using the following command (still from within the static 
folder):
```
$ npm test
```
Unit tests should always be run prior to launching didery in a production setting. This ensures that everything in the 
project is working properly.
