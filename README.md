# pylz

This is a byte-level Lempel-Ziv implementation in Python3. The encoder and decoder are implemented as coroutines which accumulate bytes until there is enough information to send bytes to the next processing stage.

The interface is similar to a subset of the gzip interface. To find out more, run:

    $ python3 lz.py -h

* **lz.py** is the main program and has the encoder and decoder logic.
* **cr.py** contains coroutine utility functions including a coroutine compositor.
* **ints.py** has functions to convert python integers to and from binary (as bytes objects).
* **progress.py** isn't currently used but contains code to display a progress bar in the terminal.

#### Lempel-Ziv implementation details

- Each block contains some number of bytes to reference its known-prefix and exactly one new-byte.
- Blocks refer to their known-prefix with absolute addressing.
- The first block has no bytes to reference a prefix.
- The last block won't have a new-byte if the encoder didn't reach unique data.

#### Other notes

- It's naive! It will compress text moderately, but not most other things.
- It's slow! Suggestions are appreciated.
- No error correction is performed. Decoding corrupt data results in a crash.

Enjoy!

-- [PLR](http://f06mote.com)

---

Requires Python 3.2.2
