import cs50
import sys


if len(sys.argv) != 2:
    print ("Error: no argument or too many arguments given.")
    quit()
elif str.isdigit(sys.argv[1]) == False:
    print ("Error: You need to give positive integer")
    quit()


key = int(sys.argv[1])
if key < 1:
    print ("Error: wrong key")
    quit()

text = cs50.get_string()
if text != None:
    for w in text:
        if str.isalpha(w) == True:
            if str.isupper(w) == True:
                k = (ord(w) - ord('A')+ key) % 26 + ord('A')
                print(chr(k), end="")
            elif str.islower(w) == True:
                k = (ord(w) - ord('a')+ key) % 26 + ord('a')
                print(chr(k), end="")
        else:
            print(w, end="")
    print()    
            