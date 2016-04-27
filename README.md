# sentrycli
CLI scripts to query and analyze data gathered by [Sentry].

### Installation
```
> pip install -U sentrycli
```
### Usage
It's a two-step process. First issue's events need to be downloaded:
```
> sentrycli query 78502 --api-key API_KEY --host http://errors.services.ams.osa
INFO:requests.packages.urllib3.connectionpool:Starting new HTTP connection (1): errors.services.ams.osa
INFO:sentrycli.query:API key is fine
INFO:sentrycli.query:Getting events for issue 78502 (may take a while)
INFO:requests.packages.urllib3.connectionpool:Starting new HTTP connection (1): errors.services.ams.osa
INFO:requests.packages.urllib3.connectionpool:Starting new HTTP connection (1): errors.services.ams.osa
INFO:sentrycli.query:200 events saved to /Users/mlowicki/projects/sentrycli_sandbox/78502.json

> sentrycli query 78502 --api-key API_KEY --host http://errors.services.ams.osa --since 2016-04-19T10:16:58+00:00
INFO:requests.packages.urllib3.connectionpool:Starting new HTTP connection (1): errors.services.ams.osa
INFO:sentrycli.query:API key is fine
INFO:sentrycli.query:Getting events for issue 78502 (may take a while)
INFO:requests.packages.urllib3.connectionpool:Starting new HTTP connection (1): errors.services.ams.osa
INFO:sentrycli.query:44 events saved to /Users/mlowicki/projects/sentrycli_sandbox/78502.json
```
By default events are stored in JSON file in the current working directory.

API keys are reachable through Sentry's UI - http://HOSTNAME/organizations/ORGANIZATION/api-keys/.

If API key or host aren't specified then last used ones (saved in ~/.sentrycli) will be utilized.

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

> sentrycli group 77268.json --header User-Agent Host --tag logger

+-----------------------------------------------------------------------------------------------------------------------+----------------+---------------------+-------+-------+
| User-Agent                                                                                                            | Host           | logger              | count |     % |
+-----------------------------------------------------------------------------------------------------------------------+----------------+---------------------+-------+-------+
| Opera ANDROID-PHONE 14.0.2065.100298 (Opera Mini Opera Mini/14.0.2065.100298/48.0.2564.22 (Android 5.1)) channel(dev) | sync.opera.com | sync.api.middleware |   232 | 100.0 |
+-----------------------------------------------------------------------------------------------------------------------+----------------+---------------------+-------+-------+

> sentrycli group 77268.json --ctime daily
+------------+-------+------+
|    day     | count |    % |
+------------+-------+------+
| 2016-04-09 |    25 | 10.8 |
| 2016-04-10 |    27 | 11.6 |
| 2016-04-11 |    14 |  6.0 |
| 2016-04-12 |     8 |  3.4 |
| 2016-04-13 |    11 |  4.7 |
| 2016-04-14 |    12 |  5.2 |
| 2016-04-15 |    18 |  7.8 |
| 2016-04-16 |    28 | 12.1 |
| 2016-04-17 |    23 |  9.9 |
| 2016-04-18 |     4 |  1.7 |
| 2016-04-19 |    15 |  6.5 |
| 2016-04-20 |    16 |  6.9 |
| 2016-04-21 |    12 |  5.2 |
| 2016-04-22 |    19 |  8.2 |
+------------+-------+------+
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
