from db import add_to_mongo
import random
from random import randint
import pandas as pd
from time import sleep
from datetime import datetime


# retrieve usernames from a column in an excel spreadsheet
def get_users_from_xlsx_list(file):
    xls = pd.ExcelFile(file)
    data = xls.parse(xls.sheet_names[0])
    usernames = data.values.tolist()
    lst = []
    for u in usernames:
        s = ''.join(u)
        lst.append(s)
    return lst


# retrieve a sample from a hashtag list
def get_sample(lst, nb):
    sample = random.sample(lst.replace('#', '').split(' '), nb)
    return sample


# function to accomplish the follow action
def follow_from_profile(webdriver, username):  # follow people based on a xlsx list
    webdriver.implicitly_wait(3)
    err = False
    try:
        follow_btn = webdriver.find_element_by_xpath(
            '/html/body/div[1]/section/main/div/header/section/div[1]/div[1]/span/span[1]/button')
    except:
        try:
            follow_btn = webdriver.find_element_by_xpath('/html/body/div[1]/section/main/div/header/section/div/button')
        except:
            err = True
    if not err:
        follow_btn.click()
        sleep(3)
        dict_followed = {
            'username': username,
            'date': datetime.now()
        }
        add_to_mongo('FOLLOWED', dict_followed)
        print(f'{username} followed')
    else:
        print('Error for : ' + username)


# function to accomplish the unfollow action
def unfollow_from_profile(webdriver, username):
    webdriver.implicitly_wait(10)
    err = False
    try:
        unfollow_btn = webdriver.find_element_by_xpath(
            '/html/body/div[1]/section/main/div/header/section/div[1]/div[2]/span/span[1]/button')
    except:
        err = True
    if not err:
        unfollow_btn.click()
        webdriver.implicitly_wait(10)
        unfollow_btn2 = webdriver.find_element_by_xpath('/html/body/div[4]/div/div/div[3]/button[1]')
        unfollow_btn2.click()
        sleep(2)
        dict_unfollowed = {
            'username': username,
            'date': datetime.now()
        }
        add_to_mongo('UNFOLLOWED', dict_unfollowed)
        print(dict_unfollowed)
    else:
        print("Error for " + username)


# function to send a message to a user
def send_message(webdriver, username, message):
    sleep(randint(1, 2))
    err = False
    sendmess = webdriver.find_elements_by_css_selector(
        '#react-root > section > main > div > header > section > div.nZSzR > div._862NM > div > button')
    try:
        sendmess[0].click()
    except:
        pass
    sleep(randint(2, 4))
    webdriver.implicitly_wait(5)
    try:
        messagebox = webdriver.find_element_by_xpath(
            '/html/body/div[1]/section/div/div[2]/div/div/div[2]/div[2]/div/div[2]/div/div/div[2]/textarea')
    except:
        err = True
    if not err:
        messagebox.send_keys(message)
        sleep(randint(2, 5))
        send = webdriver.find_element_by_xpath(
            '/html/body/div[1]/section/div/div[2]/div/div/div[2]/div[2]/div/div[2]/div/div/div[3]/button')
        send.click()
        sleep(randint(1, 3))
        dict_message = {
            'username': username,
            'text': message,
            'date': datetime.now()
        }
        add_to_mongo('MESSAGES', dict_message)
        print('Messaged : ' + str(username))
    else:
        print('Error for: ' + str(username))


# function to accomplish the block action on a user
def block(webdriver, username):
    more_btn = webdriver.find_element_by_xpath('/html/body/div[1]/section/main/div/header/section/div[1]/div/button')
    more_btn.click()
    sleep(1)
    webdriver.implicitly_wait(10)
    block_btn = webdriver.find_element_by_xpath('/html/body/div[4]/div/div/div/button[1]')
    block_btn.click()
    sleep(2)
    block_btn2 = webdriver.find_element_by_xpath("/html/body/div[4]/div/div/div[2]/button[1]")
    block_btn2.click()
    dict_blocks = {
        'username': username,
        'date': datetime.now()
    }
    add_to_mongo('BLOCKED', dict_blocks)
    print('Blocked : ' + str(username))


# like picture from a hashtag
def like(webdriver, url, username, hashtag, seconds_published):
    button_like = webdriver.find_element_by_xpath(
        '/html/body/div[4]/div[2]/div/article/div[2]/section[1]/span[1]/button')
    webdriver.execute_script("arguments[0].click();", button_like)
    # button_like.click()
    dict_liked = {
        'pic_id': url,
        'username': username,
        'sec_publ': seconds_published,
        'hashtag': hashtag,
        'date': datetime.now()
    }
    add_to_mongo('LIKES', dict_liked)


# follow user from a hashtag
def follow(p_follow, webdriver, username):
    prob = randint(1, 100)
    webdriver.implicitly_wait(10)
    seguir = webdriver.find_element_by_xpath(
        '/html/body/div[4]/div[2]/div/article/header/div[2]/div[1]/div[2]/button')
    if prob <= p_follow and seguir.text == 'Seguir':
        seguir.click()
        dict_followed = {
            'username': username,
            'date': datetime.now()
        }
        add_to_mongo('FOLLOWED', dict_followed)
    else:
        pass


# set a stop if a specific word is in the user's username
def stop_like(stoplist, username):
    stop = False
    for word in stoplist:
        if word in username:
            stop = True
    return stop
