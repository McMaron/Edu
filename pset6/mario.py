import cs50

while True:
    print ("Height: ", end="")
    Height = cs50.get_int()
    if Height > 0 and Height < 22:
        break

for rows in range(Height):
    print(" " *(Height - rows-1), end ="")
    print("#" * (rows + 2))
    
