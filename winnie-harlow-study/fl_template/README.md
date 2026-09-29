# FL Studio template files

`build_flp.py` builds `Glasshouse.flp` by copying events out of these two files, which FL Studio 20.8.4 saved itself.
FL Studio's project format has no public spec, so starting from real FL output is the safest way to write a file FL will open.

| File | What `build_flp.py` takes from it |
|---|---|
| `project.flp` | Project header, mixer (127 inserts with their default settings), playlist track settings |
| `sample_channel.fst` | The settings block of a Sampler channel with a sample loaded, cloned once per Glasshouse channel |

Both files come from the test assets of [PyFLP](https://github.com/demberto/PyFLP) (`tests/assets/patterns/multi-channel.flp` and
`tests/assets/channels/sampler-path.fst`), which is licensed under GPL-3.0.
