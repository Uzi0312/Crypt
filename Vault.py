import tkinter as tk
from tkinter import ttk
import os
import getpass
import pyautogui
from cryptography.fernet import Fernet
import mysql.connector as mysql
import getpass
import random
import os
import time
import pyperclip
from win10toast import ToastNotifier




# Global variables to know: username, password. Others have txt or some underscore variable along w them.


# MySQL Setup
global mycon
mycon=mysql.connect(host="localhost",user="root",passwd="uzair123") 
if mycon.is_connected()==False:
    print("Server error, Try again in a moment")
else:
    global mycur
    mycur=mycon.cursor()
    dq="CREATE DATABASE IF NOT EXISTS pwmaindb"
    mycur.execute(dq)
    db="USE pwmaindb"
    mycur.execute(db)
    query="CREATE TABLE IF NOT EXISTS ACCOUNTS (ID INT AUTO_INCREMENT PRIMARY KEY, APPLICATION VARCHAR(20), USERNAME VARCHAR(20), EMAIL VARCHAR(100), PASSWORD VARCHAR(8000));"
    mycur.execute(query)
    query="CREATE TABLE IF NOT EXISTS SECURITY (ID INT AUTO_INCREMENT PRIMARY KEY, UID VARCHAR(5000));"
    mycur.execute(query)


# Globals
chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0133456789!@#$%^&*()_-+=\;<>.?/"


class Main():
    @staticmethod
    def run():
        Login_Page()


# Encryption/Decryption Tools
class Tools:
    @staticmethod
    def GeneratePassword():
        pswd = ''
        for i in range(0,16):
            pswd+=random.choice(chars)
        return pswd
    
    @staticmethod
    def Encrypt(app, username, email, pswd):
        key = Fernet.generate_key()  # Generate Encryption Key
        cipher = Fernet(key) # Create an instance of the Fernet cipher using the encryption key
        input_bytes = pswd.encode() # Convert the input string to bytes
        encrypted_bytes = cipher.encrypt(input_bytes) # Encrypt the input string
        encrypted_string = encrypted_bytes.decode() + random.choice(chars) # Convert the encrypted bytes to string format & Adding Salt
        MySQL.Insert(app, username, email, encrypted_string, key)

    @staticmethod
    def decrypt(pwd, encryption_key):
        pswd = pwd[:-1] #Removing Salt
        # Convert the encrypted string to bytes
        encrypted_bytes = pswd.encode()
        # Create an instance of the Fernet cipher using the encryption key
        cipher = Fernet(encryption_key)
        try:
            # Decrypt the encrypted bytes
            decrypted_bytes = cipher.decrypt(encrypted_bytes)
            # Convert the decrypted bytes to string format
            decrypted_string = decrypted_bytes.decode()
            return decrypted_string

        except Exception as e:
            print("Error decrypting the string:", str(e))
            return None
        

#SQL Tools
class MySQL:
    @staticmethod
    def Insert(app, username, email, pswd, key):
        string_key = key.decode()
        query = "INSERT INTO ACCOUNTS (APPLICATION, USERNAME, EMAIL, PASSWORD) VALUES ('{}','{}','{}','{}')".format(app, username,email, pswd)
        mycur.execute(query)
        mycon.commit()
        query = "INSERT INTO SECURITY (UID) VALUES ('{}')".format(string_key)
        mycur.execute(query)
        mycon.commit()

    @staticmethod
    def Fetch(ID):
        query = "SELECT PASSWORD FROM ACCOUNTS WHERE ID = '{}'".format(ID)
        mycur.execute(query)
        rec = mycur.fetchone()
        pwd_list = list(rec)
        encrypted_pswd = pwd_list[0]
        query2 = "SELECT USERNAME FROM ACCOUNTS WHERE ID = '{}'".format(ID)
        mycur.execute(query2)
        user_rec = mycur.fetchone()
        user_list = list(user_rec)
        user = user_list[0]
        query = "SELECT UID FROM SECURITY WHERE ID = '{}'".format(ID)
        mycur.execute(query)
        rec = mycur.fetchone()
        key_list = list(rec)
        key_item = key_list[0]
        encryption_key = key_item.encode()
        pwd = Tools.decrypt(encrypted_pswd, encryption_key)
        return user, pwd


