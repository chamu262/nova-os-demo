# `.github/`: CI

`workflows/ci.yml` runs the test suite (`python -m unittest -v`) on every push and pull request, on Python 3.10 and 3.13. No secrets are needed because the tests never call the real API.
