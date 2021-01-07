from flask import Flask, render_template, request, redirect, url_for
from PIL import Image, ImageDraw, ImageFont
from base64 import b64encode
from hashlib import sha512
from io import BytesIO
import re

app = Flask(__name__)
pattern = [] #hashed pattern for encoding
#above black 2>66 = 0, 67 > 107 = 1 ...
whites = [66,107,141,184,209,221,244,255]
whites_dict = {
    0:[0,0,0],
    1:[0,0,1],
    2:[0,1,0],
    3:[0,1,1],
    4:[1,0,0],
    5:[1,0,1],
    6:[1,1,0],
    7:[1,1,1]
}

@app.route('/')
def index_encode(uri = "/static/Imja.png", msg = ""):
    # TODO: random password generator from brute force library
    return render_template('encode.html', uri=uri, msg=msg)

@app.route('/imja')
def index_decode(uri = "/static/Imja.png", msg = ""):
    return render_template('decode.html', uri=uri, msg=msg)

@app.route('/heroku', methods=['POST'])
def HerokuEncode():
    """This function does everything in one go in an attempt to avoid consecutive file.open(file) issues with Heroku"""
    msg = ""
    password = request.form.get('password')
    if password == "":
        msg += f'  WARNING! No password provided.'
    message = request.form.get('message')
    if message == "" or message == None:
        msg += f'  ATTENTION! No message written!'
    image = request.files['image']    
    Pattern(HashWord(password.encode()))

    input_image = Image.open(image)
    if input_image.mode == 'RGBA':
        input_image = input_image.convert('RGB')
    text_image = Image.new('L', input_image.size, color = (0))
    x_size, y_size = input_image.size
    _N = int(x_size/7) #characters before new line is inserted
    _E = int(y_size/13) #vertical limit of characters
    text_length = len(message)
    if (_N*_E) < text_length:
        msg =f'  ALERT!!! The message({text_length}) was too long to fit within the image area({_N*_E}). Use a bigger image, or a smaller message'
    text_lines = 0 #vertical lines of text
    while text_length - _N*text_lines > _N:
        text_lines+=1
        newLine_index = _N*text_lines+(1*(text_lines-1))
        add_line = message[:newLine_index]+'\n'+message[newLine_index:]
        message = add_line
        text_length = len(message)-(text_lines*2)
    #HEROKU friendly path

    #CUSTOM FONT is disabled as it throws 'ImportError: The _imagingft C module is not installed' in docker
    #text_font = ImageFont.truetype('/app/assets/fonts/Courier.dfont', 12)
    text_draw = ImageDraw.Draw(text_image)
    #text_draw.text((0,0), message, font=text_font, fill=(255))
    text_draw.text((0,0), message, fill=(255))
 
    index = 0 #32
    output_image = Image.new("RGB", input_image.size)
    tx_size, ty_size = text_image.size
    y_offset = int((y_size - ty_size) * 0.5)
    x_offset = int((x_size - tx_size) * 0.5)
    for i, pixel in enumerate(input_image.getdata()):
        textPixel = text_image.getdata()
        pixelX = i % x_size
        pixelY = int(i / x_size)
        (b,g,r) = pixel
        if pixelX >= x_offset and pixelX < (tx_size + x_offset) and pixelY >= y_offset and pixelY < (ty_size+y_offset):
            x = (pixelY - y_offset) * tx_size + (pixelX - x_offset)
            if textPixel[x] != 0:
                r = (r & 248) | pattern[index][0]
                g = (g & 248) | pattern[index][1]
                b = (b & 248) | pattern[index][2]
            else:
                if f'{r:0b}'.endswith(f'{bin(pattern[index][0])[-1]}'):
                    if r < 255:
                        r +=1
                    else :
                        r -=1      
        output_image.putpixel((pixelX, pixelY), (b,g,r))
        index += 1
        if index >= 32:
            index = 0
    
    img_byte_arr = BytesIO()
    output_image.save(img_byte_arr, format='PNG')
    img_byte_arr = b64encode(img_byte_arr.getvalue())
    img_string = str(img_byte_arr)
    regex = r"(b')|(')"
    subst = ""
    img_string = re.sub(regex, subst, img_string, 0)
    mime = "image/png"
    uri = f'data:{mime};base64,{img_string}'
    return render_template('encode.html', uri= uri, msg=msg)

@app.route('/encode', methods=['POST'])
def image_encode():
    msg = ""
    password = request.form.get('password')
    if password == "":
        msg += f'  WARNING! No password provided.'
    message = request.form.get('message')
    if message == "" or message == None:
        msg += f'  ATTENTION! No message written!'
    image = request.files['image']    

    #DEV: Open image data is scoped. Opening it here doesn't make it available to child functions

    #covert password into bytes > Hashword(bytes) returns SHA512 > Pattern(SHA512) to create list that we use to encode our image pixel by pixel
    Pattern(HashWord(password.encode()))
    t_image, error = DrawText(image, message)
    #append to the error messages
    msg += error
    o_image = Encode(image, t_image)

    img_byte_arr = BytesIO()
    o_image.save(img_byte_arr, format='PNG')
    img_byte_arr = b64encode(img_byte_arr.getvalue())

    img_string = str(img_byte_arr)
    regex = r"(b')|(')"
    subst = ""
    img_string = re.sub(regex, subst, img_string, 0)

    mime = "image/png"
    uri = f'data:{mime};base64,{img_string}'

    return render_template('encode.html', uri= uri, msg=msg)

