from tkinter import *
from tkinter import ttk
from tkinter import messagebox
from employees import connectDataBase
import hashlib
import os
import binascii


# ---------------------------------------------------------------------------
# Password / security-answer hashing helpers (PBKDF2-HMAC-SHA256, salted)
# ---------------------------------------------------------------------------
def hashValue(value, saltHex=None):
    if saltHex is None:
        saltHex = binascii.hexlify(os.urandom(16)).decode('utf-8')
    salt = binascii.unhexlify(saltHex)
    digest = hashlib.pbkdf2_hmac('sha256', value.encode('utf-8'), salt, 100000)
    return saltHex, binascii.hexlify(digest).decode('utf-8')


def verifyValue(value, saltHex, hashHex):
    _, computedHash = hashValue(value, saltHex)
    return computedHash == hashHex


def createUsersTable():
    cursor, connection = connectDataBase()
    if not cursor or not connection:
        return
    try:
        cursor.execute('CREATE DATABASE IF NOT EXISTS inventory')
        cursor.execute('USE inventory')
        cursor.execute('''CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(50) UNIQUE NOT NULL,
            password VARCHAR(255) NOT NULL,
            salt VARCHAR(64) NOT NULL,
            securityQuestion VARCHAR(255) NOT NULL,
            securityAnswer VARCHAR(255) NOT NULL,
            securityAnswerSalt VARCHAR(64) NOT NULL
        )''')
        connection.commit()
    except Exception as e:
        messagebox.showerror('Error', f'Error! {e}')
    finally:
        cursor.close()
        connection.close()


# ---------------------------------------------------------------------------
# Auth actions
# ---------------------------------------------------------------------------
def attemptLogin(window, usernameEntry, passwordEntry):
    username = usernameEntry.get().strip()
    password = passwordEntry.get()

    if username == '' or password == '':
        messagebox.showerror('Error', 'All Fields Required')
        return

    cursor, connection = connectDataBase()
    if not cursor or not connection:
        return
    try:
        cursor.execute('USE inventory')
        cursor.execute('SELECT password, salt FROM users WHERE username = %s', (username,))
        record = cursor.fetchone()
        if not record:
            messagebox.showerror('Error', 'Invalid Username or Password')
            return
        storedHash, storedSalt = record[0], record[1]
        if not verifyValue(password, storedSalt, storedHash):
            messagebox.showerror('Error', 'Invalid Username or Password')
            return
    except Exception as e:
        messagebox.showerror('Error', f'Error! {e}')
        return
    finally:
        cursor.close()
        connection.close()

    # Cancel banner timer before destroying window
    for after_id in window.tk.call('after', 'info'):
        try:
            window.after_cancel(after_id)
        except Exception:
            pass

    window.destroy()
    from dashboard import open_dashboard
    open_dashboard()
    
def registerUser(registerWindow, usernameEntry, passwordEntry, confirmEntry, questionComboBox, answerEntry):
    username = usernameEntry.get().strip()
    password = passwordEntry.get()
    confirm = confirmEntry.get()
    question = questionComboBox.get()
    answer = answerEntry.get().strip()

    if username == '' or password == '' or confirm == '' or question == 'Select Security Question' or answer == '':
        messagebox.showerror('Error', 'All Fields Required')
        return
    if password != confirm:
        messagebox.showerror('Error', 'Passwords Do Not Match')
        return

    cursor, connection = connectDataBase()
    if not cursor or not connection:
        return
    try:
        cursor.execute('USE inventory')
        cursor.execute('SELECT username FROM users WHERE username = %s', (username,))
        if cursor.fetchone():
            messagebox.showerror('Error', 'Username Already Exists')
            return
        passSalt, passHash = hashValue(password)
        ansSalt, ansHash = hashValue(answer.lower())
        cursor.execute('''INSERT INTO users (username, password, salt, securityQuestion, securityAnswer, securityAnswerSalt)
                           VALUES (%s, %s, %s, %s, %s, %s)''',
                        (username, passHash, passSalt, question, ansHash, ansSalt))
        connection.commit()
        messagebox.showinfo('Success', 'Account Created Successfully. You Can Now Log In')
        registerWindow.destroy()
    except Exception as e:
        messagebox.showerror('Error', f'Error! {e}')
    finally:
        cursor.close()
        connection.close()


