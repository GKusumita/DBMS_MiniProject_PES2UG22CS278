import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector

# ---------------------------------------------------
#     DATABASE CONNECTION
# ---------------------------------------------------
DB_CONFIG = {
    "host": "127.0.0.1",
    "user": "root",
    "password": "root",
    "database": "eportfolio_db"
}

def connect_db():
    try:
        return mysql.connector.connect(**DB_CONFIG)
    except mysql.connector.Error as e:
        messagebox.showerror("Database Error", str(e))
        return None

# ---------------------------------------------------
#     MAIN APPLICATION CLASS
# ---------------------------------------------------
class EPortfolioApp:
    def __init__(self, root):
        self.root = root
        self.root.title("PESU - E-Portfolio Management System")
        self.root.geometry("1050x650")

        # Sidebar
        sidebar = tk.Frame(root, bg="#263238", width=250)
        sidebar.pack(side="left", fill="y")

        header = tk.Label(sidebar, text="E-Portfolio System",
                          bg="#263238", fg="white", font=("Arial", 16, "bold"))
        header.pack(pady=20)

        # Buttons for navigation
        btns = [
            ("Students", self.student_ui),
            ("Portfolio", self.portfolio_ui),
            ("Projects", self.project_ui),
            ("Certifications", self.cert_ui),
            ("Skills", self.skill_ui)
        ]

        for text, command in btns:
            tk.Button(sidebar, text=text, bg="#37474F", fg="white",
                      font=("Arial", 12), bd=0, padx=10, pady=10,
                      command=command).pack(fill="x", pady=5)

        # Main content frame
        self.container = tk.Frame(root, bg="white")
        self.container.pack(side="right", expand=True, fill="both")

        self.show_welcome()

    # ---------------------------------------------------
    #  UI: Welcome screen
    # ---------------------------------------------------
    def show_welcome(self):
        for widget in self.container.winfo_children():
            widget.destroy()

        tk.Label(self.container, text="Welcome to PESU E-Portfolio System",
                 font=("Arial", 22, "bold"), bg="white").pack(pady=200)

    # ---------------------------------------------------
    #  UTILITY: Refresh table with DB data
    # ---------------------------------------------------
    def refresh_table(self, tree, table_name):
        conn = connect_db()
        if not conn: return
        cur = conn.cursor()

        cur.execute(f"SELECT * FROM {table_name}")
        rows = cur.fetchall()

        tree.delete(*tree.get_children())
        for r in rows:
            tree.insert("", "end", values=r)

        cur.close()
        conn.close()

    # ---------------------------------------------------
    #  STUDENT UI
    # ---------------------------------------------------
    def student_ui(self):
        self.load_table_ui(
            title="Student Records",
            table="Student",
            columns=[
                "StudentID", "FirstName", "LastName", "SRN",
                "Email", "Phone", "Semester", "Status"
            ]
        )

    # ---------------------------------------------------
    #  PORTFOLIO UI
    # ---------------------------------------------------
    def portfolio_ui(self):
        self.load_table_ui(
            title="Portfolio Records",
            table="Portfolio",
            columns=[
                "PortfolioID", "StudentID", "Title",
                "Visibility", "CreatedAt", "UpdatedAt"
            ]
        )

    # ---------------------------------------------------
    #  PROJECT UI
    # ---------------------------------------------------
    def project_ui(self):
        self.load_table_ui(
            title="Projects",
            table="Project",
            columns=[
                "ProjectID", "PortfolioID", "Title", "Description",
                "StartDate", "EndDate", "CreatedAt"
            ]
        )

    # ---------------------------------------------------
    #  CERT UI
    # ---------------------------------------------------
    def cert_ui(self):
        self.load_table_ui(
            title="Certifications",
            table="Certification",
            columns=[
                "CertID", "PortfolioID", "CertName",
                "IssuingOrg", "CompletionDate"
            ]
        )

    # ---------------------------------------------------
    #  SKILL UI
    # ---------------------------------------------------
    def skill_ui(self):
        self.load_table_ui(
            title="Skills",
            table="Skill",
            columns=[
                "SkillID", "PortfolioID", "SkillName",
                "Proficiency", "Endorsements"
            ]
        )

    # ---------------------------------------------------
    # REUSABLE TABLE VIEW UI
    # ---------------------------------------------------
    def load_table_ui(self, title, table, columns):
        for widget in self.container.winfo_children():
            widget.destroy()

        tk.Label(self.container, text=title,
                 font=("Arial", 20, "bold"), bg="white").pack(pady=20)

        frame = tk.Frame(self.container, bg="white")
        frame.pack(expand=True, fill="both")

        tree = ttk.Treeview(frame, columns=columns, show='headings')
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=150)
        tree.pack(expand=True, fill="both")

        btn_frame = tk.Frame(self.container, bg="white")
        btn_frame.pack(pady=10)

        tk.Button(btn_frame, text="Refresh", command=lambda: self.refresh_table(tree, table),
                  bg="#00796B", fg="white", padx=15).pack(side="left", padx=10)

        tk.Button(btn_frame, text="Add Record",
                  command=lambda: self.add_record_popup(table, columns),
                  bg="#0288D1", fg="white", padx=15).pack(side="left", padx=10)

        tk.Button(btn_frame, text="Delete Record",
                  command=lambda: self.delete_record(table, tree),
                  bg="#D32F2F", fg="white", padx=15).pack(side="left", padx=10)

        self.refresh_table(tree, table)

    # ---------------------------------------------------
    # ADD RECORD POPUP
    # ---------------------------------------------------
    def add_record_popup(self, table, columns):
        win = tk.Toplevel(self.root)
        win.title(f"Add to {table}")
        win.geometry("400x500")

        entries = {}
        for col in columns:
            tk.Label(win, text=col).pack()
            e = tk.Entry(win)
            e.pack()
            entries[col] = e

        def save():
            conn = connect_db()
            if not conn: return
            cur = conn.cursor()

            vals = [entries[c].get() for c in columns]
            placeholders = ", ".join(["%s"] * len(columns))

            try:
                cur.execute(
                    f"INSERT INTO {table} ({', '.join(columns)}) VALUES ({placeholders})",
                    vals
                )
                conn.commit()
                messagebox.showinfo("Success", "Record added successfully.")
                win.destroy()
            except mysql.connector.Error as e:
                messagebox.showerror("Error", str(e))

            cur.close()
            conn.close()

        tk.Button(win, text="Save", command=save,
                  bg="#4CAF50", fg="white", padx=20).pack(pady=20)

    # ---------------------------------------------------
    # DELETE RECORD
    # ---------------------------------------------------
    def delete_record(self, table, tree):
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Select a record to delete.")
            return

        item = tree.item(selected)['values']
        pk = item[0]  # assuming primary key = first column

        conn = connect_db()
        if not conn: return
        cur = conn.cursor()

        try:
            cur.execute(f"DELETE FROM {table} WHERE {tree['columns'][0]} = %s", (pk,))
            conn.commit()
            messagebox.showinfo("Deleted", "Record deleted successfully.")
            tree.delete(selected)
        except mysql.connector.Error as e:
            messagebox.showerror("Error", str(e))

        cur.close()
        conn.close()


# ---------------------------------------------------
#     RUN GUI
# ---------------------------------------------------
root = tk.Tk()
app = EPortfolioApp(root)
root.mainloop()
