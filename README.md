![Logo of the project](https://github.com/Genji-MS/imja/blob/main/assets/Imja.png)

# IMJA

> Stegonagraphy - encrypting a hidden text message in an image

Using a SHA512 hash, Imja (IMage ninJA) will encode a secret message across the ~~three~~ two least significant bits of an images 'RGB' color channels, pixel by pixel. Only by entering the same 'password' can the same SHA512 be generated to decode the image.


## Version History:

- V1.4
    - Images of type 'P' (Palatted) are converted to RGB when Encoding
    - non-RGB images are converted to RGB when Decoding to prevent crashes
    - Live demo updated on Heroku from V1.1 to V1.4

- V1.3
    - Hash changed to no longer combine hex values (0-15)
    - Uses a modified algo to only modify the 2 least significant bits of an image
    - Images created prior to V1.3 can not be decoded in V1.3+
    - Increased font fidelity by storing 8 shades of grey in the least sig bit
    - JS front-end to allow for dynamic text box for user input
    - Deprecates fixed font size, imported font, and word wrap
    - On image load, displays the file dimensions & adjusts the drawable text area
    - Dockerized deployment taken offline as version was outdated

- V1.2
    - Dockeized and Deployed

- V1.1
    - Restructured files/folders to deploy on Heroku
    - Refactord a new route with a long single function to prevent issues on Heroku

- V1.0
    - Takes in user input, Uses a monospaced font to fill in image area adding linebreaks as needed
    - Creates a hash from a password adding two hex values (0 - 511)
    - Encodes image using 3 least sig bits of 3 color channels = 9 bits
    - Uses Flask to create Front-end HTML

## Confidentiality by using a data URI

Imja outputs images using an embedded URI. Nothing is saved to disk or stored server side

- URI wiki: https://en.wikipedia.org/wiki/Data_URI_scheme
- A Data URI consists of:
 ```data:[<media type>][;base64],<data>```

## Limitations

- Rich text, HTML, and other code is not supported in the message. Any/All Special characters will appear as text

- IMJA supports only .png images without transparency
- 'RGBA' images will be converted to 'RGB'

- Modifying an image after it has been encoded will compromise the hidden message quality

- Images of any size are supported up to the URI character length of ~2,083 (browser limitation)

- ~~Encoded text is fixed at 7px x 13px per character~~
- ~~A message greater then the image width will be auto-wrapped by character~~
- ~~A message greater then the available image size will have visible clipping with a detailed warning of the character limit~~
- ~~Zooming into a decoded image is recommended to read the text~~

- URI's are not supported at the base level on some browzers. Opening an image in another tab may cause an error

- Encoding/Decoding a message with no image attached will result in an unhandled exception (browser error)

## DEMO

Imja is deployed on Heroku and free to use
https://imja.herokuapp.com/

~~The Dockerized version is deployed at~~
~~https://imja.dev.genji.games/~~


### What's inside:

- Flask - Backend
https://flask.palletsprojects.com/en/1.1.x/

- PIL - Pillow - Python Imaging Library
https://pillow.readthedocs.io/en/stable/

- Hashlib - Secure hashes and message digests
https://docs.python.org/3/library/hashlib.html

- Base64 - binary-to-text encoding
https://en.wikipedia.org/wiki/Base64

- BytesIO - produces bytes objects
https://docs.python.org/3/library/io.html

- re - Regex
https://docs.python.org/3/library/re.html

- Fabric.js - front end & textbox
http://fabricjs.com

### Licensing

No license is granted

### Contact information

Genji.Tapia@students.makeschool.com