@app.route('/decode', methods=['POST'])
def image_decode():
    password = request.form.get('password')
    image = request.files['image']
    msg = ""
    
    #DEV: Open image data is scoped. Opening it here doesn't make it available to child functions

    #covert password into bytes > Hashword(bytes) returns SHA512 > Pattern(SHA512) to create list that we use to encode our image pixel by pixel
    #
    Pattern(HashWord(password.encode()))
    o_image = Decode(image)

    img_byte_arr = BytesIO()
    o_image.save(img_byte_arr, format='PNG')
    img_byte_arr = b64encode(img_byte_arr.getvalue())

    #remove quotes
    img_string = str(img_byte_arr)
    regex = r"(b')|(')"
    subst = ""
    img_string = re.sub(regex, subst, img_string, 0)

    mime = "image/png"
    uri = f'data:{mime};base64,{img_string}'

    return render_template('decode.html', uri= uri, msg=msg)

def HashWord(words):
    hashedWords = sha512(words).hexdigest()
    return(hashedWords)

def Pattern(hashedWords):
    #convert the hash into sequence of digits 0-7
    for num in hashedWords:
        i = int(num,16)%8 #Hex2Int(num)
        #break hex into individual channels, search for match in the 2nd bit
        R = (i & 4) >> 1
        G = (i & 2)
        B = (i & 1) << 1
        pattern.append( (R, G, B) )
        #print(f'i:{i}  R:{R} G:{G} B:{B}')
    #return pattern #global variable

def DrawText(image, message):
    input_image = Image.open(image)
    text_image = Image.new('L', input_image.size, color = (0))

    x_size, y_size = input_image.size

    '''
    each character is appx:
    7 pixels in length. as 62 char in an image width of 435 fit perfectly.
    13 pixels in height. as 20 lines in an image height of 276 fit perfectly with no black space following.
    '''
    #constants to calculate number of characters that will fit within the image, and where line breaks will be inserted
    _N = int(x_size/7) #characters before new line is inserted
    _E = int(y_size/13) #vertical limit of characters
    text_length = len(message)
    msg = ""
    if (_N*_E) < text_length:
        msg =f'  ALERT!!! The message({text_length}) was too long to fit within the image area({_N*_E}). Use a bigger image, or a smaller message'
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

    text_font = ImageFont.truetype('/assets/fonts/Courier.dfont', 12)
    text_draw = ImageDraw.Draw(text_image)
    text_draw.text((0,0), message, font=text_font, fill=(255))
    
    #text_image.save(f'./text/{filename}.png')
    return text_image, msg

def Encode(image, t_image): #Does the text_image data get stored in the global? or do we need to pass that info
    index = 0
    input_image = Image.open(image)
    #print(f'opened as {input_image.mode}')
    if input_image.mode == 'RGBA':
        input_image = input_image.convert('RGB')
        #print(f'converted to ‘{input_image.mode}')
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
        (b,g,r) = pixel
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
                value 252 keeps everything above 3, it zeroes out the 2 least sig bits
                pattern[index] will fill in these least sig bits
                bit 2 is the pattern
                bit 1 is the shade of white 
                '''
                r = (r & 252) | pattern[index][0]
                g = (g & 252) | pattern[index][1]
                b = (b & 252) | pattern[index][2]
                #print (f'r:{r} g:{g} b:{b}')
                #set shade of white, check color of white pixel and store that info to the closest of 8 shades of white
                print (textPixel[x])
                for w in range(0,8,1):
                    if textPixel[x] <= whites[w]:
                        print(w)
                        r += whites_dict[w][0]
                        g += whites_dict[w][1]
                        b += whites_dict[w][2]
                        break
            else:
                #if text black ensure not of pattern, do NOT modify the image to be of (text)black color! 

                #old versions of if statement, reference for working with the .endswith method
                #(red ONLY) f'{color:0b}'.endswith( str( pattern[:-1] ) ):
                #f'{r}'.endswith(f'{bin(pattern[index][0])[-1]}'):

                #print (f'a:{(r & 2)} b:{pattern[index][0]} ={(r & 2) == pattern[index][0]}')
                #bugs were present with (r & 2)... and trailing in-line comments even though the print above works
                if (r&2) == pattern[index][0]:
                    if r < 254:
                        r +=2
                    else:
                        r -=2
        else:
            #not doing anything with additional outside of the text area
            pass
        
        output_image.putpixel((pixelX, pixelY), (b,g,r))
        #increase index, and repeat over our pattern
        index += 1
        # prevously was 32, because that is the length of sha512/2 as we combined every other hex
        if index >= 64:
            index = 0
    
    #output_image.save(f'./output/{filename}.png')
    return output_image

def Decode(image):
    index = 0
    input_image = Image.open(image)
    print(f'opened as {input_image.mode}')
    if input_image.mode == 'RGBA':
        input_image = input_image.convert('RGB')
        #print(f'converted to ‘{input_image.mode}')

    # Create a new PIL image with the same size as the encoded image:
    decoded_image = Image.new("RGB", input_image.size)
    x_size, y_size = input_image.size

    for i, pixel in enumerate(input_image.getdata()):
        #print(f'{pixel:0b}')
        pixelX = i % x_size
        pixelY = int(i / x_size)
        #Images are encoded backwards, we want to split accordingly
        (b,g,r) = pixel
        #Check if our color (Bit Masked) matches the indexed pattern
        '''
        value 2 masks the 2nd least sig bit to compare to our pattern
        '''
        #print (f'maskedR:{r&7} indexedR:{pattern[index][0]}')
        if (r&2) == pattern[index][0] and (g&2) == pattern[index][1] and (b&2) == pattern[index][2]:
            #Set color shade
            color = whites[(r&1)*4+(g&1)*2+(b&1)]
            decoded_image.putpixel((pixelX,pixelY), (color,color,color))#(b,g,r))

        index += 1
        if index >= 64: #32
            index = 0
    
    #decoded_image.save(f'./decode/{filename}.png')
    return decoded_image

if __name__ == '__main__':
    app.run(debug=True)