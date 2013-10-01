#!/usr/bin/python
# -*-coding:utf-8 -*

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
        min_log_level_to_mail  = None,
        min_log_level_to_save  = logger.LOG,
        min_log_level_to_print = logger.LOG,
        emails=['monitoring@alkivi.fr'])

lock = lock.Lock()

import os
import pwd
import socket
import re
import subprocess

def usage():
    print 'Usage: '+sys.argv[0]+' -h -d -s sessionId'+"\n"
    print "-h     --help      Display help"
    print "-d     --debug     Toggle debug printing on stdout"
    print "-s     --session   Session Id to delete"


def main(argv):
    # get opts
    import getopt

    # Variable that opt use
    session = None
    try:                                
        opts, args = getopt.getopt(argv, "hs:d", ["help", "session=", "debug"])
    except getopt.GetoptError:          
        usage()                         
        sys.exit(2)                     
    for opt, arg in opts:                
        if opt in ("-h", "--help"):      
            usage()                     
            sys.exit()                  
        elif opt in ("-d", "--debug"):
            logger.setMinLevelToPrint(logger.DEBUG)
            logger.debug('debug activated')
        elif opt in ("-s", "--session"): 
            session = arg

    if(session == None):
        logger.important("You forget to pass a session using --session")
        usage()
        exit(1)

    # Now fetch session
    from alkivi.l0 import archive
    Session = archive.Session().newFromCharacteristics(characteristics = { 'id': session } )
    logger.debug("Session is %s" % (Session))

    Session.deleteAllFiles()
    Session.delete()
    
    logger.log('All files from session %s have been deleted' % (session))


if __name__ == "__main__":
    try:
        main(sys.argv[1:])
    except Exception as e:
        logger.exception(e)
