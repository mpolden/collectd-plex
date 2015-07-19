# collectd-plex

A Plex plugin for [collectd](https://collectd.org/).

# Requirements

* Plex.tv authentication token (see included `get_auth_token.py` script)
* Plex Media Server
* CollectD `python` plugin

# Configuration

* `Host` - Plex server hostname (also used to identify metric)
* `Port` - Plex server port
* `AuthToken` - Plex.tv authentication token
* `Metric` - Metric to collect.  Supported metrics:
  * `movies` - number of movies
  * `shows` - number of shows
  * `episodes` - number of episodes
* **Optional:** `Section` - Plex library section to query (must match metric type)
* `Instance` - CollectD type instance

## Examples

```
<LoadPlugin python>
  Globals true
</LoadPlugin>

<Plugin python>
  ModulePath "/path/to/plugin"
  Import "plex"

  # Count all movies in a Movie section
  <Module plex>
    Host "localhost"
    Port 32400
    AuthToken <token>
    Metric movies
    Section 1
    Instance movie
  </Module>

  # Count all shows in a TV Show section
  <Module plex>
    Host "localhost"
    Port 32400
    AuthToken <token>
    Metric shows
    Section 2
    Instance tv_shows
  </Module>

  # Count all episodes in a TV Show section
  <Module plex>
    Host "localhost"
    Port 32400
    AuthToken <token>
    Metric episodes
    Section 2
    Instance episodes
  </Module>

</Plugin>
```
