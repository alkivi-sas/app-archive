#!/usr/bin/python

import sys
reload(sys)
sys.setdefaultencoding("utf-8")
sys.path.append('/')

from alkivi.common import logger
from alkivi.common import lock
from alkivi.common.logger import Logger

#
# Define Logger
#
logger.Logger.instance(
        min_log_level_to_mail  = logger.WARNING,
        min_log_level_to_save  = logger.DEBUG,
        min_log_level_to_print = logger.DEBUG,
        filename = '/var/log/alkivi/archive-syncDatabases.log',
        emails=['monitoring@alkivi.fr'])

lock = lock.Lock()

#
# Params for current application (in /etc/alkivi.conf.d/archive
#
import ConfigParser
configFile = '/etc/alkivi.conf.d/archive.conf'
logger.debug_debug("Loading config file %s" % (configFile))
config = ConfigParser.RawConfigParser()
config.read('/etc/alkivi.conf.d/archive.conf')

serviceName    = config.get('alkivi-archive', 'serviceName')
pcaServiceName = config.get('alkivi-archive', 'pcaServiceName')

logger.debug_debug('Configuration loaded')

logger.debug('Config serviceName  = %s' % (serviceName))
logger.debug('Config pcaServiceName = %s' % (pcaServiceName))

# Handle a file
def handleFile(OVH_PCA, file_id, local_session, remote_session):

    logger.debug("Starting to look at file")

    # Fetch remote file
    remote_file = OVH_PCA.getFile(local_session.id, file_id)
    
    # Fetch local file
    try:
        local_file = archive.File().newFromCharacteristicsOrCreate(characteristics = { 'id': file_id, 'session_id': local_session.id } )
    except:
        raise

    bool = local_file.syncWithRemote(remote_file)
    logger.debug_debug('syncWithRemote returned %s' % (bool))
    return bool


# Parse session files
def parseSessionFiles(OVH_PCA, local_session, remote_session):
    try:
        files = OVH_PCA.getFiles(local_session.id)
    except:
        # TODO : add expcetion data ?
        logger.warning("Unable to fetch session file session_id %s" % (local_session.id))
        local_session.local_state = 'error'
        local_session.update()
        return

    sessionOK = True
    logger.newLoopLogger()
    # Look at all files
    for file_id in files:
        prefix='f=%s' % (file_id)
        logger.newIteration(prefix=prefix)

        # handleFile return true is files are synced, false if not
        temp = handleFile(OVH_PCA, file_id, local_session, remote_session)
        if(sessionOK and (not temp)):
            sessionOK = False
    logger.delLoopLogger()

    if(sessionOK and local_session.ovh_state == 'done'):
        logger.info('Session is now done and ready to be marked as synced state')
        local_session.local_state='synced'
        local_session.update()


# Handle a session
def handleSession(OVH_PCA, Local_PCA, session_id):

    logger.debug("Starting first pass : quickly creation of session in sql")

    # Fetch remote session
    remote_session = OVH_PCA.getSession(session_id)

    # Fetch local session 
    from sqlalchemy.orm.exc import NoResultFound
    try:
        local_session = archive.Session().newFromCharacteristicsOrCreate(characteristics = { 'id': session_id, 'pca_id': Local_PCA.id } )
    except:
        logger.warning('WTF ?')
        raise

    local_session.syncWithRemote(remote_session)

def checkSession(OVH_PCA, Local_PCA, session_id):
    logger.debug("Starting second pass, deeper check in progress")

    # Fetch remote session
    remote_session = OVH_PCA.getSession(session_id)

    # Fetch local session 
    from sqlalchemy.orm.exc import NoResultFound
    try:
        local_session = archive.Session().newFromCharacteristics(characteristics = { 'id': session_id, 'pca_id': Local_PCA.id } )
    except:
        raise

    if(local_session.local_state != 'synced'):
        logger.info('Session data copied from remote, lets look at files')
        parseSessionFiles(OVH_PCA, local_session, remote_session)
    else:
        logger.info('Session is synced, no need to do shit :)')


from alkivi.api import ovh
from alkivi.l0 import archive

def main():
    # 
    # Declare api
    #
    api = ovh.API(useData='archive')


    #
    # Local PCA data
    #
    dbInstance = archive.Db() # this is only needed when creating databases but no harm to do it every time

    try:
        pca = archive.PCA().newFromCharacteristicsOrCreate(characteristics = { 'serviceName': serviceName, 'pcaServiceName': pcaServiceName } )
    except:
        raise

    #
    # Remote PCA
    #
    from alkivi.api.ovh import PCA
    OVH_PCA = PCA.OVH_PCA(api=api, serviceName=serviceName, pcaServiceName=pcaServiceName)

    # Start building list of sessions
    sessions = OVH_PCA.getSessions()

    logger.newLoopLogger()
    for session_id in sessions:
        prefix = 's=%s' % (session_id)
        logger.newIteration(prefix=prefix)
        handleSession(OVH_PCA, pca, session_id)
    logger.delLoopLogger()

    logger.newLoopLogger()
    for session_id in sessions:
        prefix = 's=%s' % (session_id)
        logger.newIteration(prefix=prefix)
        checkSession(OVH_PCA, pca, session_id)
    logger.delLoopLogger()

    logger.important('Syncing finished')

    # TODO, delete sql session that does not exist anymore ?

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.exception(e)