# Security Tools
class Security:
    def Authenticate(path, pswd):
        # Expand the user's home directory in the file path
        expanded_path = os.path.expanduser(path)
        # Check if the expanded path exists
        if os.path.exists(expanded_path):
            # Perform your desired operations with the hidden file
            with open(expanded_path, 'r') as file:
                pwd = file.read()
                if pswd == pwd:
                    return True
                else:
                    return False
        else:
            print(f"The file '{expanded_path}' does not exist.")



# Actions When Button is Triggered.
class Actions:
    def Login():
        path = "~/OneDrive/Desktop/Python Projects/Password Manager/auth_key.txt"
        user_name = username.get()
        pswd = password.get()
        if user_name == '' or pswd == '':
            pyautogui.alert(text = 'Please enter your credentials', title = 'Password Manager', button = 'OK')
        elif user_name == 'Uzair':
            sec = Security.Authenticate(path, pswd)
            if sec == True:
                login_window.destroy()
                Home_Page()
            elif sec == False:
                pyautogui.alert(text = 'Incorrect password', title = 'Password Manager', button='OK')
            else:
                pass
        else:
            pyautogui.alert(text = 'User does not exist', title = 'Password Manager', button = 'OK')


    def Logout():
        pyautogui.alert(text = 'Session Expired!', title = 'Password Manager', button = 'OK')
        home_window.destroy()
        Login_Page() 

    #needs work
    def back(curwin, nxtwin):
        global CurWin, NxtWindow
        CurWin = curwin
        NxtWindow = nxtwin
        back_bttn=tk.Button(CurWin, text='Go Back', bg='#131411', fg='#9fe803', font='SansSerif 10 bold', command=Actions.NxtWin).place(x=0, y=0)

    def NxtWin():
        CurWin.destroy()
        NxtWindow()

    
    def SaveData():
        app = app_txt.get()
        username = username_txt.get()
        email = email_txt.get()
        pswd = pwd_txt.get()
        if app == '' or username == '' or email == '' or pswd == '':
            pyautogui.alert(text='Please enter all the details', title='Password Manager', button='OK')
        else:
            Tools.Encrypt(app, username, email, pswd)
            pyautogui.alert(text="Account details saved!", title='Password Manager', button='OK')
            newacc_window.destroy()
            Home_Page()

    def PwdGen():
        global generated_pwd
        generated_pwd = Tools.GeneratePassword()
        pwd_label=tk.Label(newacc_window, text=f"Generated Password: {generated_pwd}", font='SansSerif 13 bold', bg='#131411', fg='#9fe80e').place(x=510, y=450)
        b3 = tk.Button(newacc_window, text="Copy", font='SansSerif 10 bold', command= lambda: Actions.CopyPwd(generated_pwd), bg='#131411', fg='#9fe80e', bd=0.5).place(x=865, y=445)

    def CopyPwd(arg):
        pyperclip.copy(arg)

    def Auth2Show():
        path = '~/OneDrive/Desktop/Python Projects/Password Manager/key.txt'
        pswd = auth_txt.get()
        sec = Security.Authenticate(path, pswd)
        if sec == True:
            Actions.ShowPwd()
        else:
            pyautogui.alert(text='Incorrect password', title='Password Manager', button='OK')
            
    def ShowPwd():
        user, pwd = MySQL.Fetch(req_id)
        user_label=tk.Label(auth_window, text=f"Username: {user}", font='SansSerif 13 bold', bg='#131411', fg='#9fe80e').place(x=496, y=450)
        pwd_label=tk.Label(auth_window, text=f"Password: {pwd}", font='SansSerif 13 bold', bg='#131411', fg='#9fe80e').place(x=496, y=480)
        b1 = tk.Button(auth_window, text="Copy", font='SansSerif 9 bold', command= lambda: Actions.CopyPwd(user), bg='#131411', fg='#9fe80e', bd=0.5).place(x=840, y=445)
        b2 = tk.Button(auth_window, text="Copy", font='SansSerif 9 bold', command=lambda: Actions.CopyPwd(pwd), bg='#131411', fg='#9fe80e', bd=0.5).place(x=840, y=476)
        auth_txt.delete(0,20)

    def Settings():
        pswd_label=tk.Label(settings_window, text='Administrator Key:',font='SansSerif 13 bold', bg='#131411', fg='#9fe80e').place(x=495, y=355)
        global reset_txt
        reset_txt = tk.Entry(settings_window, bd=5, width=30, show='*')
        reset_txt.place(x=650, y=353)
        b1 = tk.Button(settings_window, text="Submit", font='SansSerif 13 bold', command= Actions.ResetDB).place(x=635, y=410)

    def ResetDB():
        path = "~/OneDrive/Desktop/Python Projects/Password Manager/auth_key.txt"
        pswd = reset_txt.get()
        sec =  Security.Authenticate(path, pswd)
        if sec == True:
            reset_txt.delete(0,20)
            query = "DROP DATABASE pwtest"
            mycur.execute(query)
            pyautogui.alert(title = 'Password Manager', text = "Database reset complete. Please restart the application", button = 'OK')
            settings_window.destroy()
        else:
            pyautogui.alert(title = 'Password Manager', text = 'Incorrect admin key!  Try again.', button = 'OK')




