# PyAndSafe

A GUI to decrypt and read export files from [AndSafe](https://play.google.com/store/apps/details?id=net.clarenceho.andsafe).

You can also verify the encryption algorithm used by AndSafe by checking the `cipher.py`.
256-bit keys are derived from SCrypt and used to encrypt content with AES in CBC mode.

## How to use

You will need Python 3 to run PyAndSafe.

1. Clone the project

```
git clone https://github.com/kitsook/PyAndSafe.git
```

2. Create a Python virtualenv and install necessary packages

```
cd PyAndSafe
python3 -m venv venv
. venv/bin/activate
pip install -r requirements.txt
```

3. Start the application by running
```
python main.py
```
Follow the prompt to select an export file and input password to decrypt the content.
