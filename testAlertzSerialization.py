#!/usr/bin/python3

# testAlertzSerialization.py
import time, unittest
from io     import StringIO

from rnglib import SimpleRNG

from fieldz.parser import StringProtoSpecParser
import fieldz.fieldTypes    as F
import fieldz.msgSpec       as M
import fieldz.typed         as T
from fieldz.chan    import Channel
from fieldz.msgImpl import makeMsgClass, makeFieldClass, MsgImpl

from alertzProtoSpec       import ALERTZ_PROTO_SPEC

BUFSIZE = 16*1024
rng     = SimpleRNG( time.time() )

class TestAlertzSerialization (unittest.TestCase):

    def setUp(self):
        data = StringIO(ALERTZ_PROTO_SPEC)
        p    = StringProtoSpecParser(data)   # data should be file-like
        self.sOM        = p.parse()     # object model from string serialization
        self.protoName  = self.sOM.name # the dotted name of the protocol

    def tearDown(self):
        pass

    # utility functions #############################################
    def zoneMismatchFields(self):
        """ returns a list """
        timestamp       = rng.nextInt32()
        seqNbr          = rng.nextInt32()
        zoneName        = rng.nextFileName(8)
        expectedSerial  = rng.nextInt32()
        actualSerial    = rng.nextInt32()
        while actualSerial == expectedSerial:
            actualSerial    = rng.nextInt32()

        # NOTE that this is a list
        return [timestamp, seqNbr, zoneName, expectedSerial, actualSerial]

    def corruptListFields(self):
        timestamp       = rng.nextInt32()
        seqNbr          = rng.nextInt32()
        remarks         = rng.nextFileName(16)  # so 1 to 16 characters
        return [timestamp, seqNbr, remarks]

    # actual unit tests #############################################

    def testZoneMismatchMsg(self):
        # -----------------------------------------------------------
        # XXX This code has been crudely hacked from another test 
        # module, and so needs careful review
        # -----------------------------------------------------------

        # verify that this adds 1 (msg) + 3 (field count) to the number
        # of entries in getters, putters, etc
        
        self.assertIsNotNone(self.sOM)
        self.assertTrue(isinstance(self.sOM, M.ProtoSpec))
        self.assertEquals( 'org.xlattice.alertz', self.sOM.name )

        self.assertEquals(0,  len(self.sOM.enums) )
        self.assertEquals(16, len(self.sOM.msgs) )
        self.assertEquals(0,  len(self.sOM.seqs) )

        msgSpec = self.sOM.msgs[0]
        msgName = msgSpec.name
        self.assertEquals('zoneMismatch', msgName)
        
        # Create a channel ------------------------------------------
        # its buffer will be used for both serializing # the instance 
        # data and, by deserializing it, for creating a second instance.
        chan = Channel(BUFSIZE)
        buf  = chan.buffer
        self.assertEquals( BUFSIZE, len(buf) )

        # create the ZoneMismatchMsg class ------------------------------
        ZoneMismatchMsg     = makeMsgClass(self.sOM, msgName)

        # create a message instance ---------------------------------
        values  = self.zoneMismatchFields()        # list of quasi-random values
        zmmMsg  = ZoneMismatchMsg( values )
        
        self.assertEquals(msgSpec.name, zmmMsg.name)
        # we don't have any nested enums or messages
        self.assertEquals(0, len(zmmMsg.enums))
        self.assertEquals(0, len(zmmMsg.msgs))

        self.assertEquals(5, len(zmmMsg.fieldClasses))
        self.assertEquals(5, len(zmmMsg))        # number of fields in instance
        for i in range(len(zmmMsg)):
            self.assertEquals(values[i], zmmMsg[i].value)

        # serialize the object to the channel -----------------------

        # XXX WRITE HEADER FIRST!
        
        # DEBUG
        print("DIR (ZMM_MSG): ", end=' ') 
        print(dir(zmmMsg))
        # END
        zmmMsg.writeStandAlone(chan)
        chan.flip()

        # deserialize the channel, making a clone of the message ----
        (readBack, n2) = MsgImpl.read(chan, self.sOM) 
        self.assertIsNotNone(readBack)

        # DEBUG
        print("position after mis-match read back is %d" % chan.position)
        # END

        # verify that the messages are identical --------------------
        self.assertTrue(zmmMsg.__eq__(readBack))

        # produce another message from the same values --------------
        zmmMsg2  = ZoneMismatchMsg( values )
        chan2   = Channel(BUFSIZE)
        zmmMsg2.writeStandAlone(chan2)
        chan2.flip()

        (copy2,n3)   = MsgImpl.read(chan2, self.sOM)
        self.assertTrue(zmmMsg.__eq__(copy2))
        self.assertTrue(zmmMsg2.__eq__(copy2))       # GEEP
        
    def testCorruptListMsg(self):
        # -----------------------------------------------------------
        # XXX This code has been crudely hacked from another test 
        # module, and so needs careful review
        # -----------------------------------------------------------

        # verify that this adds 1 (msg) + 3 (field count) to the number
        # of entries in getters, writeStandAlones, etc
        
        msgSpec = self.sOM.msgs[1]          # <------
        msgName = msgSpec.name
        self.assertEquals('corruptList', msgName)
        
        # Create a channel ------------------------------------------
        # its buffer will be used for both serializing # the instance 
        # data and, by deserializing it, for creating a second instance.
        chan = Channel(BUFSIZE)
        buf  = chan.buffer
        self.assertEquals( BUFSIZE, len(buf) )

        # create the CorruptListMsg class ------------------------------
        CorruptListMsg     = makeMsgClass(self.sOM, msgName)

        # create a message instance ---------------------------------
        values  = self.corruptListFields()        # list of quasi-random values
        clMsg   = CorruptListMsg( values )
        
        self.assertEquals(msgSpec.name, clMsg.name)
        # we don't have any nested enums or messages
        self.assertEquals(0, len(clMsg.enums))
        self.assertEquals(0, len(clMsg.msgs))

        self.assertEquals(3, len(clMsg.fieldClasses))   # <---
        self.assertEquals(3, len(clMsg))        # number of fields in instance
        for i in range(len(clMsg)):
            self.assertEquals(values[i], clMsg[i].value)

        # serialize the object to the channel -----------------------
        clMsg.writeStandAlone(chan)
        chan.flip()

        # deserialize the channel, making a clone of the message ----
        (readBack,n4) = MsgImpl.read(chan, self.sOM) 
        self.assertIsNotNone(readBack)

        # DEBUG
        print("position after corrupt list read back is %d" % chan.position)
        # END

        # verify that the messages are identical --------------------
        self.assertTrue(clMsg.__eq__(readBack))

        # produce another message from the same values --------------
        clMsg2  = CorruptListMsg( values )
        chan2   = Channel(BUFSIZE)
        clMsg2.writeStandAlone(chan2)
        chan2.flip()

        (copy2,n4)  = MsgImpl.read(chan2, self.sOM)
        self.assertTrue(clMsg.__eq__(copy2))
        self.assertTrue(clMsg2.__eq__(copy2))       # GEEP
        
    def testShutdownMsg(self):
        # -----------------------------------------------------------
        # XXX This code has been crudely hacked from another test 
        # module, and so needs careful review
        # -----------------------------------------------------------

        # verify that this adds 1 (msg) + 3 (field count) to the number
        # of entries in getters, writeStandAlones, etc
        
        msgSpec = self.sOM.msgs[2]          # <------
        msgName = msgSpec.name
        self.assertEquals('shutdown', msgName)
        
        # Create a channel ------------------------------------------
        # its buffer will be used for both serializing # the instance 
        # data and, by deserializing it, for creating a second instance.
        chan = Channel(BUFSIZE)
        buf  = chan.buffer
        self.assertEquals( BUFSIZE, len(buf) )

        # create the CorruptListMsg class ------------------------------
        ShutdownMsg     = makeMsgClass(self.sOM, msgName)

        # create a message instance ---------------------------------
        values  = [ rng.nextFileName(8), ] # list of quasi-random values
        sdMsg   = ShutdownMsg( values )
        
        self.assertEquals(msgName, sdMsg.name)
        # we don't have any nested enums or messages
        self.assertEquals(0, len(sdMsg.enums))
        self.assertEquals(0, len(sdMsg.msgs))

        self.assertEquals(1, len(sdMsg.fieldClasses))   # <---
        self.assertEquals(1, len(sdMsg))        # number of fields in instance
        for i in range(len(sdMsg)):
            self.assertEquals(values[i], sdMsg[i].value)

        # serialize the object to the channel -----------------------
        sdMsg.writeStandAlone(chan)
        chan.flip()

        # deserialize the channel, making a clone of the message ----
        (readBack,n5) = MsgImpl.read(chan, self.sOM) 
        self.assertIsNotNone(readBack)

        # DEBUG
        print("position after shutdown read back is %d" % chan.position)
        # END

        # verify that the messages are identical --------------------
        self.assertTrue(sdMsg.__eq__(readBack))

        # produce another message from the same values --------------
        sdMsg2  = ShutdownMsg( values )
        chan2   = Channel(BUFSIZE)
        sdMsg2.writeStandAlone(chan2)
        chan2.flip()

        (copy2,n6)   = MsgImpl.read(chan2, self.sOM)
        self.assertTrue(sdMsg.__eq__(copy2))
        self.assertTrue(sdMsg2.__eq__(copy2))       # GEEP
        

if __name__ == '__main__':
    unittest.main()
