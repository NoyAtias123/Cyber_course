import re # The re module matches text based on defined patterns (removing punctuation marks from a string, for example)
import sys # The sys module in Python allows interaction with the Python interpreter and its runtime environment

def read_file(file_path):
    # The function attempts to read the file from the file path given by the user
    try:
        with open (file_path, 'r', encoding = 'utf-8') as f:
            print("The file was read successfully!")
            return f.read()
    except:
        print("Error: file does not exist! \ntry other file path")


def words_list(file):
    # The function cleans the text string of punctuation marks and turns it into a list
    clean_words = re.sub(r'[^\w\s]', '', file).lower()
    words_list = clean_words.split()
    return words_list


def dict_counter(clean_words_list):
    # The function creates a dictionary where the keys are the words and the values ​​are the number of times the word appeared in the file
    words_dict = {}
    for word in clean_words_list:
        words_dict[word] = words_dict.get(word, 0) + 1
    return words_dict


def sorted_appearances(words_dict):
    # The function creates a list of tuples that are sorted in descending order (from largest to smallest) by the number of times the word appeared in the file
    sorted_list = sorted(words_dict.items(), key = lambda item: item[1], reverse = True)
    return sorted_list


def most_appearances(sorted_list, n):
    # The function prints the first n (user-assigned number) words that appear in the list - the words with the largest number of occurrences in the file
    counter = 0
    for i in range (len(sorted_list)):
        if counter >= n and sorted_list[appear] != sorted_list[i][1]:
            break
        appear = sorted_list[i][1]
        print("word: '" + sorted_list[i][0] + "' appappears " + str(sorted_list[i][1]) + " times")
        counter += 1


def main():
    # Attempt to capture n from the user using sys.argv and print an appropriate message if unsuccessful
    if len(sys.argv) > 1:
        n = int(sys.argv[1])
    else:
        raise Exception("Please enter N as sys argument")
    # Attempting to capture the file path from the user using sys.argv and printing an appropriate message if unsuccessful
    try:
        file_path = str(sys.argv[2])
    except:
        raise Exception("Please enter file path as sys argument")
    file = read_file(file_path)
    # Checking whether the file read worked - if no appropriate message is printed and the main function does not continue running
    if file == None:
        sys.exit(0)
    clean_words_list = words_list(file)
    counted_words_dict = dict_counter(clean_words_list)
    sorted_words_list = sorted_appearances(counted_words_dict)
    most_appearances(sorted_words_list, n)


if __name__ == "__main__":
    main()