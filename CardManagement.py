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
    