# Key Binds
class clicker:
    def Login_Page_Clicker(event):
        Actions.Login()

    def Acc_Page_Clicker(event):
        Auth_Page()

    def Auth_Page_Clicker(event):
        Actions.Auth2Show()

    def Settings_Page_Clicker(event):
        Actions.ResetDB()

# To Open Window in Full Screen 
class FullScreenApp(object):
    def __init__(self, master, **kwargs):
        self.master=master
        pad=3
        self._geom='200x200+0+0'
        master.geometry("{0}x{1}+0+0".format(
            master.winfo_screenwidth()-pad, master.winfo_screenheight()-pad))
        master.bind('<Escape>',self.toggle_geom)            
    
    def toggle_geom(self,event):
        geom=self.master.winfo_geometry()
        print(geom,self._geom)
        self.master.geometry(self._geom)
        self._geom=geom



# Pages
def Login_Page():
    global username, password, login_window
    login_window = tk.Tk()
    login_window.configure(background='#131411')
    header=tk.Label(login_window, text='Password Manager', bg='#131411', font='Helvetica 36 bold', padx=5, pady=5,bd=1, fg='#9fe80e').place(x=435,y=3)
    line1=tk.Label(login_window, text='_______________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________-', bg='#131411', fg='#9fe80e').place(x=0,y=100)
    user_label=tk.Label(login_window, text='Username:',font='SansSerif 13 bold', bg='#131411', fg='#9fe80e').place(x=515, y=290)
    password_label=tk.Label(login_window, text='Password:', font='SansSerif 13 bold', bg='#131411', fg='#9fe80e').place(x=515, y=325)
    username = tk.Entry(login_window, bd=5, width=30,)
    username.place(x=610, y=290)
    password = tk.Entry(login_window, bd=5, width= 30, show='*')
    password.place(x=610, y=325)
    login_btn = tk.Button(login_window, text="Login", font='SansSerif 13 bold', command=Actions.Login).place(x=650, y=375)
    login_window.bind('<Return>', clicker.Login_Page_Clicker)
    #sl=tk.Label(login_window, text="Don't have an account?", font='SansSerif 10', bg='#131411', fg='#9fe80e').place(x=560, y=415)
    #signbttn=tk.Button(login_window, text="Sign Up", width=7, height=1, bd=1, bg='#131411', fg='#9fe80e', font='SansSerif 8 bold', command=None).place(x=710, y=416)
    line2=tk.Label(login_window, text='_______________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________-', bg='#131411', fg='#9fe80e').place(x=0,y=600)
    copy_right_lbl=tk.Label(login_window, text="Copyright 2021 Ⓒ EZ Technologies Pvt. Ltd", font='SansSerif 10 bold', bg='#131411', fg='#9fe80e').place(x=540,y=625)
    creator_tag=tk.Label(login_window, text='Created by Uzair', font='SansSerif 8 italic', bg='#131411', fg='#9fe80e').place(x=630, y=645)
    app=FullScreenApp(login_window)
    login_window.mainloop()


