from flask import Flask, render_template, request, redirect, url_for
from PIL import Image, ImageDraw, ImageFont
from base64 import b64encode
from hashlib import sha512
#import time
import sys
import re
import io

app = Flask(__name__)
#perhaps not needed if avoiding file saves
filename = ""
#hashed pattern for encoding
pattern = []
#is either 
#input_image = Image
#only needed when incoding
#text_image = Image
#either encoded or decoded image
#output_image = Image

@app.route('/')
def index():
    """ website form """
    # TODO: add optional error message
    # TODO: random password generator from brute force library

    return render_template('index.html')

@app.route('/imja', methods=['POST'])
def imja():
    codetype = request.form.get('codetype')
    password = request.form.get('password')
    message = request.form.get('message')
    image = request.files['image']
    #print(f'type:{codetype} pw:{password} msg:{message} img:{image}')
    # TODO: Error checking, will message fit! else reload '/' with optional error msg
    
    #DEV: Open image data is scoped. Opening it here doesn't make it available to child functions

    #covert password into bytes > Hashword(bytes) returns SHA512 > Pattern(SHA512) to create list that we use to encode our image pixel by pixel
    Pattern(HashWord(password.encode()))
    #filename = str(int(time.time())) + hashedWords[:1]
    #print(filename)

    if codetype == "Encode":
        t_image = DrawText(image, message)
        o_image = Encode(image, t_image)
    elif codetype == "Decode":
        o_image = Decode(image)
    else:
        #TODO add error message
        return redirect(url_for('index'))

    img_byte_arr = io.BytesIO()
    o_image.save(img_byte_arr, format='PNG')
    img_byte_arr = img_byte_arr.getvalue()

    encoded = b64encode(img_byte_arr)
    mime = "image/png"
    uri = "data:%s;base64,%s" % (mime, encoded)

    return render_template('image.html', uri= uri)
    #return redirect(url_for('index')) #or rather, redirect to the image

def HashWord(words):
    hashedWords = sha512(words).hexdigest()
    return(hashedWords)

def Pattern(hashedWords):
    ints = []
    #break the hash into 2 digit sequences (HEX)
    ints = re.findall('..', hashedWords)
    #Combine items into an interable list so that we can call two items per loop
    pairints = iter(ints)
    #Convert each pair of ints from hex to int, and add the pair creating a 9 bit integer
    #print (len(ints))
    for num in pairints:
        i = int(num,16) #Hex2Int(num)
        j = int(next(pairints),16) #Hex2Int(next(pairints))
        k = i + j
        Ox = bin(k)

        #break hex into individual channels
        # while len(Ox) < 11:
        #     temp = Ox[:2]+"0"+Ox[2:]
        #     Ox = temp
        # OxR = Ox[2:5]
        # OxG = Ox[5:8]
        # OxB = Ox[8:]
        R = k >> 6
        G = (k & 56) >> 3
        B = (k & 7)
        pattern.append( (R, G, B) )
        #print(f'i:{i} j:{j} k:{k} 0x:{Ox} 0xR:{OxR} 0xG:{OxG} 0xB:{OxB} R:{R} G:{G} B:{B}')
    #return pattern #global variable

def DrawText(image, message):
    input_image = Image.open(image)
    text_image = Image.new('L', input_image.size, color = (0))

    x_size, y_size = input_image.size
    #print(x_size, y_size)
    #print(pattern) #testing if we can see the pattern
    '''
    each character is appx:
    7 pixels in length. as 62 char in an image width of 435 fit perfectly.
    13 pixels in height. as 20 lines in an image height of 276 fit perfectly with no black space following.
    '''
    #constants to calculate number of characters that will fit within the image, and where line breaks will be inserted
    _N = int(x_size/7) #characters before new line is inserted
    _E = int(y_size/13) #vertical limit of characters
    text_length = len(message)
    if (_N*_E) < text_length:
        sys.exit(f'The message({text_length}) is too long to fit within the image({_N*_E})')
    text_lines = 0 #vertical lines of text
    while text_length - _N*text_lines > _N:
        #increment text_lines aka lines of vertical text
        text_lines+=1
        #calculate where we insert the linebreak (max_characters_per_line * lines + #_of_line_breaks(invisible characters that add to the index length))
        newLine_index = _N*text_lines+(1*(text_lines-1))
        #add line break by making a new string
        add_line = message[:newLine_index]+'\n'+message[newLine_index:]
        #strings are immutable in Python, so we re-write the new text back into our variable
        message = add_line
        #recalculate the length of our text MINUS 2 characters that denote each new line
        text_length = len(message)-(text_lines*2)
        #12345678901234567890
        #1 3 5 7 90 2 4 6 8 0

    text_font = ImageFont.truetype('/Library/Fonts/Courier.dfont', 12)
    text_draw = ImageDraw.Draw(text_image)
    text_draw.text((0,0), message, font=text_font, fill=(255))
    
    #text_image.save(f'./text/{filename}.png')
    return text_image

