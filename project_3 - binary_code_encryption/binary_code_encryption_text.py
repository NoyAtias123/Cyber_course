def reading_file(path):
        with open(path, 'rb') as file:
          return file.read()

def file_words_to_binary(file):
    binary_words_list = []
    for i in file:
        try:
            binary_words_list.append(bin(ord(str(i)))[2:].zfill(8))
        except:
            binary_words_list.append(bin(int(i))[2:].zfill(8))

    return binary_words_list

def calc_with_xor(bin_list, path):
    with open (path, 'w') as changing_file:
        for i in bin_list:
            bin_xor_result = bin(int(i, 2) ^ 5)[2:].zfill(8)
            changing_file.write(chr(int(bin_xor_result, 2)))
            changing_file.write(' ')

    with open(path, 'r') as changed_file:
        reading_changed_file = changed_file.read()
        return reading_changed_file

def Decryption_of_encryption(changed_file, path):
    changed_binary_list = file_words_to_binary(changed_file)[::2]
    fixed_file = calc_with_xor(changed_binary_list, path)
    return fixed_file

def main():
    path = "D:\\NOY\\קורס תכנות\\ייצוג בינארי ואופרטורים\\example.txt"
    binary_file = reading_file(path)
    binary_words_list = file_words_to_binary(binary_file)
    changed_file = calc_with_xor(binary_words_list, path)
    print(changed_file)
    fixed_file = Decryption_of_encryption(changed_file, path)
    print(fixed_file)

if __name__ == "__main__":
    main()