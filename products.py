from tkinter import *
from tkinter import ttk
from employees import connectDataBase
from tkinter import messagebox


def createProductsTable():
    cursor, connection = connectDataBase()
    if not cursor or not connection:
        return
    try:
        cursor.execute('USE inventory')
        cursor.execute('''CREATE TABLE IF NOT EXISTS products (
            id INT PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            price FLOAT NOT NULL,
            quantity INT NOT NULL,
            category_id INT NOT NULL,
            supplier_id INT NOT NULL,
            status VARCHAR(20),
            payment_method VARCHAR(30),
            FOREIGN KEY (category_id) REFERENCES categories(id),
            FOREIGN KEY (supplier_id) REFERENCES suppliers(invoice)
        )''')
        connection.commit()
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
        cursor.execute('''
            SELECT p.id, p.name, p.price, p.quantity, c.name as category, s.name as supplier, p.status, p.payment_method
            FROM products p
            JOIN categories c ON p.category_id = c.id
            JOIN suppliers s ON p.supplier_id = s.invoice
        ''')
        rows = cursor.fetchall()
        treeview.delete(*treeview.get_children())
        for row in rows:
            treeview.insert('', 'end', values=row)
    except Exception as e:
        messagebox.showerror('Error', str(e))
    finally:
        cursor.close()
        connection.close()


def populateComboBoxes(categoryComboBox, supplierComboBox):
    cursor, connection = connectDataBase()
    if not cursor or not connection:
        return
    try:
        cursor.execute('USE inventory')
        cursor.execute('SELECT name FROM categories')
        categoryNames = [row[0] for row in cursor.fetchall()]
        cursor.execute('SELECT name FROM suppliers')
        supplierNames = [row[0] for row in cursor.fetchall()]
        categoryComboBox['values'] = categoryNames
        supplierComboBox['values'] = supplierNames
    except Exception as e:
        messagebox.showerror('Error', str(e))
    finally:
        cursor.close()
        connection.close()


def clearProduct(productIdEntry, productNameEntry, priceEntry, quantityEntry,
                 categoryComboBox, supplierComboBox, statusComboBox, paymentComboBox, treeview):
    productIdEntry.delete(0, END)
    productNameEntry.delete(0, END)
    priceEntry.delete(0, END)
    quantityEntry.delete(0, END)
    categoryComboBox.set('Select Category')
    supplierComboBox.set('Select Supplier')
    statusComboBox.set('Status')
    paymentComboBox.set('Select Payment Method')
    treeview.selection_remove(treeview.selection())


def validateProductInput(productId, name, price, quantity, category, supplier, status, payment):
    if (productId == '' or name == '' or price == '' or quantity == ''
            or category == 'Select Category' or supplier == 'Select Supplier'
            or status == 'Status' or payment == 'Select Payment Method'):
        messagebox.showerror('Error', 'All Fields Required')
        return False
    try:
        int(productId)
    except ValueError:
        messagebox.showerror('Error', 'Product ID Must Be a Number')
        return False
    try:
        pv = float(price)
        if pv < 0:
            raise ValueError
    except ValueError:
        messagebox.showerror('Error', 'Price Must Be a Non-Negative Number')
        return False
    try:
        qv = int(quantity)
        if qv < 0:
            raise ValueError
    except ValueError:
        messagebox.showerror('Error', 'Quantity Must Be a Non-Negative Whole Number')
        return False
    return True


def getCategoryId(cursor, categoryName):
    cursor.execute('SELECT id FROM categories WHERE name = %s', (categoryName,))
    record = cursor.fetchone()
    return record[0] if record else None


def getSupplierId(cursor, supplierName):
    cursor.execute('SELECT invoice FROM suppliers WHERE name = %s', (supplierName,))
    record = cursor.fetchone()
    return record[0] if record else None


