# ~/dev/py/pzog/alertzProto.py

ALERTZ_PROTO_SPEC = """protocol org.xlattice.alertz

# ===================================================================
# ONLY ADD NEW MESSAGE TYPES TO THIS SECTION BY APPENDING THEM! 
# The order of declaration of these types is meaningful.
# ===================================================================

# CHECK_ZONE MESSAGES from magick -----------------------------------
# the serial number found in the DNS does not match our zone files.
message zoneMismatch:
 timestamp      fuInt32
 seqNbr         vuInt32
 zoneName       lString     # @0: alphanumeric only
 expectedSerial vuInt32
 actualSerial   vuInt32

# the zone list file itself is corrupt
message corruptList:
 # get the IP address of the reporting host from the connection
 timestamp      fuInt32
 seqNbr         vuInt32
 remarks        lString     # initially zero-length

message shutdown:
 remarks        lString     # goodbye message, null should be OK

# ===================================================================
# DO NOT USE MESSAGE TYPES BELOW THIS LINE 
# These message types are not yet being used; until they are moved
# into the section above, can edit and move types and insert new types 
# freely.
# ===================================================================

# MISC MESSAGES -----------------------------------------------------
message ack:
 remarks        lString     # null should be OK

message bye:
 remarks        lString     # null should be OK

message ok:
 remarks        lString     # null should be OK

# CHECK_IP_ADDR MESSAGES from guadalupe -----------------------------
message newGuadalupeGWAddr:
 timestamp      fuInt32
 seqNbr         vuInt32
 oldIPV4Addr    lString
 newIPV4Addr    lString

# CLJ PARSEABILITY from magick and LA and/or PA ---------------------
# Need to avoid flood of such messages

message unparseableCLJIndexPage:
 # get the IP address of the reporting host from the connection
 timestamp      fuInt32
 seqNbr         vuInt32
 url            lString

message unparseableCLJPosting:
 # get the IP address of the reporting host from the connection
 timestamp      fuInt32
 seqNbr         vuInt32
 url            lString

# CV SERVER MESSAGES ------------------------------------------------
message cvNibble:
 timestamp      fuInt32
 seqNbr         vuInt32
 prospectID     fBytes20
 ipv4Addr       lString

 # want to trace path through site

# HOST PING/SSH/BROWSEABILITY ---------------------------------------
message hostUnreachable:
 # if network is split, source (reporting host) is significant
 timestamp      fuInt32
 seqNbr         vuInt32
 ipv4Addr       lString

# mail servers --------------------------------------------
message mailServerNotUp: 
 timestamp      fuInt32
 seqNbr         vuInt32
 ipv4Addr       lString
 port           vuInt32

# name servers --------------------------------------------
message nameServerNotUp: 
 timestamp      fuInt32
 seqNbr         vuInt32
 ipv4Addr       lString
 port           vuInt32

# web servers ---------------------------------------------
message webServerNotUp: 
 timestamp      fuInt32
 seqNbr         vuInt32
 ipv4Addr       lString
 port           vuInt32

message webPageBadHash: 
 timestamp      fuInt32
 seqNbr         vuInt32
 url            lString
 expectedHash   fBytes20
 actualHash     fBytes20

# hacker activity reports ---------------------------------
# Presumably sent because of frequent hits from the addr; if activity
# is DOS, then these messages might exacerbate the problem.
message badGuy: 
 timestamp      fuInt32
 seqNbr         vuInt32
 fromAddr       lString
 fromPort       vuInt32
 toAddr         lString
 toPort         vuInt32

"""
