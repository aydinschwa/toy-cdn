import struct
from dataclasses import dataclass
from enum import Enum


def encode_domain_name(domain_name: str) -> bytes:
    encoded_domain_name = b""
    parts = domain_name.split(".") # split on dots
    lengths = [len(part) for part in parts] # get length of part
    for part, length in zip(parts, lengths):
        encoded_domain_name += struct.pack("!B", length) + part.encode() 
    encoded_domain_name += b"\x00"
    return encoded_domain_name

def extract_domain_name(buffer, pos):
    words = []
    jumped = False
    original_pos = pos
    
    while True:
        length = buffer[pos]
        
        # Check if this is a compression pointer (top 2 bits set)
        if length & 0xC0 == 0xC0:
            # Calculate offset from the two bytes
            offset = ((length & 0x3F) << 8) | buffer[pos + 1]
            if not jumped:
                original_pos = pos + 2  # Save where to continue after
            pos = offset
            jumped = True
            continue
        
        if length == 0:
            break
            
        pos += 1
        word = buffer[pos:pos + length].decode()
        words.append(word)
        pos += length
    
    # Return position after the name (or after the pointer if we jumped)
    end_pos = original_pos if jumped else pos + 1
    return ".".join(words), end_pos

def ip_to_bytes(ip_address: str) -> bytes:
    return bytes((int(octet) for octet in ip_address.split(".")))

@dataclass
class DnsHeader():
    packet_id: int
    flags: int
    qcount: int
    acount: int
    authcount: int
    addcount: int
    opcode: int
    rcode: int

    def to_bytes(self):
        return struct.pack("!HHHHHH", self.packet_id, self.flags, self.qcount, \
            self.acount, self.authcount, self.addcount)

@dataclass
class DnsQuestion():
    domain_name: str
    record_type: int
    record_class: int

    def to_bytes(self):
        return encode_domain_name(self.domain_name) + \
            struct.pack("!HH", self.record_type, self.record_class)

@dataclass
class DnsRecord():
    domain_name: str
    record_type: int
    record_class: int
    ttl: int 
    record_length: int
    ip_address: str # only applicable for A records

    def to_bytes(self):
        return encode_domain_name(self.domain_name) + \
            struct.pack("!HHIH", self.record_type, self.record_class, self.ttl, self.record_length) + \
            ip_to_bytes(self.ip_address)

class ResultCode(Enum):
    NOERROR = 0
    FORMERR = 1
    SERVFAIL = 2
    NXDOMAIN = 3
    NOTIMP = 4
    REFUSED = 5

    def __str__(self):
        return self.name
            
class RecordType(Enum):
    A = 1

    def __str__(self):
        return self.name



# This implementation ONLY handles A records for now!
class DnsQueryPacket():
    def __init__(self, buffer):
        if len(buffer) > 512:
            raise Exception(f"Invalid length for DNS packet: {len(buffer)}")
        self.buffer = buffer
        self.pos = 12 # start at the tip of the dns header

        # parse DNS header
        packet_id, flags, qcount, acount, authcount, addcount = struct.unpack("!HHHHHH", self.buffer[:self.pos])
        # grab the info I care about from the flags
        opcode = (flags >> 11) & 0x0F
        rcode = flags & 0x0F

        self.header = DnsHeader(packet_id, flags, qcount, acount, authcount, addcount, opcode, rcode)

        # parse DNS question
        # apparently it's possible to request multiple records in one go, but frowned upon in practice
        # my implementation will not handle multiple questions   
        # if qcount > 1:
        #     get mad, maybe raise a formerror?

        domain_name, self.pos = extract_domain_name(self.buffer, self.pos)

        record_type, record_class = struct.unpack("!HH", self.buffer[self.pos: self.pos + 4])
        self.pos += 4

        self.question = DnsQuestion(domain_name, record_type, record_class)

    def encode_packet(self):
        return self.header.to_bytes() + self.question.to_bytes()


def build_dns_response(query: DnsQueryPacket, ip_address: str, ttl: int) -> bytes:
    response = b""
    header = DnsHeader(
        packet_id=query.header.packet_id,
        flags=query.header.flags | 0x8000,  # flip QR bit
        qcount=1,
        acount=1,
        authcount=0,
        addcount=0,
        opcode=query.header.opcode,
        rcode=0
    )
    response += header.to_bytes()

    response += query.question.to_bytes()

    answer = DnsRecord(
        domain_name = query.question.domain_name,
        record_type = query.question.record_type,
        record_class = query.question.record_class,
        ttl = ttl,
        # this assumes I'm only returning A records
        record_length = 4,
        ip_address = ip_address
    )

    response += answer.to_bytes()

    return response  

def build_refused_response(query: DnsQueryPacket) -> bytes:
    # RCODE is the low 4 bits of flags
    # 5 = REFUSED, 4 = NOTIMP (not implemented)
    flags = query.header.flags | 0x8000  # QR bit
    flags = (flags & 0xFFF0) | 5  # set RCODE to REFUSED
    
    header = DnsHeader(
        packet_id=query.header.packet_id,
        flags=flags,
        qcount=1,
        acount=0,  # no answers
        authcount=0,
        addcount=0,
        opcode=query.header.opcode,
        rcode=5
    )

    return header.to_bytes() + query.question.to_bytes()