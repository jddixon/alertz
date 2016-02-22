#!/usr/bin/python3

# testWithDummyClient.py
import os, threading, time
import unittest
from io                 import StringIO

import fieldz.fieldTypes    as F
import fieldz.msgSpec       as M
import fieldz.typed         as T

from rnglib             import SimpleRNG
from alertz             import *
from alertz.chanIO      import *
from alertz.daemon      import runTheDaemon, clearLogs
from alertzProtoSpec    import ALERTZ_PROTO_SPEC
from fieldz.parser      import StringProtoSpecParser
from fieldz.chan        import Channel
from fieldz.msgImpl     import makeMsgClass, makeFieldClass

rng         = SimpleRNG (time.time())
nextSeqNbr  = 0                         # increment after each use

class TestWithDummyClient (unittest.TestCase):

    def setUp(self):
        pass
    def tearDown(self):
        pass

    # utility functions ---------------------------------------------
    def doClearLogs(self, options):
        self.assertIsNotNone(options)
        logDir = options.logDir
        self.assertIsNotNone(logDir)
        if not os.path.exists(logDir):
            os.mkdir(logDir)
        self.assertTrue(os.path.exists(logDir))
        clearLogs(options)
        # excessive paranoia
        files = os.listdir(logDir)
        if files:
            self.fail('logs/ has not been cleared')

    # -----------------------------------------------------
    def zoneMismatchFields(self):
        """ returns a list """
        global nextSeqNbr

        timestamp       = int(time.time())
        seqNbr          = nextSeqNbr
        nextSeqNbr     += 1     # used, so increment it

        zoneName        = rng.nextFileName(8)
        expectedSerial  = rng.nextInt32()
        actualSerial    = rng.nextInt32()
        while actualSerial == expectedSerial:
            actualSerial    = rng.nextInt32()

        # NOTE that this is a list
        return [timestamp, seqNbr, zoneName, expectedSerial, actualSerial]

    def nextZoneMismatchMsg(self):
        values = self.zoneMismatchFields()
        return ZoneMismatchMsg(values)
    
    # -----------------------------------------------------
    def corruptListFields(self):
        global nextSeqNbr
        timestamp       = int(time.time())
        seqNbr          = nextSeqNbr
        nextSeqNbr     += 1     # used, so increment it
        remarks         = rng.nextFileName(16)
        return [timestamp, seqNbr, remarks]
    
    def nextCorruptListMsg(self):
        values = self.corruptListFields()
        return CorruptListMsg(values)           # GEEP

    # -----------------------------------------------------
    def shutdownFields(self):
#       global nextSeqNbr
#       timestamp       = int(time.time())
#       seqNbr          = nextSeqNbr
#       nextSeqNbr     += 1     # used, so increment it
        remarks         = rng.nextFileName(16)
        return [remarks,]
    
    def nextShutdownMsg(self):
        values = self.shutdownFields()
        return ShutdownMsg(values)              # GEEP

    # actual unit test(s) -------------------------------------------

    def testTheDaemon(self):
        chan = Channel(BUFSIZE)
        chan.clear()        # XXX should be guaranteed on new channel

        MSG_COUNT = 8 + rng.nextInt16(25)   # so 8..32
        # DEBUG
        print("MSG_COUNT = %u" % MSG_COUNT)
        # END

        # set up options ----------------------------------
        now                 = int (time.time())
        pgmNameAndVersion   = "testWithDummyClient v%s %s" % ( 
                                        __version__, __version_date__)
        with open('/etc/hostname', 'r') as f:
            thisHost = f.read().strip()

        options = {}                           # a namespace, so to speak
        options['ec2Host']         = False
        options['justShow']        = False
        options['logDir']          = 'logs'
        options['pgmNameAndVersion']         = pgmNameAndVersion
        options['port']            = 55555
        options['showTimestamp']   = False
        options['showVersion']     = False
        options['testing']         = True
        options['thisHost']        = thisHost
        options['timestamp']       = now
        options['verbose']         = False
        ns = Namespace(options)

        # clear the log files (so delete any files under logs/) -----
        self.doClearLogs(ns)

        # start the daemon --------------------------------
        daemonT = threading.Thread(target=runTheDaemon, args=(ns,))
        daemonT.start()

        # give the daemon time to wake up  --------------------------
        time.sleep(0.15)    # XXX without this we get an abort saying
                            # that libev cannot allocate (2G - 16)B

        # start sending (some fixed number of ) messages ------------
        msgsSent = []
        for n in range(MSG_COUNT):
            msg         = self.nextZoneMismatchMsg()
            seqNbrField = msg[1]            
            # XXX by name would be better!
            self.assertEquals(n, seqNbrField.value)

            # serialize msg into the channel
            chan.clear()
            msg.writeStandAlone(chan)
            chan.flip()

            # send the msg to the daemon ------------------
            skt = sendToEndPoint( chan, '127.0.0.1', 55555)
            time.sleep(0.05)
            skt.close()
            msgsSent.append(msg)

            # DEBUG
            print("MSG %d HAS BEEN SENT" % n)
            # END

        self.assertEquals(MSG_COUNT, len(msgsSent))

        # delay a few ms --------------------------------------------
        time.sleep(0.05)

        # build and send shutdown msg -------------------------------
        msg         = self.nextShutdownMsg()
        chan.clear()
        msg.writeStandAlone(chan)
        chan.flip()

        skt = sendToEndPoint( chan, '127.0.0.1', 55555)
        # DEBUG
        print("SHUTDOWN MSG HAS BEEN SENT")
        # END

        # delay a few ms --------------------------------------------
        time.sleep(0.05)
        skt.close()

        # join the daemon thread ------------------------------------
        time.sleep(0.05)
        daemonT.join()

        # verify that the daemon's logs have the expected contents --

        # XXX STUB XXX

if __name__ == '__main__':
    unittest.main()