def Home_Page():
    username = 'Uzair'
    global home_window
    home_window=tk.Tk()
    home_window.configure(background='#131411')
    home_window.title('EZ-Book')
    header=tk.Label(home_window, text='Password Manager', bg='#131411', font='Helvetica 36 bold', padx=5, pady=5,bd=1, fg='#9fe80e').place(x=435,y=3)
    line1=tk.Label(home_window, text='_______________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________-', bg='#131411', fg='#9fe80e').place(x=0,y=100)
    l1=tk.Label(home_window, text=f"Welcome {username}", bg='#131411', fg='#9fe80e', font="Helvetica 24 italic").place(x=555, y= 175)
    l2=tk.Label(home_window, text='What do you wanna do today?', bg='#131411', fg='#9fe80e', font='Helvetica 18 italic').place(x=510, y=215)
    b1=tk.Button(home_window, text='  Show Saved Accounts ', bg='#131411', fg='#9fe80e', font='Helvetica 16', bd=1, command=Accounts_Page, width=20).place(x=550, y=275)
    b2=tk.Button(home_window, text='  Add New Account ', bg='#131411', fg='#9fe80e', font='Helvetica 16', bd=1, command=NewAcc_Page, width=20).place(x=550, y=320)
    b4=tk.Button(home_window, text="  Settings ", bg='#131411', fg='#9fe80e', font='Helvetica 16', bd=1, command=Settings_Page, width=20).place(x=550, y=365)
    b6=tk.Button(home_window, text='   Logout ', bg='#131411', fg='#9fe80e', font='Helvetica 16', bd=1, command=Actions.Logout, width=20).place(x=550, y=410)
    line2=tk.Label(home_window, text='_______________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________-', bg='#131411', fg='#9fe80e').place(x=0,y=600)
    copy_right_lbl=tk.Label(home_window, text="Copyright 2021 Ⓒ EZ Technologies Pvt. Ltd", font='SansSerif 10 bold', bg='#131411', fg='#9fe80e').place(x=535,y=625)
    creator_tag=tk.Label(home_window, text='Created by Uzair', font='SansSerif 8 italic', bg='#131411', fg='#9fe80e').place(x=630, y=645)
    app=FullScreenApp(home_window)
    home_window.mainloop()

    
def NewAcc_Page():
    home_window.destroy()
    global newacc_window
    newacc_window=tk.Tk()
    newacc_window.configure(background='#131411')
    newacc_window.title('EZ-Book')
    Actions.back(newacc_window, Home_Page)
    header=tk.Label(newacc_window, text='Password Manager', bg='#131411', font='Helvetica 36 bold', padx=5, pady=5,bd=1, fg='#9fe80e').place(x=435,y=3)
    line1=tk.Label(newacc_window, text='_______________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________-', bg='#131411', fg='#9fe80e').place(x=0,y=100)
    app_label=tk.Label(newacc_window, text='Website / App:',font='SansSerif 13 bold', bg='#131411', fg='#9fe80e').place(x=510, y=251)
    username_label=tk.Label(newacc_window, text='Username:', font='SansSerif 13 bold', bg='#131411', fg='#9fe80e').place(x=510, y=285)
    email_label=tk.Label(newacc_window, text="Email ID:", font='SansSerif 13 bold', bg='#131411', fg='#9fe80e').place(x=510, y=319)
    pwd_label=tk.Label(newacc_window, text="Password:", font='SansSerif 13 bold', bg='#131411', fg='#9fe80e').place(x=510, y=354)
    global app_txt, username_txt, email_txt, pwd_txt
    app_txt = tk.Entry(newacc_window, bd=5, width=30,)
    app_txt.place(x=630, y=248)
    username_txt = tk.Entry(newacc_window, bd=5, width=30,)
    username_txt.place(x=630, y=282)
    email_txt = tk.Entry(newacc_window, bd=5, width=30,)
    email_txt.place(x=630, y=316)
    pwd_txt = tk.Entry(newacc_window, bd=5, width=30, show='*')
    pwd_txt.place(x=630, y=350)
    b1 = tk.Button(newacc_window, text="Generate Password", font='SansSerif 13 bold', command=Actions.PwdGen).place(x=590, y=400)
    b2 = tk.Button(newacc_window, text="Save Details", font='SansSerif 13 bold', command=Actions.SaveData).place(x=620, y=500)
    line2=tk.Label(newacc_window, text='_______________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________-', bg='#131411', fg='#9fe80e').place(x=0,y=600)
    copy_right_lbl=tk.Label(newacc_window, text="Copyright 2021 Ⓒ EZ Technologies Pvt. Ltd", font='SansSerif 10 bold', bg='#131411', fg='#9fe80e').place(x=535,y=625)
    creator_tag=tk.Label(newacc_window, text='Created by Uzair', font='SansSerif 8 italic', bg='#131411', fg='#9fe80e').place(x=630, y=645)
    app=FullScreenApp(newacc_window)
    newacc_window.mainloop()


