from tkinter import *
from tkinter import ttk
from tkcalendar import DateEntry
from tkinter import messagebox
import pymysql

def connectDataBase():
    try:
        connection = pymysql.connect(
            host='localhost',
            user='root',
            password='',
            database='inventory'   
        )
        cursor = connection.cursor()
    except pymysql.MySQLError as e:
        messagebox.showerror('Error', f'Database Connection Error! {e}')
        return None, None
     
    return cursor, connection

def createDatabase():
    cursor, connection = connectDataBase()
    cursor.execute('CREATE DATABASE IF NOT EXISTS inventory')
    cursor.execute('USE inventory')
    cursor.execute('''CREATE TABLE IF NOT EXISTS inventory.employees (
        empid INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(100),
        gender VARCHAR(10),
        dob DATE,
        email VARCHAR(100),
        contact VARCHAR(15),
        address TEXT,
        education VARCHAR(50),
        doj DATE,
        jobType VARCHAR(50),
        workShift VARCHAR(50),
        salary FLOAT,
        userType VARCHAR(50),
        password VARCHAR(50)
    )''')

    
def treeviewData():
    cursor, connection = connectDataBase()
    if not cursor or not connection:
        return
    cursor.execute('USE inventory')
    try:
        cursor.execute('SELECT * FROM employees')
        employeeRecords = cursor.fetchall()
        employeeTreeview.delete(*employeeTreeview.get_children())
        for record in employeeRecords:
            employeeTreeview.insert('', END, values=record)
    except Exception as e:
        messagebox.showerror('Error', f'Error! {e}')
    finally:
        connection.close()
        cursor.close()
    

def clearFields(empIdEntry, nameEntry, genderComboBox, dobEntry, emailEntry, ContactEntry, addressText, educationComboBox, dojEntry, jobTypeComboBox, workShiftComboBox, salaryEntry, userTypeComboBox, passwordEntry, check):
    empIdEntry.delete(0, END)
    nameEntry.delete(0, END)
    genderComboBox.set('Select Gender')
    from datetime import date
    dobEntry.set_date(date.today())
    emailEntry.delete(0, END)
    ContactEntry.delete(0, END)
    addressText.delete(1.0, END)
    educationComboBox.set('Select Education')
    dojEntry.set_date(date.today())
    jobTypeComboBox.set('Select Job Type')
    workShiftComboBox.set('Select Work Shift')
    salaryEntry.delete(0, END)
    userTypeComboBox.set('Select User Type')
    passwordEntry.delete(0, END)
    if check:
        employeeTreeview.selection_remove(employeeTreeview.selection())

def updateEmployee(empId, name, gender, dob, email, contact, address, education, doj, jobType, workShift, salary, user, password):
    selected = employeeTreeview.selection()
    if not selected:
        messagebox.showerror('Error', 'No Row is is Selected')
    else:
        cursor, connection = connectDataBase()
        if not cursor or not connection:
            return
        try:
            cursor.execute('USE inventory')
            cursor.execute('SELECT * FROM employees WHERE empid = %s', (empId))
            currentData=cursor.fetchone()
            currentData = currentData[1:]
            address=address.strip()
            newData=(name, gender, dob, email, contact, address, education, doj, jobType, workShift, salary, user, password)
            if currentData == newData:
                messagebox.showinfo('Information', 'No Changes Detected')
                return
            cursor.execute('UPDATE employees SET name=%s, gender=%s, dob=%s, email=%s, contact=%s, address=%s, education=%s, doj=%s, jobType=%s, workShift=%s, salary=%s, userType=%s, password=%s WHERE empid=%s',(name, gender, dob, email, contact, address, education, doj, jobType, workShift, salary, user, password, empId))
            connection.commit()
            treeviewData()
            messagebox.showinfo('Success', 'Date is updated Successfully')
        except Exception as e:
            messagebox.showerror('Error', f'Error! {e}')
        finally:
            connection.close()
            cursor.close()

