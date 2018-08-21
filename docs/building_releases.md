# Building Wheels
Make sure you have installed wheel with apt then run the commands below
```bash
cd path/to/didery/
python3 setup.py sdist bdist_wheel
```

# Uploading to Pypi
```bash
twine upload dist/*
```

# Github
After uploading to Pypi make sure to add the release to GitHub by following the instructions [here](https://help.github.com/articles/creating-releases/)

# Documentation
The documentation is written in markdown files, and converted to restructured 
text format using pandocs.  Committing the changes will automatically upload the 
new docs to read the docs.  Use the following command to convert the .md files to .rst:

```bash
cd path/to/docs/
pandoc --from=markdown --to=rst --output=public_api.rst public_api.md
```