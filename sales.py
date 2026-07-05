from tkinter import *
from tkinter import ttk
from tkinter import messagebox
from employees import connectDataBase
from datetime import datetime, date
import csv
import os


# ---------------------------------------------------------------------------
# Table bootstrap
# ---------------------------------------------------------------------------
def createSalesTable():
    cursor, connection = connectDataBase()
    if not cursor or not connection:
        return
    try:
        cursor.execute('USE inventory')
        cursor.execute('''CREATE TABLE IF NOT EXISTS sales (
            sale_id    INT AUTO_INCREMENT PRIMARY KEY,
            product_id INT NOT NULL,
            quantity   INT NOT NULL,
            total      FLOAT NOT NULL,
            payment_method VARCHAR(30),
            sale_date  DATE NOT NULL,
            FOREIGN KEY (product_id) REFERENCES products(id)
        )''')
        connection.commit()
    except Exception as e:
        messagebox.showerror('Error', str(e))
    finally:
        cursor.close()
        connection.close()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def getProducts():
    cursor, connection = connectDataBase()
    if not cursor or not connection:
        return []
    try:
        cursor.execute('USE inventory')
        cursor.execute("SELECT id, name, price, quantity FROM products WHERE status = 'Active'")
        return cursor.fetchall()
    except Exception as e:
        messagebox.showerror('Error', str(e))
        return []
    finally:
        cursor.close()
        connection.close()


def populateProductComboBox(productComboBox):
    products = getProducts()
    productComboBox['values'] = [f"{p[0]} - {p[1]}" for p in products]


def getProductDetails(productIdName):
    """Returns (id, name, price, stock) or None."""
    if ' - ' not in productIdName:
        return None
    productId = productIdName.split(' - ')[0].strip()
    cursor, connection = connectDataBase()
    if not cursor or not connection:
        return None
    try:
        cursor.execute('USE inventory')
        cursor.execute('SELECT id, name, price, quantity FROM products WHERE id = %s', (productId,))
        return cursor.fetchone()
    except Exception as e:
        messagebox.showerror('Error', str(e))
        return None
    finally:
        cursor.close()
        connection.close()


# ---------------------------------------------------------------------------
# Auto-calculate total when product or quantity changes
# ---------------------------------------------------------------------------
def calculateTotal(productComboBox, quantityEntry, totalLabel):
    productStr = productComboBox.get()
    qty = quantityEntry.get().strip()
    if productStr == 'Select Product' or qty == '':
        totalLabel.config(text='Total: Rs. 0.00')
        return
    details = getProductDetails(productStr)
    if not details:
        totalLabel.config(text='Total: Rs. 0.00')
        return
    try:
        qty = int(qty)
        if qty < 1:
            totalLabel.config(text='Total: Rs. 0.00')
            return
        total = details[2] * qty
        totalLabel.config(text=f'Total: Rs. {total:.2f}')
    except ValueError:
        totalLabel.config(text='Total: Rs. 0.00')


# ---------------------------------------------------------------------------
# Record a sale
# ---------------------------------------------------------------------------
def makeSale(salesFrame, productComboBox, quantityEntry, paymentComboBox, totalLabel, historyTreeview):
    productStr = productComboBox.get()
    qty = quantityEntry.get().strip()
    payment = paymentComboBox.get()

    if productStr == 'Select Product' or qty == '' or payment == 'Select Payment Method':
        messagebox.showerror('Error', 'All Fields Required')
        return
    try:
        qty = int(qty)
        if qty < 1:
            raise ValueError
    except ValueError:
        messagebox.showerror('Error', 'Quantity Must Be a Positive Whole Number')
        return

    details = getProductDetails(productStr)
    if not details:
        messagebox.showerror('Error', 'Product Not Found')
        return
    productId, productName, price, stock = details
    if qty > stock:
        messagebox.showerror('Error', f'Insufficient Stock! Only {stock} unit(s) available.')
        return

    total = price * qty
    today = date.today().strftime('%Y-%m-%d')

    # Show bill preview before confirming
    confirmed = showBillPreview(salesFrame, productName, qty, price, total, payment, today)
    if not confirmed:
        return

    cursor, connection = connectDataBase()
    if not cursor or not connection:
        return
    try:
        cursor.execute('USE inventory')
        cursor.execute('''INSERT INTO sales (product_id, quantity, total, payment_method, sale_date)
                          VALUES (%s, %s, %s, %s, %s)''',
                       (productId, qty, total, payment, today))
        cursor.execute('UPDATE products SET quantity = quantity - %s WHERE id = %s', (qty, productId))
        connection.commit()
        messagebox.showinfo('Success', 'Sale Recorded Successfully')
        clearSale(productComboBox, quantityEntry, paymentComboBox, totalLabel)
        loadSalesHistory(historyTreeview)
        # refresh product list (stock changed)
        populateProductComboBox(productComboBox)
    except Exception as e:
        messagebox.showerror('Error', str(e))
    finally:
        cursor.close()
        connection.close()