def addProduct(productIdEntry, productNameEntry, priceEntry, quantityEntry,
               categoryComboBox, supplierComboBox, statusComboBox, paymentComboBox, treeview):
    productId = productIdEntry.get().strip()
    name = productNameEntry.get().strip()
    price = priceEntry.get().strip()
    quantity = quantityEntry.get().strip()
    category = categoryComboBox.get()
    supplier = supplierComboBox.get()
    status = statusComboBox.get()
    payment = paymentComboBox.get()

    if not validateProductInput(productId, name, price, quantity, category, supplier, status, payment):
        return

    cursor, connection = connectDataBase()
    if not cursor or not connection:
        return
    try:
        cursor.execute('USE inventory')
        cursor.execute('SELECT id FROM products WHERE id = %s', (productId,))
        if cursor.fetchone():
            messagebox.showerror('Error', 'Product ID Already Exists')
            return
        categoryId = getCategoryId(cursor, category)
        supplierId = getSupplierId(cursor, supplier)
        if categoryId is None or supplierId is None:
            messagebox.showerror('Error', 'Selected Category or Supplier No Longer Exists')
            return
        cursor.execute('''INSERT INTO products (id, name, price, quantity, category_id, supplier_id, status, payment_method)
                          VALUES (%s, %s, %s, %s, %s, %s, %s, %s)''',
                       (productId, name, float(price), int(quantity), categoryId, supplierId, status, payment))
        connection.commit()
        messagebox.showinfo('Success', 'Product Added Successfully')
        treeviewData(treeview)
        clearProduct(productIdEntry, productNameEntry, priceEntry, quantityEntry,
                     categoryComboBox, supplierComboBox, statusComboBox, paymentComboBox, treeview)
    except Exception as e:
        messagebox.showerror('Error', str(e))
    finally:
        cursor.close()
        connection.close()


def updateProduct(productIdEntry, productNameEntry, priceEntry, quantityEntry,
                  categoryComboBox, supplierComboBox, statusComboBox, paymentComboBox, treeview):
    selected = treeview.selection()
    if not selected:
        messagebox.showerror('Error', 'No Row is Selected')
        return
    productId = productIdEntry.get().strip()
    name = productNameEntry.get().strip()
    price = priceEntry.get().strip()
    quantity = quantityEntry.get().strip()
    category = categoryComboBox.get()
    supplier = supplierComboBox.get()
    status = statusComboBox.get()
    payment = paymentComboBox.get()

    if not validateProductInput(productId, name, price, quantity, category, supplier, status, payment):
        return

    cursor, connection = connectDataBase()
    if not cursor or not connection:
        return
    try:
        cursor.execute('USE inventory')
        categoryId = getCategoryId(cursor, category)
        supplierId = getSupplierId(cursor, supplier)
        if categoryId is None or supplierId is None:
            messagebox.showerror('Error', 'Selected Category or Supplier No Longer Exists')
            return
        cursor.execute('SELECT name, price, quantity, category_id, supplier_id, status, payment_method FROM products WHERE id = %s', (productId,))
        currentData = cursor.fetchone()
        if not currentData:
            messagebox.showerror('Error', 'Product Not Found')
            return
        newData = (name, float(price), int(quantity), categoryId, supplierId, status, payment)
        if list(currentData) == [newData[0], newData[1], newData[2], newData[3], newData[4], newData[5], newData[6]]:
            messagebox.showinfo('Info', 'No Changes Detected')
            return
        cursor.execute('''UPDATE products SET name=%s, price=%s, quantity=%s, category_id=%s,
                          supplier_id=%s, status=%s, payment_method=%s WHERE id=%s''',
                       (name, float(price), int(quantity), categoryId, supplierId, status, payment, productId))
        connection.commit()
        messagebox.showinfo('Success', 'Product Updated Successfully')
        treeviewData(treeview)
    except Exception as e:
        messagebox.showerror('Error', str(e))
    finally:
        cursor.close()
        connection.close()


def deleteProduct(productIdEntry, treeview):
    selected = treeview.selection()
    if not selected:
        messagebox.showerror('Error', 'No Row is Selected')
        return
    productId = productIdEntry.get().strip()
    if productId == '':
        messagebox.showerror('Error', 'No Row is Selected')
        return
    result = messagebox.askyesno('Confirm', 'Do you Really Want to Delete the Record?')
    if not result:
        return
    cursor, connection = connectDataBase()
    if not cursor or not connection:
        return
    try:
        cursor.execute('USE inventory')
        cursor.execute('DELETE FROM products WHERE id = %s', (productId,))
        connection.commit()
        treeviewData(treeview)
        messagebox.showinfo('Success', 'Record Deleted Successfully')
    except Exception as e:
        messagebox.showerror('Error', str(e))
    finally:
        cursor.close()
        connection.close()


