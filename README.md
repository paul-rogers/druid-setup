# Setup Utility for Apache Druid

The `druid-config` package simplifies configruation of the
[Apache Druid](https://druid.apache.org/) project. Druid uses a collection of property
files to define a Druid configuration. These files uses a set of constant values,
requiring users to edit multiple files to make certain changes.

Druid's default configurations reside within the Druid distribution directory. Usres
who modify those find themselves copying these files from one distribution to the next,
which is tedious and error prone.

Druid stores data in the distribution directory by default, making it hard to use data
from one version to the next when using Druid in the default mode.

Developers working on Druid change distributions frequenly, making the above problems
worse. While production shops likely come up with soluton to externalize configuration,
such approaches are awkward for developers.

`druid-config` addresses these issues by using a simple templating mechanism to rewrite
a "stock" configuration with your desired changes, while also moving the configuration
and data outside of the Druid distribution.

## Simplest Example

`druid-config` is based on one or more template files, encoded in YAML, that define
your setup. The files can be as simple as just three lines. Here is an example 
`my-config.yaml` file:

```yaml
druidHome: /Users/fred/apache-druid-0.23.0-SNAPSHOT
baseConfig: micro-quickstart
target: /Users/fred/druid
```

The first line points to your Apache Druid distribution (created from the `.tar.gz` download
file.) The second line says which of Druid's standard configuration sets you want to
use as the basis for your setup. The third line says where to write the rewritten files.

Create your configuation:

```bash
druid-config my-config
```

To launch the Druid cluster with your new configs:

```bash
/Users/fred/druid/start-druid
```

When you upgrade to a newer version, simply change the `druidHome` above to point to
the new version, then rerun
`druid-config` and you're ready to go. Data in your target directory is preserved,
configuration is replaced with the rewritten form of the latest Druid configuration.

You can easily change any of the configuration values using the additional lines in
your template file. A set of "context variables" let you define values once, then use
them many times, such as in setting the data directory location, memory sizes
and so on. For more advanced uses, you can factor common configuration into
library templates included into your main template.

## Template File Reference

A template file defines a map of values. The top-level values have meanings defined
by `druid-config`, while inner values depend on context. Most values can include
variables using the familar syntax of either `$var` or `${var}`:

```yaml
  foo: $druidHome/conf
  bar: ${DruidHome}Backup
```

The defined top-level keys
are:

`druidHome` (required): The path to a valid Druid installation. This is the installation that
provides the code you wish to run, and the "base" configuration for your custom
configuration.

`baseConfig` (required): The name of one of the Druid-provided configurations within
`$druidHome` or `$druidHome/conf/druid/*`. That is, you can specify just
`micro-qucikstart` instead of `conf/druid/single-server/micro-quickstart`.

`target` (required): The location to write the configuration. By default, `druid-setup` assumes
that your configuration is in `$target/conf` and your data in `$target/data`. When
updating, only the `conf` directory is replace, data is never changed or modified.

`include`: An optional list of other templates to include. Templates included earlier
(including the main template) override values defined in templates included later.

`context`: A map of variables you wish to define or override. Context variables can then
be used in other config values. (Note that variables can only refer to context variables,
not to other config values.)

`exclude`: An optional list of services to *not* generate. For example, if you run
a combined Coordinator/Overlord, you should exclude configuration of the separate
Coordinator and Overlord. Use the same names as used to define service properties.
See below.

`services`: An optional list of services *to* generate. If `exclude` is also present,
then `exclude` takes precedence: services in both lists *will not* be generated.

`custom`: A list of custom service definitions. See below.

### Services

The remaining keys refer to Druid services:

* `broker`
* `router`
* `coordinator`
* `overlord`
* `historical`
* `coordinator-overlord`
* `indexer`
* `peon`
* `zk`
* `common`

Each of the Druid-defined services has three standard sub-keys:

* `supervise`: The configuration for Druid's `supervise` script.
* `jvm`: JVM properties for the `jvm.config` file.
* `main`: The main routine for the `main.config` file.
* `properties`: The Druid properties for the `runtime.properties` file.

The "pseudo-service" `common` is not really a service. Instead, it corresponds to the
Druid `_common` directory and contains defaults for Druid services:

* `log4j`: The contents of the `log4j2.xml` configuration file.
* `properties`: Common Druid properties for the `common.runtime.properties` file.

The ZooKeeper service, `zk`, has three sub-keys:

* `supervise`: The configuration for Druid's `supervise` script.
* `jvm`: The JVM properties, as above.
* `properties`: Properties for the `zoo.cfg` file.
* `log4j`: The contents of the `log4j2.xml` configuration file as noted above.

### Supervise

Every service has an entry for the `supervise.conf` file. Although these entries
appear together in that file, they are split out across the individual services
in the `druid-setup` configuration. The entries are:

* `name`: Name of the service.
* `priority`: Optional priority as a number from 0 to 100. The default is 50.
* `command`: The command to run, such as `bin/run-druid.sh`.
* `args`: A list of additional arguments to pass to the command.

Example:

```yaml
historical:
  supervise:
    name: historical
    command: bin/run-druid.sh
    args:
      - $druidConfDir
```

### Properties

Each `properties` resource is a list of name/value pairs. For Druid properties,
the names are often in dotted form:

```yaml
historical:
  properties:
    druid.plaintextPort: 8083
```

Remember that YAML uses colons to separate keys and values, not the equal signs used
it actual property files.

### JVM Configuration

JVM configuration divides into two groups: JVM arguments and system properties. List
the keys wihout the leading dash. For system properties, omit the leading `-D`. Example:

```yaml
historical:
  jvm:
    args:
      Xms: $heapMem
    properties:
      java.io.tmpdir: /shared/tmp
```

### Main

You should never need to change the `main` properties. Still, it is helpful to know
that the main has two parts:

```yaml
historical:
  main:
    main: org.apache.druid.cli.Main
    args: server historical
```

### Custom Services

Occasionally, you may find it necessary to define a custom service. This is done
with the `custom` key:

```yaml
custom:
  data-blaster:
    copy: historical
  watchdog:
    configs:
      - main
      - log4j
```

Here we defined two services. The first starts with a copy of the `historical` base 
configs. The second says we want a `main.config` adn a `log4j2.xml` config, but we have
to provie all the values (which are included in the service config section.)

## Template Rules

The `druid-setup` system consists of a set of template rules.

### Variables

For the context variables, precendence, from lowest to highest:

1. A set of fixed system-defined variables:

    * `dataDir`: '$target/var', root data directory.
    * `zkDataDir`: '$dataDir/zk', ZooKeeper data directory.
    * `confDir`*: '$target/conf', root config directory.
    * `druidConfDir`: '$confDir/druid', the location of Druid service configs.
    * `zkConfDir`*: '$confDir/zk', location of ZooKeeper configs.
    * `superviseConfDir`: '$confDir/supervise', location of the Supervise config.
    * `superviseName`: 'cluster', the base name of the Supervise script.
    * `readme`: template for the `README` file.
    * `disclaimer`: template for the "Do not edit" message in the `.generated` and `README` files.

2. Variables defined in the `context` section of templates, with override rules defined
below.

3. Variables defined on the command line.

4. A set of pre-defined variables which always take precedence:

    * `template`: The name of the main template file.
    * `templatePath`: The absolute path to the template file.
    * `today`: The current date and time.

### Configuration

Configuration is anything written to configuation files. Variables exist to
more easily define config values. Configuration forms a "stack" of overrides:

1. Values defined within the base configuration read from the Druid distribution.

2. Values from templates. Within templates, values from included files have lower
priority than those in the template that included them. The topl-level template
has the highest priority. If an `include` key has multiple files, then those later
in the list take precedence over those earlier in the list. If the same file
appears mulltiple times, then the first appearance sets the precedence order.

3. A set of pre-defined configurations which define all data directories to
be relative to `$dataDir`:

```yaml
zk:
  properties:
    dataDir: $dataDir/zk
common:
  properties:
    druid.indexer.logs.directory: $dataDir/druid/indexing-logs
    druid.storage.storageDirectory': $dataDir/druid/segments
    # Imply extension
    druid.query.async.storage.local.directory: $dataDir/druid/async
broker:
  properties:
      druid.processing.tmpDir: $dataDir/druid/processing
coordinator-overlord:
  properties:
    derby.stream.error.file: $dataDir/druid/derby.log
historial:
  jvm:
    properties:
      java.io.tmpdir: $dataDir/tmp
  properties:
    druid.processing.tmpDir': '$dataDir/druid/processing',
    druid.segmentCache.locations': [{"path":"$dataDir/druid/segment-cache","maxSize":"300g"}]
        }
    },
historial:
  jvm:
    properties:
      java.io.tmpdir: $dataDir/tmp
  properties:
    druid.indexer.task.hadoopWorkingPath: $dataDir/druid/hadoop-tmp
        }
    },
historial:
  jvm:
    properties:
      java.io.tmpdir: $dataDir/tmp
```

The idea is that you may have library of setups which override values from the
base config. Your top-level template may override any of the library (or base
config) values.

## Generated Configuration

By default, `druid-setup` generates a `target` configuration directory with the following
form:

```
$target (target) /
  README
  .generated
  conf (confDir) /
    druid (druidConfDir) /
      _common /
        common.runtime.properties
        log4j2.xml
      broker /
        main.config
        jvm.config
        runtime.properties
      ...
    zk (zkConfDir) /
      jvm.config
      log4j2.xml
      zoo.cfg
    supervise (superviseConfDir) /
      cluster.config (superviseName)
  var (dataDir) /
```

The names in parenthesis are the context variables you can set to change the
layout. The default values are:


* `conf`: `$target/conf`
* `druidConfDir`: `$confDir/druid`
* `zkConfDir`: `$confDir/zk`
* `superviseConfDir`: `$confDir/supervise`
* `superviseName`: `cluster`
* `dataDir`: `$target/var`

The `.generated` file exists to prevent disasters: `druid-setup` will only replace an
existing directory if the `.generated` file exists. The `README` file provides a
summary of the configuration.

Data files exist outside of the `conf` directory so that they are not affected
when the configuration changges. `druid-setup` provides a default set of config
overrides that moves the data files out of the usual relative `var` path into
`$dataDir`. Druid creates any needed subdirectories as it runs.

## Command Line Arguments

Command line syntax is:

```text
usage: Druid-config [-h] [-x] [-c] [-d] template

Druid config generator

positional arguments:
  template       path to the the YAML template

optional arguments:
  -h, --help     show this help message and exit
  -x, --vars     print the variables (context)
  -c, --config   print the computed configuration
  -d, --dry-run  dry-run: load and verify, but don't generate
```

The template argument can omit the `.yaml` suffix for convenience.