# Python 3.8

import os, wx, sys, time
from tabulate import tabulate
from script import Bot
from hashtaglist import HASHTAGS
from db import get_from_mongo, query_date, query_user
from functions import get_users_from_xlsx_list


baseFolder = os.path.dirname(os.path.abspath('__file__'))
wildcard = "All files (*.*)|*.*|" \
           "Python source (*.py)|*.py"


def scale_bitmap(bitmap, width, height):
    image = wx.ImageFromBitmap(bitmap)
    image = image.Scale(width, height, wx.IMAGE_QUALITY_HIGH)
    result = wx.BitmapFromImage(image)
    return result


class Global(wx.Frame):

    def __init__(self, parent, title):
        super(Global, self).__init__(parent, title=title, size=(900, 600))
        self.InitUI()
        self.Centre()
        icon = wx.EmptyIcon()
        icon.CopyFromBitmap(wx.Bitmap("insta.ico", wx.BITMAP_TYPE_ANY))
        self.SetIcon(icon)

    def InitUI(self):
        nb = wx.Notebook(self)
        nb.AddPage(Panel1(nb), "Commands")
        nb.AddPage(Panel2(nb), "Data")
        nb.AddPage(Panel4(nb), "Logs")
        self.Show(True)


class Panel1(wx.Panel):

    def __init__(self, parent):
        super(Panel1, self).__init__(parent)

        sizer_top = wx.GridBagSizer(5, 5)
        sizer_bottom = wx.GridBagSizer(5, 5)

        # Header
        titre = wx.StaticText(self, label="Your Insta Robot")
        sizer_top.Add(titre, pos=(0, 0), span=(1, 20), flag=wx.TOP | wx.LEFT, border=15)
        ligne = wx.StaticLine(self)
        sizer_top.Add(ligne, pos=(1, 0), span=(1, 20), flag=wx.EXPAND | wx.BOTTOM | wx.LEFT, border=10)

        imageFile = baseFolder + "\\Logo.png"
        png = wx.Image(imageFile, wx.BITMAP_TYPE_ANY).ConvertToBitmap()
        png = scale_bitmap(png, 60, 60)
        logo = wx.StaticBitmap(self, -1, png, (10, 5), (png.GetWidth(), png.GetHeight()))
        sizer_top.Add(logo, pos=(0, 24), span=(4, 5), flag=wx.EXPAND | wx.BOTTOM | wx.LEFT | wx.TOP, border=10)

        # Inputs
        lbl_user = wx.StaticText(self, label="Username")
        sizer_top.Add(lbl_user, pos=(2, 0), flag=wx.LEFT | wx.ALIGN_CENTER, border=5)

        self.user = wx.TextCtrl(self, value="")
        sizer_top.Add(self.user, pos=(2, 1), flag=wx.LEFT | wx.EXPAND, border=5)

        lbl_psw = wx.StaticText(self, label="Password")
        sizer_top.Add(lbl_psw, pos=(2, 3), flag=wx.LEFT | wx.ALIGN_CENTER, border=15)

        self.psw = wx.TextCtrl(self, value="", style=wx.TE_PASSWORD)
        sizer_top.Add(self.psw, pos=(2, 4), flag=wx.LEFT | wx.EXPAND, border=5)

        lbl_browse = wx.StaticText(self, label="List of users :")
        sizer_top.Add(lbl_browse, pos=(4, 0), flag=wx.LEFT | wx.ALIGN_RIGHT, border=15)

        self.input_browse = wx.TextCtrl(self, value="")
        sizer_top.Add(self.input_browse, pos=(4, 1), span=(1, 20), flag=wx.LEFT | wx.EXPAND, border=5)

        lbl_hashtags = wx.StaticText(self, label="Hashtags : ")
        sizer_top.Add(lbl_hashtags, pos=(5, 0), flag=wx.LEFT | wx.TOP, border=15)

        self.HashtagBox = wx.TextCtrl(self, style=wx.TE_MULTILINE | wx.TE_CHARWRAP)
        sizer_top.Add(self.HashtagBox, pos=(6, 0), span=(6, 25), flag=wx.LEFT | wx.EXPAND, border=15)

        # Buttons
        btn_browse = wx.Button(self, label="Browse")
        sizer_top.Add(btn_browse, pos=(4, 24), flag=wx.RIGHT, border=5)
        self.Bind(wx.EVT_BUTTON, self.onBrowse, btn_browse)

        btn_loadhstg = wx.Button(self, label="Load Hashtags")
        sizer_bottom.Add(btn_loadhstg, pos=(12, 2), flag=wx.TOP | wx.RIGHT | wx.LEFT, border=5)
        self.Bind(wx.EVT_BUTTON, self.onLoad, btn_loadhstg)

        btn_extract = wx.Button(self, label="Extract users")
        sizer_bottom.Add(btn_extract, pos=(12, 6), flag=wx.TOP | wx.RIGHT | wx.LEFT, border=5)
        self.Bind(wx.EVT_BUTTON, self.onExtract, btn_extract)

        btn_launch = wx.Button(self, label="Launch Robot")
        sizer_bottom.Add(btn_launch, pos=(18, 9), flag=wx.TOP | wx.RIGHT | wx.LEFT, border=5)
        self.Bind(wx.EVT_BUTTON, self.onGeneral, btn_launch)

        # Options
        nbs = [str(x) for x in range(1, 16)]
        nbspb = [str(x) for x in range(100, -1, -10)]
        nbslk = [str(x) for x in range(60, -1, -5)]
        TrueFalse = ['True', 'False']
        HASHTAGLIST = list(HASHTAGS.keys())
        Modes = ['ByHashtag', 'Follow', 'Unfollow', 'Block', 'Message']
        ControlBox = wx.StaticBox(self, label="Options", pos=(15, 350), size=(750, 85), style=0)

        lbl_avg_nb_pics = wx.StaticText(ControlBox, label="Pics per hashtag", style=wx.ALIGN_RIGHT)
        sizer_bottom.Add(lbl_avg_nb_pics, pos=(1, 1), flag=wx.LEFT | wx.ALIGN_CENTER, border=5)

        self.avg_nb_pics = wx.ComboBox(ControlBox, choices=nbs, value='8')
        sizer_bottom.Add(self.avg_nb_pics, pos=(1, 2), flag=wx.ALIGN_CENTER, border=5)

        lbl_avg_hstg = wx.StaticText(ControlBox, label="Number of hashtags", style=wx.ALIGN_RIGHT)
        sizer_bottom.Add(lbl_avg_hstg, pos=(2, 1), flag=wx.LEFT | wx.ALIGN_CENTER, border=5)

        self.avg_hstg = wx.ComboBox(ControlBox, choices=nbs, value='10')
        sizer_bottom.Add(self.avg_hstg, pos=(2, 2), flag=wx.ALIGN_CENTER, border=5)

        lbl_p_like = wx.StaticText(ControlBox, label="Probability of like", style=wx.ALIGN_RIGHT)
        sizer_bottom.Add(lbl_p_like, pos=(1, 3), flag=wx.LEFT | wx.ALIGN_CENTER, border=5)

        self.p_like = wx.ComboBox(ControlBox, choices=nbspb, value='88')
        sizer_bottom.Add(self.p_like, pos=(1, 4), flag=wx.ALIGN_CENTER, border=5)

        lbl_hstgs = wx.StaticText(ControlBox, label="Choose a list", style=wx.ALIGN_RIGHT)
        sizer_bottom.Add(lbl_hstgs, pos=(2, 3), flag=wx.LEFT | wx.ALIGN_CENTER, border=5)

        self.lbl_hstgs = wx.ComboBox(ControlBox, choices=HASHTAGLIST, value='TRAVEL0')
        sizer_bottom.Add(self.lbl_hstgs, pos=(2, 4), flag=wx.ALIGN_CENTER, border=5)

        lbl_limit = wx.StaticText(ControlBox, label="Like limit", style=wx.ALIGN_RIGHT)
        sizer_bottom.Add(lbl_limit, pos=(1, 5), flag=wx.LEFT | wx.ALIGN_CENTER, border=5)

        self.limit = wx.ComboBox(ControlBox, choices=nbslk, value='55')
        sizer_bottom.Add(self.limit, pos=(1, 6), flag=wx.ALIGN_CENTER, border=5)

        lbl_sleep_margin = wx.StaticText(ControlBox, label="Sleep margin", style=wx.ALIGN_RIGHT)
        sizer_bottom.Add(lbl_sleep_margin, pos=(2, 5), flag=wx.LEFT | wx.ALIGN_CENTER, border=5)

        self.sleep_margin = wx.ComboBox(ControlBox, choices=nbs[0:5], value='2')
        sizer_bottom.Add(self.sleep_margin, pos=(2, 6), flag=wx.ALIGN_CENTER, border=5)

        self.rbox_follow = wx.RadioBox(ControlBox, label='Follow', choices=TrueFalse, majorDimension=1,
                                       style=wx.RA_SPECIFY_ROWS)
        sizer_bottom.Add(self.rbox_follow, pos=(1, 7), span=(2, 1), flag=wx.ALIGN_CENTER)

        self.rbox_mode = wx.RadioBox(self, label='Function', choices=Modes, majorDimension=1, style=wx.RA_SPECIFY_ROWS)
        sizer_bottom.Add(self.rbox_mode, pos=(17, 1), span=(4, 4))

        lbl_until = wx.StaticText(self, label="Pick from list", style=wx.ALIGN_RIGHT)
        sizer_bottom.Add(lbl_until, pos=(17, 5), flag=wx.LEFT | wx.ALIGN_CENTER, border=5)

        self.until = wx.ComboBox(self, choices=nbs, value='21')
        sizer_bottom.Add(self.until, pos=(18, 5), flag=wx.LEFT | wx.ALIGN_CENTER, border=5)

        lbl_message = wx.StaticText(self, label="Message", style=wx.ALIGN_RIGHT)
        sizer_bottom.Add(lbl_message, pos=(17, 6), span=(1, 3), flag=wx.LEFT | wx.ALIGN_CENTER, border=5)

        self.message = wx.TextCtrl(self, value='Hello !')
        sizer_bottom.Add(self.message, pos=(18, 6), span=(1, 3), flag=wx.LEFT | wx.ALIGN_CENTER, border=5)

        self.SetSizer(sizer_top)
        sizer_top.Fit(self)
        self.SetSizer(sizer_bottom)
        sizer_bottom.Fit(self)

        self.input_browse.SetValue(f'{baseFolder}\InstaData.xlsx')
        self.user.SetValue('')
        self.psw.SetValue('')
        self.rbox_follow.SetSelection(1)

    def onGeneral(self, event):

        user = self.user.GetValue()
        psw = self.psw.GetValue()
        hashtag_list = HASHTAGS[self.lbl_hstgs.GetValue()]
        avg_nb_pics = int(self.avg_nb_pics.GetValue())
        p_like = int(self.p_like.GetValue())
        follow = str(self.rbox_follow.GetStringSelection())
        avg_hstg = int(self.avg_hstg.GetValue())
        sleep_margin = int(self.sleep_margin.GetValue())
        limit = int(self.limit.GetValue())
        mode = str(self.rbox_mode.GetStringSelection())
        message = self.message.GetValue()
        list_users = self.HashtagBox.GetValue().replace('[', '').replace(']', '').replace('\'', '').replace(' ',
                                                                                                            '').split(
            ',')
        if self.until.GetValue() == '':
            until = None
        else:
            until = int(self.until.GetValue())

        if mode == 'ByHashtag':
            Bot(user, psw).by_hashtag(hashtag_list, avg_nb_pics, p_like, follow, avg_hstg, sleep_margin, limit)
        elif mode == 'Follow':
            Bot(user, psw).action_from_list(lst=list_users, action='follow', until=until)
        elif mode == 'Unfollow':
            Bot(user, psw).action_from_list(lst=list_users, action='unfollow', until=until)
        elif mode == 'Block':
            Bot(user, psw).action_from_list(lst=list_users, action='block', until=until)
        elif mode == 'Message':
            Bot(user, psw).action_from_list(lst=list_users, action='message', until=until, message=message)
        else:
            pass

    def onLoad(self, event):
        lst = self.lbl_hstgs.GetValue()
        self.HashtagBox.SetValue(HASHTAGS[lst])

    def onExtract(self, event):
        file = self.input_browse.GetValue()
        lst = get_users_from_xlsx_list(file)
        self.HashtagBox.SetValue(str(lst))

    def onBrowse(self, event):
        dlg = wx.FileDialog(
            self, message="Choose a file",
            defaultDir=baseFolder,
            defaultFile="",
            wildcard=wildcard,
            style=wx.FD_OPEN | wx.FD_MULTIPLE | wx.FD_CHANGE_DIR
        )
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            self.input_browse.Clear()
            self.input_browse.SetValue(path)
        dlg.Destroy()


