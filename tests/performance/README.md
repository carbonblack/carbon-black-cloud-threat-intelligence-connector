# Performance Test
The tests in the performance directory are unit tests that are long-running tests, that should be run only upon merging in main branch to verify that everything is working correctly.

# Run the performance tests



## Installation

```shell
$ virtualenv venv
$ source ./venv/bin/activate
(venv) $ pip install -r requirements.txt
```

## Usage

The first argument represents the number of Indicators/Observables that are going to be created and processed by the connector.

### STIX 1

Since that the parser are using two different methods to parse Indicators and Observables we use two different files.

```shell
$ time python performance_test_stix1_indicators.py 100000
```

```shell
$ time python performance_test_stix1_observables.py 100000
```

## STIX 2

```shell
$ time python performance_test_stix2.py 100000
```
