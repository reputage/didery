# Versions
Use Semantic versioning as described [here](https://semver.org/) when releasing any new code.  There are two files that need to be updated with the new version number:
```bash
didery/src/didery/__init_.py
didery/setup.py
```

# Building Wheels
Make sure you have installed the packaging dependencies
```bash
pip install wheel
pip install twine
sudo apt install npm
```

Then run these commands
```bash
cd /path/to/didery/src/didery/static/
npm install
npm run-script transcrypt

cd path/to/didery/
python3 setup.py sdist bdist_wheel
```

# Uploading to Pypi

## Test
```bash
twine upload --repository-url https://test.pypi.org/legacy/ dist/*
pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple didery
```

## Live
```bash
twine upload dist/*
```
I've run into issues with twine either giving an error about not expecting a bytes like object.  This happens if you've installed twine via apt because it's an older version. You need twine >= 1.11.0. Uninstall it with apt and use this:
```bash
pip install twine
python -m twine upload dist/*
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