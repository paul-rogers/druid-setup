# Internal Design

Key parts:

* Config stack - The config, as a big stack
* Services - know the config needed for a service
* Codecs - know how to read/write files

Config is defined as a set of layers which can include:

* user-defined settings
* included "libraries"
* built-in definitions
* base config read from the distro

In all cases, a layer is:

* Layer: {key: value}

Where each value can be a dictionary of other key/value pairs.

Meaning is applied via meta-data:

* Top-level keys define the app
* Within each top-level, a domain-specific entity defines meaning
* At the leaf level, meaning is defined by a codec.

