# from cryptography.fernet import Fernet
# import os

# key_path = os.path.join(os.getcwd(), "app_modules", "security", "secret.key")

# def generate_key():
#     key = Fernet.generate_key()
#     return key

# def load_key():
#     key = open(key_path, "rb").read()
#     return key

# def encrypt_data(data, key):
#     fnt = Fernet(key)
#     en_data = fnt.encrypt(data.encode())
#     return en_data.decode()

# def decrypt_data(data, key):
#     fnt = Fernet(key)
#     d_data = fnt.decrypt(data.encode())
#     return d_data.decode()

def _unpad(data):
    chars= []
    for i in range(5, len(data), 6):
        chars.append(data[i])
    return "".join(chars)

def _reverse(data):
    data = data[::-1]
    char_codes= []
    for i in range(len(data)):
        char_codes.append(ord(data[i]) - 3)
    chars = [chr(i) for i in char_codes]
    return "".join(chars)

def _inverse_case(data):
    chars = []
    for i in data:
        if i.islower(): 
            chars.append(i.upper())
        else:
            chars.append(i.lower())
    return "".join(chars)

def decrypt(data):
    return _inverse_case(_reverse(_unpad(data)))

# if __name__ == "__main__":
#     key = load_key()
#     val = input("Enter the password: ")
#     output = encrypt_data(val, key).strip()
#     isClip = input(
#         "Do you want to copy the encrypted data to clipboard? (y/n): ")
#     if(isClip.lower() == "y"):
#         os.system('echo|set /p="%s"|clip' % output)
#     else:
#         print(output)