def resetPassword(resetWindow, usernameEntry, questionLabelVar, answerEntry, newPasswordEntry, confirmEntry):
    username = usernameEntry.get().strip()
    answer = answerEntry.get().strip()
    newPassword = newPasswordEntry.get()
    confirm = confirmEntry.get()

    if username == '' or answer == '' or newPassword == '' or confirm == '':
        messagebox.showerror('Error', 'All Fields Required')
        return
    if newPassword != confirm:
        messagebox.showerror('Error', 'Passwords Do Not Match')
        return

    cursor, connection = connectDataBase()
    if not cursor or not connection:
        return
    try:
        cursor.execute('USE inventory')
        cursor.execute('SELECT securityAnswer, securityAnswerSalt FROM users WHERE username = %s', (username,))
        record = cursor.fetchone()
        if not record:
            messagebox.showerror('Error', 'Username Not Found')
            return
        storedAnswerHash, storedAnswerSalt = record[0], record[1]
        if not verifyValue(answer.lower(), storedAnswerSalt, storedAnswerHash):
            messagebox.showerror('Error', 'Incorrect Answer to Security Question')
            return
        newSalt, newHash = hashValue(newPassword)
        cursor.execute('UPDATE users SET password = %s, salt = %s WHERE username = %s', (newHash, newSalt, username))
        connection.commit()
        messagebox.showinfo('Success', 'Password Reset Successfully')
        resetWindow.destroy()
    except Exception as e:
        messagebox.showerror('Error', f'Error! {e}')
    finally:
        cursor.close()
        connection.close()


def loadSecurityQuestion(usernameEntry, questionLabelVar):
    username = usernameEntry.get().strip()
    if username == '':
        messagebox.showerror('Error', 'Enter Username First')
        return
    cursor, connection = connectDataBase()
    if not cursor or not connection:
        return
    try:
        cursor.execute('USE inventory')
        cursor.execute('SELECT securityQuestion FROM users WHERE username = %s', (username,))
        record = cursor.fetchone()
        if not record:
            messagebox.showerror('Error', 'Username Not Found')
            questionLabelVar.set('Security Question: ---')
            return
        questionLabelVar.set(f'Security Question: {record[0]}')
    except Exception as e:
        messagebox.showerror('Error', f'Error! {e}')
    finally:
        cursor.close()
        connection.close()


# ---------------------------------------------------------------------------
# Eye toggle
# ---------------------------------------------------------------------------
def togglePasswordVisibility(passwordEntry, eyeButton, openEyeImage, closeEyeImage, state):
    if state['visible']:
        passwordEntry.config(show='*')
        eyeButton.config(image=closeEyeImage)
        state['visible'] = False
    else:
        passwordEntry.config(show='')
        eyeButton.config(image=openEyeImage)
        state['visible'] = True


# ---------------------------------------------------------------------------
# Forgot Password window
# ---------------------------------------------------------------------------
def open_forgot_password(parentWindow, forgotImage):
    resetWindow = Toplevel(parentWindow)
    resetWindow.title('Forgot Password')
    resetWindow.geometry('420x420')
    resetWindow.config(bg='white')
    resetWindow.resizable(False, False)
    resetWindow.grab_set()

    iconLabel = Label(resetWindow, image=forgotImage, bg='white')
    iconLabel.image = forgotImage
    iconLabel.pack(pady=(20, 10))

    headingLabel = Label(resetWindow, text='Reset Password', font=('times new roman', 16, 'bold'), bg='white', fg='#0f4d7d')
    headingLabel.pack(pady=(0, 10))

    formFrame = Frame(resetWindow, bg='white')
    formFrame.pack(fill=X, padx=30)

    usernameLabel = Label(formFrame, text='Username', font=('times new roman', 12), bg='white', anchor='w')
    usernameLabel.pack(fill=X)
    usernameEntry = Entry(formFrame, font=('times new roman', 12), bg='lightyellow', fg='black', bd=1, relief=GROOVE)
    usernameEntry.pack(fill=X, pady=(0, 10))

    questionLabelVar = StringVar(value='Security Question: ---')
    questionLabel = Label(formFrame, textvariable=questionLabelVar, font=('times new roman', 10, 'italic'), bg='white', fg='#555555', anchor='w', wraplength=350, justify=LEFT)
    questionLabel.pack(fill=X)

    loadQuestionButton = Button(formFrame, text='Load Security Question', font=('times new roman', 10, 'bold'), bg='#0f4d7d', fg='white', cursor='hand2', command=lambda: loadSecurityQuestion(usernameEntry, questionLabelVar))
    loadQuestionButton.pack(pady=(5, 10))

    answerLabel = Label(formFrame, text='Answer', font=('times new roman', 12), bg='white', anchor='w')
    answerLabel.pack(fill=X)
    answerEntry = Entry(formFrame, font=('times new roman', 12), bg='lightyellow', fg='black', bd=1, relief=GROOVE)
    answerEntry.pack(fill=X, pady=(0, 10))

    newPasswordLabel = Label(formFrame, text='New Password', font=('times new roman', 12), bg='white', anchor='w')
    newPasswordLabel.pack(fill=X)
    newPasswordEntry = Entry(formFrame, font=('times new roman', 12), bg='lightyellow', fg='black', bd=1, relief=GROOVE, show='*')
    newPasswordEntry.pack(fill=X, pady=(0, 10))

    confirmLabel = Label(formFrame, text='Confirm Password', font=('times new roman', 12), bg='white', anchor='w')
    confirmLabel.pack(fill=X)
    confirmEntry = Entry(formFrame, font=('times new roman', 12), bg='lightyellow', fg='black', bd=1, relief=GROOVE, show='*')
    confirmEntry.pack(fill=X, pady=(0, 15))

    resetButton = Button(resetWindow, text='Reset Password', font=('times new roman', 12, 'bold'), bg='#0f4d7d', fg='white', cursor='hand2', width=18,
                          command=lambda: resetPassword(resetWindow, usernameEntry, questionLabelVar, answerEntry, newPasswordEntry, confirmEntry))
    resetButton.pack(pady=5)