def Accounts_Page():
    q="SELECT ID, APPLICATION, USERNAME, EMAIL FROM accounts"
    mycur.execute(q)
    r=mycur.fetchall()
    if len(r)==0:
        pyautogui.alert(title = 'Password Manager', text = "Database empty!", button = 'OK')
    else:
        home_window.destroy()
        global accounts_window
        accounts_window=tk.Tk()
        accounts_window.configure(background='#131411')
        accounts_window.title('EZ-Book')
        header=tk.Label(accounts_window, text='Password Manager', bg='#131411', font='Helvetica 36 bold', padx=5, pady=5,bd=1, fg='#9fe80e').place(x=435,y=3)
        Actions.back(accounts_window, Home_Page)
        line1=tk.Label(accounts_window, text='_______________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________-', bg='#131411', fg='#9fe80e').place(x=0,y=100)
        frm=tk.Frame(accounts_window)
        frm.place(x=150,y=200)
        tv=ttk.Treeview(frm)
        tv['columns']=('S.no','Application','Username','Email')
        tv.column('#0',width=0, minwidth=25)
        tv.column('S.no',width=50, minwidth=20, anchor=tk.CENTER)
        tv.column('Application',width=170, minwidth=25,anchor=tk.CENTER)
        tv.column('Username',width=200, minwidth=25, anchor=tk.CENTER)
        tv.column('Email',width=300, minwidth=25, anchor=tk.CENTER)
        tv.pack()
        tv.heading('S.no', text='S.NO', anchor=tk.CENTER)  
        tv.heading('Application', text='APPLICATION', anchor=tk.CENTER)  
        tv.heading('Username', text='USERNAME', anchor=tk.CENTER)  
        tv.heading('Email', text='EMAIL', anchor=tk.CENTER)  
        style=ttk.Style(accounts_window)
        style.theme_use('clam')
        style.configure('Treeview', background='silver',foreground='black',rowheight=25,fieldbackground='silver')
        style.map('Treeview',background=[('selected','black')])
        global rec_count
        rec_count = len(r)
        for i in r:
            tv.insert('','end',values=i)
        pswd_label=tk.Label(accounts_window, text='App / Website ID:',font='SansSerif 13 bold', bg='#131411', fg='#9fe80e').place(x=915, y=200)
        global id_txt
        id_txt = tk.Entry(accounts_window, bd=5, width=30)
        id_txt.place(x=1060, y=200)
        b1 = tk.Button(accounts_window, text="Show Password", font='SansSerif 11 bold', command=Auth_Page).place(x=1095, y=250)
        accounts_window.bind('<Return>', clicker.Acc_Page_Clicker)
        line2=tk.Label(accounts_window, text='_______________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________-', bg='#131411', fg='#9fe80e').place(x=0,y=600)
        copy_right_lbl=tk.Label(accounts_window, text="Copyright 2021 Ⓒ EZ Technologies Pvt. Ltd", font='SansSerif 10 bold', bg='#131411', fg='#9fe80e').place(x=535,y=625)
        creator_tag=tk.Label(accounts_window, text='Created by Uzair', font='SansSerif 8 italic', bg='#131411', fg='#9fe80e').place(x=630, y=645)
        app=FullScreenApp(accounts_window)
        accounts_window.mainloop()


