import tkinter as tk
import pymongo
from selenium import webdriver
import time
import instaloader
import certifi
import os
from PIL import ImageTk, Image

USERNAME = ""
SITE = ""


def sendentry():
    global USERNAME, SITE
    USERNAME = Entry.get()
    Entry.delete(0, 'end')
    SITE = defaulttext.get()
    whatsite()

root = tk.Tk()
root.geometry("700x400")  # gui screen size

# Dropdown menu
defaulttext = tk.StringVar(root)
defaulttext.set("Choose a Site")  # default value
w = tk.OptionMenu(root, defaulttext, "Facebook", "Instagram", "TikTok").place(x=335, y=120,
                                                                                                anchor="center")
Entry = tk.Entry(root, width=17)
Entry.place(x=335, y=190, anchor="center")
print(Entry.get())

# Button For Sending the Uid
b1 = tk.Button(root,
               text="Get Items",
               width=4,
               bg='black',
               fg='white',
               padx=30,
               command=sendentry)
b1.place(x=335,
          y=220,
          anchor="center")

# Header
Text = tk.Label(root, text="Enter Uid", ).place(x=335, y=170, anchor="center")


def instagetter():

    L = instaloader.Instaloader()
    posts = instaloader.Profile.from_username(L.context, USERNAME).get_posts()
    count = 1
    os.mkdir(os.path.join(os.getcwd(),USERNAME))
    for post in posts:
        L.download_post(post, USERNAME)
        count = count+1
        if(count >3):
            break
    l = os.listdir(os.path.join(os.getcwd(),USERNAME))
    l = filter(lambda x:'txt' in x, l)
    myclient = pymongo.MongoClient(
      "mongodb+srv://admin:admin@cluster0.hpip7.mongodb.net/myFirstDatabase?retryWrites=true&w=majority", tlsCAFile=certifi.where()
    )
    mydb = myclient["panda"]
    mycol = mydb["instagram"]
    for i in l:
        mydict = { "name": USERNAME, "file": i.split(".")[0] }
        mycol.insert_one(mydict)



client = pymongo.MongoClient(
    "mongodb+srv://admin:admin@cluster0.hpip7.mongodb.net/myFirstDatabase?retryWrites=true&w=majority"
)
DB = client['panda']
FACEBOOK = DB['Facebook']
INSTAGRAM = DB['instagram']


# TODO: scraping function

def download_facebook_post(page):
    driver = webdriver.Chrome()
    driver.get('https://www.facebook.com/' + page + '/')
    for scroll in range(5):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
    posts = driver.find_elements_by_class_name("userContentWrapper")
    result = []
    for post in posts:
        row = {}
        row.update({"scrap_type": "facebook"})
        row.update({"page": page})
        time_element = post.find_element_by_css_selector("abbr")
        utime = time_element.get_attribute("data-utime")
        row.update({"utime": utime})

        text = ""
        text_elements = post.find_elements_by_css_selector("p")
        for elm in text_elements:
            text += elm.text
        row.update({"post": text})
        result.append(row)
    driver.close()
    FACEBOOK.insert_many(result[-3::])


def whatsite():
    if SITE == 'Instagram':
        if not list(INSTAGRAM.find({'name': USERNAME})):
            instagetter()

        for post in INSTAGRAM.find({'name': USERNAME}):
            filename = post['file'] + '.jpg'

            if not os.path.isfile(os.path.join(os.getcwd(), USERNAME, filename)):
                filename = post['file'] + '_1.jpg'

            filename = os.path.join(os.getcwd(), USERNAME, filename)
            img = Image.open(filename)
            img.show()

    elif SITE == 'Facebook':
        if not list(FACEBOOK.find({'page': USERNAME})):
            download_facebook_post(USERNAME)


root.mainloop()

