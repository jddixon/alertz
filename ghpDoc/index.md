<h1 class="libTop">alertz</h1>
**alertz** is a Python3-based system for reporting events over a
network of machines, some on a local network (a cluster of machines
behind a firewall) and other machines on the global Internet.  As
conceived at the moment, the latter are virtual machines on Amazon's
[AWS EC2](http://aws.amazon.com/ec2) cloud.  Participating servers communicate
using messages in standard formats.  These are specified using either
Google's
[Protocol Buffers](http://developers.google.com/protocol-buffers)
or (more likely) the
[fieldz](https://jddixon.github.io/fieldz)
protocol, which is meant to be compatible with Protocol Buffers.

alertz is still being specified.

## Message Types

Initially these relate to

* network partitioning
* DNS errors
* hacking attempts

All message types carry a UTC timestamp, a 32-bit value.  Many or most
message types will include an optional, possibly zero-length, remarks
section.

### DNS Errors

Some of the alertz-connected machines on the global Internet act as
[name servers](https://en.wikipedia.org/wiki/Name_server).
Each of these should report the same information on receiving a
zone request.  The name servers are monitored by a utility (not part of
this project) which periodically requests zone information for domains
handled by the name servers.  If the information is not as expected,
a **zoneMismatch** message is sent over the alertz system.

The utility monitoring the name servers relies a **zoneList**, a list
of domain names to check.  If this has internally inconsistent, the
utiltiy sends a **corruptZoneList** alert, signifying that the utility
has failed and cannot proceed without some intervention.

### Hacking Attempts

If a participating machine detects an attemtpted hack attack, it can
send a **badGuy** alert giving the UTC time of the attempt, the
originating IP address and port, and the target address and port number.

The software for detecting such hacking attempts and that for handling them
is not part of the alertz system.

### Network Partitioning

This can occur for a number of reasons, but the most likely is that
the firewall router is down or has the wrong IP address.  If such a
conditon is detected, a **newGWAddr** alert is sent.

## Underlying Messaging System

[ZeroMQ](http://zeromq.org).  This is a mature, fast, distributed
messaging system with implementations in a variety of programming
languages.

## Dependencies

* [fieldz](https://jddixon.github.io/fieldz)
* [ZeroMQ](http://zeromq.org)

## Project Status

Pre-alpha.  The specification is tentative and incomplete.  Code and unit
tests exist, but some tests fail.

