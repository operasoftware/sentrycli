# sentrycli
CLI tools to query and analyze data gathered by [Sentry]. Introduction to `sentrycli` as guest post on [blog.getsentry.com](https://blog.getsentry.com/2016/06/21/sentry-at-opera.html).

### Installation
Install [pip](https://pip.pypa.io/en/stable/installing/) and run:
```
> pip install -U sentrycli
```
The same command is used to upgrade to the latest version.

### Usage

First we need to get issue's identifier which is part of the URL:

![Sentry issue's identifier](https://github.com/operasoftware/sentrycli/blob/master/issue_id.png)


Then it's a two-step process. First issue's events need to be downloaded:
```
> sentrycli query 78502 --api-key API_KEY --host http://errors.services.ams.osa
INFO:requests.packages.urllib3.connectionpool:Starting new HTTP connection (1): errors.services.ams.osa
INFO:sentrycli.query:API key is fine
INFO:sentrycli.query:Getting events for issue 78502 (may take a while)
INFO:requests.packages.urllib3.connectionpool:Starting new HTTP connection (1): errors.services.ams.osa
INFO:requests.packages.urllib3.connectionpool:Starting new HTTP connection (1): errors.services.ams.osa
INFO:sentrycli.query:200 events saved to /Users/mlowicki/projects/sentrycli_sandbox/78502.json
```

If API key or host aren't specified then last used ones (saved in ~/.sentrycli) will be utilized.

```
> sentrycli query 78502 --since 2016-04-19
INFO:requests.packages.urllib3.connectionpool:Starting new HTTP connection (1): errors.services.ams.osa
INFO:sentrycli.query:API key is fine
INFO:sentrycli.query:Getting events for issue 78502 (may take a while)
INFO:requests.packages.urllib3.connectionpool:Starting new HTTP connection (1): errors.services.ams.osa
INFO:sentrycli.query:44 events saved to /Users/mlowicki/projects/sentrycli_sandbox/78502.json
```
By default events are stored in JSON file in the current working directory.

API keys are reachable through Sentry's UI - http://HOSTNAME/organizations/ORGANIZATION/api-keys/.

When events are ready we can start analyzing (grouping) them:
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
+------------+----------------+---------------------+-------+-------+
| User-Agent | Host           | logger              | count |     % |
+------------+----------------+---------------------+-------+-------+
| Opera Mini | sync.opera.com | sync.api.middleware |   232 | 100.0 |
+------------+----------------+---------------------+-------+-------+

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

> sentrycli group 41384.json --breadcrumbs "requests.*sync.commit" --tags server_name
+----------------------+----------------------+-------+------+
| server_name          | breadcrumbs in order | count |    % |
+----------------------+----------------------+-------+------+
| front1.sync.ams.osa  | False                |   143 | 13.3 |
| front6.sync.ams.osa  | False                |   132 | 12.3 |
| front6.sync.lati.osa | False                |   122 | 11.4 |
| front5.sync.ams.osa  | False                |   109 | 10.2 |
| front1.sync.lati.osa | False                |   101 |  9.4 |
| front2.sync.ams.osa  | False                |   100 |  9.3 |
| front3.sync.ams.osa  | False                |    90 |  8.4 |
| front4.sync.ams.osa  | False                |    86 |  8.0 |
| front3.sync.lati.osa | False                |    84 |  7.8 |
| front4.sync.lati.osa | False                |    49 |  4.6 |
| front2.sync.lati.osa | False                |    29 |  2.7 |
| front5.sync.lati.osa | False                |    27 |  2.5 |
| front1.sync.ams.osa  | True                 |     1 |  0.1 |
+----------------------+----------------------+-------+------+


> sentrycli breadcrumbs 41384.json -a requests:data.status_code
+----------------------------------+-------+------+
| ('requests', 'data.status_code') | count |    % |
+----------------------------------+-------+------+
| <NOT PRESENT>                    |  1072 | 99.9 |
| 200                              |     1 |  0.1 |
+----------------------------------+-------+------+

> sentrycli breadcrumbs 41384.json -a requests:data.status_code sync.commit:data.mobile

+----------------------------------+--------------------------------+-------+------+
| ('requests', 'data.status_code') | ('sync.commit', 'data.mobile') | count |    % |
+----------------------------------+--------------------------------+-------+------+
| <NOT PRESENT>                    | <NOT PRESENT>                  |   930 | 86.7 |
| <NOT PRESENT>                    | True                           |    76 |  7.1 |
| <NOT PRESENT>                    | False                          |    66 |  6.2 |
| 200                              | True                           |     1 |  0.1 |
+----------------------------------+--------------------------------+-------+------+
```

To get list of available grouping options 
(in `group` and `breadcrumbs` subcommands) use `--options` switch:
```
> sentrycli group 76342.json --options
+-------------------+-------------+--------+-------------------+-------------+
| Headers           | Context     | Params | Vars              | Tags        |
+-------------------+-------------+--------+-------------------+-------------+
| Accept-Encoding   | filename    |        | args              | browser     |
| Accept-Language   | lineno      |        | auth_header       | device      |
| Authorization     | pathname    |        | bound_func        | level       |
| Cache-Control     | process     |        | callback          | logger      |
| Connection        | processName |        | callback_args     | os          |
| Content-Length    | request     |        | callback_kwargs   | release     |
| Content-Type      | sys.argv    |        | circuitbreaker    | server_name |
...

> sentrycli breadcrumbs 41384.json -o

+----------------------------------------------------+-------------------------+
| Categories                                         | Attributes              |
+----------------------------------------------------+-------------------------+
...
+----------------------------------------------------+-------------------------+
| requests                                           | data.status_code        |
|                                                    | level                   |
|                                                    | event_id                |
|                                                    | timestamp               |
|                                                    | data.url                |
|                                                    | data.reason             |
|                                                    | message                 |
|                                                    | type                    |
|                                                    | data.method             |
+----------------------------------------------------+-------------------------+
| services_raven.clients.django.ServicesDjangoClient | level                   |
|                                                    | event_id                |
|                                                    | timestamp               |
|                                                    | message                 |
|                                                    | type                    |
+----------------------------------------------------+-------------------------+

```

[sentry]: <https://github.com/getsentry/sentry>
