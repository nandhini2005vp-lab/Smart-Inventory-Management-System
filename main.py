import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3

# Database connection
conn = sqlite3.connect("inventory.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    price REAL NOT NULL,
    quantity INTEGER NOT NULL
)
""")

conn.commit()


# Main window
root = tk.Tk()
root.title("Smart Inventory Management System")
root.geometry("650x750")
root.configure(bg="#eaf2f8")


# Heading
heading = tk.Label(
    root,
    text="Smart Inventory Management System",
    font=("Arial", 22, "bold"),
    bg="#eaf2f8",
    fg="darkblue"
)
heading.pack(pady=40)


# Add Product Function
def open_add_product():

    product_window = tk.Toplevel(root)
    product_window.title("Add New Product")
    product_window.geometry("400x400")
    product_window.configure(bg="white")

    tk.Label(
        product_window,
        text="Add New Product",
        font=("Arial", 18, "bold"),
        bg="white"
    ).pack(pady=20)

    tk.Label(product_window, text="Product Name", bg="white").pack()
    name_entry = tk.Entry(product_window)
    name_entry.pack(pady=5)

    tk.Label(product_window, text="Price", bg="white").pack()
    price_entry = tk.Entry(product_window)
    price_entry.pack(pady=5)

    tk.Label(product_window, text="Quantity", bg="white").pack()
    quantity_entry = tk.Entry(product_window)
    quantity_entry.pack(pady=5)

    def save_product():

        name = name_entry.get().strip()
        price = price_entry.get().strip()
        quantity = quantity_entry.get().strip()

        if name == "" or price == "" or quantity == "":
            messagebox.showwarning(
                "Warning",
                "Please fill all fields"
            )
            return

        try:
            price = float(price)
            quantity = int(quantity)

            if price <= 0 or quantity < 0:
                messagebox.showwarning(
                    "Invalid Input",
                    "Price must be positive and quantity cannot be negative"
                )
                return

        except ValueError:
            messagebox.showerror(
                "Error",
                "Enter a valid price and whole-number quantity"
            )
            return

        cursor.execute(
            "SELECT id FROM products WHERE LOWER(name) = LOWER(?)",
            (name,)
        )

        existing_product = cursor.fetchone()

        if existing_product:
            messagebox.showwarning(
                "Duplicate Product",
                "This product already exists!"
            )
            return

        cursor.execute(
            "INSERT INTO products (name, price, quantity) VALUES (?, ?, ?)",
            (name, price, quantity)
        )

        conn.commit()

        messagebox.showinfo(
            "Success",
            "Product added successfully!"
        )

        product_window.destroy()
        
    # Add Product Button
    tk.Button(
        product_window,
        text="Add Product",
        width=15,
        bg="darkgreen",
        fg="white",
        font=("Arial", 11, "bold"),
        command=save_product
    ).pack(pady=20)

    # Delete Product Function
def delete_product():

    delete_window = tk.Toplevel(root)
    delete_window.title("Delete Product")
    delete_window.geometry("350x250")

    tk.Label(
        delete_window,
        text="Delete Product",
        font=("Arial", 18, "bold")
    ).pack(pady=20)

    tk.Label(
        delete_window,
        text="Enter Product ID:"
    ).pack()

    id_entry = tk.Entry(delete_window)
    id_entry.pack(pady=10)

    def confirm_delete():

        product_id = id_entry.get().strip()

        if not product_id.isdigit():
            messagebox.showwarning(
                "Warning",
                "Please enter a valid Product ID"
            )
            return

        cursor.execute(
            "SELECT name FROM products WHERE id = ?",
            (product_id,)
        )

        product = cursor.fetchone()

        if product is None:
            messagebox.showerror(
                "Error",
                "Product not found"
            )
            return

        answer = messagebox.askyesno(
            "Confirm Delete",
            f"Delete {product[0]}?"
        )

        if answer:
            cursor.execute(
                "DELETE FROM products WHERE id = ?",
                (product_id,)
            )

            conn.commit()

            messagebox.showinfo(
                "Success",
                "Product deleted successfully!"
            )

            delete_window.destroy()

    tk.Button(
        delete_window,
        text="Delete",
        command=confirm_delete
    ).pack(pady=15)
    

# View Products Function
def view_products():

    view_window = tk.Toplevel(root)
    view_window.title("View Products")
    view_window.geometry("600x400")

    tk.Label(
        view_window,
        text="Product Details",
        font=("Arial", 18, "bold")
    ).pack(pady=15)

    columns = ("ID", "Name", "Price", "Quantity")

    table = ttk.Treeview(
        view_window,
        columns=columns,
        show="headings"
    )

    for column in columns:
        table.heading(column, text=column)
        table.column(column, width=130)

    search_frame = tk.Frame(view_window)
    search_frame.pack(pady=10)

    search_label = tk.Label(
        search_frame,
        text="Search Product:"
    )
    search_label.pack(side="left", padx=5)

    search_entry = tk.Entry(search_frame)
    search_entry.pack(side="left", padx=5)

    def search_products():
        search_text = search_entry.get()
        if not search_text.strip():
            messagebox.showwarning(
                "Search",
                "Please enter a product name!"
            )
            return
        for item in table.get_children():
            table.delete(item)

        cursor.execute(
            "SELECT * FROM products WHERE name LIKE ?",
            ('%' + search_text + '%',)
        )

        results = cursor.fetchall()
        if not results:
            messagebox.showinfo(
                "Search",
                "No products found!"
            )
            return
        for product in results:
            table.insert("", "end", values=product)

    search_button = tk.Button(
        search_frame,
        text="Search",
        command=search_products
    )
    search_button.pack(side="left", padx=5)
    table.pack(fill="both", expand=True, padx=10, pady=10)

    cursor.execute("SELECT * FROM products")
    products = cursor.fetchall()
    low_stock = [
        product for product in products
        if product[3] <= 5
    ]

    if low_stock:
        message = "Low Stock Products:\n"

        for product in low_stock:
            message += f"{product[1]} - Only {product[3]} left\n"

        messagebox.showwarning("Low Stock Alert", message)

    for product in products:
        table.insert("", "end", values=product)


# Stock In / Stock Out Function
def stock_management():

    stock_window = tk.Toplevel(root)
    stock_window.title("Stock Management")
    stock_window.geometry("400x350")

    tk.Label(
        stock_window,
        text="Stock In / Stock Out",
        font=("Arial", 18, "bold")
    ).pack(pady=20)

    cursor.execute("SELECT id, name FROM products")
    products = cursor.fetchall()

    if not products:
        messagebox.showinfo("Information", "Please add products first.")
        stock_window.destroy()
        return

    product_choices = [
        f"{product[0]} - {product[1]}" for product in products
    ]

    tk.Label(stock_window, text="Select Product").pack()
    product_box = ttk.Combobox(
        stock_window,
        values=product_choices,
        state="readonly"
    )
    product_box.pack(pady=10)
    product_box.current(0)

    tk.Label(stock_window, text="Enter Quantity").pack()
    quantity_entry = tk.Entry(stock_window)
    quantity_entry.pack(pady=10)

    def update_stock(action):

        try:
            amount = int(quantity_entry.get())

            if amount <= 0:
                messagebox.showwarning(
                    "Warning",
                    "Enter a quantity greater than zero"
                )
                return

        except ValueError:
            messagebox.showerror(
                "Error",
                "Enter a valid whole number"
            )
            return

        selected = product_box.get()
        product_id = int(selected.split(" - ")[0])

        cursor.execute(
            "SELECT quantity FROM products WHERE id = ?",
            (product_id,)
        )
        result = cursor.fetchone()

        if action == "out" and amount > result[0]:
            messagebox.showwarning(
                "Warning",
                "Not enough stock available"
            )
            return

        if action == "in":
            new_quantity = result[0] + amount
        else:
            new_quantity = result[0] - amount

        cursor.execute(
            "UPDATE products SET quantity = ? WHERE id = ?",
            (new_quantity, product_id)
        )

        conn.commit()

        messagebox.showinfo(
            "Success",
            "Stock updated successfully!"
        )

        stock_window.destroy()

    button_frame = tk.Frame(stock_window)
    button_frame.pack(pady=20)

    tk.Button(
        button_frame,
        text="Stock In",
        bg="darkgreen",
        fg="white",
        command=lambda: update_stock("in")
    ).pack(side="left", padx=10)

    tk.Button(
        button_frame,
        text="Stock Out",
        bg="darkred",
        fg="white",
        command=lambda: update_stock("out")
    ).pack(side="left", padx=10)

# Dashboard Function
def dashboard():

    dashboard_window = tk.Toplevel(root)
    dashboard_window.title("Inventory Dashboard")
    dashboard_window.geometry("650x550")
    dashboard_window.configure(bg="#eaf2f8")

    cursor.execute("SELECT COUNT(*) FROM products")
    total_products = cursor.fetchone()[0]

    cursor.execute("SELECT SUM(quantity) FROM products")
    total_stock = cursor.fetchone()[0] or 0

    cursor.execute(
        "SELECT SUM(price * quantity) FROM products"
    )
    inventory_value = cursor.fetchone()[0] or 0

    tk.Label(
        dashboard_window,
        text="Inventory Dashboard",
        font=("Arial", 20, "bold"),
        bg="#eaf2f8",
        fg="darkblue"
    ).pack(pady=20)

    tk.Label(
        dashboard_window,
        text=f"Total Products: {total_products}",
        font=("Arial", 15, "bold"),
        bg="white",
        width=30
    ).pack(pady=10)

    tk.Label(
        dashboard_window,
        text=f"Total Stock Quantity: {total_stock}",
        font=("Arial", 15, "bold"),
        bg="white",
        width=30
    ).pack(pady=10)

    tk.Label(
        dashboard_window,
        text=f"Total Inventory Value: ₹{inventory_value:,.2f}",
        font=("Arial", 15, "bold"),
        bg="white",
        width=30
    ).pack(pady=10)
    
    # Product-wise Stock Table
    table_frame = tk.Frame(dashboard_window)
    table_frame.pack(pady=15, fill="both", expand=True)

    columns = ("Name", "Price", "Quantity", "Total Value")

    tree = ttk.Treeview(
        table_frame,
        columns=columns,
        show="headings",
        height=8
    )

    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, width=130, anchor="center")

    tree.pack(fill="both", expand=True)

    cursor.execute(
        "SELECT name, price, quantity, price * quantity FROM products"
    )

    tree.tag_configure("low_stock", background="#ffcccc")

    for product in cursor.fetchall():
        if product[2] <= 5:
            tree.insert(
                "",
                "end",
                values=product,
                tags=("low_stock",)
            )
        else:
            tree.insert("", "end", values=product)

# Edit Product Function
def edit_product():
    edit_window = tk.Toplevel(root)
    edit_window.title("Edit Product")
    edit_window.geometry("350x400")
    edit_window.configure(bg="#eaf2f8")

    tk.Label(edit_window, text="Enter Product ID",
             bg="#eaf2f8").pack(pady=5)

    id_entry = tk.Entry(edit_window)
    id_entry.pack(pady=5)

    def search_product():
        product_id = id_entry.get()

        cursor.execute(
            "SELECT * FROM products WHERE id = ?",
            (product_id,)
        )
        product = cursor.fetchone()

        if product is None:
            messagebox.showerror("Error", "Product not found")
            return

        tk.Label(edit_window, text="Product Name",
                 bg="#eaf2f8").pack(pady=5)
        name_entry = tk.Entry(edit_window)
        name_entry.insert(0, product[1])
        name_entry.pack(pady=5)

        tk.Label(edit_window, text="Price",
                 bg="#eaf2f8").pack(pady=5)
        price_entry = tk.Entry(edit_window)
        price_entry.insert(0, product[2])
        price_entry.pack(pady=5)

        tk.Label(edit_window, text="Quantity",
                 bg="#eaf2f8").pack(pady=5)
        quantity_entry = tk.Entry(edit_window)
        quantity_entry.insert(0, product[3])
        quantity_entry.pack(pady=5)

        def update_product():

            name = name_entry.get().strip()
            price = price_entry.get().strip()
            quantity = quantity_entry.get().strip()

            if name == "" or price == "" or quantity == "":
                messagebox.showwarning(
                    "Warning",
                    "Please fill all fields"
                )
                return

            try:
                price = float(price)
                quantity = int(quantity)

                if price <= 0 or quantity < 0:
                    messagebox.showwarning(
                        "Invalid Input",
                        "Price must be positive and quantity cannot be negative"
                    )
                    return

            except ValueError:
                messagebox.showerror(
                    "Error",
                    "Enter a valid price and whole-number quantity"
                )
                return

            cursor.execute(
                """UPDATE products
                   SET name = ?, price = ?, quantity = ?
                   WHERE id = ?""",
                (name, price, quantity, product_id)
            )

            conn.commit()

            messagebox.showinfo(
                "Success",
                "Product updated successfully!"
            )

            edit_window.destroy()

        tk.Button(
            edit_window,
            text="Update Product",
            bg="darkgreen",
            fg="white",
            command=update_product
        ).pack(pady=15)

    tk.Button(
        edit_window,
        text="Search Product",
        bg="darkblue",
        fg="white",
        command=search_product
    ).pack(pady=15)


# Buttons
main_frame = tk.Frame(root, bg="#eaf2f8")
main_frame.pack(pady=20)

tk.Button(
    main_frame,
    text="Dashboard",
    width=25,
    height=2,
    bg="darkgreen",
    fg="white",
    font=("Arial", 12, "bold"),
    command=dashboard
).pack(pady=10)

tk.Button(
    main_frame,
    text="Add Products",
    width=25,
    height=2,
    bg="darkblue",
    fg="white",
    font=("Arial", 12, "bold"),
    command=open_add_product
).pack(pady=10)

tk.Button(
    main_frame,
    text="View Products",
    width=25,
    height=2,
    bg="darkblue",
    fg="white",
    font=("Arial", 12, "bold"),
    command=view_products
).pack(pady=10)

tk.Button(
    main_frame,
    text="Stock In / Stock Out",
    width=25,
    height=2,
    bg="darkblue",# Main 
    fg="white",
    font=("Arial", 12, "bold"),
    command=stock_management
).pack(pady=10)
tk.Button(
    main_frame,
    text="Delete Products",
    width=25,
    height=2,
    bg="darkred",
    fg="white",
    font=("Arial", 12, "bold"),
    command=delete_product
).pack(pady=10)
  
# Main Window - Edit Product Button
tk.Button(
    main_frame,
    text="Edit Product",
    width=25,
    height=2,
    bg="darkgreen",
    fg="white",
    font=("Arial", 12, "bold"),
    command=edit_product
).pack(pady=10)

# Run Application
root.mainloop()