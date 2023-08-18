import random
import sqlite3


def checkalgo(review):
    # creating list to convert strings of numbers to list
    list_convert = []
    for item in list(review):
        list_convert.append(int(item))
    # removing the last digit
    card_no = list_convert[:-1]
    # making card number temporary list
    tmp_list = card_no.copy()

    # to ensure there is no double digit
    for i in range(0,len(tmp_list),2):
        tmp_list[i]*=2
        if tmp_list[i]>9:
            tmp_list[i]-=9
    # extending it to card_no
    checksum = list(str(10-sum(tmp_list)%10))
    if len(checksum)!=1:
        checksum = [0]
    # extending it to review
    card_no.extend(review)
    del tmp_list
    card_no_db = ''.join(map(str,card_no))
    if card_no_db == review:
        return True
    else:
        return False

# Creating card and pin
def create_card():
    def get_pin():
        pin = ""
        for each in random.sample(range(9), k=4):
            pin += str(each)
        return pin
    
    # connecting to sql
    conn = sqlite3.connect("card.s3db")
    curr = conn.cursor()
    iin = [4, 2, 0, 0, 1, 0]

    # generating account number from range 0 to 9
    random_acc_no = random.sample(range(9), 9)
    card_no = []
    card_no.extend(iin)
    card_no.extend(random_acc_no)

    # making temp list
    tmp_list = card_no.copy()
    for i in range(0, len(tmp_list), 2):
        tmp_list[i] *= 2
        if tmp_list[i] > 9:
            tmp_list[i] -= 9
    checksum = list(str(10 - sum(tmp_list) % 10))
    if len(checksum) != 1:
        checksum = [0]
    card_no.extend(checksum)
    del tmp_list
    card_no_for_db = ''.join(map(str, card_no))
    card_pin_for_db = get_pin()
    print("\nYour card has been created")
    print("Your card number:\n{}\nYour card PIN:\n{}\n".format(card_no_for_db, card_pin_for_db))
    curr.execute('SELECT id from card;')
   
    db_return = curr.fetchall()
    try:
        listofrows = (lambda l: [item for sublist in l for item in sublist])(db_return)
        myid = max(listofrows)
    except ValueError:
         myid = 0
    dontsqlinjectme = (myid, card_no_for_db, card_pin_for_db)
    curr.execute('INSERT INTO card (id, number, pin) VALUES (?, ?, ?);', dontsqlinjectme)
    conn.commit()


    # retrieving form the database
def retrieve_from_db(user_enter_card, user_enter_pin):
    conn = sqlite3.connect("card.s3db")
    curr = conn.cursor()
    card_number = user_enter_card
    pin = user_enter_pin
    dontsqlinjectme = (card_number, pin)
    curr.execute('SELECT number, pin FROM card WHERE number = ? and pin = ?;', dontsqlinjectme)
    db_return = curr.fetchone()
    match = False
    # try and check if it is available in the database 
    try:
        if card_number in db_return and pin in db_return:
            match = True
            print("You have successfully logged in!")   
    except sqlite3.OperationalError:
        print("\nWrong card number or PIN!\n")
    except TypeError:
        print("\nWrong card number or PIN!\n")
    while match:
        print("####### Card Holder Management System #######\n\n1.Balance\n2.Add Money\n3.Transfer money\n4.Close account\n5.Log out\n0.Exit")
        second_menu_choice = int(input("\nEnter your choice: "))
        if second_menu_choice == 1:
            curr.execute('SELECT balance FROM card WHERE number = ? and pin = ?;', (card_number, pin))
            db_return = curr.fetchone()
            print("\nBalance: {}\n".format(db_return[0]))
        elif second_menu_choice == 2:
            print("\nEnter Money:")
            dontsqlinjectme = (int(input()), card_number, pin)
            curr.execute('UPDATE card SET balance = balance + ? WHERE number = ? and pin = ?;', dontsqlinjectme)
            conn.commit()
            print("Money was added!")
        elif second_menu_choice == 3:
            global transfer_destination
            transfer_destination = []
            print("Enter card number:")
            user_enters_transferdest = input()
            if len(user_enters_transferdest) != 16:
                print("\nProbably you made a mistake in the card number.\nPlease try again!\n")
                continue
            elif len(user_enters_transferdest) == 16:
                if user_enters_transferdest == card_number:
                    print("\nYou can't transfer money to the same account!\n")
                    continue
                elif not check_luhn_algo(user_enters_transferdest):
                    '# IF CHECK LUHN ALGO RETURNS FALSE. NOT FALSE = TRUE AND THEN WE CONTINUE'
                    print("\nLUHN CHECK:Probably you made a mistake in the card number.\nPlease try again!\n")
                    continue
                else:
                    transfer_destination = (int(user_enters_transferdest),)
            curr.execute('SELECT number FROM card WHERE number = ?;', transfer_destination)
            db_return = curr.fetchone()
            try:
                len(db_return)
                print("\nEnter how much money you want to transfer:\n")
                user_enters_transfermoney = int(input())
                curr.execute('SELECT balance FROM card WHERE number = ? and pin = ?', (card_number, pin))
                db_return = curr.fetchone()
                if user_enters_transfermoney > db_return[0]:
                    print("\nNot enough money!\n")
                    continue
                else:
                    curr.execute('UPDATE card SET balance = balance + ? WHERE number = ?;', (
                        user_enters_transfermoney, int(user_enters_transferdest)))
                    curr.execute('UPDATE card SET balance = balance - ? WHERE number = ?;', (
                        user_enters_transfermoney, card_number))
                    conn.commit()
                    print("\nSuccess!\n")
                    continue
            except TypeError:
                print("\nSuch a card does not exist.\n")
                continue

        elif second_menu_choice == 4:
            dontsqlinjectme = (card_number, pin)
            curr.execute('DELETE FROM card WHERE number = ? and pin = ?;', dontsqlinjectme)
            conn.commit()
            print("\nThe account has been closed!\n")
            break
        elif second_menu_choice == 5:
            print("You have successfully logged out!")
            match = False
        elif second_menu_choice == 0:
            print("Bye!")
            conn.close()
            exit()


def create_db():
    conn = sqlite3.connect("card.s3db")
    curr = conn.cursor()
    try:
        curr.execute('create table card (id INTEGER, number TEXT, pin TEXT, balance INTEGER default 0);')
    except sqlite3.OperationalError:
        curr.execute('DROP TABLE card;')
        curr.execute('create table card (id INTEGER, number TEXT, pin TEXT, balance INTEGER default 0);')
    finally:
        conn.commit()


program_is_running = True
create_db()
while program_is_running:
    print("======== Card Holder Management System ========\n1. Create New Account(Auto Generate)\n2. User Account\n0. Exit")
    first_menu_choice = int(input("Enter your choice: "))
    if first_menu_choice == 1:
        create_card()
    elif first_menu_choice == 2:
        print("\nEnter your card number:")
        user_enters_card_no = input()
        print("Enter your PIN:")
        user_enters_pin = input()
        retrieve_from_db(user_enters_card_no, user_enters_pin)
    elif first_menu_choice == 0:
        print("\nThank you! Bye!")
        program_is_running = False