# ---------------------------------------------------------------------------
# Register window
# ---------------------------------------------------------------------------
def open_register(parentWindow):
    registerWindow = Toplevel(parentWindow)
    registerWindow.title('Create Account')
    registerWindow.geometry('420x460')
    registerWindow.config(bg='white')
    registerWindow.resizable(False, False)
    registerWindow.grab_set()

    headingLabel = Label(registerWindow, text='Create Account', font=('times new roman', 16, 'bold'), bg='white', fg='#0f4d7d')
    headingLabel.pack(pady=(20, 10))

    formFrame = Frame(registerWindow, bg='white')
    formFrame.pack(fill=X, padx=30)

    usernameLabel = Label(formFrame, text='Username', font=('times new roman', 12), bg='white', anchor='w')
    usernameLabel.pack(fill=X)
    usernameEntry = Entry(formFrame, font=('times new roman', 12), bg='lightyellow', fg='black', bd=1, relief=GROOVE)
    usernameEntry.pack(fill=X, pady=(0, 10))

    passwordLabel = Label(formFrame, text='Password', font=('times new roman', 12), bg='white', anchor='w')
    passwordLabel.pack(fill=X)
    passwordEntry = Entry(formFrame, font=('times new roman', 12), bg='lightyellow', fg='black', bd=1, relief=GROOVE, show='*')
    passwordEntry.pack(fill=X, pady=(0, 10))

    confirmLabel = Label(formFrame, text='Confirm Password', font=('times new roman', 12), bg='white', anchor='w')
    confirmLabel.pack(fill=X)
    confirmEntry = Entry(formFrame, font=('times new roman', 12), bg='lightyellow', fg='black', bd=1, relief=GROOVE, show='*')
    confirmEntry.pack(fill=X, pady=(0, 10))

    questionLabel = Label(formFrame, text='Security Question', font=('times new roman', 12), bg='white', anchor='w')
    questionLabel.pack(fill=X)
    questionComboBox = ttk.Combobox(formFrame, values=(
        "What is your mother's maiden name?",
        'What was the name of your first pet?',
        'What city were you born in?',
        'What is your favorite book?'
    ), font=('times new roman', 11), state='readonly')
    questionComboBox.set('Select Security Question')
    questionComboBox.pack(fill=X, pady=(0, 10))

    answerLabel = Label(formFrame, text='Answer', font=('times new roman', 12), bg='white', anchor='w')
    answerLabel.pack(fill=X)
    answerEntry = Entry(formFrame, font=('times new roman', 12), bg='lightyellow', fg='black', bd=1, relief=GROOVE)
    answerEntry.pack(fill=X, pady=(0, 15))

    registerButton = Button(registerWindow, text='Create Account', font=('times new roman', 12, 'bold'), bg='#0f4d7d', fg='white', cursor='hand2', width=18,
                             command=lambda: registerUser(registerWindow, usernameEntry, passwordEntry, confirmEntry, questionComboBox, answerEntry))
    registerButton.pack(pady=5)


# ---------------------------------------------------------------------------
# Rotating banner on the left panel
# ---------------------------------------------------------------------------
def cycleBannerImages(window, bannerLabel, images, state):
    if not bannerLabel.winfo_exists():
        return
    state['index'] = (state['index'] + 1) % len(images)
    bannerLabel.config(image=images[state['index']])
    window.after(2500, cycleBannerImages, window, bannerLabel, images, state)


