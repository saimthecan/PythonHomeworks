file_path = 'emails.txt'


def check_email_and_login(email):
    
    with open(file_path, 'r') as file:
        emails = file.read().splitlines()
    
    # Check if the email is in the list
    if email in emails:
        return "login success"
    else:
        with open(file_path, 'a') as file:
            if emails:
                file.write(f"\n{email}")
            else:
                file.write(email)
        return "Email added to the list"

test_email = input("Please enter your email address: ")
result = check_email_and_login(test_email)
print(result)
