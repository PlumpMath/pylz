# Lempel-Ziv via Coroutines

This is a byte-level Lempel-Ziv implementation in Python3 via coroutines.

- Each block contains some number of bytes to reference its known-prefix and exactly one new-byte.
- Blocks refer to their known-prefix with absolute addressing.
- The first block has no bytes to reference a prefix.
- The last block won't have a new-byte if the encoder didn't reach unique data.
- No error correction is performed. Incorrect data results in a crash.

The encoder and decoder are implemented as coroutines which accumulate bytes until there is enough information to send bytes to the next processing stage.

**lz.py** is the main program and has the encoder and decoder logic.
**cr.py** contains coroutine utility functions including a coroutine composition function.  
**ints.py** has functions to convert python integers to and from binary (as bytes objects).
**progress.py** isn't currently used but contains code to display a progress bar on the terminal.

-- [PLR](http://f06mote.com)

---

Requires Python 3.2.2
