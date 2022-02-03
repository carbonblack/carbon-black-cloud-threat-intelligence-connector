# Performance Test
The tests in the performance directory are unit tests that are long-running tests, that should be run only upon merging in main branch to verify that everything is working correctly.

## How to run the tests

### To run all tests
``pytest`` or ``coverage run -m pytest``

### To exclude long-running tests
``pytest tests/unit`` or ``coverage run -m pytest tests/unit``
