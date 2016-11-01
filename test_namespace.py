#!/usr/bin/env python3

# testNamespace.py
import os
import threading
import time
import unittest
from rnglib import SimpleRNG
from alertz import Namespace

RNG = SimpleRNG(time.time())

# THIS WILL BE WRONG
next_seq_nbr = 0                 # increment after each use


class TestNamespace(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    # utility functions ---------------------------------------------

    def msg_values(self):
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

    # actual unit test(s) -------------------------------------------

    def testANamespace(self):

        now = int(time.time())
        options = {}                # what we convert into a namespace of sorts
        options['justShow'] = True  # False
        options['log_dir'] = 'logs'
        options['port'] = 55555
        options['showTimestamp'] = False
        options['showVersion'] = False
        options['testing'] = False
        options['timestamp'] = now
        options['verbose'] = True  # False

        ns_ = Namespace(options)

        self.assertTrue(ns_.justShow)
        self.assertEqual('logs', ns_.log_dir)
        self.assertEqual(55555, ns_.port)
        self.assertFalse(ns_.showTimestamp)
        self.assertFalse(ns_.showVersion)
        self.assertFalse(ns_.testing)
        self.assertEqual(now, ns_.timestamp)
        self.assertTrue(ns_.verbose)

if __name__ == '__main__':
    unittest.main()
