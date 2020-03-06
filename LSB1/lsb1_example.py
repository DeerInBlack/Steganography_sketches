from LSB1 import stego_lsb1
from pathlib import Path, PurePath

INFO = "This script is an example of my implementation of steganographic LSB\n" \
       "(LeastSignificant Bit) method. The essence of this method is to replace\n" \
       "the last significant bits in the container with the bits of the message\n" \
       "to be hidden. It is simple but unstable to compression and all types of\n" \
       "attacks.\n" \
       "LSB1 works only with image containers. It replacing by default last two\n" \
       "bits of blue color channel (to which our eyes is less sensitive) of\n" \
       "pixel with sparseness of 10. That makes it hard for eye to distinguish\n" \
       "'corrupted' image from original one and harder to notice any abnormal\n" \
       "characteristics in the distribution of the values of the range of\n" \
       "the least significant bits, but the max size of embedded information is\n" \
       "only 0.6% of uncompressed image size. The 'message' can actually be any\n" \
       "type of information and not only ASCII text but I decided it's enough\n" \
       "for this small example script. Default configurations can be changed\n" \
       "(see README for details on\n" \
       "https://github.com/DeerInBlack/steganography-sketches)."
FORMATS = ['.jpg', '.png']


def ascii_to_bit_seq(string):
    if not string.isascii():
        raise ValueError("ASCII only allowed")
    return "".join(f"{ord(i):08b}" for i in string)


def bit_seq_to_ascii(bit_seq):
    st = ''
    while bit_seq:
        st += chr(int(bit_seq[:8], 2))
        bit_seq = bit_seq[8:]
    return st


def ext_selector(file, ext_list):
    ext = PurePath(file).suffix
    if ext in ext_list:
        return True
    else:
        return False


def image_choice(im_lt, formats):
    print("Example images: ",
          "\n                ".join(f"{im_lt.index(im)}. {im.name}"
                                    for im in im_lt), sep='')
    while True:
        choice = input("->Enter number of example image or path to "
                       "your image\n"
                       " (or '-return' to return to options): ").strip()
        if choice.isdecimal() and int(choice) < len(im_lt):
            return im_lt[int(choice)]
        elif Path(choice).is_file() and \
                ext_selector(choice, formats):
            return Path(choice)
        elif choice == '-return':
            return False
        else:
            print("!!!Invalid input!!!")


def text_choice():
    while True:
        print("Text options: 'f' - text from file, 't' - type in,\n"
              "              '-return' - back to options")
        inp_choice = input("->Choose option: ").strip()
        if inp_choice == '-return':
            return False
        elif inp_choice == 'f':
            f_path = input("->Enter path to text file: ")
            if Path(f_path).is_file() and \
                    ext_selector(f_path, '.txt'):
                try:
                    with open(Path(f_path), 'r') as f:
                        text = f.read()
                        if text.isascii():
                            return text
                        else:
                            print("ASCII.only.please -_-")
                            continue
                except Exception as e:
                    print("!!!Can't read file!!!\n", e)
                    continue
            else:
                print("!!!Wrong path!!!")
        elif inp_choice == 't':
            text = input("->Enter your message (ASCII only!): ")
            if text.isascii():
                return text
            else:
                print("ASCII.only.please -_-")
                continue
        else:
            print("!!!Choose one of those!!!")


def main():
    ex_path = Path("examples")
    print("LSB1 steganography sketch".center(71, '-'))
    while True:
        print("Options: 0. Info about LSB1\n"
              "         1. Embed message\n"
              "         2. Pluck out message\n"
              "         3. Exit")
        op_choice = input("->Enter number of option: ").strip()
        if not op_choice.isdecimal() or int(op_choice) > 3:
            print("!!!Invalid option!!!\n")
            continue
        op_choice = int(op_choice)
        if op_choice == 0:
            print(''.center(71, '-'), INFO, ''.center(71, '-'), sep='\n')
            continue
        elif op_choice == 3:
            exit(0)
        else:
            ex_files = [x for x in ex_path.iterdir() if x.is_file()]
            ex_images = list(filter(lambda x: ext_selector(x, FORMATS),
                                    ex_files))
            if op_choice == 2:
                ex_images = list(filter(lambda x: ext_selector(x, FORMATS[1])
                                        and '_corrupted' in x.name, ex_files))
            im_path = image_choice(ex_images, FORMATS)
            if not im_path:
                continue
            try:
                if op_choice == 1:
                    message_str = text_choice()
                    if not message_str:
                        continue
                    message_bs = ascii_to_bit_seq(message_str)
                    new_im_path, rest = stego_lsb1.embed(message_bs, im_path)
                    print(f"|Message was successfully embedded!\n"
                          f"|Corrupted image path: {new_im_path}\n",
                          f"|{len(rest)} bits did not fit in"
                          if len(rest) > 0 else '')
                else:
                    message_bs = stego_lsb1.pluck_out(im_path)
                    message_str = bit_seq_to_ascii(message_bs)
                    print("|Plucked out message:\n", message_str)
            except IOError as e:
                print("!!!Some troubles on opening/saving!!!\n"
                      "Try again, please.")
                continue
            except Exception as e:
                print("!!!", e, "!!!", type(e), sep='')
                continue


if __name__ == '__main__':
    main()
