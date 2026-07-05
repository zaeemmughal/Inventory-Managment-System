from tkinter import *
from tkinter import messagebox
from employees import employee_form, connectDataBase
from suppliers import supplier_form
from categories import category_form
from products import product_form
from sales import sales_page


def getCount(table):
    cursor, connection = connectDataBase()
    if not cursor or not connection:
        return 0
    try:
        cursor.execute('USE inventory')
        cursor.execute(f'SELECT COUNT(*) FROM {table}')
        result = cursor.fetchone()
        return result[0] if result else 0
    except Exception:
        return 0
    finally:
        cursor.close()
        connection.close()


def refreshStats(totalEmpCount, totalSupCount, totalCatCount, totalProdCount, totalSalesCount):
    totalEmpCount.config(text=str(getCount('employees')))
    totalSupCount.config(text=str(getCount('suppliers')))
    totalCatCount.config(text=str(getCount('categories')))
    totalProdCount.config(text=str(getCount('products')))
    totalSalesCount.config(text=str(getCount('sales')))


# ---------------------------------------------------------------------------
# Navigation helpers — refresh stats after returning from a sub-page
# ---------------------------------------------------------------------------
def openPage(window, pageFunc, statLabels):
    pageFunc(window)
    # after any sub-page opens, also schedule a stat refresh on next idle
    window.after(500, lambda: refreshStats(*statLabels))


def logoutAction(window):
    result = messagebox.askyesno('Logout', 'Are you sure you want to logout?')
    if result:
        window.destroy()
        from login import login_window
        login_window()


def exitAction(window):
    result = messagebox.askyesno('Exit', 'Are you sure you want to exit the application?')
    if result:
        window.destroy()


