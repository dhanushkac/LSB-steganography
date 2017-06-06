import cv2, copy, sys, time

def int_to_bin(number):
    return "{0:b}".format(number).zfill(8)

def change_bits(secret_px_bin_val, cover_px_bin_val, bit_count):
    return cover_px_bin_val[:-bit_count] + secret_px_bin_val[:bit_count]

def extract_bits(steg_px_bin_val, bit_count):
    return steg_px_bin_val[-bit_count:]

def extract_cover_bits(cover_px_bin_val, bit_count):
    return cover_px_bin_val[:-bit_count]

def normalize_secret_bits(extract_steg_px_bin_val):
    bit_val = extract_steg_px_bin_val.ljust(8,'0')
    extract_steg_px_int_to_bin_val = bin_to_int(bit_val)
    return extract_steg_px_int_to_bin_val

def normalize_cover_bits(extract_cover_px_bin_val):
    bit_val = extract_cover_px_bin_val.zfill(8)
    extract_cover_px_val = bin_to_int(bit_val)
    return extract_cover_px_val

def bin_to_int(bin_value):
    return int(bin_value, 2)

#this function change the cover pixel value using secret pixel value
def change_lsb(secret_px, cover_px, bit_count):

    #RGB binary values of secret image pixel
    secret_px_b_val = int_to_bin(secret_px[0])
    secret_px_g_val = int_to_bin(secret_px[1])
    secret_px_r_val = int_to_bin(secret_px[2])

    #RGB binary values of cover image pixel
    cover_px_b_val = int_to_bin(cover_px[0])
    cover_px_g_val = int_to_bin(cover_px[1])
    cover_px_r_val = int_to_bin(cover_px[2])

    #change lsb using bit_count
    cover_px_b_bin_val = change_bits(secret_px_b_val, cover_px_b_val, bit_count)
    cover_px_g_bin_val = change_bits(secret_px_g_val, cover_px_g_val, bit_count)
    cover_px_r_bin_val = change_bits(secret_px_r_val, cover_px_r_val, bit_count)

    #apply calculated RGB value to the pixel
    cover_px[0] = bin_to_int(cover_px_b_bin_val)
    cover_px[1] = bin_to_int(cover_px_g_bin_val)
    cover_px[2] = bin_to_int(cover_px_r_bin_val)

    return cover_px

def extract_secret(steg_px, bit_count):

    #RGB binary values of steg image pixel
    steg_px_b_val = int_to_bin(steg_px[0])
    steg_px_g_val = int_to_bin(steg_px[1])
    steg_px_r_val = int_to_bin(steg_px[2])

    #extract lower bits from steg image
    extract_steg_px_b_val = extract_bits(steg_px_b_val, bit_count)
    extract_steg_px_g_val = extract_bits(steg_px_g_val, bit_count)
    extract_steg_px_r_val = extract_bits(steg_px_r_val, bit_count)

    #normalize steg pixel bits for secret image
    norm_extract_steg_px_b_val = normalize_secret_bits(extract_steg_px_b_val)
    norm_extract_steg_px_g_val = normalize_secret_bits(extract_steg_px_g_val)
    norm_extract_steg_px_r_val = normalize_secret_bits(extract_steg_px_r_val)

    #apply calculated RGB value to the pixel
    steg_px[0] = norm_extract_steg_px_b_val
    steg_px[1] = norm_extract_steg_px_g_val
    steg_px[2] = norm_extract_steg_px_r_val

    return steg_px

def extract_cover(cover_px, bit_count):

    #RGB binary values of steg image pixel
    cover_px_b_val = int_to_bin(cover_px[0])
    cover_px_g_val = int_to_bin(cover_px[1])
    cover_px_r_val = int_to_bin(cover_px[2])

    #extract upper bits from steg image
    extract_cover_px_b_val = extract_cover_bits(cover_px_b_val, bit_count)
    extract_cover_px_g_val = extract_cover_bits(cover_px_g_val, bit_count)
    extract_cover_px_r_val = extract_cover_bits(cover_px_r_val, bit_count)

    #normalize steg pixel bits for cover image
    norm_extract_cover_px_b_val = normalize_secret_bits(extract_cover_px_b_val)
    norm_extract_cover_px_g_val = normalize_secret_bits(extract_cover_px_g_val)
    norm_extract_cover_px_r_val = normalize_secret_bits(extract_cover_px_r_val)

    #apply calculated RGB value to the pixel
    cover_px[0] = norm_extract_cover_px_b_val
    cover_px[1] = norm_extract_cover_px_g_val
    cover_px[2] = norm_extract_cover_px_r_val

    return cover_px

