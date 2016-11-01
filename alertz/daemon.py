# ~/dev/py/alertz/alertz/daemon.py

__all__ = ['clear_logs', 'runTheDaemon',
           ]

import os
import socket
import sys
import time
from xlattice.ftLog import LogMgr
from xlattice.procLock import ProcLock
from io import StringIO

from fieldz.field_types import FieldTypes as F, FieldStr as FS
import fieldz.msg_spec as M
import fieldz.typed as T

from alertz import *
from alertz.chanIO import *

from alertzProtoSpec import ALERTZ_PROTO_SPEC
from fieldz.parser import StringProtoSpecParser
from fieldz.chan import Channel
from fieldz.msg_impl import make_msg_class, make_field_class, MsgImpl

# DAEMON ------------------------------------------------------------


def clear_logs(options):
    log_dir = options.log_dir
    print("DEBUG: clearLogs, logDir = '%s'" % log_dir)
    if os.path.exists(log_dir):
        if log_dir.startswith('/') or log_dir.startswith('..'):
            raise RuntimeError("cannot delete %s/*" % log_dir)
        files = os.listdir(log_dir)
        if files:
            if options.verbose:
                print("found %u files" % len(files))
            for file in files:
                os.unlink(os.path.join(log_dir, file))


def actuallyRunTheDaemon(options):
    verbose = options.verbose
    chan = Channel(BUFSIZE)
    string = None
    (cnx, addr) = (None, None)
    string = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    string.bind(('', options.port))
    string.listen(1)
    try:
        running = True
        while running:
            print("\nWAITING FOR CONNECTION")              # DEBUG
            cnx, addr = string.accept()
            try:
                acceptMsg = "CONNECTION FROM %s" % str(addr)
                if verbose:
                    print(acceptMsg)
                print("BRANCH TO options.accessLog.log()")
                sys.stdout.flush()
                options.access_log.log(acceptMsg)
                print("BACK FROM options.access.log()")
                sys.stdout.flush()

                while 1:
                    chan.clear()

#                   print "BRANCH TO recvFromCnx"  ; sys.stdout.flush()
                    msgNdx = recv_from_cnx(cnx, chan)  # may raise exception

                    (msg, realNdx) = MsgImpl.read(chan, STR_OBJ_MODEL)
#                   print "  MSG_NDX: CALCULATED %s, REAL %s" % (
#                                             msgNdx, realNdx)
                    # switch on message type
                    if msgNdx == 0:
                        print("GOT ZONE MISMATCH MSG")
                        print("    timestamp      %s" % msg.timestamp)
                        print("    seqNbr         %s" % msg.seq_nbr)
                        print("    zoneName       %s" % msg.zone_name)
                        print("    expectedSerial %s" % msg.expected_serial)
                        print("    actualSerial   %s" % msg.actual_serial)
                        text =\
                            "mismatch, domain %s: expected serial %s, got %s" % (
                                msg.zone_name, msg.expected_serial, msg.actual_serial)
                        options.alertz_log.log(text)

                    elif msgNdx == 1:
                        # timestamp, seqNb
                        print("GOT CORRUPT LIST MSG")
                        print("    timestamp      %s" % msg.timestamp)
                        print("    seqNbr         %s" % msg.seq_nbr)
                        text = "corrupt list: %s" % (msg.seq_nbr)
                        options.alertz_log.log(text)

                    elif msgNdx == 2:
                        # has one field, remarks
                        print("GOT SHUTDOWN MSG")
                        print("    remarks        %s" % msg.remarks)
                        running = False
                        string.close()
                        # XXX STUB: log the message
                        text = "shutdown: %s" % (msg.remarks)
                        options.alertz_log.log(text)

                    cnx.close()
                    break                   # permit only one message/cnx

            except KeyboardInterrupt as k_exc:
                print("<keyboard interrupt received while connection open>")
                if cnx:
                    cnx.close()
                running = False

    except KeyboardInterrupt as k_exc:
        print("<keyboard interrupt received while listening>")
        # listening socket will be closed
    finally:
        if cnx:
            cnx.close()
        if string:
            string.close()

        # COMMENTING THIS OUT PREVENTS SEGFAULT ON STOCKTON ---------
#       if options.logMgr is not None:
#           options.logMgr.close()
#           options.logMgr = None
        # END COMMENTING OUT ----------------------------------------

        if options.lock_mgr is not None:
            options.lock_mgr.unlock()
            options.lock_mgr = None


def runTheDaemon(options):
    """
    Completes setting up the namespace; if this isn't a "just-show" run,
    creates lock and log managers, creates the logs, and actually runs
    the daemon.
    """
    if options.verbose or options.showVersion or options.justShow:
        print(options.pgm_name_and_version, end=' ')
    if options.showTimestamp:
        print('run at %s GMT' % timestamp)   # could be prettier
    else:
        print()                               # there's a comma up there

    if options.justShow or options.verbose:
        print('justShow         = ' + str(options.justShow))
        print('logDir           = ' + str(options.log_dir))
        print('port             = ' + str(options.port))
        print('showTimestamp    = ' + str(options.showTimestamp))
        print('showVersion      = ' + str(options.showVersion))
        print('testing          = ' + str(options.testing))
        print('timestamp        = ' + str(options.timestamp))
        print('verbose          = ' + str(options.verbose))

    if not options.justShow:
        lock_mgr = None
        access_log = None
        errorLog = None

        try:
            lock_mgr = ProcLock('alertzd')
            options.lock_mgr = lock_mgr
            log_mgr = LogMgr(options.log_dir)
            options.log_mgr = log_mgr

            access_log = log_mgr.open('access')
            options.access_log = access_log

            alertz_log = log_mgr.open('alertz')
            options.alertz_log = alertz_log

            errorLog = log_mgr.open('error')
            options.errorLog = errorLog

            actuallyRunTheDaemon(options)
        except:
            print_exc()
            sys.exit(1)
        finally:
            lock_mgr.unlock()
