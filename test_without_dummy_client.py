#!/usr/bin/env python3

# testWithDummyClient.py
import os
import threading
import time
import unittest
from io import StringIO

from fieldz.field_types import FieldTypes as F, FieldStr as FS
import fieldz.msg_spec as M
import fieldz.typed as T

from rnglib import SimpleRNG
from alertz import *
from alertz.chanIO import *
from alertz.daemon import runTheDaemon, clear_logs
from alertzProtoSpec import ALERTZ_PROTO_SPEC
from fieldz.parser import StringProtoSpecParser
from fieldz.chan import Channel
from fieldz.msg_impl import make_msg_class, make_field_class

RNG = SimpleRNG(time.time())
next_seq_nbr = 0                         # increment after each use


class TestWithDummyClient(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    # utility functions ---------------------------------------------
    def do_clear_logs(self, options):
        self.assertIsNotNone(options)
        log_dir = options.log_dir
        self.assertIsNotNone(log_dir)
        if not os.path.exists(log_dir):
            os.mkdir(log_dir)
        self.assertTrue(os.path.exists(log_dir))
        clear_logs(options)
        # excessive paranoia
        files = os.listdir(log_dir)
        if files:
            self.fail('logs/ has not been cleared')

    # -----------------------------------------------------
    def zone_mismatch_fields(self):
        """ returns a list """
        global next_seq_nbr

        timestamp = int(time.time())
        seq_nbr = next_seq_nbr
        next_seq_nbr += 1     # used, so increment it

        zone_name = RNG.next_file_name(8)
        expected_serial = RNG.next_int32()
        actual_serial = RNG.next_int32()
        while actual_serial == expected_serial:
            actual_serial = RNG.next_int32()

        # NOTE that this is a list
        return [timestamp, seq_nbr, zone_name, expected_serial, actual_serial]

    def next_zone_mismatch_msg(self):
        values = self.zone_mismatch_fields()
        return ZoneMismatchMsg(values)

    # -----------------------------------------------------
    def corrupt_list_fields(self):
        global next_seq_nbr
        timestamp = int(time.time())
        seq_nbr = next_seq_nbr
        next_seq_nbr += 1     # used, so increment it
        remarks = RNG.next_file_name(16)
        return [timestamp, seq_nbr, remarks]

    def nextCorruptListMsg(self):
        values = self.corrupt_list_fields()
        return CorruptListMsg(values)           # GEEP

    # -----------------------------------------------------
    def shutdownFields(self):
        #       global nextSeqNbr
        #       timestamp       = int(time.time())
        #       seqNbr          = nextSeqNbr
        #       nextSeqNbr     += 1     # used, so increment it
        remarks = RNG.next_file_name(16)
        return [remarks, ]

    def nextShutdownMsg(self):
        values = self.shutdownFields()
        return SHUTDOWN_MSG(values)              # GEEP

    # actual unit test(s) -------------------------------------------

    def test_the_daemon(self):
        chan = Channel(BUFSIZE)
        chan.clear()        # XXX should be guaranteed on new channel

        msg_count = 8 + RNG.next_int16(25)   # so 8..32
        # DEBUG
        print("MSG_COUNT = %u" % msg_count)
        # END

        # set up options ----------------------------------
        now = int(time.time())
        pgm_name_and_version = "testWithDummyClient v%s %s" % (
            __version__, __version_date__)
        with open('/etc/hostname', 'r') as file:
            this_host = file.read().strip()

        options = {}                           # a namespace, so to speak
        options['ec2Host'] = False
        options['justShow'] = False
        options['log_dir'] = 'logs'
        options['pgm_name_and_version'] = pgm_name_and_version
        options['port'] = 55555
        options['showTimestamp'] = False
        options['showVersion'] = False
        options['testing'] = True
        options['this_host'] = this_host
        options['timestamp'] = now
        options['verbose'] = False
        ns_ = Namespace(options)

        # clear the log files (so delete any files under logs/) -----
        self.do_clear_logs(ns_)

        # start the daemon --------------------------------
        daemon_t = threading.Thread(target=runTheDaemon, args=(ns_,))
        daemon_t.start()

        # give the daemon time to wake up  --------------------------
        time.sleep(0.15)    # XXX without this we get an abort saying
        # that libev cannot allocate (2G - 16)B

        # start sending (some fixed number of ) messages ------------
        msgs_sent = []
        for nnn in range(msg_count):
            msg = self.next_zone_mismatch_msg()
            seqNbrField = msg[1]
            # XXX by name would be better!
            self.assertEqual(nnn, seqNbrField.value)

            # serialize msg into the channel
            chan.clear()
            msg.write_stand_alone(chan)
            chan.flip()

            # send the msg to the daemon ------------------
            skt = send_to_end_point(chan, '127.0.0.1', 55555)
            time.sleep(0.05)
            skt.close()
            msgs_sent.append(msg)

            # DEBUG
            print("MSG %d HAS BEEN SENT" % nnn)
            # END

        self.assertEqual(msg_count, len(msgs_sent))

        # delay a few ms --------------------------------------------
        time.sleep(0.05)

        # build and send shutdown msg -------------------------------
        msg = self.nextShutdownMsg()
        chan.clear()
        msg.write_stand_alone(chan)
        chan.flip()

        skt = send_to_end_point(chan, '127.0.0.1', 55555)
        # DEBUG
        print("SHUTDOWN MSG HAS BEEN SENT")
        # END

        # delay a few ms --------------------------------------------
        time.sleep(0.05)
        skt.close()

        # join the daemon thread ------------------------------------
        time.sleep(0.05)
        daemon_t.join()

        # verify that the daemon's logs have the expected contents --

        # XXX STUB XXX

if __name__ == '__main__':
    unittest.main()
