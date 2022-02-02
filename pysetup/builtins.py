from . import consts

root_context = {
    consts.DATA_DIR_KEY: '$target/var',
    consts.ZK_DATA_DIR_KEY: '$dataDir/zk',
    consts.CONFIG_DIR_KEY: '$target/conf',
    consts.DRUID_CONFIG_DIR_KEY: '$confDir/druid',
    consts.ZK_CONFIG_DIR_KEY: '$confDir/zk',
    consts.SUPERVISE_CONFIG_DIR_KEY: '$confDir/supervise',
    consts.SUPERVISE_CONFIG_NAME_KEY: 'cluster',
    consts.README_KEY: consts.DEFAULT_README,
    consts.DISCLAIMER_KEY: consts.DISCLAIMER
}

default_config = {
    consts.ZK_SERVICE: {
        consts.PROPERTIES_KEY: {
            'dataDir': '$dataDir/zk'
        }
    },
    consts.COMMON_SERVICE: {
        consts.PROPERTIES_KEY: {
            'druid.indexer.logs.directory': '$dataDir/druid/indexing-logs',
            'druid.storage.storageDirectory': '$dataDir/druid/segments',
            # Imply extension
            'druid.query.async.storage.local.directory': '$dataDir/druid/async'
        }
    },
    consts.BROKER_SERVICE: {
        consts.PROPERTIES_KEY: {
            'druid.processing.tmpDir': '$dataDir/druid/processing'
        }
    },
    consts.MASTER_SERVICE: {
        consts.PROPERTIES_KEY: {
            'derby.stream.error.file': '$dataDir/druid/derby.log'
        }
    },
    consts.HISTORICAL_SERVICE: {
        consts.JVM_KEY: {
            consts.PROPERTIES_KEY: {
                'java.io.tmpdir': '$dataDir/tmp'
            }
        },
        consts.PROPERTIES_KEY: {
            'druid.processing.tmpDir': '$dataDir/druid/processing',
            'druid.segmentCache.locations': [{
                "path":"$dataDir/druid/segment-cache",
                "maxSize":"300g"}]
        }
    },
    consts.MIDDLE_MANAGER_SERVICE: {
        consts.JVM_KEY: {
            consts.PROPERTIES_KEY: {
                'java.io.tmpdir': '$dataDir/tmp'
            }
        },
        consts.PROPERTIES_KEY: {
            'druid.indexer.task.hadoopWorkingPath': '$dataDir/druid/hadoop-tmp',
        }
    },
    consts.ROUTER_SERVICE: {
        consts.JVM_KEY: {
            consts.PROPERTIES_KEY: {
                'java.io.tmpdir': '$dataDir/tmp'
            }
        }
    }
}
