#!/usr/bin/python3

# ~/dev/py/alertz/zmqlogger.py

"""
Hacked from pyzmq/examples/zmglogger.py:

Simple example of using zmq log handlers

This starts a number of subprocesses with PUBHandlers that generate
log messages at a regular interval.  The main process has a SUB socket,
which aggregates and logs all of the messages to the root logger.
"""

import logging
from multiprocessing import Process
import os
import random
import sys
import time

import zmq
from zmq.log.handlers import PUBHandler

LOG_LEVELS = (
    logging.DEBUG,
    logging.INFO,
    logging.WARN,
    logging.ERROR,
    logging.CRITICAL)


def sub_logger(port, level=logging.DEBUG):
    ctx = zmq.Context()
    # pylint can't cope with the way zmq sets 'constants'
    # pylint: disable=no-member
    sub = ctx.socket(zmq.SUB)
    sub.bind('tcp://127.0.0.1:%i' % port)

    # pylint: disable=no-member
    sub.setsockopt(zmq.SUBSCRIBE, "")
    logging.basicConfig(level=level)

    while True:
        # XXX 2017-02-02 THIS MAY BE AN ERROR: zmq.Socket.recv_multipart
        # returns one value, and that is a list of Frames or bytes.
        # I also find a number of lines like
        #    msg = subscriber.recv_multipart()
        # which also doesn't match the pattern in the next line.
        # Per readthedocs it returns a list.
        level, message = sub.recv_multipart()
        if message.endswith('\n'):
            # trim trailing newline, which will get appended again
            message = message[:-1]
        log = getattr(logging, level.lower())
        log(message)


def log_worker(port, interval=1, level=logging.DEBUG):
    ctx = zmq.Context()
    import fieldz.reg as R
    # pylint: disable=no-member
    pub = ctx.socket(zmq.PUB)
    pub.connect('tcp://127.0.0.1:%i' % port)

    logger = logging.getLogger(str(os.getpid()))
    logger.setLevel(level)
    handler = PUBHandler(pub)
    logger.addHandler(handler)
    print("starting logger at %i with level=%s" % (os.getpid(), level))

    while True:
        level = random.choice(LOG_LEVELS)

        logger.log(level, "Hello from %i!" % os.getpid())
        time.sleep(interval)


def main():
    if len(sys.argv) > 1:
        ndx = int(sys.argv[1])
    else:
        ndx = 2

    port = 5555

    # start the log generators
    workers = [
        Process(
            target=log_worker, args=(
                port,), kwargs=dict(
                    level=random.choice(LOG_LEVELS))) for i in range(ndx)]
    [worker.start() for worker in workers]

    # start the log watcher
    try:
        sub_logger(port)
    except KeyboardInterrupt:
        pass
    finally:
        for worker in workers:
            worker.terminate()

if __name__ == '__main__':
    main()