def selectData(event, empIdEntry, nameEntry, genderComboBox, dobEntry, emailEntry, ContactEntry, addressText, educationComboBox, dojEntry, jobTypeComboBox, workShiftComboBox, salaryEntry, userTypeComboBox, passwordEntry):
    index=employeeTreeview.selection()
    content=employeeTreeview.item(index)
    values=content['values']
    clearFields(empIdEntry, nameEntry, genderComboBox, dobEntry, emailEntry, ContactEntry, addressText, educationComboBox, dojEntry, jobTypeComboBox, workShiftComboBox, salaryEntry, userTypeComboBox, passwordEntry, False)
    empIdEntry.insert(0, values[0])
    nameEntry.insert(0, values[1])
    genderComboBox.set(values[2])
    dobEntry.set_date(values[3])
    emailEntry.insert(0, values[4])
    ContactEntry.insert(0, values[5])
    addressText.insert(1.0, values[6])
    educationComboBox.set(values[7])
    dojEntry.set_date(values[8])
    jobTypeComboBox.set(values[9])
    workShiftComboBox.set(values[10])
    salaryEntry.insert(0, values[11])
    userTypeComboBox.set(values[12])
    passwordEntry.insert(0, values[13])

def deleteEmployee(empId):
    selected = employeeTreeview.selection()
    if not selected:
        messagebox.showerror('Error', 'No Row is Selected')
    else:
        result=messagebox.askyesno('Confirm', 'Do you Really Want to Delete the Record')
        if result:
            cursor, connection = connectDataBase()
            if not cursor or not connection:
                return
            try:
                cursor.execute('USE inventory')
                cursor.execute('DELETE FROM employees WHERE empid=%s',(empId))
                connection.commit()
                treeviewData()
                messagebox.showinfo('Success', 'Record Deleted Successfully')
            except Exception as e:
                messagebox.showerror('Error', f'Error! {e}')
            finally:
                connection.close()
                cursor.close()

def addEmployee(empIdEntry, nameEntry, genderComboBox, dobEntry, emailEntry, ContactEntry, addressText, educationComboBox, dojEntry, jobTypeComboBox, workShiftComboBox, salaryEntry, userTypeComboBox, passwordEntry):
    empId = empIdEntry.get()
    name = nameEntry.get()
    gender = genderComboBox.get()
    dob = dobEntry.get()
    email = emailEntry.get()
    contact = ContactEntry.get()
    address = addressText.get(1.0, END).strip()
    education = educationComboBox.get()
    doj = dojEntry.get()
    jobType = jobTypeComboBox.get()
    workShift = workShiftComboBox.get()
    salary = salaryEntry.get()
    user = userTypeComboBox.get()
    password = passwordEntry.get()

    if (empId == '' or name == '' or gender == 'Select Gender' or email == '' or contact == '' or address == '' or education == 'Select Education' or jobType == 'Select Job Type' or workShift == 'Select Work Shift' or salary == '' or user == 'Select User Type' or password == ''):
        messagebox.showerror('Error', 'All Fields Required')
    else:
        cursor, connection = connectDataBase()
        if not cursor or not connection:
            return
        cursor.execute('USE inventory')
        try:
            cursor.execute('SELECT empid FROM employees WHERE empid = %s', (empId))
            if cursor.rowcount > 0:
                messagebox.showerror('Error', 'Employee ID Already Exists')
                return
            cursor.execute('INSERT INTO employees (empid, name, gender, dob, email, contact, address, education, doj, jobType, workShift, salary, userType, password) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)', 
                           (empId, name, gender, dob, email, contact, address, education, doj, jobType, workShift, salary, user, password))
            connection.commit()
            messagebox.showinfo('Success', 'Employee Added Successfully')
            treeviewData()
            clearFields(empIdEntry, nameEntry, genderComboBox, dobEntry, emailEntry, ContactEntry, addressText, educationComboBox, dojEntry, jobTypeComboBox, workShiftComboBox, salaryEntry, userTypeComboBox, passwordEntry, True)
        except Exception as e:
            messagebox.showerror('Error', f'Error! {e}')
        finally:
            connection.close()
            cursor.close()

def searchEmployee(searchOption, value):
    if searchOption == 'Search By':
        messagebox.showerror('Error', 'No Option is Selected')
    elif value == '':
        messagebox.showerror('Error', 'Enter the Value to Search')
    else:
        cursor, connection = connectDataBase()
        if not cursor or not connection:
            return
        try:
            cursor.execute('USE inventory')
            query = f"SELECT * FROM employees WHERE {searchOption} LIKE %s"
            cursor.execute(query, ('%' + value + '%',))
            records = cursor.fetchall()
            employeeTreeview.delete(*employeeTreeview.get_children())
            for record in records:
                employeeTreeview.insert('', END, values=record)
        except Exception as e:
            messagebox.showerror('Error', f'Error! {e}')
        finally:
            connection.close()
            cursor.close()

def showAll(searchEntry, searchComboBox):
    treeviewData()
    searchEntry.delete(0,END)
    searchComboBox.set('Search By')