def Auth_Page():
    global req_id
    req_id = int(id_txt.get())
    if req_id>rec_count:
        pyautogui.alert(title='Password Manager', text='Please enter a valid ID', button='OK')
    else:
        accounts_window.destroy()
        global auth_window
        auth_window=tk.Tk()
        auth_window.configure(background='#131411')
        auth_window.title('EZ-Book')
        header=tk.Label(auth_window, text='Password Manager', bg='#131411', font='Helvetica 36 bold', padx=5, pady=5,bd=1, fg='#9fe80e').place(x=435,y=3)
        Actions.back(auth_window, Home_Page)
        line1=tk.Label(auth_window, text='_______________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________-', bg='#131411', fg='#9fe80e').place(x=0,y=100)
        pswd_label=tk.Label(auth_window, text='Administrator Key:',font='SansSerif 13 bold', bg='#131411', fg='#9fe80e').place(x=495, y=250)
        global auth_txt
        auth_txt = tk.Entry(auth_window, bd=5, width=30, show='*')
        auth_txt.place(x=650, y=248)
        b1 = tk.Button(auth_window, text="Submit", font='SansSerif 13 bold', command= Actions.Auth2Show).place(x=635, y=320)
        auth_window.bind('<Return>', clicker.Auth_Page_Clicker)
        line2=tk.Label(auth_window, text='_______________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________-', bg='#131411', fg='#9fe80e').place(x=0,y=600)
        copy_right_lbl=tk.Label(auth_window, text="Copyright 2021 Ⓒ EZ Technologies Pvt. Ltd", font='SansSerif 10 bold', bg='#131411', fg='#9fe80e').place(x=535,y=625)
        creator_tag=tk.Label(auth_window, text='Created by Uzair', font='SansSerif 8 italic', bg='#131411', fg='#9fe80e').place(x=630, y=645)
        app=FullScreenApp(auth_window)
        auth_window.mainloop()

def Settings_Page():
    home_window.destroy()
    global settings_window
    settings_window=tk.Tk()
    settings_window.configure(background='#131411')
    settings_window.title('EZ-Book')
    header=tk.Label(settings_window, text='Password Manager', bg='#131411', font='Helvetica 36 bold', padx=5, pady=5,bd=1, fg='#9fe80e').place(x=435,y=3)
    Actions.back(settings_window, Home_Page)
    line1=tk.Label(settings_window, text='_______________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________-', bg='#131411', fg='#9fe80e').place(x=0,y=100)
    l1=tk.Label(settings_window, text="Settings", bg='#131411', fg='#9fe80e', font="Helvetica 28").place(x=600, y= 130)
    b2=tk.Button(settings_window, text='  Reset Database ', bg='#131411', fg='#9fe80e', font='Helvetica 16', bd=1, command=Actions.Settings, width=20).place(x=550, y=250)
    settings_window.bind('<Return>', clicker.Settings_Page_Clicker)
    line2=tk.Label(settings_window, text='_______________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________-', bg='#131411', fg='#9fe80e').place(x=0,y=600)
    copy_right_lbl=tk.Label(settings_window, text="Copyright 2021 Ⓒ EZ Technologies Pvt. Ltd", font='SansSerif 10 bold', bg='#131411', fg='#9fe80e').place(x=535,y=625)
    creator_tag=tk.Label(settings_window, text='Created by Uzair', font='SansSerif 8 italic', bg='#131411', fg='#9fe80e').place(x=630, y=645)
    app=FullScreenApp(settings_window)
    settings_window.mainloop()


Main.run()