import random

name = input("what is your name? ")
num = random.randint(1,100)
guesses_left = 7
x = num - random.randint(1,5)
y = num + random.randint(1,5)
start = input("Are you ready if so click start or if not click exit: ")
if start == "start":
    print("goodluck...")
if start == "exit":
    print("noooo")


print("you have: " + str(guesses_left) + " guesses left")
while guesses_left > 0: 
    guess = int((input("what number do you guess? "))) 
    if guess == num:
        print("Congratulations " +  name  + " you entered correct!")
        exit()
    if guess > num:
        print("your guess is high try again")
        guesses_left -= 1
        print("I will give you a hint, the number is between " + str(x) + " and " + str(y))
        print("you have: " + str(guesses_left) + " guesses left")
        print("try again")
    if guess < num:
        print("you are low try again")
        guesses_left -= 1
        print("I will give you a hint, the number is between " + str(x) + " and " + str(y))
        print("you have: " + str(guesses_left) + " guesses left")
        print("try again")
else:
    print("you lose")
    exit()