# ---------------------------------------------------------------------------
# Bill preview Toplevel
# ---------------------------------------------------------------------------
def showBillPreview(parent, productName, qty, price, total, payment, saleDate):
    billWindow = Toplevel(parent)
    billWindow.title('Sale Bill')
    billWindow.geometry('400x380')
    billWindow.config(bg='white')
    billWindow.resizable(False, False)
    billWindow.grab_set()

    confirmed = {'value': False}

    try:
        billLogoImg = PhotoImage(file='bill_logo.png').subsample(2, 2)
        logoLabel = Label(billWindow, image=billLogoImg, bg='white')
        logoLabel.image = billLogoImg
        logoLabel.pack(pady=(10, 0))
    except Exception:
        pass

    Label(billWindow, text='===  SALE RECEIPT  ===', font=('times new roman', 14, 'bold'), bg='white', fg='#0f4d7d').pack()
    Label(billWindow, text=f'Date: {saleDate}', font=('times new roman', 11), bg='white').pack()

    sep = Frame(billWindow, bg='#0f4d7d', height=2)
    sep.pack(fill=X, padx=30, pady=5)

    detailsFrame = Frame(billWindow, bg='white')
    detailsFrame.pack(padx=30, anchor='w')

    rows = [
        ('Product:', productName),
        ('Unit Price:', f'Rs. {price:.2f}'),
        ('Quantity:', str(qty)),
        ('Payment:', payment),
        ('TOTAL:', f'Rs. {total:.2f}'),
    ]
    for label, value in rows:
        rowFrame = Frame(detailsFrame, bg='white')
        rowFrame.pack(fill=X, pady=2)
        Label(rowFrame, text=label, font=('times new roman', 11, 'bold'), bg='white', width=12, anchor='w').pack(side=LEFT)
        Label(rowFrame, text=value, font=('times new roman', 11), bg='white', anchor='w').pack(side=LEFT)

    sep2 = Frame(billWindow, bg='#0f4d7d', height=2)
    sep2.pack(fill=X, padx=30, pady=5)

    buttonFrame = Frame(billWindow, bg='white')
    buttonFrame.pack(pady=10)

    def confirm():
        confirmed['value'] = True
        billWindow.destroy()

    def cancel():
        billWindow.destroy()

    Button(buttonFrame, text='Confirm Sale', font=('times new roman', 11, 'bold'), bg='#059669', fg='white',
           cursor='hand2', width=14, command=confirm).grid(row=0, column=0, padx=10)
    Button(buttonFrame, text='Cancel', font=('times new roman', 11, 'bold'), bg='#c0392b', fg='white',
           cursor='hand2', width=10, command=cancel).grid(row=0, column=1, padx=10)

    billWindow.wait_window()
    return confirmed['value']


# ---------------------------------------------------------------------------
# Clear sale form
# ---------------------------------------------------------------------------
def clearSale(productComboBox, quantityEntry, paymentComboBox, totalLabel):
    productComboBox.set('Select Product')
    quantityEntry.delete(0, END)
    paymentComboBox.set('Select Payment Method')
    totalLabel.config(text='Total: Rs. 0.00')


# ---------------------------------------------------------------------------
# Sales History
# ---------------------------------------------------------------------------
def loadSalesHistory(treeview, fromDate=None, toDate=None):
    cursor, connection = connectDataBase()
    if not cursor or not connection:
        return
    try:
        cursor.execute('USE inventory')
        if fromDate and toDate:
            cursor.execute('''SELECT s.sale_id, p.name, s.quantity, s.total, s.payment_method, s.sale_date
                              FROM sales s JOIN products p ON s.product_id = p.id
                              WHERE s.sale_date BETWEEN %s AND %s
                              ORDER BY s.sale_date DESC''', (fromDate, toDate))
        else:
            cursor.execute('''SELECT s.sale_id, p.name, s.quantity, s.total, s.payment_method, s.sale_date
                              FROM sales s JOIN products p ON s.product_id = p.id
                              ORDER BY s.sale_date DESC''')
        rows = cursor.fetchall()
        treeview.delete(*treeview.get_children())
        for row in rows:
            treeview.insert('', 'end', values=row)
    except Exception as e:
        messagebox.showerror('Error', str(e))
    finally:
        cursor.close()
        connection.close()


