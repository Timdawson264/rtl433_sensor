#!/bin/env python3

from bitarray import bitarray, util
import bitarray
import msgpack
import os
import base64
import paho.mqtt.client as mqtt

symbols = bytearray.fromhex("0d 0e 13 15 16 19 1a 1c 23 25 26 29 2a 2c 32 34")

#payload = "b152cb2cbb2cb2c5b15a659559558b70bb0b00"
payload = "7162cb2cbb2cb2cc7265c39a55969a2ec71a2ec65c5b155969ac5ab2a2ea2e971c0"

def symbol_6to4( symbol ):
    #print("Decode, byte, start", hex(symbol), (symbol>>2)&(1<<4), 16)
    res = bytearray(1)
    for i in range( (symbol>>2)&(1<<4) , 16):
        if symbol == symbols[i]:
            res[0] = i
            return res
    print("symbol error")
    return None  # Not found


def decode_payload( payload ):
    bit_payload = bitarray.util.hex2ba(payload)
    
    print( "Decoding bytes expect:", len(bit_payload) , "From bits:", len(bit_payload) )

    output = bytearray()

    for i in range(0, len(bit_payload)  , 12):
        if( i+12 > len(bit_payload) ): continue

        #print("Decoding 1 byte", i, i+12)
        rxBits_raw = bit_payload[ i: i+12 ]
        
        bitsHigh = rxBits_raw[ 0:6 ]
        bitsLow  = rxBits_raw[ 6:12 ]
        
        #reverse endian, pad to 8bits and shift right
        bitsHigh.reverse()
        bitsLow.reverse()
        bitsHigh.fill()
        bitsLow.fill() 
        bitsHigh >>=2
        bitsLow >>=2

        #print( bitsLow.tobytes().hex() , bitsHigh.tobytes().hex()  )

        h_nib = symbol_6to4( bitsHigh.tobytes()[0] )
        l_nib = symbol_6to4( bitsLow.tobytes()[0] )
        if( l_nib is None or h_nib is None):
            #Bad symbol
            return
        res_b = bytearray(1)
        res_b[0] = h_nib[0]<<4 | l_nib[0]
        output.extend( res_b )

    return output


def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("rtl_433/+/devices/radiohead_msgpak/rows/+/data")

#https://gist.github.com/oysstu/68072c44c02879a2abf94ef350d1c7c6
def crc16(data: bytes, poly=0x8408):
    '''
    CRC-16-CCITT Algorithm
    '''
    data = bytearray(data)
    crc = 0xFFFF
    for b in data:
        cur_byte = 0xFF & b
        for _ in range(0, 8):
            if (crc & 0x0001) ^ (cur_byte & 0x0001):
                crc = (crc >> 1) ^ poly
            else:
                crc >>= 1
            cur_byte >>= 1
    crc = (~crc & 0xFFFF)
    crc = (crc << 8) | ((crc >> 8) & 0xFF)
    
    return crc & 0xFFFF

def verify_checksum( data: bytes ):
    pkt_crc_bits = bitarray.bitarray(endian='big')
    pkt_crc_bits.frombytes( data[-2:] )
    pkt_crc16 = hex(bitarray.util.ba2int(pkt_crc_bits))
    rx_crc16 = hex(crc16( data[: - 2] ))

    return rx_crc16==pkt_crc16

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    print(msg.topic+" "+str(payload))
    mp_payload = decode_message( msg.payload )
    client.publish("/msgpack/payload", payload=str(mp_payload) , qos=0, retain=False)

def decode_message(payload):
    
    decoded = decode_payload( payload  )

    if not verify_checksum( decoded ):
        print( f"bad checksum pkt: calc"  )
        return None

    pkt = {
        "data_len": int(decoded[0]) - 6 ,
        "to": decoded[1:2].hex(),
        "from": decoded[2:3].hex(),
        "id": decoded[3:4].hex(),
        "flags": decoded[4:5].hex(),
        "data": decoded[5:-2],
        "crc16": decoded[-2:].hex()

    }

    print(pkt)

    data_len = pkt["data_len"]
    data_mp = msgpack.unpackb( pkt["data"][0:data_len] )
    return data_mp


#decode_message(payload)

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect("mqtt", 1883, 60)
client.loop_forever()





