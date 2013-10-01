#!/usr/bin/python

import sys
reload(sys)
sys.setdefaultencoding("utf-8")
sys.path.append('/')

from alkivi.common import logger
from alkivi.common.logger import Logger

#
# Define Logger
#
logger = Logger.instance(
        min_log_level_to_mail  = None,
        min_log_level_to_save  = logger.DEBUG,
        min_log_level_to_print = logger.DEBUG,
        emails=['anthony@alkivi.fr'])

#
# Params for current application
#
serviceName    = 'publiccloud-passport-20697181'
pcaServiceName = 'pca-vl24383-20697181'


#
# First get list of directory in DONE_PATH set in /etc/alkivi.conf.d/archive.conf
#

#
# For each directory, try to find a local pca sessions
#

#
# Do we have a synced session that is worth to look ?
#

# 
# Then for each local file, get name and size (sha ?) and try to find the associated file in databse
#

# 
# If file is present in database, we can remove it :)
#
