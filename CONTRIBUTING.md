# Contributing and Development Guidelines

## License

PyTrackDat is licensed under the GPL version 3. By contributing to the project,
you agree to license your contributed code under the same license.

## Code Style

PyTrackDat uses the [PEP-8](https://www.python.org/dev/peps/pep-0008/) style
guide.

## Release Checklist

 - [ ] Check that `pytrackdat`'s `analyze`, `test`, and `django-manage` 
       entrypoints work  correctly on Windows, Mac, and Linux.
 - [ ] Make sure all changes are in the changelog and any relevant
       documentation is added / updated.
 - [ ] Bump the version number in `pytrackdat/common.py`
   - If necessary, update the copyright dates.
 - [ ] Bump the version number in `setup.py`
 - [ ] Publish a release to the **test** PyPI repository.
 - [ ] Confirm the release works in a virtual environment on Windows, Mac, and Linux.
 - [ ] Publish a release to PyPI.
