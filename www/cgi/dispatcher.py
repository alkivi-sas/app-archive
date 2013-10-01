#!/usr/bin/python
import sys
import json
reload(sys)
sys.setdefaultencoding("utf-8")
sys.path.append('/')

import cgi
import cgitb
cgitb.enable()

from alkivi.common import logger

# Define the global logger
logger.Logger.instance(
        #min_log_level_to_mail  = logger.WARNING,
        min_log_level_to_mail  = None,
        min_log_level_to_save  = logger.DEBUG_DEBUG,
        min_log_level_to_print = logger.INFO,
        filename='/var/log/alkivi/archive.log',
        emails=['root@localhost'])

from alkivi.l0 import archive


def main():

    #
    # Params
    #
    arguments = cgi.FieldStorage()
    action    = arguments['action'].value

    #
    # Get Local PCA data
    #
    dbInstance = archive.Db()

    logger.debug('action to do: %s' % (action))

    if(action=='sessionList'):
        response = getSessions(arguments)
    elif(action=='pcaList'):
        response = getPCAs()
    elif(action=='fileList'):
        response = getFiles(arguments)
    elif(action=='searchFiles'):
        response = searchFiles(arguments)
    else:
        returnError('I did not understand this action')


    print "Content-type: application/json"
    print
    print json.JSONEncoder().encode(response)

def searchFiles(arg):

    fileName = arg['fileName'].value
    if(not(fileName)):
        returnError('Filename is missing')

    response = {}

    try:
        fileList = archive.File().newListFromCharacteristics(characteristics = { 'fileName': { 'operator': 'like', 'value': fileName } })
        response['status'] = 100

        data = []
        for file in fileList:
            data.append(file.as_dict())

        response['value'] = data
    except Exception as e:
        logger.warning('Unable to fetch file list', e)
        response['status'] = 200

    return response

def getFiles(arg):

    sessionId = arg['sessionId'].value
    if(not(sessionId)):
        returnError('PCA id is missing')

    response = {}

    try:
        fileList = archive.File().newListFromCharacteristics(characteristics = { 'session_id': sessionId })
        response['status'] = 100

        data = []
        for file in fileList:
            data.append(file.as_dict())

        response['value'] = data
    except Exception as e:
        logger.warning('Unable to fetch file list', e)
        response['status'] = 200

    return response

def getSessions(arg):

    pcaId = arg['pcaId'].value
    if(not(pcaId)):
        returnError('PCA id is missing')

    response = {}

    try:
        sessionList = archive.Session().newListFromCharacteristics(characteristics = { 'pca_id': pcaId })
        response['status'] = 100

        data = []
        for session in sessionList:
            data.append(session.as_dict())

        response['value'] = data
    except Exception as e:
        logger.warning('Unable to fetch session list', e)
        response['status'] = 200

    return response

def getPCAs():
    response = {}

    try:
        pcaList = archive.PCA().newListFromCharacteristics()
        response['status'] = 100

        data = []
        for pca in pcaList:
            data.append(pca.as_dict())

        response['value'] = data
    except Exception as e:
        logger.warning('Unable to fetch pca list', e)
        response['status'] = 200

    return response

def returnError(message):
    response = { 'status': 200, 'msg': message }
    print "Content-type: application/json"
    print
    print json.JSONEncoder().encode(response)



if __name__ == "__main__":
    main()
