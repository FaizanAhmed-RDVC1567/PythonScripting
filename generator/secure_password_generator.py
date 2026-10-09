import random
import string

def create_character_collection() -> dict:
    """
    Generate a string of characters to use for password generation, using
    ASCII uppercase, lowercase, digits and special characters.
    
    Assign the generated strings to a key-value pair and store them in
    a dictionary, then return the dictionary.
    """
    character_collection = {
        "lowercase": string.ascii_lowercase,
        "uppercase": string.ascii_uppercase,
        "digits": string.digits,
        "symbols": string.punctuation
    }
    
    """character_list = (string.digits + 
                      string.ascii_uppercase + 
                      string.ascii_lowercase #+ #
                      #string.punctuation
                      )
    """

    return character_collection


def get_password_length() -> int:
    """
    Prompt user for length of the password and get a positive integer between 8 and 100.
    Returns the submitted length after passing checks.
    """
    success = False
    while not success:
        try:
            length = int(input("Please enter your desired password length: "))

            if length < 8:
                print("Password length must be at least 8 characters for security.")
            elif length > 100:
                print("Password length too long! Please choose 100 or fewer characters.")
            else:
                success = True
                break

        except ValueError:
            print("\nInvalid input! Please enter a number.\n")

    return length


def generate_password(character_collection: dict, password_length: int) -> str:
    
    # This particular expression is a lambda expression that is used to
    # guarantee at least one character from each group
    generated_password = [random.choice(group) for group in character_collection.values()]

    # after getting one type of character in the generated password, fill the rest with
    # random characters from all the groups combined
    all_characters = ''.join(character_collection.values())
    generated_password += [random.choice(all_characters) for _ in range(
        password_length - len(character_collection))]

    # To avoid getting a predictable sequence of chars, call 'shuffle()'
    random.shuffle(generated_password)

    # return the password string
    return ''.join(generated_password)


def main():
    password_chars = create_character_collection()
    
    # print(password_chars)
    # for keys, value in password_chars.items():
        # print(f"Key: {keys}, Values: {value}")
    
    password_length = get_password_length()
    user_password = generate_password(password_chars, password_length)

    print(f"Your generated password is: {user_password}\n")


if __name__ == "__main__":
    """
    This line above deals with whether the file is run as is, or has been imported as a module.
    If the file is run as is, the value inside '__name__' is "__main__".
    Otherwise the value of '__name__' is something else. This is part of good practice in
    Python programming if you want to execute the file only when it is run as is.
    """
    main()