class Panel2(wx.Panel):

    def __init__(self, parent):

        super(Panel2, self).__init__(parent)
        sizer = wx.GridBagSizer(5, 5)

        # Header
        titre = wx.StaticText(self, label="Retrieve information from your database")
        sizer.Add(titre, pos=(0, 0), span=(1, 8), flag=wx.EXPAND | wx.TOP | wx.LEFT, border=15)
        ligne = wx.StaticLine(self)
        sizer.Add(ligne, pos=(1, 0), span=(1, 8), flag=wx.EXPAND | wx.BOTTOM | wx.LEFT, border=10)

        # Inputs
        lblList = ['Likes', 'Messages', 'Followed', 'Unfollowed', 'Blocked']
        self.rbox_collections = wx.RadioBox(self, label='Search in collection : ', pos=(20, 20), choices=lblList,
                                            majorDimension=1, style=wx.RA_SPECIFY_ROWS)
        sizer.Add(self.rbox_collections, pos=(2, 1), span=(2, 6), flag=wx.EXPAND | wx.BOTTOM | wx.RIGHT, border=20)

        lbl_user = wx.StaticText(self, label="Search for username : ")
        sizer.Add(lbl_user, pos=(4, 0), span=(1, 2), flag=wx.LEFT | wx.ALIGN_CENTER, border=5)

        self.user = wx.TextCtrl(self, value="")
        sizer.Add(self.user, pos=(4, 2), flag=wx.LEFT | wx.EXPAND, border=5)

        lbl_date = wx.StaticText(self, label="Search for date")
        sizer.Add(lbl_date, pos=(4, 3), flag=wx.LEFT | wx.ALIGN_CENTER, border=15)

        self.date = wx.TextCtrl(self, value="")
        sizer.Add(self.date, pos=(4, 4), flag=wx.LEFT | wx.EXPAND, border=5)

        self.ResultBox = wx.TextCtrl(self, style=wx.TE_READONLY | wx.TE_MULTILINE)
        sizer.Add(self.ResultBox, pos=(6, 0), span=(8, 10), flag=wx.LEFT | wx.EXPAND, border=15)

        # Buttons
        btn_search = wx.Button(self, label="Search All")
        sizer.Add(btn_search, pos=(2, 9), flag=wx.TOP, border=15)
        self.Bind(wx.EVT_BUTTON, self.onGet, btn_search)

        btn_find = wx.Button(self, label="Find")
        sizer.Add(btn_find, pos=(4, 9), flag=wx.RIGHT, border=5)
        self.Bind(wx.EVT_BUTTON, self.onGet2, btn_find)

        btn_CSV = wx.Button(self, label="Generate CSV")
        sizer.Add(btn_CSV, pos=(15, 1), flag=wx.RIGHT, border=5)
        self.Bind(wx.EVT_BUTTON, self.onCSV, btn_CSV)

        self.SetSizer(sizer)
        sizer.Fit(self)

    def onGet(self, event):
        col = self.rbox_collections.GetStringSelection().upper()
        res, nb = get_from_mongo(col)
        res = tabulate(res, headers='keys', showindex=False)
        self.ResultBox.SetValue('There are {0} entries ! \n\rHere is the list : \n\r {1}'.format(nb, res))

    def onGet2(self, event):
        col = self.rbox_collections.GetStringSelection().upper()
        username = self.user.GetValue()
        date = self.date.GetValue()
        if username != '':
            res_username = query_user(col, username)
            res_username = tabulate(res_username, headers='keys', showindex=False)
            self.ResultBox.SetValue(res_username)
        if date != '':
            res_date, nb = query_date(col, date)
            res_date = tabulate(res_date, headers='keys', showindex=False)
            self.ResultBox.SetValue('There are {0} entries ! \n\r {1}'.format(nb, res_date))

    def onCSV(self, event):
        col = self.rbox_collections.GetStringSelection().upper()
        res, nb = get_from_mongo(col)
        if not os.path.exists(baseFolder + "\\Extractions"):
            os.makedirs(baseFolder + "\\Extractions\\")
        res.to_csv(baseFolder + "\\Extractions\\ " + time.strftime("%Y%m%d-%H%M%S") + "_Extract.csv")


