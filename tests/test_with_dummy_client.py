#!/usr/bin/env python3

# testWithDummyClient.py
import os
import threading
import time
import unittest
from io import StringIO

from rnglib import SimpleRNG
from wireops.chan import Channel
import wireops.typed as T

import fieldz.msg_spec as M
from fieldz.parser import StringProtoSpecParser
from fieldz.msg_impl import make_msg_class, make_field_class

from alertz import(CORRUPT_LIST_MSG, ZONE_MISMATCH_MSG,
                   __version__, __version_date__, Namespace, BUFSIZE)
from alertz.chan_io import send_to_end_point
from alertz.daemon import run_the_daemon, clear_logs
from alertz_proto_spec import ALERTZ_PROTO_SPEC

RNG = SimpleRNG(time.time())
NEXT_SEQ_NBR = 0                         # increment after each use


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
        global NEXT_SEQ_NBR

        timestamp = int(time.time())
        seq_nbr = NEXT_SEQ_NBR
        NEXT_SEQ_NBR += 1     # used, so increment it

        zone_name = RNG.next_file_name(8)
        expected_serial = RNG.next_int32()
        actual_serial = RNG.next_int32()
        while actual_serial == expected_serial:
            actual_serial = RNG.next_int32()

        # NOTE that this is a list
        return [timestamp, seq_nbr, zone_name, expected_serial, actual_serial]

    def next_zone_mismatch_msg(self):
        values = self.zone_mismatch_fields()
        return ZONE_MISMATCH_MSG(values)

    # -----------------------------------------------------
    def corrupt_list_fields(self):
        global NEXT_SEQ_NBR
        timestamp = int(time.time())
        seq_nbr = NEXT_SEQ_NBR
        NEXT_SEQ_NBR += 1     # used, so increment it
        remarks = RNG.next_file_name(16)
        return [timestamp, seq_nbr, remarks]

    def next_corrupt_list_msg(self):
        values = self.corrupt_list_fields()
        return CORRUPT_LIST_MSG(values)           # GEEP

    # -----------------------------------------------------
    def shutdown_fields(self):
        #       global nextSeqNbr
        #       timestamp       = int(time.time())
        #       seqNbr          = nextSeqNbr
        #       nextSeqNbr     += 1     # used, so increment it
        remarks = RNG.next_file_name(16)
        return [remarks, ]

    def next_shutdown_msg(self):
        values = self.shutdown_fields()
        return shutdown_msg_cls(values)              # GEEP

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
        daemon_t = threading.Thread(target=run_the_daemon, args=(ns_,))
        daemon_t.start()

        # give the daemon time to wake up  --------------------------
        time.sleep(0.15)    # XXX without this we get an abort saying
        # that libev cannot allocate (2G - 16)B

        # start sending (some fixed number of ) messages ------------
        msgs_sent = []
        for nnn in range(msg_count):
            msg = self.next_zone_mismatch_msg()
            seq_nbr_field = msg[1]
            # XXX by name would be better!
            self.assertEqual(nnn, seq_nbr_field.value)

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
        msg = self.next_shutdown_msg()
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
