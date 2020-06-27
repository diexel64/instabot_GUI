# instabot_GUI
An easy-to-use robot for instagram with a graphical interface using wxPython and MongoDB.

1. Before using

You will need to install a few libraries listed below. To do this, just type pip install {nameofthelibrary}.
- wxPython
- selenium
- pandas
- xlrd
- openpyxl
- pymongo
- tabulate

2. Use

The easiest way to use the robot is to launch the file "Robot.py". Then, a GUI interface is going to appear with some of the fields already completed. This fields can be modified by the user. Before launching the robot, the username and password fields must be filled, otherwise the web browser won't be able to log into the account.

Once all the required fields are filled just click on the "Launch" button.

3. Modes

The robot supports different tasks:

- the default mode is "by hashtag", this means the robot will go through a predefined list of hashtags and likes a defined number of pictures for each of them, based on a defined probability.

- other modes are based on a list of usernames. This list has to be placed in the InstaData.xlsx file, in the first column of the first sheet. The robot will then be able to extract the users and start the given task on all of them. These tasks can be to follow or unfollow, to block each user, or even to message each user. In the last case, a message has to be set before.

4. Caution

The robot is very slow, especially in the "by hashtag" mode. It has been built like this on purpose to avoid getting identified as a robot. Therefore some random sleeps have been set, but also a default like limit around 55 pics. At the time of writing, more than 60 likes per hour is considered by Instagram as too much, so the account can be temporarily banned. When it comes to other modes, the robot could follow or unfollow 10, 100, or 1000 users if a list is given, however, a possibility of picking up to N number of users is available.

5. Further ideas

- make a more beautiful GUI interface
- add a "remember me" functionality for the GUI interface
- add a chat function, making the robot able to read a conversation and respond accordingly
- add functions / filters to retreive data easily from mongo database
