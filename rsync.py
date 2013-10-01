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
        min_log_level_to_mail  = logger.WARNING,
        min_log_level_to_save  = logger.DEBUG,
        min_log_level_to_print = logger.DEBUG,
        filename = '/var/log/alkivi/archive-rsync.log',
        emails=['monitoring@alkivi.fr'])

lock = lock.Lock()

import os
import pwd
import socket
import re
import subprocess


#
# Some globals needed for emailing
#
MAILUSER = pwd.getpwuid(os.getuid()).pw_name
MAILHOST = socket.gethostname()

ALKIVIDOMAIN = re.split('\.', MAILHOST)[0]
FROMADDR     = 'support-%s@alkivi.fr' % (ALKIVIDOMAIN)


#
# Functions definitions
#
def sendUserArchiveRecap(user, data):

    # Add customer user
    toaddrs  = [ getEmailFromUser(user) ]

    logger.log('Going to email from %s report to %s' % (FROMADDR, ' '.join(toaddrs)), data)

    msg = "From: %s\r\nTo: %s\r\nSubject: %s\r\n\r\n" % (FROMADDR, ', '.join(toaddrs), 'Alkivi Archive Daily Recap')

    # Global information
    msg = msg + "Bonjour %s,\r\n" % (user) + "\r\n"
    msg = msg + 'Aujourd\'hui, nous avons archivé les données suivantes vous appartenant:\r\n'

    # Data info
    for line in data:
        msg = msg + "\t- " + line + "\r\n"

    msg = msg + "\r\nBonne nuit/journée :)\r\n\r\n"
    msg = msg + "-- L\'équipe Alkivi Archive"
 
    import smtplib

    smtp = smtplib.SMTP('localhost')
    smtp.sendmail(FROMADDR, toaddrs, msg)
    smtp.quit()

def sendGlobalArchiveRecap(data):

    # Global header
    toaddrs  = [ 'archive@alkivi.fr' ]

    logger.log('Going to email report to %s' % (' '.join(toaddrs)), data)

    msg = "From: %s\r\nTo: %s\r\nSubject: %s\r\n\r\n" % (FROMADDR, ', '.join(toaddrs), 'Alkivi Archive Daily Recap')

    msg = msg + "Hello Alkivi Admin that rocks !\r\n\r\n"
    msg = msg + "Today, I archived the following data :\r\n\r\n"

    # Global information
    for user, userData in data.iteritems():
        msg = msg + "\tUser %s\r\n" % (user)

        # Data info
        for line in userData:
            msg = msg + "\t\t- " + line + "\r\n"

        msg = msg + "\r\n"

    msg = msg + "\r\nBizoux"
 
    import smtplib

    smtp = smtplib.SMTP('localhost')
    smtp.sendmail(FROMADDR, toaddrs, msg)
    smtp.quit()


# TODO : extract email info from ldap or local ?
def getEmailFromUser(user):
    return '%s@%s' % (user, mailDomain)

def getHumanReadableSize(num):
    for x in ['bytes','Kb','Mb','Gb']:
        if num < 1024.0:
            return "%3.1f %s" % (num, x)
        num /= 1024.0
    return "%3.1f %s" % (num, 'Tb')

def getFileSize(file):
    return os.stat(file).st_size

def getDirSize(dir):
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(dir):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            total_size += os.path.getsize(fp)
    return total_size


#
# Load conf
#
import ConfigParser
configFile = '/etc/alkivi.conf.d/archive.conf'
logger.debug_debug("Loading config file %s" % (configFile))
config = ConfigParser.RawConfigParser()
config.read('/etc/alkivi.conf.d/archive.conf')

todoPath        = config.get('alkivi-archive', 'todoPath')
doingPath       = config.get('alkivi-archive', 'doingPath')
donePath        = config.get('alkivi-archive', 'donePath')

pcaLogin        = config.get('alkivi-archive', 'pcaLogin')
pcaHost         = config.get('alkivi-archive', 'pcaHost')
pcaPort         = config.get('alkivi-archive', 'pcaPort')
pcaDest         = config.get('alkivi-archive', 'pcaDest')

mailDomain      = config.get('alkivi-archive', 'mailDomain')

logger.debug_debug('Configuration loaded')

logger.debug('Config todoPath  = %s' % (todoPath))
logger.debug('Config doingPath = %s' % (doingPath))
logger.debug('Config donePath  = %s' % (donePath))
logger.debug('Config pcaLogin  = %s' % (pcaLogin))
logger.debug('Config pcaHost   = %s' % (pcaHost))
logger.debug('Config pcaPort   = %s' % (pcaPort))
logger.debug('Config pcaDest   = %s' % (pcaDest))


# TODO : parameterize
dryrun=0
excludeFile=None

