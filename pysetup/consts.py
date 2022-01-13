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

# Template keys

# Other properties
PROPERTIES_KEY = 'properties'
JVM_KEY = 'jvm'
SYSTEM_KEY = 'system'
CONTEXT_KEY = 'context'
INCLUDE_KEY = 'include'
COMMENTS_KEY = 'comments'

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
COMMON_DIR = '_common'
ZK_SERVICE = 'zk'

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

