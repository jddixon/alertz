# ~/dev/py/alertz/alertz/daemon.py

__all__ = ['clearLogs', 'runTheDaemon',
           ]

import os
import socket
import sys
import time
from xlattice.ftLog import LogMgr
from xlattice.procLock import ProcLock
from io import StringIO

import fieldz.fieldTypes as F
import fieldz.msgSpec as M
import fieldz.typed as T

from alertz import *
from alertz.chanIO import *

from alertzProtoSpec import ALERTZ_PROTO_SPEC
from fieldz.parser import StringProtoSpecParser
from fieldz.chan import Channel
from fieldz.msgImpl import makeMsgClass, makeFieldClass, MsgImpl

# DAEMON ------------------------------------------------------------


def clearLogs(options):
    logDir = options.logDir
    print("DEBUG: clearLogs, logDir = '%s'" % logDir)
    if os.path.exists(logDir):
        if logDir.startswith('/') or logDir.startswith('..'):
            raise RuntimeError("cannot delete %s/*" % logDir)
        files = os.listdir(logDir)
        if files:
            if options.verbose:
                print("found %u files" % len(files))
            for file in files:
                os.unlink(os.path.join(logDir, file))


def actuallyRunTheDaemon(options):
    verbose = options.verbose
    chan = Channel(BUFSIZE)
    s = None
    (cnx, addr) = (None, None)
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('', options.port))
    s.listen(1)
    try:
        running = True
        while running:
            print("\nWAITING FOR CONNECTION")              # DEBUG
            cnx, addr = s.accept()
            try:
                acceptMsg = "CONNECTION FROM %s" % str(addr)
                if verbose:
                    print(acceptMsg)
                print("BRANCH TO options.accessLog.log()")
                sys.stdout.flush()
                options.accessLog.log(acceptMsg)
                print("BACK FROM options.access.log()")
                sys.stdout.flush()

                while 1:
                    chan.clear()

#                   print "BRANCH TO recvFromCnx"  ; sys.stdout.flush()
                    msgNdx = recvFromCnx(cnx, chan)  # may raise exception

                    (msg, realNdx) = MsgImpl.read(chan, sOM)
#                   print "  MSG_NDX: CALCULATED %s, REAL %s" % (
#                                             msgNdx, realNdx)
                    # switch on message type
                    if msgNdx == 0:
                        print("GOT ZONE MISMATCH MSG")
                        print("    timestamp      %s" % msg.timestamp)
                        print("    seqNbr         %s" % msg.seqNbr)
                        print("    zoneName       %s" % msg.zoneName)
                        print("    expectedSerial %s" % msg.expectedSerial)
                        print("    actualSerial   %s" % msg.actualSerial)
                        text = \
                            "mismatch, domain %s: expected serial %s, got %s" % (
                                msg.zoneName, msg.expectedSerial, msg.actualSerial)
                        options.alertzLog.log(text)

                    elif msgNdx == 1:
                        # timestamp, seqNb
                        print("GOT CORRUPT LIST MSG")
                        print("    timestamp      %s" % msg.timestamp)
                        print("    seqNbr         %s" % msg.seqNbr)
                        text = "corrupt list: %s" % (msg.seqNbr)
                        options.alertzLog.log(text)

                    elif msgNdx == 2:
                        # has one field, remarks
                        print("GOT SHUTDOWN MSG")
                        print("    remarks        %s" % msg.remarks)
                        running = False
                        s.close()
                        # XXX STUB: log the message
                        text = "shutdown: %s" % (msg.remarks)
                        options.alertzLog.log(text)

                    cnx.close()
                    break                   # permit only one message/cnx

            except KeyboardInterrupt as ke:
                print("<keyboard interrupt received while connection open>")
                if cnx:
                    cnx.close()
                running = False

    except KeyboardInterrupt as ke:
        print("<keyboard interrupt received while listening>")
        # listening socket will be closed
    finally:
        if cnx:
            cnx.close()
        if s:
            s.close()

        # COMMENTING THIS OUT PREVENTS SEGFAULT ON STOCKTON ---------
#       if options.logMgr is not None:
#           options.logMgr.close()
#           options.logMgr = None
        # END COMMENTING OUT ----------------------------------------

        if options.lockMgr is not None:
            options.lockMgr.unlock()
            options.lockMgr = None


def runTheDaemon(options):
    """
    Completes setting up the namespace; if this isn't a "just-show" run,
    creates lock and log managers, creates the logs, and actually runs
    the daemon.
    """
    if options.verbose or options.showVersion or options.justShow:
        print(options.pgmNameAndVersion, end=' ')
    if options.showTimestamp:
        print('run at %s GMT' % timestamp)   # could be prettier
    else:
        print()                               # there's a comma up there

    if options.justShow or options.verbose:
        print('justShow         = ' + str(options.justShow))
        print('logDir           = ' + str(options.logDir))
        print('port             = ' + str(options.port))
        print('showTimestamp    = ' + str(options.showTimestamp))
        print('showVersion      = ' + str(options.showVersion))
        print('testing          = ' + str(options.testing))
        print('timestamp        = ' + str(options.timestamp))
        print('verbose          = ' + str(options.verbose))

    if not options.justShow:
        lockMgr = None
        accessLog = None
        errorLog = None

        try:
            lockMgr = ProcLock('alertzd')
            options.lockMgr = lockMgr
            logMgr = LogMgr(options.logDir)
            options.logMgr = logMgr

            accessLog = logMgr.open('access')
            options.accessLog = accessLog

            alertzLog = logMgr.open('alertz')
            options.alertzLog = alertzLog

            errorLog = logMgr.open('error')
            options.errorLog = errorLog

            actuallyRunTheDaemon(options)
        except:
            print_exc()
            sys.exit(1)
        finally:
            lockMgr.unlock()
