# Druid Setup Notes

Working directory: must be the Druid build directory? Multiple things located from there?

## Supervise

Usage:

```text
bin/supervise -c <conf file> [-d <var dir>]
```

`/bin/supervise` runs the script. Need to understand its assumptions.

`-c <config file>` - Identifies the system config file.

Example config file:

```text
:verify bin/verify-java
:verify bin/verify-default-ports
#:verify bin/verify-version-check
:kill-timeout 10

!p10 zk bin/run-zk conf-quickstart
coordinator bin/run-druid coordinator conf-quickstart/druid
#broker bin/run-druid broker conf-quickstart/druid
router bin/run-druid router conf-quickstart/druid
historical bin/run-druid historical conf-quickstart/druid
!p80 overlord bin/run-druid overlord conf-quickstart/druid
!p90 indexer bin/run-druid indexer conf-quickstart/druid
#pivot bin/run-pivot-quickstart conf-quickstart/druid
```

The lines that start with `#` are comments. Lines that start with `:` are ??

Other lines are of the format:

* `p<n>` Set startup/shutdown order to `n`. Default is 50.
* Command name.
* Arguments(s) to the command

## Run-Druid

Usage

```text
bin/run-druid <service> [conf-dir]
```

This script assumes it runs a service, with the name as the first argument.

The second argument is the config directory:

```text
<conf-dir>
|- jvm.config (required)
|- runtime.properties (optional)
|- main.config (required)
```

The Java command line created is:

```text
java
  <args from jvm.config>
  -cp
  <conf-dir>/<service>
  <conf-dir>/_common
  <conf-dir>/../_common
  <druid-home>/lib
  <args from main.config>
```

There are also Hadoop items which are ignored above.

Typical `jvm.config`:

```text
-server
-Xms512m
-Xmx512m
-XX:MaxDirectMemorySize=768m
-XX:+ExitOnOutOfMemoryError
-XX:+UseG1GC
-Duser.timezone=UTC
-Dfile.encoding=UTF-8
-Djava.io.tmpdir=var/tmp
-Djava.util.logging.manager=org.apache.logging.log4j.jul.LogManager
```

Typical `main.config`:

```text
org.apache.druid.cli.Main server broker
```