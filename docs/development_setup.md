Testing
=======
```
pip install pytest-cov
pytest --cov-report term:skip-covered --cov-report term-missing --cov src/didery --ignore src/didery/static/ tests/ -v
```