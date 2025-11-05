## Upgrading to azure-monitor-opentelemetry==1.4.0

Traceback of the packaged application running using azure-monitor-opentelemetry==1.4.0
```
Traceback (most recent call last):
  File "run.py", line 4, in <module>
    autoscription_main.run()
  File "C:\Users\D4md1\project\selenium\dist\autoscription_main\autoscription_main.py", line 79, in run
  File "C:\Users\D4md1\project\selenium\dist\autoscription_main\src\autoscription\core\logging.py", line 54, in config_azure_monitor
  File "C:\Users\D4md1\project\selenium\dist\autoscription_main\azure\monitor\opentelemetry\_configure.py", line 79, in configure_azure_monitor
    configurations = _get_configurations(**kwargs)
  File "C:\Users\D4md1\project\selenium\dist\autoscription_main\azure\monitor\opentelemetry\_util\configurations.py", line 67, in _get_configurations
    _default_resource(configurations)
  File "C:\Users\D4md1\project\selenium\dist\autoscription_main\azure\monitor\opentelemetry\_util\configurations.py", line 109, in _default_resource
    configurations[RESOURCE_ARG] = Resource.create()
  File "opentelemetry\sdk\resources\__init__.py", line 185, in create
StopIteration
```


### ISSUE - Nuitka fails to transpile opentelemetry
- relevant issue on nuitka github https://github.com/Nuitka/Nuitka/issues/2014
	- tried to `--include-distribution-metadata=opentelemetry`
- same issue on opentelemetry github
	https://github.com/open-telemetry/opentelemetry-python/issues/3153

### Experiment - include opentelemetry as data during packaging

```
Traceback (most recent call last):
  File "C:\Users\D4md1\project\selenium\dist\autoscription_main\opentelemetry\propagate\__init__.py", line 138, in <module>
    next(  # type: ignore
StopIteration

During handling of the above exception, another exception occurred:
Traceback (most recent call last):
  File "run.py", line 1, in <module>
    import autoscription_main
  File "C:\Users\D4md1\project\selenium\dist\autoscription_main\autoscription_main.py", line 13, in <module autoscription_main>
  File "<frozen importlib._bootstrap>", line 991, in _find_and_load
  File "<frozen importlib._bootstrap>", line 975, in _find_and_load_unlocked
  File "<frozen importlib._bootstrap>", line 671, in _load_unlocked
  File "C:\Users\D4md1\project\selenium\dist\autoscription_main\src\autoscription\core\logging.py", line 7, in <module src.autoscription.core.logging>
  File "C:\Users\D4md1\project\selenium\dist\autoscription_main\azure\monitor\opentelemetry\__init__.py", line 7, in <module>
    from azure.monitor.opentelemetry._configure import configure_azure_monitor
  File "C:\Users\D4md1\project\selenium\dist\autoscription_main\azure\monitor\opentelemetry\_configure.py", line 28, in <module>
    from azure.core.tracing.ext.opentelemetry_span import OpenTelemetrySpan
  File "C:\Users\D4md1\project\selenium\dist\autoscription_main\azure\core\tracing\ext\opentelemetry_span\__init__.py", line 17, in <module>
    from opentelemetry.propagate import extract, inject  # type: ignore[attr-defined]
  File "C:\Users\D4md1\project\selenium\dist\autoscription_main\opentelemetry\propagate\__init__.py", line 148, in <module>
    raise ValueError(
ValueError: Propagator tracecontext not found. It is either misspelled or not installed.
```
### Experiment - Adding the following as hidden imports failed as the above
```
  'opentelemetry.trace.propagation.tracecontext',
  'opentelemetry.baggage.propagation'
```

### Rolling back to azure-monitor-opentelemetry==1.0.0b13


### Thoughts moving forward:
Try to exclude **opentelemetry** follow path using the suggestion provided and included as data only,
that way it will run as python
[here](https://github.com/Nuitka/Nuitka/issues/486)

`--nofollow-import-to=*.tests`
