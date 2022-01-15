# Root context
DRUID_HOME_KEY = 'druidHome'
TEMPLATE_KEY = 'template'
TEMPLATE_PATH_KEY = 'templatePath'
DATA_DIR_KEY = 'dataDir'
ZK_DATA_DIR_KEY = 'zkDataDir'
DISTRO_KEY = 'distro'
TARGET_KEY = 'target'
BASE_CONFIG_KEY = 'baseConfig'
BASE_CONFIG_PATH_KEY = 'baseConfigPath'
BASE_ZK_DIR_KEY = 'baseZkDir'
README_KEY = 'readme'
TODAY_KEY = 'today'
DISCLAIMER_KEY = 'disclaimer'

# Service names
HISTORICAL_SERVICE = 'historical'
BROKER_SERVICE = 'broker'
ROUTER_SERVICE = 'router'
OVERLORD_SERVICE = 'overlord'
MASTER_SERVICE = 'coordinatorOverlord'
INDEXER_SERVICE = 'indexer'
PEON_SERVICE = 'peon'
COMMON_SERVICE = '_common'
ZK_SERVICE = 'zk'

# Template keys
ZK_KEY = 'zk'

# Other properties
PROPERTIES_KEY = 'properties'
JVM_KEY = 'jvm'
SYSTEM_KEY = 'system'
CONTEXT_KEY = 'context'
INCLUDE_KEY = 'include'
COMMENTS_KEY = 'comments'
MAIN_KEY = 'main'
LOG4J_KEY = 'log4j'
JVM_ARGS_KEY = "args"

# Unset value marker
NULL_VALUE = "<null>"

# Distro names
APACHE_DISTRO = 'apache'
IMPLY_DISTRO = 'imply'

# File names
GENERATED_FILE = '.generated'
README_FILE = "README"
USER_CLASSPATH_DIR = 'user-classpath'
JVM_CONFIG_FILE= 'jvm.config'
RUNTIME_PROPERTIES_FILE = 'runtime.properties'
MAIN_CONFIG_FILE = 'main.config'
COMMON_PROPERTIES_FILE = 'common.runtime.properties'
LOG4J_FILE = 'log4j2.xml'
ZOO_CFG_FILE = 'zoo.cfg'

# Service Names

# Misc
DISCLAIMER = 'Generated Druid Config - Do Not Edit'
DEFAULT_README = """
$disclaimer

To make changes, modify the template and regenerate.

Generated from: $template
Generated on:   $today
Druid home:     $druidHome
Distro kind:    $distro
Base config:    $baseConfig
"""

