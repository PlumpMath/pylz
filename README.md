# Lempel-Ziv via Coroutines

This is a byte-level implementation of Lempel-Ziv in which each block contains some number of bytes to reference its known-prefix and exactly one new-byte.

- Blocks refer to their known-prefix with absolute addressing.
- The first block has no reference to a prefix.
- The last block may or may not have a new-byte.

This program does not perform error correction at this time, so don't entrust your important data to it.

-- [PLR](http://f06mote.com)

---

Requires Python 3.2.2