def selectData(event, productIdEntry, productNameEntry, priceEntry, quantityEntry,
               categoryComboBox, supplierComboBox, statusComboBox, paymentComboBox, treeview):
    index = treeview.selection()
    if not index:
        return
    content = treeview.item(index)
    actualContent = content['values']

    productIdEntry.delete(0, END)
    productNameEntry.delete(0, END)
    priceEntry.delete(0, END)
    quantityEntry.delete(0, END)
    categoryComboBox.set('Select Category')
    supplierComboBox.set('Select Supplier')
    statusComboBox.set('Status')
    paymentComboBox.set('Select Payment Method')

    productIdEntry.insert(0, actualContent[0])
    productNameEntry.insert(0, actualContent[1])
    priceEntry.insert(0, actualContent[2])
    quantityEntry.insert(0, actualContent[3])
    categoryComboBox.set(actualContent[4])
    supplierComboBox.set(actualContent[5])
    statusComboBox.set(actualContent[6])
    paymentComboBox.set(actualContent[7])


def product_form(window):
    global backImage
    createProductsTable()

    productFrame = Frame(window, bg='white', width=1070, height=567)
    productFrame.place(x=200, y=100)
    backImage = PhotoImage(file='back.png')
    backButton = Button(productFrame, image=backImage, font=('times new roman', 12, 'bold'), bg='white', bd=0,
                        cursor='hand2', command=lambda: productFrame.place_forget())
    backButton.place(x=20, y=10)

    leftFrame = Frame(productFrame, bg='white', bd=2, relief=RIDGE, width=500, height=500)
    leftFrame.place(x=20, y=50)

    heading_label = Label(leftFrame, text='Manage Product Details', font=('times new roman', 16, 'bold'),
                          bg='#0f4d7d', fg='white', bd=0)
    heading_label.grid(row=0, column=0, columnspan=2, sticky='we')

    productIdLabel = Label(leftFrame, text='Product ID:', font=('times new roman', 14, 'bold'), bg='white')
    productIdLabel.grid(row=1, column=0, padx=20, pady=10, sticky='w')
    productIdEntry = Entry(leftFrame, font=('times new roman', 14), bd=2, bg='light yellow', relief=GROOVE)
    productIdEntry.grid(row=1, column=1, padx=20, pady=10, sticky='w')

    productNameLabel = Label(leftFrame, text='Product Name:', font=('times new roman', 14, 'bold'), bg='white')
    productNameLabel.grid(row=2, column=0, padx=20, pady=10, sticky='w')
    productNameEntry = Entry(leftFrame, font=('times new roman', 14), bd=2, bg='light yellow', relief=GROOVE)
    productNameEntry.grid(row=2, column=1, padx=20, pady=10, sticky='w')

    priceLabel = Label(leftFrame, text='Price:', font=('times new roman', 14, 'bold'), bg='white')
    priceLabel.grid(row=3, column=0, padx=20, pady=10, sticky='w')
    priceEntry = Entry(leftFrame, font=('times new roman', 14), bd=2, bg='light yellow', relief=GROOVE)
    priceEntry.grid(row=3, column=1, padx=20, pady=10, sticky='w')

    QuantityLabel = Label(leftFrame, text='Quantity:', font=('times new roman', 14, 'bold'), bg='white')
    QuantityLabel.grid(row=4, column=0, padx=20, pady=10, sticky='w')
    QuantityEntry = Entry(leftFrame, font=('times new roman', 14), bd=2, bg='light yellow', relief=GROOVE)
    QuantityEntry.grid(row=4, column=1, padx=20, pady=10, sticky='w')

    categoryLabel = Label(leftFrame, text='Category:', font=('times new roman', 14, 'bold'), bg='white')
    categoryLabel.grid(row=5, column=0, padx=20, pady=10, sticky='w')
    categoryComboBox = ttk.Combobox(leftFrame, font=('times new roman', 14), state='readonly', width=18)
    categoryComboBox.grid(row=5, column=1, padx=20, pady=10, sticky='w')
    categoryComboBox.set('Select Category')

    supplierLabel = Label(leftFrame, text='Supplier:', font=('times new roman', 14, 'bold'), bg='white')
    supplierLabel.grid(row=6, column=0, padx=20, pady=10, sticky='w')
    supplierComboBox = ttk.Combobox(leftFrame, font=('times new roman', 14), state='readonly', width=18)
    supplierComboBox.grid(row=6, column=1, padx=20, pady=10, sticky='w')
    supplierComboBox.set('Select Supplier')

    statusLabel = Label(leftFrame, text='Status:', font=('times new roman', 14, 'bold'), bg='white')
    statusLabel.grid(row=7, column=0, padx=20, pady=10, sticky='w')
    statusComboBox = ttk.Combobox(leftFrame, values=('Active', 'Inactive'), font=('times new roman', 14),
                                  state='readonly', width=18)
    statusComboBox.grid(row=7, column=1, padx=20, pady=10, sticky='w')
    statusComboBox.set('Status')

    paymentLabel = Label(leftFrame, text='Payment Method:', font=('times new roman', 14, 'bold'), bg='white')
    paymentLabel.grid(row=8, column=0, padx=20, pady=10, sticky='w')
    paymentComboBox = ttk.Combobox(leftFrame,
                                   values=('COD', 'Credit Card', 'Debit Card', 'Bank Transfer', 'PayPal', 'Others'),
                                   font=('times new roman', 14), state='readonly', width=18)
    paymentComboBox.grid(row=8, column=1, padx=20, pady=10, sticky='w')
    paymentComboBox.set('Select Payment Method')

    # Populate category/supplier comboboxes from DB
    populateComboBoxes(categoryComboBox, supplierComboBox)

    buttonFrame = Frame(leftFrame, bg='white')
    buttonFrame.grid(row=9, column=0, columnspan=2, pady=20)

    addButton = Button(buttonFrame, text='Add', font=('times new roman', 12, 'bold'), bg='#0f4d7d', fg='white',
                       bd=2, relief=GROOVE, cursor='hand2',
                       command=lambda: addProduct(productIdEntry, productNameEntry, priceEntry, QuantityEntry,
                                                  categoryComboBox, supplierComboBox, statusComboBox,
                                                  paymentComboBox, treeview))
    addButton.grid(row=0, column=0, padx=10, pady=10)

    updateButton = Button(buttonFrame, text='Update', font=('times new roman', 12, 'bold'), bg='#0f4d7d', fg='white',
                          bd=2, relief=GROOVE, cursor='hand2',
                          command=lambda: updateProduct(productIdEntry, productNameEntry, priceEntry, QuantityEntry,
                                                        categoryComboBox, supplierComboBox, statusComboBox,
                                                        paymentComboBox, treeview))
    updateButton.grid(row=0, column=1, padx=10, pady=10)

    deleteButton = Button(buttonFrame, text='Delete', font=('times new roman', 12, 'bold'), bg='#0f4d7d', fg='white',
                          bd=2, relief=GROOVE, cursor='hand2',
                          command=lambda: deleteProduct(productIdEntry, treeview))
    deleteButton.grid(row=0, column=2, padx=10, pady=10)

    clearButton = Button(buttonFrame, text='Clear', font=('times new roman', 12, 'bold'), bg='#0f4d7d', fg='white',
                         bd=2, relief=GROOVE, cursor='hand2',
                         command=lambda: clearProduct(productIdEntry, productNameEntry, priceEntry, QuantityEntry,
                                                      categoryComboBox, supplierComboBox, statusComboBox,
                                                      paymentComboBox, treeview))
    clearButton.grid(row=0, column=3, padx=10, pady=10)

    treeviewFrame = Frame(productFrame, bg='white')
    treeviewFrame.place(x=530, y=50, height=500, width=500)
    scrollY = Scrollbar(treeviewFrame, orient=VERTICAL)
    scrollX = Scrollbar(treeviewFrame, orient=HORIZONTAL)
    treeview = ttk.Treeview(treeviewFrame,
                             columns=('id', 'name', 'price', 'quantity', 'category', 'supplier', 'status', 'payment'),
                             show='headings', yscrollcommand=scrollY.set, xscrollcommand=scrollX.set)
    treeview.pack(fill=BOTH, expand=1)
    scrollY.pack(side=RIGHT, fill=Y)
    scrollX.pack(side=BOTTOM, fill=X)
    scrollY.config(command=treeview.yview)
    scrollX.config(command=treeview.xview)
    treeview.heading('id', text='ID.')
    treeview.heading('name', text='Product Name')
    treeview.heading('price', text='Price')
    treeview.heading('quantity', text='Quantity')
    treeview.heading('category', text='Category')
    treeview.heading('supplier', text='Supplier')
    treeview.heading('status', text='Status')
    treeview.heading('payment', text='Payment Method')
    treeview['show'] = 'headings'
    treeview.column('id', width=60)
    treeview.column('name', width=140)
    treeview.column('price', width=80)
    treeview.column('quantity', width=80)
    treeview.column('category', width=100)
    treeview.column('supplier', width=100)
    treeview.column('status', width=80)
    treeview.column('payment', width=140)
    treeviewData(treeview)

    treeview.bind('<ButtonRelease-1>', lambda event: selectData(event, productIdEntry, productNameEntry,
                                                                priceEntry, QuantityEntry, categoryComboBox,
                                                                supplierComboBox, statusComboBox,
                                                                paymentComboBox, treeview))