def filterSales(treeview, fromDateEntry, toDateEntry):
    fromDate = fromDateEntry.get().strip()
    toDate = toDateEntry.get().strip()
    if fromDate == '' or toDate == '':
        messagebox.showerror('Error', 'Enter Both From and To Dates (YYYY-MM-DD)')
        return
    try:
        datetime.strptime(fromDate, '%Y-%m-%d')
        datetime.strptime(toDate, '%Y-%m-%d')
    except ValueError:
        messagebox.showerror('Error', 'Date Format Must Be YYYY-MM-DD')
        return
    loadSalesHistory(treeview, fromDate, toDate)


def exportToCSV(historyTreeview):
    rows = [(historyTreeview.item(child)['values']) for child in historyTreeview.get_children()]
    if not rows:
        messagebox.showerror('Error', 'No Records to Export')
        return
    fileName = f'sales_report_{date.today().strftime("%Y%m%d")}.csv'
    try:
        with open(fileName, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Sale ID', 'Product', 'Quantity', 'Total', 'Payment Method', 'Date'])
            writer.writerows(rows)
        messagebox.showinfo('Success', f'Report Exported: {os.path.abspath(fileName)}')
    except Exception as e:
        messagebox.showerror('Error', str(e))


# ---------------------------------------------------------------------------
# Main sales page
# ---------------------------------------------------------------------------
def sales_page(window):
    global backImage, billLogoImg2

    createSalesTable()

    salesFrame = Frame(window, bg='white', width=1070, height=567)
    salesFrame.place(x=200, y=100)

    headingLabel = Label(salesFrame, text='Sales & Billing', font=('times new roman', 16, 'bold'),
                         bg='#0f4d7d', fg='white', bd=0)
    headingLabel.place(x=0, y=0, relwidth=1)

    backImage = PhotoImage(file='back.png')
    backButton = Button(salesFrame, image=backImage, font=('times new roman', 12, 'bold'), bg='white', bd=0,
                        cursor='hand2', command=lambda: salesFrame.place_forget())
    backButton.place(x=20, y=30)

    # ---- LEFT: New Sale Form ----
    saleFormFrame = Frame(salesFrame, bg='white', bd=2, relief=RIDGE, width=440, height=480)
    saleFormFrame.place(x=15, y=65)

    Label(saleFormFrame, text='New Sale', font=('times new roman', 15, 'bold'),
          bg='#0f4d7d', fg='white').place(x=0, y=0, relwidth=1)

    Label(saleFormFrame, text='Product:', font=('times new roman', 13, 'bold'), bg='white').place(x=15, y=40)
    productComboBox = ttk.Combobox(saleFormFrame, font=('times new roman', 12), state='readonly', width=28)
    productComboBox.set('Select Product')
    productComboBox.place(x=120, y=42)
    populateProductComboBox(productComboBox)

    Label(saleFormFrame, text='Quantity:', font=('times new roman', 13, 'bold'), bg='white').place(x=15, y=90)
    quantityEntry = Entry(saleFormFrame, font=('times new roman', 12), bg='lightyellow', bd=1, relief=GROOVE, width=20)
    quantityEntry.place(x=120, y=92)

    Label(saleFormFrame, text='Payment:', font=('times new roman', 13, 'bold'), bg='white').place(x=15, y=140)
    paymentComboBox = ttk.Combobox(saleFormFrame,
                                   values=('Cash', 'Credit Card', 'Debit Card', 'Bank Transfer', 'PayPal', 'Others'),
                                   font=('times new roman', 12), state='readonly', width=28)
    paymentComboBox.set('Select Payment Method')
    paymentComboBox.place(x=120, y=142)

    totalLabel = Label(saleFormFrame, text='Total: Rs. 0.00', font=('times new roman', 16, 'bold'),
                       bg='white', fg='#059669')
    totalLabel.place(x=15, y=195)

    # Bind recalculate
    productComboBox.bind('<<ComboboxSelected>>',
                         lambda e: calculateTotal(productComboBox, quantityEntry, totalLabel))
    quantityEntry.bind('<KeyRelease>',
                       lambda e: calculateTotal(productComboBox, quantityEntry, totalLabel))

    saleButton = Button(saleFormFrame, text='Record Sale', font=('times new roman', 13, 'bold'),
                        bg='#059669', fg='white', cursor='hand2', width=22,
                        command=lambda: makeSale(salesFrame, productComboBox, quantityEntry,
                                                 paymentComboBox, totalLabel, historyTreeview))
    saleButton.place(x=60, y=250)

    clearSaleButton = Button(saleFormFrame, text='Clear', font=('times new roman', 12, 'bold'),
                             bg='#0f4d7d', fg='white', cursor='hand2', width=22,
                             command=lambda: clearSale(productComboBox, quantityEntry, paymentComboBox, totalLabel))
    clearSaleButton.place(x=60, y=300)

    # ---- RIGHT: Sales History ----
    historyFrame = Frame(salesFrame, bg='white', bd=2, relief=RIDGE, width=590, height=480)
    historyFrame.place(x=470, y=65)

    Label(historyFrame, text='Sales History', font=('times new roman', 15, 'bold'),
          bg='#0f4d7d', fg='white').place(x=0, y=0, relwidth=1)

    # Date filter row
    filterBar = Frame(historyFrame, bg='white')
    filterBar.place(x=10, y=35, width=565, height=40)

    Label(filterBar, text='From:', font=('times new roman', 11, 'bold'), bg='white').pack(side=LEFT)
    fromDateEntry = Entry(filterBar, font=('times new roman', 11), bg='lightyellow', bd=1, relief=GROOVE, width=11)
    fromDateEntry.pack(side=LEFT, padx=4)
    fromDateEntry.insert(0, date.today().strftime('%Y-%m-%d'))

    Label(filterBar, text='To:', font=('times new roman', 11, 'bold'), bg='white').pack(side=LEFT)
    toDateEntry = Entry(filterBar, font=('times new roman', 11), bg='lightyellow', bd=1, relief=GROOVE, width=11)
    toDateEntry.pack(side=LEFT, padx=4)
    toDateEntry.insert(0, date.today().strftime('%Y-%m-%d'))

    Button(filterBar, text='Filter', font=('times new roman', 10, 'bold'), bg='#0f4d7d', fg='white',
           cursor='hand2',
           command=lambda: filterSales(historyTreeview, fromDateEntry, toDateEntry)).pack(side=LEFT, padx=4)
    Button(filterBar, text='Show All', font=('times new roman', 10, 'bold'), bg='#0f4d7d', fg='white',
           cursor='hand2', command=lambda: loadSalesHistory(historyTreeview)).pack(side=LEFT, padx=4)
    Button(filterBar, text='Export CSV', font=('times new roman', 10, 'bold'), bg='#059669', fg='white',
           cursor='hand2', command=lambda: exportToCSV(historyTreeview)).pack(side=LEFT, padx=4)

    # Treeview
    tvFrame = Frame(historyFrame, bg='white')
    tvFrame.place(x=5, y=80, width=575, height=380)

    scrollY = Scrollbar(tvFrame, orient=VERTICAL)
    scrollX = Scrollbar(tvFrame, orient=HORIZONTAL)
    historyTreeview = ttk.Treeview(tvFrame,
                                   columns=('sale_id', 'product', 'qty', 'total', 'payment', 'date'),
                                   show='headings',
                                   yscrollcommand=scrollY.set,
                                   xscrollcommand=scrollX.set)
    historyTreeview.pack(fill=BOTH, expand=1)
    scrollY.pack(side=RIGHT, fill=Y)
    scrollX.pack(side=BOTTOM, fill=X)
    scrollY.config(command=historyTreeview.yview)
    scrollX.config(command=historyTreeview.xview)

    historyTreeview.heading('sale_id', text='Sale ID')
    historyTreeview.heading('product', text='Product')
    historyTreeview.heading('qty', text='Qty')
    historyTreeview.heading('total', text='Total (Rs)')
    historyTreeview.heading('payment', text='Payment')
    historyTreeview.heading('date', text='Date')

    historyTreeview.column('sale_id', width=60)
    historyTreeview.column('product', width=140)
    historyTreeview.column('qty', width=50)
    historyTreeview.column('total', width=90)
    historyTreeview.column('payment', width=110)
    historyTreeview.column('date', width=100)

    loadSalesHistory(historyTreeview)
