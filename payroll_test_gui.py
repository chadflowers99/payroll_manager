# -*- coding: utf-8 -*-
"""
Created on Fri Oct 17 08:47:59 2025

@author: busin
"""

# payroll_test_gui.py

import tkinter as tk
from tkinter import messagebox
from datetime import datetime, timedelta
import csv
import sqlite3
from pathlib import Path

# --- Setup ---
DATA_FILE = Path("payroll_output.csv")
DB_FILE = Path("payroll_data.db")

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    # Payroll table
    c.execute("""
        CREATE TABLE IF NOT EXISTS payroll (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            rate REAL,
            start_time TEXT,
            end_time TEXT,
            hours REAL,
            gross REAL,
            tax REAL,
            net REAL,
            created_at TEXT
        )
    """)
    # Session log table
    c.execute("""
        CREATE TABLE IF NOT EXISTS session_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            start_time TEXT,
            end_time TEXT,
            rate REAL,
            logged INTEGER DEFAULT 0
        )
    """)
    conn.commit()
    conn.close()

def calculate_hours(start, end):
    return round((end - start).total_seconds() / 3600, 2)

def compute_pay(hours, rate):
    if hours > 40:
        reg = 40 * rate
        otp = (hours - 40) * rate * 1.5
        return reg + otp
    return hours * rate

def apply_tax(gross, tax_rate=0.15):
    tax = gross * tax_rate
    return round(tax, 2), round(gross - tax, 2)

