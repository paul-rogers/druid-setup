# Design Notes

## Goals

* Single source for Imply and Druid configs.
* Easy to reuse options
* Set options in one place.
* Separate config from distro
* Use distro configs as a base
* Inheritance

## Config

Some basic config settings:

* DRUID_HOME - distro
* DRUID_CONFIG - configs
* DRUID_VAR - data
* Base config (path relative to distro)
* JVM configs (override defaults)
* Common configs
* Per-service configs

Something like:

```text
DRUID_HOME = ...
DRUID_CONFIG = ...
broker-config = {
    foo: bar
}
var-dir = ...
```

Should the file be Python or JSON? Python is executable, but JSON (or YAML) may be more understandable.

If YAML for a specific config:

```text
targetDir: ~/apps/example`
configDir: config
dataDir: var
base-config: micro-quickstart
historical:
  - config:
      foo: bar
  - jvm:
      foo
```

## Operation

* Load each file
* Key codec for each (esp. for JVM args)
* Chained dictionaries of options
* None indicates drop an option
* Chain can go multiple ways: maybe via indirections
* Values can be (or include) substitutions
* Generate k/v pairs
* Codec to write pairs to final output

## Key Parts

* Walkers: for Druid or Imply setups, or others
* Writers: for structure and for files
* Config descriptions: says what to walk or write
* Config tree descriptions: what to combine
* Property sets: chaining, substitution

## Config File

### Top-Level File

Simplest top-level file:

```text
druidHome: <path-to-druid>
target: <path-to-target>
baseConfig: <relative-path-to-config>
```

This will essentially copy the base config into the target directory.

More interesting is to define a config to apply to the base. Easiest to do that with
two files:

```text
druidHome: <path-to-druid>
target: <path-to-target>
include:
    - <path-to-defn>
```

The second file:

```
baseConfig: <relative-path-to-config>
context:
    xmx: 1G
services:
    javaArgs:
        ea:
historical:
    javaArgs:
        Xmx: $xmx
    javaProps:
        foo: 30
    config:
        druid.some.prop: true
```

In this case, the first file simply defines one instance of a general config: how to create a specific
setup given a Druid distro and a "template" for createing the config. The template can be applied on
top of any distro. The "services" section is options to set for all services: typically used for
Java options.

The top-level commands are:

* `druidHome`: Location of the Druid distro
* `target`: Location of the target directory with config and data
* `baseConfig`: Path, erlative to `druidHome` of the config to start with.
* `include`: A list of file names to include. Later files override earlier ones.
* `services`: Options to copy to all services.
* `common`: Common configuration (in the `_common` directory)
* `<service>`: Name of a Druid service
* `context`: Name-value pairs to use for variable substitution.