# ---------------------------------------------------------------------------
# Main login window (entry point of the application)
# ---------------------------------------------------------------------------
def login_window():
    global loginIcon, openEyeImage, closeEyeImage, forgotImage, bannerImages

    createUsersTable()

    window = Tk()
    window.title('Inventory Management System - Login')
    window.geometry('1266x668+0+0')
    window.minsize(900, 550)
    window.config(bg='white')

    # ---- Left banner panel (relative placement so it scales with the window) ----
    bannerFrame = Frame(window, bg='#0f4d7d')
    bannerFrame.place(relx=0, rely=0, relwidth=0.4, relheight=1)

    bannerImages = [PhotoImage(file=f'login_logo{i}.png') for i in range(1, 8)]
    bannerLabel = Label(bannerFrame, image=bannerImages[0], bg='#0f4d7d')
    bannerLabel.place(relx=0.5, rely=0.5, anchor=CENTER)
    bannerState = {'index': 0}
    window.after(2500, cycleBannerImages, window, bannerLabel, bannerImages, bannerState)

    # ---- Right form panel ----
    formFrame = Frame(window, bg='white')
    formFrame.place(relx=0.4, rely=0, relwidth=0.6, relheight=1)

    loginIcon = PhotoImage(file='login.png')
    iconLabel = Label(formFrame, image=loginIcon, bg='white')
    iconLabel.place(relx=0.5, rely=0.12, anchor=CENTER)

    headingLabel = Label(formFrame, text='Inventory Management System', font=('times new roman', 20, 'bold'), bg='white', fg='#0f4d7d')
    headingLabel.place(relx=0.5, rely=0.28, anchor=CENTER)

    subHeadingLabel = Label(formFrame, text='Login to Continue', font=('times new roman', 14), bg='white', fg='#555555')
    subHeadingLabel.place(relx=0.5, rely=0.34, anchor=CENTER)

    innerFormFrame = Frame(formFrame, bg='white')
    innerFormFrame.place(relx=0.5, rely=0.52, anchor=CENTER)

    usernameLabel = Label(innerFormFrame, text='Username', font=('times new roman', 13, 'bold'), bg='white', anchor='w')
    usernameLabel.grid(row=0, column=0, columnspan=2, sticky='w', pady=(0, 4))
    usernameEntry = Entry(innerFormFrame, font=('times new roman', 13), bg='lightyellow', fg='black', bd=1, relief=GROOVE, width=28)
    usernameEntry.grid(row=1, column=0, columnspan=2, pady=(0, 15), ipady=4)

    passwordLabel = Label(innerFormFrame, text='Password', font=('times new roman', 13, 'bold'), bg='white', anchor='w')
    passwordLabel.grid(row=2, column=0, columnspan=2, sticky='w', pady=(0, 4))
    passwordEntry = Entry(innerFormFrame, font=('times new roman', 13), bg='lightyellow', fg='black', bd=1, relief=GROOVE, width=24, show='*')
    passwordEntry.grid(row=3, column=0, pady=(0, 5), ipady=4, sticky='w')

    openEyeImage = PhotoImage(file='open_eye.png')
    closeEyeImage = PhotoImage(file='close_eye.png')
    eyeState = {'visible': False}
    eyeButton = Button(innerFormFrame, image=closeEyeImage, bd=0, bg='lightyellow', cursor='hand2',
                        command=lambda: togglePasswordVisibility(passwordEntry, eyeButton, openEyeImage, closeEyeImage, eyeState))
    eyeButton.grid(row=3, column=1, pady=(0, 5), padx=(5, 0), sticky='w')

    forgotImage = PhotoImage(file='forgot-password.png').subsample(4, 4)
    forgotLabel = Label(innerFormFrame, text='Forgot Password?', font=('times new roman', 10, 'underline'), bg='white', fg='#0f4d7d', cursor='hand2')
    forgotLabel.grid(row=4, column=0, columnspan=2, sticky='w', pady=(0, 15))
    forgotLabel.bind('<Button-1>', lambda event: open_forgot_password(window, forgotImage))

    loginButton = Button(innerFormFrame, text='Login', font=('times new roman', 13, 'bold'), bg='#0f4d7d', fg='white', cursor='hand2', width=24,
                          command=lambda: attemptLogin(window, usernameEntry, passwordEntry))
    loginButton.grid(row=5, column=0, columnspan=2, pady=(0, 15), ipady=4)

    registerLabel = Label(innerFormFrame, text="Don't have an account? Create one", font=('times new roman', 10, 'underline'), bg='white', fg='#0f4d7d', cursor='hand2')
    registerLabel.grid(row=6, column=0, columnspan=2)
    registerLabel.bind('<Button-1>', lambda event: open_register(window))

    window.bind('<Return>', lambda event: attemptLogin(window, usernameEntry, passwordEntry))

    window.mainloop()


if __name__ == '__main__':
    login_window()