class Panel4(wx.Panel):
    def __init__(self, parent):
        super(Panel4, self).__init__(parent)
        sizer = wx.GridBagSizer(5, 5)

        # Header
        titre = wx.StaticText(self, label="Logs of the application")
        sizer.Add(titre, pos=(0, 0), span=(1, 20), flag=wx.TOP | wx.LEFT, border=15)
        ligne = wx.StaticLine(self)
        sizer.Add(ligne, pos=(1, 0), span=(1, 20), flag=wx.EXPAND | wx.BOTTOM | wx.LEFT, border=10)

        # Inputs
        lbl3 = wx.StaticText(self, label="Logs")
        sizer.Add(lbl3, pos=(5, 0), flag=wx.LEFT | wx.TOP, border=15)

        self.ResultBox = wx.TextCtrl(self, style=wx.TE_READONLY | wx.TE_MULTILINE)
        sizer.Add(self.ResultBox, pos=(6, 0), span=(12, 40), flag=wx.LEFT | wx.EXPAND, border=15)

        # Buttons
        btn_TXT = wx.Button(self, label="Generate .txt")
        sizer.Add(btn_TXT, pos=(19, 1), flag=wx.RIGHT, border=5)
        self.Bind(wx.EVT_BUTTON, self.onTxt, btn_TXT)

        self.SetSizer(sizer)
        sizer.Fit(self)

        sys.stdout = self.ResultBox

    def onTxt(self, event):
        log = self.ResultBox.GetValue()
        if not os.path.exists(baseFolder + "\\Logs"):
            os.makedirs(baseFolder + "\\Logs\\")
        f = open(baseFolder + "\\Logs\\" + time.strftime("%Y%m%d-%H%M%S") + "_Log.txt", "w")
        f.write(log)
        f.close()


def main():
    app = wx.App()
    Global(None, 'InstaBot').Show()
    app.MainLoop()


if __name__ == '__main__':
    main()
