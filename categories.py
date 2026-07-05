from tkinter import *
from tkinter import ttk
from employees import connectDataBase
from tkinter import messagebox
 

def addCategory(id, name, description, treeview):
    if id == '' or name == '' or description == '':
        messagebox.showerror('Error', 'All fields are required')
    else:
        cursor, connection = connectDataBase()
        if not cursor or not connection:
            messagebox.showerror('Error', 'Database connection error')
            return
        try:
            cursor.execute('USE inventory')
            cursor.execute('CREATE TABLE IF NOT EXISTS categories (id INT PRIMARY KEY, name VARCHAR(100), description TEXT)')
            cursor.execute('SELECT * FROM categories WHERE id=%s', (id,))
            if cursor.fetchone():
                messagebox.showerror('Error', 'Category already exists')
                return
            cursor.execute('INSERT INTO categories VALUES (%s, %s, %s)', (id, name, description))
            connection.commit()
            messagebox.showinfo('Success', 'Category added successfully')
            treeviewData(treeview)
        except Exception as e:
            messagebox.showerror('Error', str(e))
        finally:
            cursor.close()
            connection.close()

def updateCategory(id, name, description, treeview):
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
        cursor.execute('SELECT * FROM categories WHERE id = %s', (id,))
        currentData = cursor.fetchone()
        
        if not currentData:  # Prevent IndexError
            messagebox.showerror('Error', 'Category not found')
            return
        
        currentData = currentData[1:]  # Skip ID
        newData = (name, description)

        if currentData == newData:
            messagebox.showinfo('Info', 'No Changes Detected')
            return

        cursor.execute('UPDATE categories SET name = %s, description = %s WHERE id = %s', (name, description, id))
        connection.commit()
        messagebox.showinfo('Info', 'Data Updated Successfully')
        treeviewData(treeview)
    except Exception as e:
        messagebox.showerror('Error', str(e))
    finally:
        cursor.close()
        connection.close()

def treeviewData(treeview):
    cursor, connection = connectDataBase()
    if not cursor or not connection:
        messagebox.showerror('Error', 'Database connection error')
        return
    try:
        cursor.execute('USE inventory')
        cursor.execute('SELECT * FROM categories')
        data = cursor.fetchall()
        treeview.delete(*treeview.get_children())
        for i in data:
            treeview.insert('', 'end', values=i)
    except Exception as e:
        messagebox.showerror('Error', str(e))
    finally:
        cursor.close()
        connection.close()

def clear(idEntry, CategoryNameEntry, descriptionTextBox, treeview):
    idEntry.delete(0, END)
    CategoryNameEntry.delete(0, END)
    descriptionTextBox.delete(1.0, END)
    treeview.selection_remove(treeview.selection())

def deleteCategory(id, treeview):
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
        cursor.execute('DELETE from categories WHERE id = %s', (id,))
        connection.commit()
        treeviewData(treeview)
        messagebox.showinfo('Info', ' Record Deleted Successfully')
    except Exception as e:
        messagebox.showerror('Error', str(e))
    finally:
        cursor.close()
        connection.close()

def selectData(event, idEntry, categoryNameEntry, descriptionTextBox, treeview):
    index = treeview.selection()
    content = treeview.item(index)
    actualContent = content['values']
    
    idEntry.delete(0, END)
    categoryNameEntry.delete(0, END)
    descriptionTextBox.delete(1.0, END)

    idEntry.insert(0, actualContent[0])
    categoryNameEntry.insert(0, actualContent[1])
    descriptionTextBox.insert(1.0, actualContent[2])

