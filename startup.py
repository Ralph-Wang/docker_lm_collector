from logicmonitor_core.Collector import Collector
import re
import logging
import os
import signal
import socket
import sys
import glob

install_dir = '/usr/local/logicmonitor/agent'
logfile = install_dir + '/logs/wrapper.log'
lockdir = install_dir + '/bin'
rundir = '/run'


def getParams():
    # parse parameters
    params = {}
    params['company'] = os.environ['company']
    params['user'] = os.environ['username']
    params['password'] = os.environ['password']
    if 'collector_id' in os.environ:
        params['collector_id'] = os.environ['collector_id']
    params['description'] = ''
    if 'description' in os.environ:
        params['description'] = os.environ['description']
    else:
        # put this here to set a default description. The portal will default
        # to this on its own, but for the purpose of doing an uninstall, it's
        # best to do it here as well.
        params['description'] = socket.gethostname()
    return params


def startup(params):
    # create collector object
    collector = Collector(params)

    # detect whether collector already exists
    if glob.glob('/usr/local/logicmonitor/logicmonitorsetup\d+_\d+.bin'):
        logging.debug('Collector already installed.')
        logging.debug('Cleaning any existing lock files.')
        cleanup()
        logging.debug('Starting collector.')
        # start collector
        collector.start()
    else:
        logging.debug('Installing collector.')
        # create collector
        collector.create()


# cleanup any leftover lock files
def cleanup():
    if os.path.isdir(lockdir):
        for f in os.listdir(lockdir):
            if re.search('.*\.lck', f):
                logging.debug('Removing ' + f + '.')
                os.remove(os.path.join(lockdir, f))
            elif re.search('.*\.pid', f):
                logging.debug('Removing ' + f + '.')
                os.remove(os.path.join(lockdir, f))
    if os.path.isdir(rundir):
        for f in os.listdir(rundir):
            if re.search('.*\.lck', f):
                logging.debug('Removing ' + f + '.')
                os.remove(os.path.join(rundir, f))
            elif re.search('.*\.pid', f):
                logging.debug('Removing ' + f + '.')
                os.remove(os.path.join(rundir, f))


# gracefully catch and handle docker stop
def signal_handler(signal, frame):
    logging.debug('Caught signal ' + str(signal) + '. Exiting.')
    sys.exit(0)


def main():
    # validate credentials exist
    if (
        'company' in os.environ and
        'username' in os.environ and
        'password' in os.environ
    ):
            # install and/or start collector
            params = getParams()
            startup(params)

    else:
        print('Please specify company, username, and password')
        sys.exit(1)

# TERM handler
signal.signal(signal.SIGTERM, signal_handler)
signal.signal(signal.SIGINT, signal_handler)

main()
