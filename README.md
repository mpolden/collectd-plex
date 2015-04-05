# collectd-plex

A Plex plugin for [collectd](https://collectd.org/).

## Examples

```
<LoadPlugin python>
  Globals true
</LoadPlugin>

<Plugin python>
  ModulePath "/path/to/plugin"
  Import "plex"

  # Count all videos in a section
  <Module plex>
    Host "localhost"
    Port 32400
    Section 1
    Instance tv_shows
    SumLeaf false
  </Module>

  # Count all leaf videos (e.g. episodes) in a section
  <Module plex>
    Host "localhost"
    Port 32400
    Section 1
    Instance episodes
    SumLeaf true
  </Module>
</Plugin>
```
