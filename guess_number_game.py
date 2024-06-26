import random

def guess_number_game():
    target_number = random.randint(1, 100) 
    while True:
        try:
            guess = int(input("Enter your guess: "))
            if guess < 1 or guess > 100:
                print("Please enter a number between 1 and 100.")
                continue

            if guess == target_number:
                print("Congratulations! You guessed correctly.")
                break
            elif guess > target_number:
               print("Your guess is too high. Try a smaller number.")
            else:
                print("Your guess is too low. Try a larger number.")

        except ValueError:
            print("Please enter a valid number.")

# Start the game
guess_number_game()