def employee_form(window):
    global backImage, employeeTreeview
    employeeFrame = Frame(window, bg='white', width=1070, height=567)
    employeeFrame.place(x=200, y=100)
    headingLabel = Label(employeeFrame, text='Manage Employee Details', font=('times new roman', 16, 'bold'), bg='#0f4d7d', fg='white', bd=0)
    headingLabel.place(x=0, y=0, relwidth=1)

    topFrame = Frame(employeeFrame, bg='white')
    topFrame.place(x=0, y=40, relwidth=1, height=235)
    
    backImage = PhotoImage(file='back.png')
    backButton = Button(topFrame, image = backImage, font=('times new roman', 12, 'bold'), bg = 'white', bd=0, cursor='hand2', command = lambda: employeeFrame.place_forget())
    backButton.place(x=20, y=0)
    searchFrame = Frame(topFrame, bg='white')
    searchFrame.pack()
    searchComboBox = ttk.Combobox(searchFrame, values =('Empid', 'Name', 'Email', 'Gender', 'Job Type', 'Work Shift', 'Education', 'Salary', 'Date of Joining')  ,font=('times new roman', 12), state='readonly')
    searchComboBox.set('Search By')
    searchComboBox.grid(row=0, column=0)
    searchEntry = Entry(searchFrame, font=('times new roman', 12), bg='lightyellow', fg='black', bd=1, relief=GROOVE)
    searchEntry.grid(row=0, column=1, padx=20)
    searchButton = Button(searchFrame, text='Search', font=('times new roman', 12, 'bold'), bg='#0f4d7d', fg='white', cursor='hand2', width=10, command= lambda: searchEmployee(searchComboBox.get(), searchEntry.get()))
    searchButton.grid(row=0, column=2, padx=20)
    showAllButton = Button(searchFrame, text='Show All', font=('times new roman', 12, 'bold'), bg='#0f4d7d', fg='white', cursor='hand2', width=10, command = lambda: showAll(searchEntry, searchComboBox))
    showAllButton.grid(row=0, column=3, padx=20)

    horizontalScrollbar = Scrollbar(topFrame, orient=HORIZONTAL)
    verticalScrollbar = Scrollbar(topFrame, orient=VERTICAL)

    employeeTreeview = ttk.Treeview(topFrame, columns=('empid', 'name', 'gender', 'dob', 'email', 'contact', 'address', 'education', 'doj', 'jobType', 'workShft', 'salary'), show='headings', yscrollcommand=verticalScrollbar.set, xscrollcommand=horizontalScrollbar.set)
    
    horizontalScrollbar.pack(side=BOTTOM, fill=X)
    verticalScrollbar.pack(side=RIGHT, fill=Y, pady=(10,0))
    verticalScrollbar.config(command=employeeTreeview.yview)
    horizontalScrollbar.config(command=employeeTreeview.xview)
    employeeTreeview.pack(pady=(10,0))

    employeeTreeview.heading('empid', text = 'EmpId')
    employeeTreeview.heading('name', text ='Name')
    employeeTreeview.heading('gender', text = 'Gender')
    employeeTreeview.heading('dob', text ='Date of Birth')
    employeeTreeview.heading('email', text ='Email')
    employeeTreeview.heading('contact', text ='Contact')
    employeeTreeview.heading('address', text ='Address')
    employeeTreeview.heading('education', text ='Education')
    employeeTreeview.heading('doj', text ='Date of Joining')
    employeeTreeview.heading('jobType', text ='Job Type')
    employeeTreeview.heading('workShft', text ='Work Shift')
    employeeTreeview.heading('salary', text ='Salary')
    

    employeeTreeview.column('empid', width=60)
    employeeTreeview.column('name', width=140)
    employeeTreeview.column('gender', width=80)
    employeeTreeview.column('dob', width=100)
    employeeTreeview.column('email', width=180)
    employeeTreeview.column('contact', width=100)
    employeeTreeview.column('address', width=200)
    employeeTreeview.column('education', width=120)
    employeeTreeview.column('doj', width=100)
    employeeTreeview.column('salary', width=100)
    employeeTreeview.column('jobType', width=120)
    employeeTreeview.column('workShft', width=100)
    
    treeviewData()
    

    detailFrame = Frame(employeeFrame, bg='white')
    detailFrame.place(x=20, y=280, relwidth=1, height=235)

    empIdLabel = Label(detailFrame, text='Emp Id', font=('times new roman', 12), bg='white')
    empIdLabel.grid(row=0, column=0, padx=20, pady=10, sticky = 'w')
    empIdEntry = Entry(detailFrame, font=('times new roman', 12), bg='lightyellow', fg='black', bd=1, relief=GROOVE)
    empIdEntry.grid(row=0, column=1, padx=20, pady=10)

    nameLabel = Label(detailFrame, text='Name', font=('times new roman', 12), bg='white')
    nameLabel.grid(row=0, column=2, padx=20, pady=10, sticky = 'w')
    nameEntry = Entry(detailFrame, font=('times new roman', 12), bg='lightyellow', fg='black', bd=1, relief=GROOVE)
    nameEntry.grid(row=0, column=3, padx=20, pady=10)

    emailLabel = Label(detailFrame, text='Email', font=('times new roman', 12), bg='white')
    emailLabel.grid(row=0, column=4, padx=20, pady=10, sticky = 'w')
    emailEntry = Entry(detailFrame, font=('times new roman', 12), bg='lightyellow', fg='black', bd=1, relief=GROOVE)
    emailEntry.grid(row=0, column=5, padx=20, pady=10)

    genderLabel = Label(detailFrame, text='Gender', font=('times new roman', 12), bg='white')
    genderLabel.grid(row=1, column=0, padx=20, pady=10, sticky = 'w')
    genderComboBox=ttk.Combobox(detailFrame, values=('Male', 'Female', 'Other'), font=('times new roman', 12), state='readonly', width=17)
    genderComboBox.set('Select Gender')
    genderComboBox.grid(row=1, column=1, padx=20, pady=10)

    dobLabel = Label(detailFrame, text='Date of Birth', font=('times new roman', 12), bg='white')
    dobLabel.grid(row=1, column=2, padx=20, pady=10, sticky = 'w')
    dobEntry = DateEntry(detailFrame, font=('times new roman', 12), bg='lightyellow', fg='black', bd=1, relief=GROOVE, width = 17, date_pattern = 'YYYY/MM/DD')
    dobEntry.grid(row=1, column=3, padx=20, pady=10)

    ContactLabel = Label(detailFrame, text='Contact', font=('times new roman', 12), bg='white')
    ContactLabel.grid(row=1, column=4, padx=20, pady=10, sticky = 'w')
    ContactEntry = Entry(detailFrame, font=('times new roman', 12), bg='lightyellow', fg='black', bd=1, relief=GROOVE)
    ContactEntry.grid(row=1, column=5, padx=20, pady=10)

    jobTypeLabel = Label(detailFrame, text='Job Type', font=('times new roman', 12), bg='white')
    jobTypeLabel.grid(row=2, column=0, padx=20, pady=10, sticky = 'w')
    jobTypeComboBox=ttk.Combobox(detailFrame, values=('Supplies Manager', 'Operation Manager', 'Warehouse Worker', 'Security Guard', 'Office Assistant', 'Inventory Staff', 'Sales Manager', 'Contact Support Representative', 'IT Worker'), font=('times new roman', 12), state='readonly', width=17)
    jobTypeComboBox.set('Select Job Type')
    jobTypeComboBox.grid(row=2, column=1, padx=20, pady=10)

    educationLabel = Label(detailFrame, text='Education', font=('times new roman', 12), bg='white')
    educationLabel.grid(row=2, column=4, padx=20, pady=10, sticky = 'w')
    educationComboBox=ttk.Combobox(detailFrame, values=('BBA', 'MBA', 'BS', 'MS', 'Bachlor in Inventory Managment', 'Bachelor/Master in Operations Management', 'B.Com', 'M.Com', 'BSc.', 'MSc.', 'Matric', 'Inter', 'Diploma', 'Diploma in IT', 'BSCS', 'BSSE', 'BSIT' ), font=('times new roman', 12), state='readonly', width=17)
    educationComboBox.set('Select Education')
    educationComboBox.grid(row=2, column=5, padx=20, pady=10)

    workShiftLabel = Label(detailFrame, text='Work Shift', font=('times new roman', 12), bg='white')
    workShiftLabel.grid(row=2, column=2, padx=20, pady=10, sticky = 'w')
    workShiftComboBox=ttk.Combobox(detailFrame, values=('Morning', 'Evening', 'Night'), font=('times new roman', 12), state='readonly', width=17)
    workShiftComboBox.set('Select Work Shift')
    workShiftComboBox.grid(row=2, column=3, padx=20, pady=10)

    addressLabel = Label(detailFrame, text='Address', font=('times new roman', 12), bg='white')
    addressLabel.grid(row=3, column=0, padx=20, pady=10, sticky = 'w')
    addressText = Text(detailFrame, font=('times new roman', 12), bg='lightyellow', fg='black', bd=1, relief=GROOVE, width=20, height=3)
    addressText.grid(row=3, column=1, padx=20, pady=10, rowspan=2)

    dojLabel = Label(detailFrame, text='Date of Joining', font=('times new roman', 12), bg='white')
    dojLabel.grid(row=3, column=2, padx=20, pady=10, sticky = 'w')
    dojEntry = DateEntry(detailFrame, font=('times new roman', 12), bg='lightyellow', fg='black', bd=1, relief=GROOVE, width = 17, date_pattern = 'YYYY/MM/DD')
    dojEntry.grid(row=3, column=3, padx=20, pady=10)

    userTypeLabel = Label(detailFrame, text='User Type', font=('times new roman', 12), bg='white')
    userTypeLabel.grid(row=4, column=2, padx=20, pady=10, sticky = 'w')
    userTypeComboBox=ttk.Combobox(detailFrame, values=('Admin', 'Employee'), font=('times new roman', 12), state='readonly', width=17)
    userTypeComboBox.set('Select User Type')
    userTypeComboBox.grid(row=4, column=3, padx=20, pady=10)

    salaryLabel = Label(detailFrame, text='Salary', font=('times new roman', 12), bg='white')
    salaryLabel.grid(row=3, column=4, padx=20, pady=10, sticky = 'w')
    salaryEntry = Entry(detailFrame, font=('times new roman', 12), bg='lightyellow', fg='black', bd=1, relief=GROOVE)
    salaryEntry.grid(row=3, column=5, padx=20, pady=10)

    passwordLabel = Label(detailFrame, text='Password', font=('times new roman', 12), bg='white')
    passwordLabel.grid(row=4, column=4, padx=20, pady=10, sticky = 'w')
    passwordEntry = Entry(detailFrame, font=('times new roman', 12), bg='lightyellow', fg='black', bd=1, relief=GROOVE)
    passwordEntry.grid(row=4, column=5, padx=20, pady=10)

    buttonFrame = Frame(employeeFrame, bg='white')
    buttonFrame.place(x=200, y=510, relwidth=1, height=50)
    addButton = Button(buttonFrame, text='Add', font=('times new roman', 12, 'bold'), bg='#0f4d7d', fg='white', cursor='hand2', width=10, command=lambda: addEmployee(empIdEntry, nameEntry, genderComboBox, dobEntry, emailEntry, ContactEntry, addressText, educationComboBox, dojEntry, jobTypeComboBox, workShiftComboBox, salaryEntry, userTypeComboBox, passwordEntry))
    addButton.grid(row=0, column=0, padx=20, pady=10)
    updateButton = Button(buttonFrame, text='Update', font=('times new roman', 12, 'bold'), bg='#0f4d7d', fg='white', cursor='hand2', width=10, command=lambda: updateEmployee(empIdEntry.get(), nameEntry.get(), genderComboBox.get(), dobEntry.get(), emailEntry.get(), ContactEntry.get(), addressText.get(1.0, END), educationComboBox.get(), dojEntry.get(), jobTypeComboBox.get(), workShiftComboBox.get(), salaryEntry.get(), userTypeComboBox.get(), passwordEntry.get()))
    updateButton.grid(row=0, column=1, padx=20, pady=10)
    deleteButton = Button(buttonFrame, text='Delete', font=('times new roman', 12, 'bold'), bg='#0f4d7d', fg='white', cursor='hand2', width=10, command = lambda: deleteEmployee(empIdEntry.get()))
    deleteButton.grid(row=0, column=2, padx=20, pady=10)
    clearButton = Button(buttonFrame, text='Clear', font=('times new roman', 12, 'bold'), bg='#0f4d7d', fg='white', cursor='hand2', width=10, command =lambda: clearFields( empIdEntry, nameEntry, genderComboBox, dobEntry, emailEntry, ContactEntry, addressText, educationComboBox, dojEntry, jobTypeComboBox, workShiftComboBox, salaryEntry, userTypeComboBox, passwordEntry, True))
    clearButton.grid(row=0, column=3, padx=20, pady=10)
    createDatabase()
    employeeTreeview.bind('<ButtonRelease-1>', lambda event: selectData(event, empIdEntry, nameEntry, genderComboBox, dobEntry, emailEntry, ContactEntry, addressText, educationComboBox, dojEntry, jobTypeComboBox, workShiftComboBox, salaryEntry, userTypeComboBox, passwordEntry))
 