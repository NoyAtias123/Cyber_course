def get_input():
    positive_decimal = int(input("Enter a positive integer: "))
    bit_size = int(input("Enter the memory size in bits: "))

    return positive_decimal, bit_size

def decimal_to_binary(n, bits):
    binary_representation = bin(n)[2:]

    return binary_representation.zfill(bits)

def two_complement(binary_str):
    inverted_binary = ''.join('1' if bit == '0' else '0' for bit in binary_str)
    decimal_value = int(inverted_binary, base = 2) + 1
    
    return bin(decimal_value)[2:].zfill(len(binary_str)) 

def main():
    positive_decimal, bit_size = get_input()
    binary_representation = decimal_to_binary(positive_decimal, bit_size)
    negative_binary = two_complement(binary_representation)
    print(f"Tow's complement (negative binary): {negative_binary}")

if __name__ == "__main__":
    main()
