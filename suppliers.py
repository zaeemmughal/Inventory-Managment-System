from tkinter import *
from tkinter import ttk
from employees import connectDataBase
from tkinter import messagebox

def searchSupplier(searchValue, treeview):
    if searchValue == '':
        messagebox.showerror('Error', 'Please Enter Invoice No.')
    else:
        cursor, connection = connectDataBase()
        if not cursor or not connection:
            messagebox.showerror('Error', 'Database connection error')
            return 
        try:
            cursor.execute('USE inventory')
            cursor.execute('SELECT * from suppliers WHERE invoice = %s', searchValue)
            record = cursor.fetchone()
            if not record:
                messagebox.showerror('Error', 'No Record Found')
                return
            treeview.delete(*treeview.get_children())
            treeview.insert('', END, values= record)
        except Exception as e:
            messagebox.showerror('Error', str(e))
        finally:
            cursor.close()
            connection.close()

def showAll(treeview, searchEntry):
    treeviewData(treeview)
    searchEntry.delete(0, END)

def clear(invoiceEntry, nameEntry, contactEntry, descriptionTextBox, treeview):
    invoiceEntry.delete(0, END)
    nameEntry.delete(0, END)
    contactEntry.delete(0, END)
    descriptionTextBox.delete(1.0, END)
    treeview.selection_remove(treeview.selection())

def deleteSupplier(invoice, treeview):
    index = treeview.selection()
    if not index:
        messagebox.showerror('Error', 'No Row is Selected')
        return
    cursor, connection = connectDataBase()
    if not cursor or not connection:
        messagebox.showerror('Error', 'Database connection error')
        return
    try:
        cursor.execute('USE inventory')
        cursor.execute('DELETE from suppliers WHERE invoice = %s', invoice)
        connection.commit()
        treeviewData(treeview)
        messagebox.showinfo('Info', ' Record Deleted Successfully')
    except Exception as e:
        messagebox.showerror('Error', str(e))
    finally:
        cursor.close()
        connection.close()

def updateSuppliers(invoice, name, contact, description, treeview):
    index = treeview.selection()
    if not index:
        messagebox.showerror('Error', 'No Row is Selected')
        return
    cursor, connection = connectDataBase()
    if not cursor or not connection:
        messagebox.showerror('Error', 'Database connection error')
        return
    try:
        cursor.execute('USE inventory')
        cursor.execute('SELECT * from suppliers WHERE invoice = %s', invoice)
        currentData = cursor.fetchone()
        currentData = currentData[1:]
        newData = (name, contact, description)
        if currentData == newData:
            messagebox.showinfo('Info', 'No Changes Detected')
            return

        cursor.execute('UPDATE suppliers SET name = %s, contact = %s, description = %s WHERE invoice = %s',  (name, contact, description, invoice))
        connection.commit()
        messagebox.showinfo('Info', 'Data is Updated Successfully')
        treeviewData(treeview)
    except Exception as e:
        messagebox.showerror('Error', str(e))
    finally:
        cursor.close()
        connection.close()

def selectData(event, invoiceEntry, nameEntry, contactEntry, descriptionTextBox, treeview):
    index = treeview.selection()
    content = treeview.item(index)
    actualContent = content['values']
    if not actualContent:
        return  
    invoiceEntry.delete(0, END)
    nameEntry.delete(0, END)
    contactEntry.delete(0, END)
    descriptionTextBox.delete(1.0, END)

    invoiceEntry.insert(0, actualContent[0])
    nameEntry.insert(0, actualContent[1])
    contactEntry.insert(0, actualContent[2])
    descriptionTextBox.insert(1.0, actualContent[3])



def treeviewData(treeview):
    cursor, connection = connectDataBase()
    if not cursor or not connection:
        messagebox.showerror('Error', 'Database connection error')
        return
    try:
        cursor.execute('USE inventory')
        cursor.execute('SELECT * FROM suppliers')
        data = cursor.fetchall()
        treeview.delete(*treeview.get_children())
        for i in data:
            treeview.insert('', 'end', values=i)
    except Exception as e:
        messagebox.showerror('Error', str(e))
    finally:
        cursor.close()
        connection.close()