import datetime
t = datetime.datetime.now()
now = t.strftime('%Y-%m-%d_%H:%M:%S')
logger.log('Recorded started time is %s' % (now))

def main():
    for dir in [ donePath, todoPath]:
        if(not(os.path.isdir(dir))):
            logger.warning('Directory %s does not exist, check me out' % (dir))
            return

    if(dryrun):
        logger.debug("drymode activated")
    else:
        pass

       

    # Do we have opened files ?
    logger.debug('Testing opened files')
    openedFiles = int(subprocess.check_output("lsof +D %s | grep ' REG ' | grep -v %s | wc -l" % (todoPath,doingPath), shell=True))
    logger.debug('Testing opened files : %d opened file' % (openedFiles))
    if(openedFiles > 0):
        logger.log('We have %s files opened in %s. We skip this run of archive' % (openedFiles, todoPath))
        return
        
    # Is the directory empty ?
    # TODO : exclude doing and done path ?
    import glob
    logger.debug('Testing if we have some file to archive')
    if(len(glob.glob(os.path.join(todoPath, '*'))) == 0):
        logger.log('Directory %s is empty, abording archive' % (todoPath))
        return
    logger.debug('We do have some file to archive :)')

    # Move files to a doing repository
    logger.debug('Moving data to temp dir')
    import shutil
    for filename in glob.glob(os.path.join(todoPath, '*')):
        if(dryrun):
            logger.debug('Drymode is activated, i would have move %s to %s' % (filename, todoPath))
        else:
            logger.debug('Moving %s to %s' % (filename, doingPath))
            shutil.move(filename, doingPath)
    logger.debug('All data has been moved to %s' % (todoPath))

    # Calculate total size
    totalSize = 0
    for rootFile in os.listdir(todoPath):
        # Get user name
        realFile = os.path.join(todoPath,rootFile)
        if(os.path.isdir(realFile)):
            totalSize +=getDirSize(realFile)
        elif(os.path.isfile(realFile)):
            totalSize += getFileSize(realFile)

    logger.log('Going to archive %s of data' % (getHumanReadableSize(totalSize)))

    # Build params
    extraArgs=['-ovaPx']
    if excludeFile:
        extraArgs.append("--exclude-from")
        extraArgs.append(excludeFile)

    # Always exclude @eaDir (files that sucks on synology nas ;)
    extraArgs.append("--exclude")
    extraArgs.append("@eaDir")

    #extraArgs.append("--rsh='ssh -p%s'" % (pcaPort))

    if dryrun:
        extraArgs.append('-n')

    command=["rsync"] + extraArgs + [ "%s/*" % (doingPath), '%s@%s:%s' % (pcaLogin, pcaHost, pcaDest) ]
    logger.log('Going to execute %s' % (' '.join(command)))

    # Call command, capture stdin stderr
    result = subprocess.check_output(' '.join(command), stderr=subprocess.STDOUT, shell=True)
    #logger.debug_debug("Rsync :", result)

    # Move file to a new directory, based on time and date
    finalPath = os.path.join(donePath,now)
    logger.debug('Moving data to finalPath %s' % (finalPath))
    if(dryrun):
        logger.log("DRYMODE : i would have created %s and mv %s/* in it" % ( finalPath, doingPath))
    else:
        os.mkdir(finalPath)
        for filename in glob.glob(os.path.join(doingPath, '*')):
            logger.debug('Moving %s to %s' % (filename, finalPath))
            shutil.move(filename, finalPath)


    userData = {}

    logger.debug('Checking ownership of files to build email data')
    for rootFile in os.listdir(finalPath):
        # Get user name
        stat_info = os.stat(os.path.join(finalPath,rootFile))
        uid = stat_info.st_uid
        user = pwd.getpwuid(uid)[0]
        logger.debug('%s belong to %s' % (rootFile,user))
        if(user in userData):
            userData[user].append(rootFile)
        else:
            userData[user]=[rootFile]

    # now email the following data
    globalData = {}
    for user,files in userData.iteritems():
        # build file information
        mailData=[]
        for file in files:
            realFile = finalPath + '/' + file
            if(os.path.isdir(realFile)):
                dirSize=getDirSize(realFile)
                humanSize=getHumanReadableSize(dirSize)
                mailData.append('Directory %s : %s' % (file,humanSize))
            elif(os.path.isfile(realFile)):
                fileSize=getFileSize(realFile)
                humanSize=getHumanReadableSize(fileSize)
                mailData.append('File %s : %s' % (file,humanSize))
            else:
                logger.warning('WTF ? %s is neither a dir or a file ?' % (realFile))

        globalData[user]=mailData
        sendUserArchiveRecap(user=user, data=mailData)

    sendGlobalArchiveRecap(data=globalData)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.exception(e)