def log_session(action):
    name = name_entry.get().strip().lower()
    rate_str = rate_entry.get().strip()

    if not name:
        messagebox.showwarning("Missing Name", "Please enter an employee name.")
        return

    now = datetime.now()

    if action == "start":
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("INSERT INTO session_log (name, start_time) VALUES (?, ?)", (name, now.isoformat()))
        conn.commit()
        conn.close()
        messagebox.showinfo("Session Started", f"{name.title()} clocked in at {now.isoformat()}")

    elif action == "end":
        if not rate_str:
            messagebox.showwarning("Missing Rate", "Please enter hourly rate before ending session.")
            return
        
        try:
            rate = float(rate_str)
        except ValueError:
            messagebox.showerror("Rate Error", "Hourly rate must be a number.")
            return

        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("""
            SELECT id, start_time FROM session_log
            WHERE name = ? AND end_time IS NULL
            ORDER BY start_time DESC LIMIT 1
        """, (name,))
        row = c.fetchone()

        if not row:
            messagebox.showwarning("No Session", f"No active session found for {name.title()}")
            conn.close()
            return

        session_id, start_str = row
        start = datetime.fromisoformat(start_str)
        duration = calculate_hours(start, now)
        gross = compute_pay(duration, rate)
        tax, net = apply_tax(gross)
        created_at = datetime.now().isoformat()

        # Update session_log
        c.execute("""
            UPDATE session_log SET end_time = ?, rate = ?, logged = 1 WHERE id = ?
        """, (now.isoformat(), rate, session_id))

        # Write to payroll table
        c.execute("""
            INSERT INTO payroll (name, rate, start_time, end_time, hours, gross, tax, net, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (name, rate, start.isoformat(), now.isoformat(), duration, gross, tax, net, created_at))

        conn.commit()
        conn.close()

        # Write to CSV
        write_header = not DATA_FILE.exists()
        with DATA_FILE.open("a", newline='') as f:
            writer = csv.DictWriter(f, fieldnames=[
                "name", "rate", "start_time", "end_time", "hours", "gross", "tax", "net", "created_at"
            ])
            if write_header:
                writer.writeheader()
            writer.writerow({
                "name": name,
                "rate": rate,
                "start_time": start.isoformat(),
                "end_time": now.isoformat(),
                "hours": duration,
                "gross": round(gross, 2),
                "tax": tax,
                "net": net,
                "created_at": created_at
            })

        messagebox.showinfo("Session Logged", f"{name.title()} → {duration} hrs @ ${rate:.2f}/hr\nGross: ${gross:.2f} | Tax: ${tax:.2f} | Net: ${net:.2f}")
        name_entry.delete(0, tk.END)
        rate_entry.delete(0, tk.END)

def run_payroll():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()

    # Filter: Fixed Sunday–Saturday Week
    today = datetime.now()
    weekday = today.weekday()  # 0 = Monday, 6 = Sunday
    
    # Always anchor to the most recent Sunday
    start_of_week = today - timedelta(days=(weekday + 1) % 7)
    end_of_week = start_of_week + timedelta(days=7)
    
    c.execute("""
        SELECT name, rate, SUM(hours), SUM(gross), SUM(tax), SUM(net)
        FROM payroll
        WHERE date(created_at) >= ? AND date(created_at) < ?
        GROUP BY name, rate
    """, (start_of_week.date().isoformat(), end_of_week.date().isoformat()))
    results = c.fetchall()
    
    # 🔍 Diagnostic print
    print("Start of week:", start_of_week.date())
    print("End of week:", end_of_week.date())
    print("Query results:")
    for row in results:
        print(row)
    conn.close()

    if not results:
        messagebox.showinfo("Run Payroll", "No payroll data found for the past week.")
        return

    summary_window = tk.Toplevel(root)
    summary_window.title("Weekly Payroll Summary")

    text = tk.Text(summary_window, width=70, height=25)
    text.pack(padx=10, pady=10)

    total_paid_hours = total_unpaid_hours = 0
    total_gross = total_tax = total_net = 0

    markdown_lines = ["# Weekly Payroll Summary\n"]

    for name, rate, hours, gross, tax, net in results:
        label = "Paid" if rate > 0 else "Unpaid"
        text.insert(tk.END, f"{name.title():<10} | {label:<6} | Hours: {hours:.2f} | Gross: ${gross:.2f} | Tax: ${tax:.2f} | Net: ${net:.2f}\n")
        markdown_lines.append(f"- **{name.title()}** ({label}): {hours:.2f} hrs, Gross ${gross:.2f}, Tax ${tax:.2f}, Net ${net:.2f}")

        if rate > 0:
            total_paid_hours += hours
            total_gross += gross
            total_tax += tax
            total_net += net
        else:
            total_unpaid_hours += hours

    text.insert(tk.END, "\n")
    text.insert(tk.END, f"🧾 Paid Hours: {total_paid_hours:.2f}\n")
    text.insert(tk.END, f"🧾 Unpaid Hours: {total_unpaid_hours:.2f}\n")
    text.insert(tk.END, f"💰 Total Gross: ${total_gross:.2f}\n")
    text.insert(tk.END, f"🧾 Total Tax: ${total_tax:.2f}\n")
    text.insert(tk.END, f"💸 Total Net: ${total_net:.2f}\n")

    markdown_lines.append("\n---")
    markdown_lines.append(f"**Total Paid Hours**: {total_paid_hours:.2f}")
    markdown_lines.append(f"**Total Unpaid Hours**: {total_unpaid_hours:.2f}")
    markdown_lines.append(f"**Total Gross**: ${total_gross:.2f}")
    markdown_lines.append(f"**Total Tax**: ${total_tax:.2f}")
    markdown_lines.append(f"**Total Net**: ${total_net:.2f}")


    # Get current ISO week and year
    now = datetime.now()
    week_id = now.strftime("%Y-W%V")  # e.g., "2025-W42"
    filename = f"weekly_summary_{week_id}.md"


    # Write markdown summary
    with open(filename, "w") as md:
        md.write("\n".join(markdown_lines))

# --- GUI Layout ---
root = tk.Tk()
root.title("Payroll_Hours Logger")
root.geometry("400x300")

tk.Label(root, text="Name").grid(row=0, column=0, padx=10, pady=5, sticky="e")
name_entry = tk.Entry(root, width=30)
name_entry.grid(row=0, column=1, padx=10, pady=5)

tk.Label(root, text="Hourly Rate").grid(row=1, column=0, padx=10, pady=5, sticky="e")
rate_entry = tk.Entry(root, width=30)
rate_entry.grid(row=1, column=1, padx=10, pady=5)

button_frame = tk.Frame(root)
button_frame.grid(row=2, column=0, columnspan=2, pady=10)
tk.Button(button_frame, text="Start Work Session", command=lambda: log_session("start")).grid(row=0, column=0, padx=5)
tk.Button(button_frame, text="End Work Session", command=lambda: log_session("end")).grid(row=0, column=1, padx=5)

tk.Button(root, text="Run Payroll", command=run_payroll).grid(row=3, column=0, columnspan=2, pady=15)

init_db()
root.mainloop()