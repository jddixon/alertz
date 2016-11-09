#!/usr/bin/env python3

# testAlertzSerialization.py
import time
import unittest
from io import StringIO
from importlib import reload        # <---------------------
from rnglib import SimpleRNG

from fieldz.parser import StringProtoSpecParser
from fieldz.field_types import FieldTypes as F, FieldStr as FS
import fieldz.msg_spec as M
import fieldz.typed as T
from fieldz.chan import Channel
from fieldz.msg_impl import make_msg_class, make_field_class, MsgImpl

#import alertz_proto_spec
# reload(alertz_proto_spec)
from alertz_proto_spec import ALERTZ_PROTO_SPEC

BUFSIZE = 16 * 1024
RNG = SimpleRNG(time.time())


class TestAlertzSerialization(unittest.TestCase):

    def setUp(self):
        #       data = StringIO(ALERTZ_PROTO_SPEC)
        #       str_ps_parser = StringProtoSpecParser(data) # data must be file-like
        #       # object model from string serialization
        #       self.str_obj_model = str_ps_parser.parse()
        # self.proto_name = self.str_obj_model.name  # dotted name of protocol

        data = StringIO(ALERTZ_PROTO_SPEC)

        print("AAA")

        str_ps_parser = StringProtoSpecParser(data)  # data must be file-like

        print("BBB")

        # object model from string serialization
        self.str_obj_model = str_ps_parser.parse()

        print("CCC")

        self.proto_name = self.str_obj_model.name  # dotted name of protocol

        print("NNN")

    def tearDown(self):
        pass

    # utility functions #############################################
    def zone_mismatch_fields(self):
        """ returns a list """
        timestamp = RNG.next_int32()
        seq_nbr = RNG.next_int32()
        zone_name = RNG.next_file_name(8)
        expected_serial = RNG.next_int32()
        actual_serial = RNG.next_int32()
        while actual_serial == expected_serial:
            actual_serial = RNG.next_int32()

        # NOTE that this is a list
        return [timestamp, seq_nbr, zone_name, expected_serial, actual_serial]

    def corrupt_list_fields(self):
        timestamp = RNG.next_int32()
        seq_nbr = RNG.next_int32()
        remarks = RNG.next_file_name(16)  # so 1 to 16 characters
        return [timestamp, seq_nbr, remarks]

    # actual unit tests #############################################

    def test_zone_mismatch_msg(self):
        # DEBUG
        print("\nTEST_ZONE_MISMATCH_MSG")
        # END

        # from setUp(): =============================================

        # end stuff from setup ======================================

        # -----------------------------------------------------------
        # XXX This code has been crudely hacked from another test
        # module, and so needs careful review
        # -----------------------------------------------------------

        # verify that this adds 1 (msg) + 3 (field count) to the number
        # of entries in getters, putters, etc

        self.assertIsNotNone(self.str_obj_model)
        self.assertTrue(isinstance(self.str_obj_model, M.ProtoSpec))
        self.assertEqual('org.xlattice.alertz', self.str_obj_model.name)

        self.assertEqual(0, len(self.str_obj_model.enums))
        self.assertEqual(16, len(self.str_obj_model.msgs))
        self.assertEqual(0, len(self.str_obj_model.seqs))

        msg_spec = self.str_obj_model.msgs[0]
        msg_name = msg_spec.name
        self.assertEqual('zoneMismatch', msg_name)

        # Create a channel ------------------------------------------
        # its buffer will be used for both serializing # the instance
        # data and, by deserializing it, for creating a second instance.
        chan = Channel(BUFSIZE)
        buf = chan.buffer
        self.assertEqual(BUFSIZE, len(buf))

        # create the ZoneMismatchMsg class ------------------------------
        zone_mismatch_msg_cls = make_msg_class(self.str_obj_model, msg_name)

        # create a message instance ---------------------------------
        values = self.zone_mismatch_fields()        # list of quasi-random values
        zmm_msg = zone_mismatch_msg_cls(values)

        self.assertEqual(msg_spec.name, zmm_msg._name)
        # we don't have any nested enums or messages
        self.assertEqual(0, len(zmm_msg.enums))
        self.assertEqual(0, len(zmm_msg.msgs))

        self.assertEqual(5, len(zmm_msg.field_classes))
        self.assertEqual(5, len(zmm_msg))        # number of fields in instance
        self.assertEqual(values[0], zmm_msg.timestamp)
        self.assertEqual(values[1], zmm_msg.seq_nbr)
        self.assertEqual(values[2], zmm_msg.zone_name)
        self.assertEqual(values[3], zmm_msg.expected_serial)
        self.assertEqual(values[4], zmm_msg.actual_serial)

        # serialize the object to the channel -----------------------

        # XXX WRITE HEADER FIRST!

        # DEBUG
        print("DIR (ZMM_MSG): ", end=' ')
        print(dir(zmm_msg))
        # END
        zmm_msg.write_stand_alone(chan)
        chan.flip()

        # deserialize the channel, making a clone of the message ----
        (read_back, nn2) = MsgImpl.read(chan, self.str_obj_model)
        self.assertIsNotNone(read_back)

        # DEBUG
        print("position after mis-match read back is %d" % chan.position)
        # END

        # verify that the messages are identical --------------------
        self.assertTrue(zmm_msg.__eq__(read_back))

        # produce another message from the same values --------------
        zmm_msg2 = zone_mismatch_msg_cls(values)
        chan2 = Channel(BUFSIZE)
        zmm_msg2.write_stand_alone(chan2)
        chan2.flip()

        (copy2, nn3) = MsgImpl.read(chan2, self.str_obj_model)
        self.assertTrue(zmm_msg.__eq__(copy2))
        self.assertTrue(zmm_msg2.__eq__(copy2))       # GEEP

    def test_corrupt_list_msg(self):

        # DEBUG
        print("\nTEST_CORRUPT_LIST_MSG")
        # END

        # -----------------------------------------------------------
        # XXX This code has been crudely hacked from another test
        # module, and so needs careful review
        # -----------------------------------------------------------

        # verify that this adds 1 (msg) + 3 (field count) to the number
        # of entries in getters, writeStandAlones, etc

        msg_spec = self.str_obj_model.msgs[1]          # <------
        msg_name = msg_spec.name
        self.assertEqual('corruptZoneList', msg_name)

        # Create a channel ------------------------------------------
        # its buffer will be used for both serializing # the instance
        # data and, by deserializing it, for creating a second instance.
        chan = Channel(BUFSIZE)
        buf = chan.buffer
        self.assertEqual(BUFSIZE, len(buf))

        # create the CorruptListMsg class ------------------------------
        corrupt_list_msg_cls = make_msg_class(self.str_obj_model, msg_name)

        # create a message instance ---------------------------------
        values = self.corrupt_list_fields()        # list of quasi-random values
        cl_msg = corrupt_list_msg_cls(values)

        self.assertEqual(msg_spec.name, cl_msg._name)
        # we don't have any nested enums or messages
        self.assertEqual(0, len(cl_msg.enums))
        self.assertEqual(0, len(cl_msg.msgs))

        self.assertEqual(3, len(cl_msg.field_classes))   # <---
        self.assertEqual(3, len(cl_msg))        # number of fields in instance
        self.assertEqual(values[0], cl_msg.timestamp)
        self.assertEqual(values[1], cl_msg.seq_nbr)
        self.assertEqual(values[2], cl_msg.remarks)

        # serialize the object to the channel -----------------------
        cl_msg.write_stand_alone(chan)
        chan.flip()

        # deserialize the channel, making a clone of the message ----
        (read_back, nn4) = MsgImpl.read(chan, self.str_obj_model)
        self.assertIsNotNone(read_back)

        # DEBUG
        print("position after corrupt list read back is %d" % chan.position)
        # END

        # verify that the messages are identical --------------------
        self.assertTrue(cl_msg.__eq__(read_back))

        # produce another message from the same values --------------
        cl_msg2 = corrupt_list_msg_cls(values)
        chan2 = Channel(BUFSIZE)
        cl_msg2.write_stand_alone(chan2)
        chan2.flip()

        (copy2, nn4) = MsgImpl.read(chan2, self.str_obj_model)
        self.assertTrue(cl_msg.__eq__(copy2))
        self.assertTrue(cl_msg2.__eq__(copy2))       # GEEP GEEP

    def test_shutdown_msg(self):
        # DEBUG
        print("\nTEST_SHUTDOWN_MSG")
        # END

        # -----------------------------------------------------------
        # XXX This code has been crudely hacked from another test
        # module, and so needs careful review
        # -----------------------------------------------------------

        # verify that this adds 1 (msg) + 3 (field count) to the number
        # of entries in getters, writeStandAlones, etc

        msg_spec = self.str_obj_model.msgs[2]          # <------
        msg_name = msg_spec.name
        self.assertEqual('shutdown', msg_name)

        # Create a channel ------------------------------------------
        # its buffer will be used for both serializing # the instance
        # data and, by deserializing it, for creating a second instance.
        chan = Channel(BUFSIZE)
        buf = chan.buffer
        self.assertEqual(BUFSIZE, len(buf))

        # create the CorruptListMsg class ------------------------------
        shutdown_msg_cls = make_msg_class(self.str_obj_model, msg_name)

        # create a message instance ---------------------------------
        values = [RNG.next_file_name(8), ]  # list of quasi-random values
        sd_msg = shutdown_msg_cls(values)

        self.assertEqual(msg_name, sd_msg._name)
        # we don't have any nested enums or messages
        self.assertEqual(0, len(sd_msg.enums))
        self.assertEqual(0, len(sd_msg.msgs))

        self.assertEqual(1, len(sd_msg.field_classes))   # <---
        self.assertEqual(1, len(sd_msg))        # number of fields in instance
        self.assertEqual(values[0], sd_msg.remarks)

        # serialize the object to the channel -----------------------
        sd_msg.write_stand_alone(chan)
        chan.flip()

        # deserialize the channel, making a clone of the message ----
        (read_back, nn5) = MsgImpl.read(chan, self.str_obj_model)
        self.assertIsNotNone(read_back)

        # DEBUG
        print("position after shutdown read back is %d" % chan.position)
        # END

        # verify that the messages are identical --------------------
        self.assertTrue(sd_msg.__eq__(read_back))

        # produce another message from the same values --------------
        sd_msg2 = shutdown_msg_cls(values)
        chan2 = Channel(BUFSIZE)
        sd_msg2.write_stand_alone(chan2)
        chan2.flip()

        (copy2, nn6) = MsgImpl.read(chan2, self.str_obj_model)
        self.assertTrue(sd_msg.__eq__(copy2))
        self.assertTrue(sd_msg2.__eq__(copy2))       # GEEP GEEP GEEP


if __name__ == '__main__':
    unittest.main()
