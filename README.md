# PyAndSafe

A GUI to decrypt and read export files from [AndSafe](https://play.google.com/store/apps/details?id=net.clarenceho.andsafe).

You can also verify the encryption algorithm used by AndSafe by checking the `cipher.py`.
256-bit keys are derived from SCrypt and used to encrypt content with AES in CBC mode.
