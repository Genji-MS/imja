from hashlib import sha512
from PIL import Image, ImageDraw
import re

filename = ""
pattern = []
#83e331c3b883b3fb6904bd12b9cfbaa68f9f1d3e9675cbc0cefd0a008867dfc403331a5548313ee19691eaa1d0e2ee8e8168caf4d507a62a150771f73654e68f

def HashWord(words):
    hashedWords = sha512(words).hexdigest()
    return(hashedWords)

def Hex2Int(HeX):
    return int(HeX,16)

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

        R = k >> 6
        G = (k & 56) >> 3
        B = (k & 7)
        #break hex into individual channels visually as 'binary strings' *NOT FOR ACTUAL USE*
        # while len(Ox) < 11:
        #     temp = Ox[:2]+"0"+Ox[2:]
        #     Ox = temp
        # OxR = Ox[2:5]
        # OxG = Ox[5:8]
        # OxB = Ox[8:]
        # pattern.append((OxR, OxG, OxB))
        pattern.append( (R, G, B) )
        #print(f'i:{i} j:{j} k:{k} 0x:{Ox} 0xR:{OxR} 0xG:{OxG} 0xB:{OxB} R:{R} G:{G} B:{B}')
    return pattern

def Encode():
    index = 0 #32
    input_image = Image.open(f'./image/{filename}.png')
    text_image = Image.open(f'./text/{filename}.png')

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
    
    output_image.save(f'./output/{filename}.png')

    #option to black empty spaces, How to determine empty text area? or dont touch... Grey color in encode.
    #> optionaly check for grey, depends on encoding

def Decode():
    index = 0
    input_image = Image.open(f'./output/{filename}.png')

    # Create a new PIL image with the same size as the encoded image:
    decoded_image = Image.new("RGB", input_image.size)
    x_size, y_size = input_image.size

    for i, pixel in enumerate(input_image.getdata()):
        #print(f'{pixel:0b}')
        pixelX = i % x_size
        pixelY = int(i / x_size)

        #Images are encoded backwards, we want to split accordingly
        #get colors of image
        (b,g,r) = pixel
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
    
    decoded_image.save(f'./decode/{filename}.png')



if __name__ == "__main__":
    #test image uses 'twelve'
    #words = input(f'Enter code word:')
    words = 'twelve'

    filename = hashedWords = HashWord(words.encode())
    #print(hashedWords) #32 hex digits 64characters

    Pattern(hashedWords)
    #print(pattern)

    Encode()
    Decode()