def Encode(image, t_image): #Does the text_image data get stored in the global? or do we need to pass that info
    index = 0 #32
    input_image = Image.open(image)
    text_image = t_image #Image.open(f'./text/{filename}.png')

    # Create a new PIL image with the same size as the encoded image:
    output_image = Image.new("RGB", input_image.size)
    x_size, y_size = input_image.size
    tx_size, ty_size = text_image.size
    #allow us to center the text
    y_offset = int((y_size - ty_size) * 0.5)
    x_offset = int((x_size - tx_size) * 0.5)
    #print (f'Y_offset:{y_offset} X_offset:{x_offset}')

    for i, pixel in enumerate(input_image.getdata()):
        textPixel = text_image.getdata()
        #print(f'{pixel:0b}')
        pixelX = i % x_size
        pixelY = int(i / x_size)

        #Images are encoded backwards, we want to split accordingly
        #get colors of image
        #print (pixel)
        (b,g,r,a) = pixel
        #center text into image with offset
        if pixelX >= x_offset and pixelX < (tx_size + x_offset) and pixelY >= y_offset and pixelY < (ty_size+y_offset):
            #get colors of text
            #current pixel in smaller image, as width SHOULD be smaller
            x = (pixelY - y_offset) * tx_size + (pixelX - x_offset)
            #print(f'X:{pixelX} Y:{pixelY} x:{x}')
            #Check if our color is not black, if so adjust our target image
            if textPixel[x] != 0:
                #if text white apply pattern
                #{color} & 1111 1000 => | 00000{pattern}
                #print (f' r:{bin(r)[2:]} mask:{bin(248)[2:]} &:{ bin(r & 248) } pattern:{bin(pattern[index][0])} finalR:{bin((r&248)|pattern[index][0])}')
                '''
                value 248 keeps everything above 7, it zeroes out the 3 least sig bits
                pattern[index] will fill in these least sig bits
                '''
                r = (r & 248) | pattern[index][0]
                g = (g & 248) | pattern[index][1]
                b = (b & 248) | pattern[index][2]
            else:
                #if text black ensure not of pattern, do NOT make 000,000,000
                #(red ONLY) f'{color:0b}'.endswith( str( pattern[:-1] ) ):
                    #if {color} < 255 +=1
                    #-=1
                if f'{r:0b}'.endswith(f'{bin(pattern[index][0])[-1]}'):
                    if r < 255:
                        r +=1
                    else :
                        r -=1
        else:
            #not doing anything with additional outside of the text area
            pass
        
        output_image.putpixel((pixelX, pixelY), (b,g,r))
        #increase index, and repeat over our pattern
        index += 1
        if index >= 32:
            index = 0
    
    #option to black empty spaces, How to determine empty text area? or dont touch... Grey color in encode.
    #> optionaly check for grey, depends on encoding

    #output_image.save(f'./output/{filename}.png')
    return output_image

def Decode(image):
    index = 0
    input_image = Image.open(image)

    # Create a new PIL image with the same size as the encoded image:
    decoded_image = Image.new("RGB", input_image.size)
    x_size, y_size = input_image.size

    for i, pixel in enumerate(input_image.getdata()):
        #print(f'{pixel:0b}')
        pixelX = i % x_size
        pixelY = int(i / x_size)

        #Images are encoded backwards, we want to split accordingly
        #get colors of image
        (b,g,r,a) = pixel
        #Check if our color (Big Masked) matches the indexed pattern
        '''
        value 7 masks the 3 least sig bits to compare to our pattern (0 - 7)
        '''
        #print (f'maskedR:{r&7} indexedR:{pattern[index][0]}')
        if (r&7) == pattern[index][0] and (g&7) == pattern[index][1] and (b&7) == pattern[index][2]:
            decoded_image.putpixel((pixelX,pixelY), (255,255,255))#(b,g,r))

        index += 1
        if index >= 32:
            index = 0
    
    #decoded_image.save(f'./decode/{filename}.png')
    return decoded_image

if __name__ == '__main__':
    app.run(debug=True)