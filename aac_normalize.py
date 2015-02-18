#!/usr/bin/env python

import click
from sys import exit
from functools import partial
from bitstring import Bits, BitArray

@click.command()
@click.option('--switch-pad', '-s', is_flag=True, 
              help='Insert null frame on channel configuration switch '
              'to compensate for gaps in the original transport stream.')
@click.argument('null_frame', type=click.File('rb'))
@click.argument('input', type=click.File('rb'))
@click.argument('output', type=click.File('wb'))

def normalize(input, output, null_frame, switch_pad):
    crc_vbr_offsets = tuple([15,] + range(43, 54))
    prev_channels = None
    null_frame = null_frame.read()
    
    out_channels, = Bits(bytes=null_frame[:7]).unpack('pad:23, uint:3')
    
    for hdr in iter(partial(input.read, 7), ''):
        bs = BitArray(bytes=hdr)   
            
        sync, channels, length = bs.unpack('uint:12, pad:11, uint:3, pad:4, uint:13')
        if sync != 0xfff:
            exit('Error: ADTS syncword not found.')
        
        if prev_channels != channels:
            if switch_pad and prev_channels:
                output.write(null_frame)
            prev_channels = channels
        
        length -= 7
        if channels != out_channels:
            output.write(null_frame)
            input.seek(length, 1)
        else:
            bs.set(False, (12, 26))
            if not bs[15]:
                # ignore crc, adjust frame length
                bs.overwrite(Bits(uint=length + 5, length=13), 30)
                input.seek(2, 1)
                length -= 2
            # mark crc absent, vbr
            bs.set(True, crc_vbr_offsets)
            output.write(bs.tobytes())
            output.write(input.read(length))
            
if __name__ == '__main__':
    normalize()