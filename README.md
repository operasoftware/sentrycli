# sentrycli
CLI scripts to query and analyze data gathered by [Sentry].

### Usage
It's a two-step process. First issue's events need to be downloaded:
```
> sentrycli query API_KEY 78502 http://errors.services.ams.osa
INFO:requests.packages.urllib3.connectionpool:Starting new HTTP connection (1): errors.services.ams.osa
INFO:sentrycli.query:API key is fine
INFO:sentrycli.query:Getting events for issue 78502 (may take a while)
INFO:requests.packages.urllib3.connectionpool:Starting new HTTP connection (1): errors.services.ams.osa
INFO:requests.packages.urllib3.connectionpool:Starting new HTTP connection (1): errors.services.ams.osa
INFO:sentrycli.query:200 events saved to /Users/mlowicki/projects/sentrycli_sandbox/78502.json

> sentrycli query API_KEY 78502 http://errors.services.ams.osa --since 2016-04-19T10:16:58+00:00
INFO:requests.packages.urllib3.connectionpool:Starting new HTTP connection (1): errors.services.ams.osa
INFO:sentrycli.query:API key is fine
INFO:sentrycli.query:Getting events for issue 78502 (may take a while)
INFO:requests.packages.urllib3.connectionpool:Starting new HTTP connection (1): errors.services.ams.osa
INFO:sentrycli.query:44 events saved to /Users/mlowicki/projects/sentrycli_sandbox/78502.json
```
By default events are stored in JSON file in the current working directory.

API keys are reachable through Sentry's UI - http://HOSTNAME/organizations/ORGANIZATION/api-keys/.

When events are ready we can start analyzing them:
```
> sentrycli group 78502.json --tags server_name

+----------------------+-------+------+
| server_name          | count |    % |
+----------------------+-------+------+
| front2.sync.ams.osa  |    20 | 45.5 |
| front6.sync.lati.osa |    19 | 43.2 |
| front6.sync.ams.osa  |     4 |  9.1 |
| front5.sync.lati.osa |     1 |  2.3 |
+----------------------+-------+------+
Total: 44

> sentrycli group 78502.json --headers Content-Type

+--------------------------+-------+-------+
| Content-Type             | count |     % |
+--------------------------+-------+-------+
| application/octet-stream |    44 | 100.0 |
+--------------------------+-------+-------+
Total: 44

> sentrycli group 78502.json --tags server_name release

+---------+----------------------+-------+------+
| release | server_name          | count |    % |
+---------+----------------------+-------+------+
| 5d74084 | front2.sync.ams.osa  |    20 | 45.5 |
| 5d74084 | front6.sync.lati.osa |    19 | 43.2 |
| 5d74084 | front6.sync.ams.osa  |     4 |  9.1 |
| 5d74084 | front5.sync.lati.osa |     1 |  2.3 |
+---------+----------------------+-------+------+
```

To get list of avaialble grouping options use `--options` switch:
```
> sentrycli group 76342.json --options
+-------------------+-------------+--------+-------------------+-------------+
| Headers           | Extras      | Params | Vars              | Tags        |
+-------------------+-------------+--------+-------------------+-------------+
| Accept-Encoding   | filename    |        | args              | browser     |
| Accept-Language   | lineno      |        | auth_header       | device      |
| Authorization     | pathname    |        | bound_func        | level       |
| Cache-Control     | process     |        | callback          | logger      |
| Connection        | processName |        | callback_args     | os          |
| Content-Length    | request     |        | callback_kwargs   | release     |
| Content-Type      | sys.argv    |        | circuitbreaker    | server_name |
...
```

[sentry]: <https://github.com/getsentry/sentry>