def addSuppliers(invoice, name, contact, description, treeview):
    if invoice == '' or name == '' or contact == '' or description == '':
        messagebox.showerror('Error', 'All fields are required')
    else:
        cursor, connection = connectDataBase()
        if not cursor or not connection:
            messagebox.showerror('Error', 'Database connection error')
            return
        try:
            cursor.execute('USE inventory')
            cursor.execute('CREATE TABLE IF NOT EXISTS suppliers (invoice INT PRIMARY KEY, name VARCHAR(100), contact VARCHAR(50), description TEXT)')
            cursor.execute('SELECT * FROM suppliers WHERE invoice=%s', (invoice,))
            if cursor.fetchone():
                messagebox.showerror('Error', 'Supplier already exists')
                return
            cursor.execute('INSERT INTO suppliers VALUES (%s, %s, %s, %s)', (invoice, name, contact, description))
            connection.commit()
            messagebox.showinfo('Success', 'Supplier added successfully')
            treeviewData(treeview)
        except Exception as e:
            messagebox.showerror('Error', str(e))
        finally:
            cursor.close()
            connection.close()


def supplier_form(window):
    global backImage
    supplierFrame = Frame(window, bg='white', width=1070, height=567)
    supplierFrame.place(x=200, y=100)
    headingLabel = Label(supplierFrame, text='Manage Supplier Details', font=('times new roman', 16, 'bold'), bg='#0f4d7d', fg='white', bd=0)
    headingLabel.place(x=0, y=0, relwidth=1)
    backImage = PhotoImage(file='back.png')
    backButton = Button(supplierFrame, image=backImage, font=('times new roman', 12, 'bold'), bg='white', bd=0, cursor='hand2', command=lambda: supplierFrame.place_forget())
    backButton.place(x=20, y=30)

    leftFrame = Frame(supplierFrame, bg='white')
    leftFrame.place(x=10, y=100)

    invoiceLabel = Label(leftFrame, text='Invoice No.', font=('times new roman', 16, 'bold'), bg='white')
    invoiceLabel.grid(row=0, column=0, padx=20, pady=15, sticky='w')
    invoiceEntry = Entry(leftFrame, font=('times new roman', 16), bd=2, bg='light yellow', relief=GROOVE)
    invoiceEntry.grid(row=0, column=1, padx=20, pady=15, sticky='w')

    nameLabel = Label(leftFrame, text='Supplier Name', font=('times new roman', 16, 'bold'), bg='white')
    nameLabel.grid(row=1, column=0, padx=20, pady=15, sticky='w')
    nameEntry = Entry(leftFrame, font=('times new roman', 16), bd=2, bg='light yellow', relief=GROOVE)
    nameEntry.grid(row=1, column=1, padx=20, pady=15, sticky='w')

    contactLabel = Label(leftFrame, text='Contact No.', font=('times new roman', 16, 'bold'), bg='white')
    contactLabel.grid(row=2, column=0, padx=20, pady=15, sticky='w')
    contactEntry = Entry(leftFrame, font=('times new roman', 16), bd=2, bg='light yellow', relief=GROOVE)
    contactEntry.grid(row=2, column=1, padx=20, pady=15, sticky='w')

    descriptionLabel = Label(leftFrame, text='Description', font=('times new roman', 16, 'bold'), bg='white')
    descriptionLabel.grid(row=3, column=0, padx=20, pady=15, sticky='nw')
    descriptionTextBox = Text(leftFrame, font=('times new roman', 16), bd=2, bg='light yellow', relief=GROOVE, width=20, height=4)
    descriptionTextBox.grid(row=3, column=1, padx=20, pady=15, sticky='w')

    buttonFrame = Frame(leftFrame, bg='white')
    buttonFrame.grid(row=4, column=0, columnspan=2, pady=20)
    addButton = Button(buttonFrame, text='Add', font=('times new roman', 12, 'bold'), bg='#0f4d7d', fg='white', bd=2, relief=GROOVE, cursor='hand2', command= lambda: addSuppliers(invoiceEntry.get(), nameEntry.get(), contactEntry.get(), descriptionTextBox.get(1.0, END).strip(), treeview))
    addButton.grid(row=0, column=0, padx=10, pady=10)
    updateButton = Button(buttonFrame, text='Update', font=('times new roman', 12, 'bold'), bg='#0f4d7d', fg='white', bd=2, relief=GROOVE, cursor='hand2', command= lambda: updateSuppliers(invoiceEntry.get(), nameEntry.get(), contactEntry.get(), descriptionTextBox.get(1.0, END).strip(), treeview))
    updateButton.grid(row=0, column=1, padx=10)
    deleteButton = Button(buttonFrame, text='Delete', font=('times new roman', 12, 'bold'), bg='#0f4d7d', fg='white', bd=2, relief=GROOVE, cursor='hand2', command= lambda: deleteSupplier(invoiceEntry.get(), treeview))
    deleteButton.grid(row=0, column=2, padx=10)
    clearButton = Button(buttonFrame, text='Clear', font=('times new roman', 12, 'bold'), bg='#0f4d7d', fg='white', bd=2, relief=GROOVE, cursor='hand2', command= lambda: clear(invoiceEntry, nameEntry, contactEntry, descriptionTextBox, treeview))
    clearButton.grid(row=0, column=3, padx=10)

    rightFrame = Frame(supplierFrame, bg='white')
    rightFrame.place(x=520, y=95, width=500, height=350)

    searchFrame = Frame(rightFrame, bg='white')
    searchFrame.pack(pady=(0, 10))
    searchLabel = Label(searchFrame, text='Invoice No.', font=('times new roman', 14, 'bold'), bg='white')
    searchLabel.grid(row=0, column=0, padx=10, pady=10, sticky='w')

    searchEntry = Entry(searchFrame, font=('times new roman', 12), bd=2, bg='light yellow', relief=GROOVE)
    searchEntry.grid(row=0, column=1, padx=10, pady=10, sticky='w')
    
    searchButton = Button(searchFrame, text='Search', font=('times new roman', 12, 'bold'), bg='#0f4d7d', fg='white', bd=2, relief=GROOVE, cursor='hand2', command= lambda: searchSupplier(searchEntry.get(), treeview))
    searchButton.grid(row=0, column=2, padx=10, pady=10)
    showButton = Button(searchFrame, text='Show all', font=('times new roman', 12, 'bold'), bg='#0f4d7d', fg='white', bd=2, relief=GROOVE, cursor='hand2', command= lambda: showAll(treeview, searchEntry))
    showButton.grid(row=0, column=3, padx=10, pady=10)

    scrollY = Scrollbar(rightFrame, orient=VERTICAL)
    scrollX = Scrollbar(rightFrame, orient=HORIZONTAL)
    treeview = ttk.Treeview(rightFrame, columns=('invoice', 'name', 'contact', 'description'), show='headings', yscrollcommand=scrollY.set, xscrollcommand=scrollX.set)
    treeview.pack(fill=BOTH, expand=1)
    scrollY.pack(side=RIGHT, fill=Y)
    scrollX.pack(side=BOTTOM, fill=X)
    scrollY.config(command=treeview.yview)
    scrollX.config(command=treeview.xview)

    treeview.heading('invoice', text='Invoice No.')
    treeview.heading('name', text='Supplier Name')
    treeview.heading('contact', text='Contact No.')
    treeview.heading('description', text='Description')
    treeview['show'] = 'headings'
    treeview.column('invoice', width=80)
    treeview.column('name', width=160)
    treeview.column('contact', width=160)
    treeview.column('description', width=200)
    treeviewData(treeview)

    treeview.bind('<ButtonRelease-1>', lambda event: selectData(event, invoiceEntry, nameEntry, contactEntry, descriptionTextBox, treeview))