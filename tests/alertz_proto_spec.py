# ~/dev/py/pzog/alertzProto.py

ALERTZ_PROTO_SPEC = """protocol org.xlattice.alertz

# ===================================================================
# ONLY ADD NEW MESSAGE TYPES TO THIS SECTION BY APPENDING THEM!
# The order of declaration of these types is meaningful.
# ===================================================================

# CHECK_ZONE MESSAGES from magick -----------------------------------
# the serial number found in the DNS does not match our zone files.
message zoneMismatch:
 timestamp      fuint32
 seqNbr         vuint32
 zoneName       lstring     # @0: alphanumeric only
 expectedSerial vuint32
 actualSerial   vuint32

# the zone list file itself is corrupt
message corruptZoneList:
 # get the IP address of the reporting host from the connection
 timestamp      fuint32
 seqNbr         vuint32
 remarks        lstring     # initially zero-length

message shutdown:
 remarks        lstring     # goodbye message, null should be OK

# ===================================================================
# DO NOT USE MESSAGE TYPES BELOW THIS LINE
# These message types are not yet being used; until they are moved
# into the section above, can edit and move types and insert new types
# freely.
# ===================================================================

# MISC MESSAGES -----------------------------------------------------
message ack:
 remarks        lstring     # null should be OK

message bye:
 remarks        lstring     # null should be OK

message ok:
 remarks        lstring     # null should be OK

# CHECK_IP_ADDR MESSAGES from guadalupe -----------------------------
message newGWAddr:
 timestamp      fuint32
 seqNbr         vuint32
 oldIPV4Addr    lstring
 newIPV4Addr    lstring

# CLJ PARSEABILITY from magick and LA and/or PA ---------------------
# Need to avoid flood of such messages

message unparseableCLJIndexPage:
 # get the IP address of the reporting host from the connection
 timestamp      fuint32
 seqNbr         vuint32
 url            lstring

message unparseableCLJPosting:
 # get the IP address of the reporting host from the connection
 timestamp      fuint32
 seqNbr         vuint32
 url            lstring

# CV SERVER MESSAGES ------------------------------------------------
message cvNibble:
 timestamp      fuint32
 seqNbr         vuint32
 prospectID     fbytes20
 ipv4Addr       lstring

 # want to trace path through site

# HOST PING/SSH/BROWSEABILITY ---------------------------------------
message hostUnreachable:
 # if network is split, source (reporting host) is significant
 timestamp      fuint32
 seqNbr         vuint32
 ipv4Addr       lstring

# mail servers --------------------------------------------
message mailServerNotUp:
 timestamp      fuint32
 seqNbr         vuint32
 ipv4Addr       lstring
 port           vuint32

# name servers --------------------------------------------
message nameServerNotUp:
 timestamp      fuint32
 seqNbr         vuint32
 ipv4Addr       lstring
 port           vuint32

# web servers ---------------------------------------------
message webServerNotUp:
 timestamp      fuint32
 seqNbr         vuint32
 ipv4Addr       lstring
 port           vuint32

message webPageBadHash:
 timestamp      fuint32
 seqNbr         vuint32
 url            lstring
 expectedHash   fbytes20
 actualHash     fbytes20

# hacker activity reports ---------------------------------
# Presumably sent because of frequent hits from the addr; if activity
# is DOS, then these messages might exacerbate the problem.
message badGuy:
 timestamp      fuint32
 seqNbr         vuint32
 fromAddr       lstring
 fromPort       vuint32
 toAddr         lstring
 toPort         vuint32

"""