def category_form(window):
    global backImage, logo
    categoryFrame = Frame(window, bg='white', width=1070, height=567)
    categoryFrame.place(x=200, y=100)
    headingLabel = Label(categoryFrame, text='Manage Categories', font=('times new roman', 16, 'bold'), bg='#0f4d7d', fg='white', bd=0)
    headingLabel.place(x=0, y=0, relwidth=1)
    backImage = PhotoImage(file='back.png')
    backButton = Button(categoryFrame, image=backImage, font=('times new roman', 12, 'bold'), bg='white', bd=0, cursor='hand2', command=lambda: categoryFrame.place_forget())
    backButton.place(x=20, y=30)
    logo = PhotoImage(file='product_category.png')
    label = Label(categoryFrame, image = logo, bg = 'white')
    label.place(x=30, y=100)

    detailsFrame = Frame(categoryFrame, bg = 'white')
    detailsFrame.place(x=500, y=60)

    idLabel = Label(detailsFrame, text='Id', font=('times new roman', 14, 'bold'), bg='white')
    idLabel.grid(row=0, column=0, padx=20, pady=10, sticky='w')
    idEntry = Entry(detailsFrame, font=('times new roman', 14), bd=2, bg='light yellow', relief=GROOVE)
    idEntry.grid(row=0, column=1, padx=20, pady=10, sticky='w')

    categoryNameLabel = Label(detailsFrame, text='Category Name', font=('times new roman', 14, 'bold'), bg='white')
    categoryNameLabel.grid(row=1, column=0, padx=20, pady=10, sticky='w')
    categoryNameEntry = Entry(detailsFrame, font=('times new roman', 14), bd=2, bg='light yellow', relief=GROOVE)
    categoryNameEntry.grid(row=1, column=1, padx=20, pady=10, sticky='w')

    descriptionLabel = Label(detailsFrame, text='Description', font=('times new roman', 14, 'bold'), bg='white')
    descriptionLabel.grid(row=3, column=0, padx=20, pady=10, sticky='nw')
    descriptionTextBox = Text(detailsFrame, font=('times new roman', 14), bd=2, bg='light yellow', relief=GROOVE, width=20, height=4)
    descriptionTextBox.grid(row=3, column=1, padx=20, pady=10, sticky='w')

    buttonFrame = Frame(categoryFrame, bg = 'white')
    buttonFrame.place(x=690, y=270)

    addButton = Button(buttonFrame, text='Add', font=('times new roman', 12, 'bold'), bg='#0f4d7d', fg='white', bd=2, relief=GROOVE, cursor='hand2', command= lambda: addCategory(idEntry.get(), categoryNameEntry.get(), descriptionTextBox.get(1.0, END).strip(), treeview))
    addButton.grid(row=0, column=0, padx=10, pady=10)
    updateButton = Button(buttonFrame, text='Update', font=('times new roman', 12, 'bold'), bg='#0f4d7d', fg='white', bd=2, relief=GROOVE, cursor='hand2', command= lambda: updateCategory(idEntry.get(), categoryNameEntry.get(), descriptionTextBox.get(1.0, END).strip(), treeview))
    updateButton.grid(row=0, column=1, padx=10)
    deleteButton = Button(buttonFrame, text='Delete', font=('times new roman', 12, 'bold'), bg='#0f4d7d', fg='white', bd=2, relief=GROOVE, cursor='hand2', command= lambda: deleteCategory(idEntry.get(), treeview))
    deleteButton.grid(row=0, column=2, padx=10)
    clearButton = Button(buttonFrame, text='Clear', font=('times new roman', 12, 'bold'), bg='#0f4d7d', fg='white', bd=2, relief=GROOVE, cursor='hand2', command= lambda: clear(idEntry, categoryNameEntry, descriptionTextBox, treeview))
    clearButton.grid(row=0, column=3, padx=10)

    treeviewFrame = Frame(categoryFrame, bg = 'white')
    treeviewFrame.place(x=530, y=330, height= 200, width= 500)
    scrollY = Scrollbar(treeviewFrame, orient=VERTICAL)
    scrollX = Scrollbar(treeviewFrame, orient=HORIZONTAL)
    treeview = ttk.Treeview(treeviewFrame, columns=('id', 'name', 'description'), show='headings', yscrollcommand=scrollY.set, xscrollcommand=scrollX.set)
    treeview.pack(fill=BOTH, expand=1)
    scrollY.pack(side=RIGHT, fill=Y)
    scrollX.pack(side=BOTTOM, fill=X)
    scrollY.config(command=treeview.yview)
    scrollX.config(command=treeview.xview)
    treeview.heading('id', text='ID.')
    treeview.heading('name', text='Category Name')
    treeview.heading('description', text='Description')
    treeview['show'] = 'headings'
    treeview.column('id', width=80)
    treeview.column('name', width=160)
    treeview.column('description', width=200)
    treeviewData(treeview)

    treeview.bind('<ButtonRelease-1>', lambda event: selectData(event, idEntry, categoryNameEntry, descriptionTextBox, treeview))