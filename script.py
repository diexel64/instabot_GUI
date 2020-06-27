import os
from selenium import webdriver
from time import sleep
from random import randint
from datetime import datetime
from hashtaglist import HASHTAGS
from functions import stop_like, send_message, get_sample, follow, like
from functions import get_users_from_xlsx_list, block, follow_from_profile, unfollow_from_profile
from db import check_in_collection

baseFolder = os.path.dirname(os.path.abspath(__file__))
# Buttons
LOGIN = '/html/body/div[1]/section/main/div/article/div/div[1]/div/form/div[4]/button'
POPUP1 = '/html/body/div[1]/section/main/div/div/div/div/button'
POPUP2 = '/html/body/div[4]/div/div/div/div[3]/button[2]'
NEXT = '/html/body/div[3]/div[1]/div/div/a[2]'
# Settings
stopwords = ['bitcoin', 'btc', 'trade']


class Bot(object):

    def __init__(self, user, psw):
        self.webdriver = webdriver.Chrome(executable_path=baseFolder + '\\chromedriver.exe')
        self.user = user
        self.password = psw

    def connection(self):
        # Open browser and maximize it
        wd = self.webdriver
        wd.get('https://www.instagram.com/accounts/login/?source=auth_switcher')
        wd.maximize_window()
        # Try to login
        try:
            wd.find_element_by_name('username').send_keys(self.user)
            wd.find_element_by_name('password').send_keys(self.password)
            wd.implicitly_wait(10)
            wd.find_element_by_xpath(LOGIN).click()
        except:
            print('ERROR : different login page')
        # Wait for pop ups and bypass them
        wd.implicitly_wait(10)
        wd.find_element_by_xpath(POPUP1).click()
        wd.implicitly_wait(10)
        wd.find_element_by_xpath(POPUP2).click()

    def action_from_list(self, lst, action, until=None, message=None):
        # Check if a valid action is being used
        if action not in ["follow", "unfollow", "message", "block"]:
            print("Please, use an action such as follow, unfollow, message or block")
        else:
            wd = self.webdriver
            # Get the data to use from an Excel list
            if type(lst) != list:
                user_list = get_users_from_xlsx_list(lst)
            else:
                user_list = lst
            # Get into Instagram account
            self.connection()
            # Action for each line
            for user in user_list[0:until]:
                wd.get('https://www.instagram.com/' + str(user) + '/')
                wd.implicitly_wait(10)
                if action == "follow":
                    follow_from_profile(wd, user)
                elif action == "unfollow":
                    unfollow_from_profile(wd, user)
                elif action == "message":
                    send_message(wd, user, message)
                elif action == "block":
                    block(wd, user)
                else:
                    print("Invalid action")
            wd.quit()

    def by_hashtag(self, hashtag_list, avg_nb_pics=5, p_like=64, follow_active=False, avg_hstg=15, sleep_margin=2, limit=50):
        # Initialize and get into the Instagram account
        startTime = datetime.now()
        wd = self.webdriver
        self.connection()
        # Choose a random limit of likes to avoid robotic behaviour
        limit = randint(limit - 3, limit + 3)
        # Get a hashtag sample from a wider list to avoid robotic behaviour (like always using same hashtags)
        hashtag_sample = get_sample(hashtag_list, randint(avg_hstg - 1, avg_hstg + 1))
        print(hashtag_sample)
        # Start the loop for each hashtag
        like_counter = 0
        for hstg in hashtag_sample:
            wd.get('https://www.instagram.com/explore/tags/' + hstg + '/')
            wd.implicitly_wait(10)
            firstline_thumbnail = wd.find_element_by_xpath(
                '//*[@id="react-root"]/section/main/article/div[2]/div/div[1]/div['
                + str(randint(1, 3)) + ']/a/div/div[2]')
            # Sleeping to avoid robotic behaviour
            sleep(randint(sleep_margin, 3 + sleep_margin))
            try:
                firstline_thumbnail.click()
            # It sometimes gets stuck
            except:
                wd.implicitly_wait(10)
                firstline_thumbnail = wd.find_element_by_xpath(
                    '//*[@id="react-root"]/section/main/article/div[2]/div/div[1]/div[1]/a/div/div[2]')
                firstline_thumbnail.click()
            # Looping through each picture
            for n in range(1, randint(avg_nb_pics - 2, avg_nb_pics + 2)):
                print('Hashtag : ' + hstg + '\nPicture nº' + str(n))
                sleep(randint(sleep_margin, 2 + sleep_margin))
                try:
                    wd.implicitly_wait(10)
                    url = wd.current_url.split("p/")[1].replace("/", "")
                    wd.implicitly_wait(10)
                    username = wd.find_element_by_xpath(
                        '/html/body/div[4]/div[2]/div/article/header/div[2]/div[1]/div[1]/a').text
                    seconds_published = wd.find_element_by_xpath(
                        '/html/body/div[4]/div[2]/div/article/div[2]/div[2]/a/time').text
                except:
                    print('error with ' + str(n))
                    # Go to next picture
                    wd.find_element_by_xpath(NEXT).click()
                    sleep(randint(1 + sleep_margin, 3 + sleep_margin))
                    wd.implicitly_wait(10)
                    username = wd.find_element_by_xpath(
                        '/html/body/div[4]/div[2]/div/article/header/div[2]/div[1]/div[1]/a').text
                    seconds_published = wd.find_element_by_xpath(
                        '/html/body/div[4]/div[2]/div/article/div[2]/div[2]/a/time').text

                print('Username : ' + username + '\nPublished : ' + seconds_published.lower() + '\nUrl : ' + url + '\n')
                sleep(randint(1 + sleep_margin, 4 + sleep_margin))
                # Set a stop and do not interact with users with specific words in their usernames
                stop = stop_like(stopwords, username)
                # Check if the bot has already liked pics from that user
                liked_already = check_in_collection('LIKES', url)
                # Proceed to the liking step
                prob = randint(1, 100)
                if prob <= p_like and liked_already is None and stop == False:
                    # Like pic
                    like(wd, url, username, hstg, seconds_published)
                    sleep(randint(sleep_margin, 13 + sleep_margin))
                    like_counter += 1
                else:
                    # Ignore pic
                    print('{} not liked'.format(url))
                # Follow step
                if follow_active:
                    followed_already = check_in_collection('FOLLOWED', username)
                    if followed_already is None:
                        follow(10, wd, username)
                        sleep(randint(sleep_margin, 3 + sleep_margin))
                # Next picture
                try:
                    wd.find_element_by_link_text('Siguiente').click()
                except:
                    wd.find_element_by_xpath('/html/body/div[5]/div/div/div[2]/button[2]').click()
                    wd.implicitly_wait(5)
                    wd.find_element_by_link_text('Siguiente').click()
                sleep(randint(sleep_margin, 2 + sleep_margin))
                # Check if the limit is reached
                if like_counter >= limit:
                    print('LIMIT OF {} LIKES REACHED'.format(str(limit)))
                    break
        wd.quit()
        # Print summary of the run
        print('')
        print('Bot launched for around {0} pics on {1} hashtags.'.format(avg_nb_pics, len(hashtag_sample)))
        print('Liked {} photos.'.format(like_counter))
        print('Hashtags used : {}'.format(hashtag_sample))
        print('Execution time : ' + str(datetime.now() - startTime).split('.')[0] + '.')
        print('Finished at : ' + str(datetime.now()).split('.')[0])


if __name__ == '__main__':
    #Bot('YOURUSERNAME', 'YOURPASSWORD').action_from_list(lst=baseFolder + '\InstaData.xlsx', action='follow', until=18)
    #Bot('YOURUSERNAME', 'YOURPASSWORD').action_from_list(lst='\InstaData.xlsx', action='unfollow')
    #Bot('YOURUSERNAME', 'YOURPASSWORD').action_from_list(lst='\InstaData.xlsx', action='block')
    #Bot('YOURUSERNAME', 'YOURPASSWORD').action_from_list(lst='\InstaData.xlsx', action='message', until=None, message='Hello World !')
    Bot('YOURUSERNAME', 'YOURPASSWORD').by_hashtag(hashtag_list=HASHTAGS['TRAVEL3'], avg_nb_pics=8, p_like=88,
                                                follow_active=False, avg_hstg=10, sleep_margin=0, limit=55)
