from flask import Flask, render_template, request, jsonify
from PIL import Image, ImageDraw
from base64 import b64encode, b64decode
from hashlib import sha512
from io import BytesIO
import re

app = Flask(__name__, static_url_path='', static_folder='assets')
pattern = [] #hashed pattern for encoding
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
def index_encode(uri = "/Imja.png", msg = ""):
    # TODO: random password generator from brute force library
    return render_template('encode.html', uri=uri, msg=msg)

@app.route('/imja')
def index_decode(uri = "/Imja.png", msg = ""):
    return render_template('decode.html', uri=uri, msg=msg)

@app.route('/encodeJS', methods=['POST'])
def image_encode_JS():
    image = request.form['image_data']
    password = request.form['password_data'][1:-1] #Trim the first and last characters of ' " " '
    message = request.form['message_data']
    #print(f'image pulled: {image}\npassword_pulled: {password}\nmessage pulled: {message}')
    Pattern(HashWord(password.encode()))
    #u_image = b64decode(str(image))
    #t_image = b64decode(str(message))
    '''WARNING, Do not Regex an image URI, for some reason it will crash!!!!
    regex = r'(.+,)|(")'
    subst = ""
    u_image = re.sub(regex, subst, image, 0)'''
    #Remove the base64 header and trailing "
    u_image = image[23:-1]
    t_image = message[23:-1]

    #This creates local files
    u_image = b64decode(u_image)
    # filename = 'user_image.png'  # I assume you have a way of picking unique filenames
    # with open(filename, 'wb') as f: #"w"rite and "b"inary
    #     f.write(u_image)
    t_image = b64decode(t_image)
    # filename = 'text_image.png'  # I assume you have a way of picking unique filenames
    # with open(filename, 'wb') as f: #"w"rite and "b"inary
    #     f.write(t_image)
    #o_image = Encode('user_image.png','text_image.png')

    o_image = Encode(u_image,t_image)

    img_byte_arr = BytesIO()
    o_image.save(img_byte_arr, format='PNG')
    img_byte_arr = b64encode(img_byte_arr.getvalue())

    img_string = str(img_byte_arr)
    regex = r"(b')|(')"
    subst = ""
    img_string = re.sub(regex, subst, img_string, 0)

    mime = "image/png"
    uri = f'data:{mime};base64,{img_string}'

    return jsonify(uri)

@app.route('/decode', methods=['POST'])
def image_decode():
    password = request.form.get('password')
    image = request.files['image']
    msg = ""
    print(f'password_pulled: {password}')
    #DEV: Open image data is scoped. Opening it here doesn't make it available to child functions

    #covert password into bytes > Hashword(bytes) returns SHA512 > Pattern(SHA512) to create list that we use to encode our image pixel by pixel
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
    pattern.clear() #If the variable isn't cleared it will continue to stack values from previous entries
    for num in hashedWords:
        i = int(num,16)%8 #Hex2Int(num)
        #break hex into individual channels, search for match in the 2nd bit
        R = (i & 4) >> 1
        G = (i & 2)
        B = (i & 1) << 1
        pattern.append( (R, G, B) )
        #print(f'i:{i}  R:{R} G:{G} B:{B}')
    #return pattern #global variable

def Encode(image, t_image): #Does the text_image data get stored in the global? or do we need to pass that info
    index = 0
    #assume to convert as images of type 'P'alleted can be written as type .png, but contain 1 color channel
    #https://stackoverflow.com/questions/52307290/what-is-the-difference-between-images-in-p-and-l-mode-in-pil
    input_image = Image.open(BytesIO(image)).convert('RGB')
    #input_image = Image.open(image)
    #print(f'mime type: {input_image.get_format_mimetype()})
    #print(f'opened as {input_image.mode}')

    text_image = Image.open(BytesIO(t_image))
    #text_image = Image.open(t_image) #text_image = t_image #Image.open(f'./text/{filename}.png')
    #Convert text image to Greyscale, as it will import as RGBA
    text_image = text_image.convert('L')

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
        if i == 0:
            print (pixel)
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
                #print (textPixel[x])
                for w in range(0,8,1):
                    if textPixel[x] <= whites[w]:
                        #print(w)
                        r += whites_dict[w][0]
                        g += whites_dict[w][1]
                        b += whites_dict[w][2]
                        break
            else:
                #if text black ensure not of pattern, do NOT modify the image to be of (text)black color! 

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
        if index >= 128:
            index = 0
    
    return output_image

def Decode(image):
    index = 0
    #to prevent errors from users importing images of single channel
    input_image = Image.open(image).convert('RGB')
    # print(f'opened as {input_image.mode}')

    # Create a new PIL image with the same size as the encoded image:
    decoded_image = Image.new("L", input_image.size)
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
            decoded_image.putpixel((pixelX,pixelY), (color))#(b,g,r))

        index += 1
        if index >= 128: #32
            index = 0
    
    #decoded_image.save(f'./decode/{filename}.png')
    return decoded_image

if __name__ == '__main__':
    app.run(debug=True)