#this function embed secret image array into cover image array using LSB
def embed_image(secret_px_array, cover_px_array, bit_count):
    cover_px_array_new = copy.deepcopy(cover_px_array)
    secret_px_array_new = copy.deepcopy(secret_px_array)
    for i in range(len(secret_px_array_new)):
        for j in range(len(secret_px_array_new[0])):
            cover_px_array_new[i][j] = change_lsb(secret_px_array_new[i][j], cover_px_array_new[i][j], bit_count)
    return cover_px_array_new

def decode_images(steg_image_px_array, bit_count):
    secret_image_px_array_new = copy.deepcopy(steg_image_px_array)
    cover_image_px_array_new = copy.deepcopy(steg_image_px_array)
    for i in range(len(secret_image_px_array_new)):
        for j in range(len(secret_image_px_array_new[0])):
            secret_image_px_array_new[i][j] = extract_secret(secret_image_px_array_new[i][j], bit_count)
            cover_image_px_array_new[i][j] = extract_cover(cover_image_px_array_new[i][j], bit_count)
    return secret_image_px_array_new, cover_image_px_array_new

#steg_image = embed_image(secret_px_array, cover_px_array, bit_count)
#extracted_secret_image, extracted_cover_image = decode_images(steg_image_px_array, bit_count)

def main(argv):
    if argv[0] == "-e" and len(argv) == 7:
        #take image filenames from args
        secret_arg = argv[2]
        cover_arg = argv[4]
        
        print 'Start reading files...'
        #read images
        secret = cv2.imread(secret_arg, cv2.IMREAD_COLOR)
        cover = cv2.imread(cover_arg, cv2.IMREAD_COLOR)

        s_rows, s_cols, s_channels = secret.shape
        c_rows, c_cols, c_channels = cover.shape

        #get RGB values of cover & secret
        secret_px_array = secret[0:s_rows, 0:s_cols]
        cover_px_array = cover[0:c_rows, 0:c_cols]
        print 'Pixel values extracted.'

        bit_count = int(argv[6])

        steg_image = embed_image(secret_px_array, cover_px_array, bit_count)

        print 'Steg image created.'

        millis = str(int(round(time.time() * 1000)))
        filename = 'steg_image_' + millis + '.png'

        print 'Saving as '+filename+'.'

        cv2.imshow(filename, steg_image)
        cv2.imwrite(filename, steg_image)

        print 'Done.'

        cv2.waitKey(0)
        cv2.destroyAllWindows()


    elif argv[0] == "-d" and len(argv) == 5:

        #take image filenames from args
        steg_arg = argv[2]
        print 'Start reading files...'        
        steg = cv2.imread(steg_arg, cv2.IMREAD_COLOR)

        s_rows, s_cols, s_channels = steg.shape

        #get RGB values of steg
        steg_image_px_array = steg[0:s_rows, 0:s_cols]
        print 'Pixel values extracted.'

        bit_count = int(argv[4])

        extracted_secret_image, extracted_cover_image = decode_images(steg_image_px_array, bit_count)

        print 'Secret image & cover image created.'

        millis = str(int(round(time.time() * 1000)))
        secret_filename = 'secret_image_' + millis + '.png'
        cover_filename = 'cover_image_' + millis + '.png'

        print 'Cover image saving as '+cover_filename+'.'
        print 'Secret image saving as '+cover_filename+'.'

        cv2.imshow(secret_filename, extracted_secret_image)
        cv2.imwrite(secret_filename, extracted_secret_image)        

        cv2.imshow(cover_filename, extracted_cover_image)
        cv2.imwrite(cover_filename, extracted_cover_image)

        print 'Done.'

        cv2.waitKey(0)
        cv2.destroyAllWindows()

    elif argv[0] == "-h":
        print '--------------Help Doc--------------'
        print 'Encode Images >>'
        print '-e -s <image need to hide> -c <image use to cover> -nb <number of bits uses to store secret image>'
        print 'Decode Images >>'
        print '-d -s <encoded image> -nb <number of bits used to store secret image>'
        print 'Help Doc >>' 
        print '-h'
    else:
        print 'Wrong argument encountered. Try help.'

if __name__ == "__main__":
   main(sys.argv[1:])