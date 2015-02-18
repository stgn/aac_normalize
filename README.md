aac_normalize
=============

Removes undesired channel configurations from AAC streams (ADTS format only) that contain more than one. Requires Python 2.7, [click](http://click.pocoo.org/), and [bitstring](https://code.google.com/p/python-bitstring/).

Usage
-----

    # aac_normalize.py --help
    Usage: aac_normalize.py [OPTIONS] NULL_FRAME INPUT OUTPUT

    Options:
      -s, --switch-pad  Insert null frame on channel configuration switch to
                        compensate for gaps in the original transport stream.
      --help            Show this message and exit.

Why?
----

Some television stations switch format parameters of the audio stream instead of up/downmixing when broadcasting material with different channel configurations one after another. Unfortunately, handling of this behavior is poorly defined, causing issues with many decoders since it typically requires reinitialization of the decoder and renderer on every switch.

How?
----

Using a *null frame* file (i.e. a file containing a single silent AAC frame) as reference, the tool goes through the input stream and replaces any frames that do not match the channel configuration of the null frame with the null frame itself, effectively silencing them. The rest of the frames are passed through untouched.

You must create the null frame file yourself. For maximum compatibility, extract a frame from your input stream that you would like to use as the null frame. You may also use your favorite encoder to generate a null frame, but a stream containing frames from different encoders may cause issues (although usually benign) with certain decoders.