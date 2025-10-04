import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from tkcalendar import Calendar
import sqlite3
from datetime import date
from os import path
from tkinter import filedialog
from PIL import Image, ImageTk


# مسیر کامل فایل دیتابیس
db_path = path.join(path.dirname(__file__), "cafe.db")

# تنظیمات پایگاه داده
def initialize_database():
    try:
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS items (id INTEGER PRIMARY KEY, name TEXT, price INTEGER)")
        cursor.execute("CREATE TABLE IF NOT EXISTS sales (id INTEGER PRIMARY KEY, item_id INTEGER, quantity INTEGER, payment_type TEXT, price INTEGER, date TEXT, FOREIGN KEY (item_id) REFERENCES items(id))")
        cursor.execute("CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value INTEGER)")
        cursor.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('tax_rate', 10)")
        cursor.execute("""
                CREATE TABLE IF NOT EXISTS purchases (
                    id INTEGER PRIMARY KEY,
                    item_id INTEGER,
                    quantity INTEGER,
                    payment_method TEXT,
                    total_price INTEGER,
                    date TEXT
                )
        """)
        conn.commit()
        conn.close()
    except sqlite3.OperationalError as e:
        print("Error creating tables:", e)
    finally:
        conn.close()

initialize_database()

class CafeApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("برنامه مدیریت کافه")
        self.geometry("800x700")
        self.show_main_page()

    def show_main_page(self):
        self.clear_window()
        main_frame = tk.Frame(self)
        main_frame.pack(pady=50)

        tk.Button(main_frame, text="مدیریت اقلام", command=self.show_item_management_page).pack(pady=5)
        tk.Button(main_frame, text="صفحه خرید", command=self.show_purchase_page).pack(pady=5)
        tk.Button(main_frame, text="درآمد روزانه", command=self.show_daily_accounting_page).pack(pady=5)
        tk.Button(main_frame, text="درآمد ماهانه", command=self.show_monthly_accounting_page).pack(pady=5)
        tk.Button(main_frame, text="درآمد سالانه", command=self.show_yearly_accounting_page).pack(pady=5)

    def show_item_management_page(self):
        self.clear_window()
        management_frame = tk.Frame(self)
        management_frame.pack(pady=20)

        # فیلدهای ثبت اقلام جدید
        tk.Label(management_frame, text="نام کالا:").grid(row=0, column=0, padx=5, pady=5)
        item_name_entry = tk.Entry(management_frame)
        item_name_entry.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(management_frame, text="قیمت:").grid(row=1, column=0, padx=5, pady=5)
        item_price_entry = tk.Entry(management_frame)
        item_price_entry.grid(row=1, column=1, padx=5, pady=5)

        # دکمه ثبت کالا
        def add_item():
            name = item_name_entry.get()
            price = item_price_entry.get()
            if name and price.isdigit():
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                cursor.execute("INSERT INTO items (name, price) VALUES (?, ?)", (name, int(price)))
                conn.commit()
                conn.close()
                item_name_entry.delete(0, tk.END)
                item_price_entry.delete(0, tk.END)
                update_item_list()
                messagebox.showinfo("موفقیت", "کالا با موفقیت ثبت شد.")
            else:
                messagebox.showerror("خطا", "لطفاً نام و قیمت معتبر وارد کنید.")

        tk.Button(management_frame, text="ثبت کالا", command=add_item).grid(row=2, column=1, pady=10)

        # لیست اقلام
        tk.Label(management_frame, text="لیست اقلام:").grid(row=3, column=0, padx=5, pady=5)
        item_listbox = tk.Listbox(management_frame)
        item_listbox.grid(row=4, column=0, columnspan=2, padx=5, pady=5)
        
         # اضافه کردن فیلد تعداد برای هر آیتم
        quantity_vars = {}#################
        # به‌روزرسانی لیست اقلام
        def update_item_list():
            item_listbox.delete(0, tk.END)
            ##################
            for widget in management_frame.grid_slaves(row=4):  # حذف ویجت‌های قبلی تعداد
                if widget.winfo_class() == "Entry":
                    widget.destroy()
            #conn = sqlite3.connect("cafe.db")
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT id, name, price FROM items")
            items = cursor.fetchall()
            conn.close()
            for item in items:
                item_listbox.insert(tk.END, f"{item[0]} - {item[1]}: {item[2]} تومان")
            
        # حذف کالا
        def delete_item():
            try:
                selected_item = item_listbox.get(item_listbox.curselection())
                item_id = int(selected_item.split(" - ")[0])
                #conn = sqlite3.connect("cafe.db")
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                cursor.execute("DELETE FROM items WHERE id=?", (item_id,))
                conn.commit()
                conn.close()
                update_item_list()
                messagebox.showinfo("موفقیت", "کالا حذف شد.")
            except:
                messagebox.showerror("خطا", "لطفاً کالایی برای حذف انتخاب کنید.")

        # ویرایش کالا
        def edit_item():
            try:
                selected_item = item_listbox.get(item_listbox.curselection())
                print('debug #######################   :   ', selected_item.split(": ")[1].split(' ')[1])
                item_id, name, price = selected_item.split(" - ")[0], selected_item.split(": ")[0].split(" - ")[1], selected_item.split(": ")[1].split(' ')[0]
                new_name = simpledialog.askstring("ویرایش کالا", "نام جدید کالا:", initialvalue=name)
                new_price = simpledialog.askinteger("ویرایش قیمت", "قیمت جدید کالا:", initialvalue=int(price))
                if new_name and new_price:
                    #conn = sqlite3.connect("cafe.db")
                    conn = sqlite3.connect(db_path)
                    cursor = conn.cursor()
                    cursor.execute("UPDATE items SET name=?, price=? WHERE id=?", (new_name, new_price, item_id))
                    conn.commit()
                    conn.close()
                    update_item_list()
                    messagebox.showinfo("موفقیت", "کالا ویرایش شد.")
            except:
                messagebox.showerror("خطا", "لطفاً کالایی برای ویرایش انتخاب کنید.")

         # تنظیم نرخ مالیات
        def update_tax_rate():
            new_tax_rate = simpledialog.askinteger("تنظیم نرخ مالیات", "درصد مالیات جدید را وارد کنید:")
            if new_tax_rate is not None:
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                cursor.execute("UPDATE settings SET value=? WHERE key='tax_rate'", (new_tax_rate,))
                conn.commit()
                conn.close()
                messagebox.showinfo("موفقیت", f"نرخ مالیات به {new_tax_rate}% تغییر یافت.")
        
        tk.Button(management_frame, text="تنظیم نرخ مالیات", command=update_tax_rate).grid(row=6, column=1, pady=10)


        tk.Button(management_frame, text="حذف کالا", command=delete_item).grid(row=5, column=0, pady=5)
        tk.Button(management_frame, text="ویرایش کالا", command=edit_item).grid(row=5, column=1, pady=5)
        update_item_list()

        tk.Button(management_frame, text="بازگشت به صفحه اصلی", command=self.show_main_page).grid(row=7, column=1, pady=10)

    def show_purchase_page(self):
        self.clear_window()
        purchase_frame = tk.Frame(self)
        purchase_frame.pack(pady=20)

        ################
        # ایجاد بوم برای اسکرول کردن
        canvas = tk.Canvas(purchase_frame, width=700, height=600)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # افزودن اسکرول عمودی
        scrollbar = tk.Scrollbar(purchase_frame, orient="vertical", command=canvas.yview)
        scrollbar.pack(side=tk.RIGHT, fill="y")
        canvas.configure(yscrollcommand=scrollbar.set)

        # ایجاد یک فریم داخلی در بوم برای نمایش داده‌ها
        purchase_inner_frame = tk.Frame(canvas)
        canvas.create_window((0, 0), window=purchase_inner_frame, anchor="nw")

        # تابع برای تنظیم ابعاد بوم بعد از اضافه کردن داده‌ها
        def configure_canvas(event):
            canvas.configure(scrollregion=canvas.bbox("all"))

        purchase_inner_frame.bind("<Configure>", configure_canvas)
        ################        

        tk.Label(purchase_inner_frame, text="تاریخ خرید:").grid(row=0, column=0, padx=5, pady=5)
        cal = Calendar(purchase_inner_frame, selectmode='day', date_pattern='yyyy-mm-dd')
        cal.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(purchase_inner_frame, text="لیست اقلام:").grid(row=1, column=0, padx=5, pady=5)
        item_listbox = tk.Listbox(purchase_inner_frame, selectmode="multiple")
        item_listbox.grid(row=2, column=0, columnspan=2, padx=5, pady=5)

        #conn = sqlite3.connect("cafe.db")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, price FROM items")
        items = cursor.fetchall()
        conn.close()

        quantity_vars = {}
        for item in items:
            item_listbox.insert(tk.END, f"{item[0]} - {item[1]}: {item[2]} تومان")
            quantity_var = tk.IntVar(value=1)  # مقدار پیش‌فرض برای هر آیتم
            quantity_entry = tk.Entry(purchase_inner_frame, textvariable=quantity_var, width=3)
            quantity_entry.grid(row=2 + item[0], column=2)  # تنظیم موقعیت برای هر آیتم
            quantity_vars[item[0]] = quantity_var  # ذخیره مقدار فیلد تعداد
    

        payment_var = tk.StringVar(value="نقدی")
        tk.Radiobutton(purchase_inner_frame, text="نقدی", variable=payment_var, value="نقدی").grid(row=3, column=0, padx=5, pady=5)
        tk.Radiobutton(purchase_inner_frame, text="کارت", variable=payment_var, value="کارت").grid(row=3, column=1, padx=5, pady=5)

        total_label = tk.Label(purchase_inner_frame, text="جمع کل: 0 تومان")
        total_label.grid(row=4, column=0, columnspan=2, padx=5, pady=5)
        

        def calculate_total():
            selected_items = [item_listbox.get(i) for i in item_listbox.curselection()]
            total_price = 0
            for item in selected_items:
                item_id = int(item.split(" - ")[0])
                price = int(item.split(": ")[1].split(" ")[0])
                quantity = quantity_vars[item_id].get()
                total_price += price * quantity
            total_label.config(text=f"جمع کل: {total_price} تومان")

        item_listbox.bind("<<ListboxSelect>>", lambda _: calculate_total())


        def purchase_items():
            selected_date = cal.get_date()
            payment_type = payment_var.get()
            selected_items = [item_listbox.get(i) for i in item_listbox.curselection()]

            if not selected_items:
                messagebox.showerror("خطا", "لطفاً حداقل یک کالا انتخاب کنید.")
                return

            tax_rate = 0
            if payment_type == "کارت":
                tax_rate = simpledialog.askinteger("مالیات", "درصد مالیات را وارد کنید:")
                if tax_rate is None:
                    messagebox.showerror("خطا", "لطفاً درصد مالیات را وارد کنید.")
                    return

            #conn = sqlite3.connect("cafe.db")
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            total_purchase_price = 0
            for item in selected_items:
                item_id = int(item.split(" - ")[0])
                price = int(item.split(": ")[1].split(" ")[0])
                quantity = quantity_vars[item_id].get()
                final_price = price * quantity * (1 + tax_rate / 100) if payment_type == "کارت" else price * quantity                
                cursor.execute("INSERT INTO sales (item_id, quantity, payment_type, price, date) VALUES (?, ?, ?, ?, ?)",
                           (item_id, quantity, payment_type, final_price, selected_date))
                total_purchase_price += final_price
            conn.commit()
            conn.close()
            messagebox.showinfo("موفقیت", f"خرید با موفقیت ثبت شد.\nمبلغ نهایی: {total_purchase_price} تومان")
            calculate_total()

        tk.Button(purchase_inner_frame, text="ثبت خرید", command=purchase_items).grid(row=5, column=1, pady=10)
        tk.Button(purchase_inner_frame, text="بازگشت به صفحه اصلی", command=self.show_main_page).grid(row=6, column=1, pady=5)



    # سایر متدهای دخل روزانه و ماهانه

    def clear_window(self):
        for widget in self.winfo_children():
            widget.destroy()
    

    def show_daily_accounting_page(self):
        self.clear_window()
        daily_frame = tk.Frame(self)
        daily_frame.pack(pady=20)

        tk.Label(daily_frame, text="دخل روزانه", font=("Arial", 16)).pack(pady=5)

        # ایجاد بوم برای اسکرول کردن
        canvas = tk.Canvas(daily_frame, width=500, height=400)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # افزودن اسکرول عمودی
        scrollbar = tk.Scrollbar(daily_frame, orient="vertical", command=canvas.yview)
        scrollbar.pack(side=tk.RIGHT, fill="y")
        canvas.configure(yscrollcommand=scrollbar.set)

        # ایجاد یک فریم داخلی در بوم برای نمایش داده‌ها
        sales_inner_frame = tk.Frame(canvas)
        canvas.create_window((0, 0), window=sales_inner_frame, anchor="nw")

        # تابع برای تنظیم ابعاد بوم بعد از اضافه کردن داده‌ها
        def configure_canvas(event):
            canvas.configure(scrollregion=canvas.bbox("all"))

        sales_inner_frame.bind("<Configure>", configure_canvas)

        # دریافت و نمایش فروش‌های روزانه
        today = date.today().strftime("%Y-%m-%d")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT items.id, items.name, sales.quantity, sales.payment_type, sales.price FROM sales JOIN items ON sales.item_id = items.id WHERE sales.date = ?", (today,))
        sales = cursor.fetchall()
        conn.close()

        total_sales = 0
        total_tax = 0
        for sale in sales:
            item_id, name, quantity, payment_type, price = sale
            tax = int(price * 0.1) if payment_type == "کارت" else 0  # محاسبه مالیات
            total_sales += price
            total_tax += tax

            sale_label = tk.Label(sales_inner_frame, text=f"{name} - تعداد: {quantity} - نوع پرداخت: {payment_type} - قیمت: {price} تومان - مالیات: {tax} تومان")
            sale_label.pack(anchor="w", padx=10, pady=2)

        # نمایش جمع کل فروش و مالیات
        tk.Label(daily_frame, text=f"جمع کل فروش: {total_sales} تومان", font=("Arial", 12, "bold")).pack(pady=10)
        tk.Label(daily_frame, text=f"جمع کل مالیات: {total_tax} تومان", font=("Arial", 12, "bold")).pack(pady=10)

        tk.Button(daily_frame, text="بازگشت به صفحه اصلی", command=self.show_main_page).pack(pady=10)

    def show_monthly_accounting_page(self):
        self.clear_window()
        daily_sales_frame = tk.Frame(self)
        daily_sales_frame.pack(pady=20)

        # تاریخ انتخاب
        tk.Label(daily_sales_frame, text="تاریخ را انتخاب کنید:").pack(pady=5)
        cal = Calendar(daily_sales_frame, selectmode='day', date_pattern='yyyy-mm-dd')
        cal.pack(pady=5)

        # ایجاد بوم برای اسکرول کردن
        canvas = tk.Canvas(daily_sales_frame, width=500, height=400)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # افزودن اسکرول عمودی
        scrollbar = tk.Scrollbar(daily_sales_frame, orient="vertical", command=canvas.yview)
        scrollbar.pack(side=tk.RIGHT, fill="y")
        canvas.configure(yscrollcommand=scrollbar.set)

        # ایجاد یک فریم داخلی در بوم برای نمایش داده‌ها
        sales_inner_frame = tk.Frame(canvas)
        canvas.create_window((0, 0), window=sales_inner_frame, anchor="nw")

        # تابع برای تنظیم ابعاد بوم بعد از اضافه کردن داده‌ها
        def configure_canvas(event):
            canvas.configure(scrollregion=canvas.bbox("all"))

        sales_inner_frame.bind("<Configure>", configure_canvas)
        ############
        selected_date = cal.get_date()
        selected_month = selected_date[:7]  # استخراج ماه به‌صورت "yyyy-mm"

        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # دریافت جمع کل فروش و مالیات برای ماه انتخاب شده
        cursor.execute("SELECT SUM(price), SUM(price * 0.1) FROM sales WHERE date LIKE ? AND payment_type = 'کارت'", (selected_month + "%",))
        monthly_sales, monthly_tax = cursor.fetchone()
        monthly_sales = monthly_sales or 0  # در صورتی که فروش یافت نشود، مقدار ۰ قرار می‌دهد
        monthly_tax = monthly_tax or 0  # در صورتی که مالیات یافت نشود، مقدار ۰ قرار می‌دهد

        # نمایش جمع فروش ماهانه و مالیات ماهانه
        tk.Label(daily_sales_frame, text=f"جمع فروش ماهانه: {monthly_sales} تومان", font=("Arial", 12, "bold")).pack(pady=5)
        tk.Label(daily_sales_frame, text=f"جمع مالیات ماهانه: {monthly_tax} تومان", font=("Arial", 12, "bold")).pack(pady=5)

        # دکمه نمایش اطلاعات فروش روزانه
        def display_sales():
            # پاک کردن داده‌های قبلی
            for widget in sales_inner_frame.winfo_children():
                widget.destroy()

            selected_date = cal.get_date()                        
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT item_id, quantity, payment_type, price FROM sales WHERE date = ?", (selected_date,))
            sales = cursor.fetchall()
            conn.close()

            if not sales:
                tk.Label(sales_inner_frame, text="هیچ فروش برای تاریخ انتخاب شده یافت نشد.").pack()
                return
            # نمایش اطلاعات فروش
            total_sales = 0
            total_tax = 0
            for sale in sales:
                item_id, quantity, payment_type, price = sale
                total_sales += price
                tax = int(price * 0.1) if payment_type == "کارت" else 0  # محاسبه مالیات برای پرداخت با کارت
                total_tax += tax
                tk.Label(sales_inner_frame, text=f"کالا: {item_id} | تعداد: {quantity} | نوع پرداخت: {payment_type} | قیمت: {price} تومان").pack(anchor="w", padx=10, pady=2)

            # نمایش جمع کل فروش
            tk.Label(sales_inner_frame, text=f"جمع کل فروش: {total_sales} تومان", font=("Arial", 12, "bold")).pack(pady=10)
            tk.Label(sales_inner_frame, text=f"جمع کل مالیات: {total_tax} تومان", font=("Arial", 12, "bold")).pack(pady=10)


        # دکمه نمایش درآمد ماهانه
        def display_monthly_sales():
            
            selected_date = cal.get_date()
            month = selected_date[:7]  # استخراج ماه و سال به صورت "YYYY-MM"
            
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # دریافت جمع فروش و مالیات برای ماه انتخاب شده
            cursor.execute("SELECT SUM(price), SUM(price * 0.1) FROM sales WHERE strftime('%Y-%m', date) = ?", (month,))            
            total_sales, total_tax = cursor.fetchone()            

            
            # پاک کردن نمایش قبلی و نمایش جمع ماهانه
            for widget in daily_sales_frame.winfo_children():
                if isinstance(widget, tk.Label) and widget != cal:
                    widget.destroy()
            if total_sales and total_tax != None:
                tk.Label(daily_sales_frame, text=f"جمع فروش ماهانه: {total_sales} تومان", font=("Arial", 12, "bold")).pack(pady=5)
                tk.Label(daily_sales_frame, text=f"جمع مالیات ماهانه: {total_tax} تومان", font=("Arial", 12, "bold")).pack(pady=5)
            else :
                tk.Label(sales_inner_frame, text="هیچ فروش برای ماه انتخاب شده یافت نشد.").pack()
                return

        tk.Button(daily_sales_frame, text="نمایش درآمد ماه ", command=display_monthly_sales).pack(pady=10)
        tk.Button(daily_sales_frame, text="نمایش فروش روز", command=display_sales).pack(pady=10)
        tk.Button(daily_sales_frame, text="بازگشت به صفحه اصلی", command=self.show_main_page).pack(pady=5)


    def show_yearly_accounting_page(self):
        self.clear_window()
        yearly_frame = tk.Frame(self)
        yearly_frame.pack(pady=20)

        tk.Label(yearly_frame, text="درآمد سالانه", font=("Arial", 16)).pack(pady=5)

        year = date.today().year
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT SUM(price), SUM(price * 0.1) FROM sales WHERE strftime('%Y', date) = ?", (str(year),))
        total_sales, total_tax = cursor.fetchone()
        conn.close()

        tk.Label(yearly_frame, text=f"درآمد سال {year}: {total_sales} تومان", font=("Arial", 12, "bold")).pack(pady=10)
        tk.Label(yearly_frame, text=f"مالیات سال {year}: {total_tax} تومان", font=("Arial", 12, "bold")).pack(pady=10)
        tk.Button(yearly_frame, text="بازگشت به صفحه اصلی", command=self.show_main_page).pack(pady=10)

if __name__ == "__main__":
    app = CafeApp()
    app.mainloop() 