# ~/dev/py/alertz/alertz/chanIO.py

""" Send and receive messages on a connection. """

import socket

from wireops.enum import PrimTypes
from wireops.raw import read_field_hdr, read_raw_varint

from alertz import BUFSIZE

__all__ = ['recv_from_cnx', 'send_on_cnx', 'send_to_end_point', ]


def recv_from_cnx(cnx, chan):
    """
    Receive a serialized message from a connection into a channel.

    On return the channel has been flipped (offset = 0, limit =
    data length).  Returns the msgNbr.
    """

    # ---------------------------------------------------------------
    # SEE fieldz.msgImpl for an example of this kind of Channel
    # manipulation.  Use a Python buffer to select the region of the
    # buffer we want to write into.
    # ---------------------------------------------------------------

    # receive something from the connection
    chan.clear()
    count = cnx.recv_into(chan.buffer, BUFSIZE)
    if count <= 0:
        raise IOError('initial read of message gets zero bytes')

    # read the header to determine the message type and its length
    (p_type, msg_nbr) = read_field_hdr(chan)
    # DEBUG
    print("CHAN_IO: count = %d; pType = %s, msgNbr = %s" % (
        count, p_type, msg_nbr))
    # END
    if p_type != PrimTypes.LEN_PLUS:
        raise IOError(
            'message header type is %d, not PrimTypes.LEN_PLUS' %
            p_type)
    # XXX raise exception of msgNbr <0 or msgNbr > 2

    msg_len = read_raw_varint(chan)

    # XXX ignoring pathological possibility that offset > count

    # if we don't have all of the data, loop getting the rest
    while count < msg_len:
        # vBuf = buffer(chan.buffer, count)
        v_buf = memoryview(chan.buffer)[count:]
        count += cnx.recv_into(v_buf, BUFSIZE - count)
    chan.position = count
    chan.flip()
    return msg_nbr


def send_on_cnx(chan, cnx):
    """
    Send a serialized message from a channel over an existing connection.

    Suitable for use by servers sending replies or clients continuing a
    conversation.
    """
    _, _ = chan, cnx
    # pass        # XXX STUB


def send_to_end_point(chan, host, port):
    """
    Send a serialized message from a channel over a new connection.

    Suitable for use by clients sending a first message to a server.
    """
    if not host:
        raise IOError('null or empty host name')
    if port < 0 or port > 65535:
        raise IOError("port number '%d' is out of range" % port)
    skt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    skt.connect((host, port))
    # DEBUG
    print("SEND_TO_END_POINT: host %s port %s limit %s" % (
        host, port, chan.limit))
    # END
    #vBuf = buffer(chan.buffer, 0, chan.limit)
    v_buf = memoryview(chan.buffer)[0:chan.limit]
    skt.sendall(v_buf)               # raises exception on error
    return skt                      # the sender has to close it