# ---------------------------------------------------------------------------
# Dashboard builder — called by login after successful auth
# ---------------------------------------------------------------------------
def open_dashboard():
    window = Tk()
    window.title('Dashboard')
    window.geometry('1266x668+0+0')
    window.minsize(900, 600)
    window.config(bg='white')

    # ---- Header ----
    bgImage = PhotoImage(file='inventory.png')
    titleLable = Label(window, image=bgImage, compound=LEFT,
                       text='  Inventory Management System',
                       font=('times new roman', 30, 'bold'),
                       bg='#059669', fg='white', anchor='w', padx=20)
    titleLable.place(x=0, y=0, relwidth=1)

    logoutButton = Button(window, text='Logout', font=('times new roman', 15, 'bold'),
                          bg='white', fg='#059669', bd=0, cursor='hand2',
                          command=lambda: logoutAction(window))
    logoutButton.place(x=1100, y=18)

    subTitleLable = Label(window, text='Welcome Admin',
                          font=('times new roman', 15, 'bold'), bg='#4d636d', fg='white')
    subTitleLable.place(x=0, y=70, relwidth=1)

    # ---- Left sidebar menu ----
    leftFrame = Frame(window, bd=2, bg='white')
    leftFrame.place(x=0, y=100, width=200, height=555)

    logoImage = PhotoImage(file='logo.png')
    imageLabel = Label(leftFrame, image=logoImage, bg='white')
    imageLabel.pack(side=TOP, fill=X)

    menuLabel = Label(leftFrame, text='Menu', font=('times new roman', 20, 'bold'),
                      bg='#009688', fg='white')
    menuLabel.pack(side=TOP, fill=X)

    employeeLogo = PhotoImage(file='employee.png')
    employeeButton = Button(leftFrame, image=employeeLogo, compound=LEFT, text=' Employees',
                            font=('times new roman', 20), bg='white', cursor='hand2', anchor='w', padx=10,
                            command=lambda: openPage(window, employee_form, statLabels))
    employeeButton.pack(side=TOP, fill=X)

    supplierLogo = PhotoImage(file='supplier.png')
    supplierButton = Button(leftFrame, image=supplierLogo, compound=LEFT, text=' Suppliers',
                            font=('times new roman', 20), bg='white', cursor='hand2', anchor='w', padx=10,
                            command=lambda: openPage(window, supplier_form, statLabels))
    supplierButton.pack(side=TOP, fill=X)

    categoryLogo = PhotoImage(file='category.png')
    categoryButton = Button(leftFrame, image=categoryLogo, compound=LEFT, text=' Categories',
                            font=('times new roman', 20), bg='white', cursor='hand2', anchor='w', padx=10,
                            command=lambda: openPage(window, category_form, statLabels))
    categoryButton.pack(side=TOP, fill=X)

    productLogo = PhotoImage(file='product.png')
    productButton = Button(leftFrame, image=productLogo, compound=LEFT, text=' Products',
                           font=('times new roman', 20), bg='white', cursor='hand2', anchor='w', padx=10,
                           command=lambda: openPage(window, product_form, statLabels))
    productButton.pack(side=TOP, fill=X)

    saleLogo = PhotoImage(file='sales.png')
    saleButton = Button(leftFrame, image=saleLogo, compound=LEFT, text=' Sales',
                        font=('times new roman', 20), bg='white', cursor='hand2', anchor='w', padx=10,
                        command=lambda: openPage(window, sales_page, statLabels))
    saleButton.pack(side=TOP, fill=X)

    exitLogo = PhotoImage(file='exit.png')
    exitButton = Button(leftFrame, image=exitLogo, compound=LEFT, text=' Exit',
                        font=('times new roman', 20), bg='white', cursor='hand2', anchor='w', padx=10,
                        command=lambda: exitAction(window))
    exitButton.pack(side=TOP, fill=X)

    # ---- Stat Cards (grid with weights so they flex on resize) ----
    cardArea = Frame(window, bg='white')
    cardArea.place(x=200, y=100, relwidth=0.842, relheight=0.867)
    cardArea.columnconfigure((0, 1, 2), weight=1)
    cardArea.rowconfigure((0, 1, 2), weight=1)

    def makeCard(parent, row, col, imgFile, labelText, countVar, rowspan=1, colspan=1):
        frame = Frame(parent, bg='#2C3E50', bd=3, relief=RIDGE)
        frame.grid(row=row, column=col, rowspan=rowspan, columnspan=colspan,
                   padx=20, pady=20, sticky='nsew')
        try:
            img = PhotoImage(file=imgFile)
            imgLabel = Label(frame, image=img, bg='#2C3E50')
            imgLabel.image = img
            imgLabel.pack(pady=(10, 0))
        except Exception:
            pass
        Label(frame, text=labelText, font=('times new roman', 18, 'bold'),
              bg='#2C3E50', fg='white').pack()
        countLabel = Label(frame, text='0', font=('times new roman', 28, 'bold'),
                           bg='#2C3E50', fg='white')
        countLabel.pack(pady=(0, 10))
        return countLabel

    totalEmpCount  = makeCard(cardArea, 0, 0, 'total_emp.png',   'Total Employees',  None)
    totalSupCount  = makeCard(cardArea, 0, 1, 'total_sup.png',   'Total Suppliers',  None)
    totalCatCount  = makeCard(cardArea, 1, 0, 'total_cat.png',   'Total Categories', None)
    totalProdCount = makeCard(cardArea, 1, 1, 'total_prod.png',  'Total Products',   None)
    totalSalesCount= makeCard(cardArea, 2, 0, 'total_sales.png', 'Total Sales',      None, colspan=2)

    # Bundle stat labels for easy passing
    statLabels = (totalEmpCount, totalSupCount, totalCatCount, totalProdCount, totalSalesCount)

    # Initial load of live counts
    refreshStats(*statLabels)

    # Keep references so GC doesn't collect images
    window._keepalive = [bgImage, logoImage, employeeLogo, supplierLogo,
                         categoryLogo, productLogo, saleLogo, exitLogo]

    window.mainloop()


# ---------------------------------------------------------------------------
# Legacy direct-run support (still works if someone runs dashboard.py alone)
# ---------------------------------------------------------------------------
if __name__ == '__main__':
    open_dashboard()
