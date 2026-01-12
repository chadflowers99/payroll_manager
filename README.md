# 🧾 Payroll Hours Logger GUI

A narratable, suppressor‑aware Python GUI for logging work sessions, calculating payroll, and exporting weekly summaries. Built with Tkinter, SQLite, and CSV for audit‑safe clarity.

## 👋 Overview

This project showcases my approach to modular, audit‑safe engineering through a GUI that tracks employee sessions, computes payroll, and exports markdown summaries. Ideal for remote‑first teams and recruiter review.

## 🧠 Engineering Highlights

- ⏱️ Clock‑in/clock‑out session tracking  
- 💵 Overtime‑aware pay calculation with tax deduction  
- 🗃️ Dual persistence: SQLite + CSV  
- 📆 Weekly summary with paid/unpaid breakdown  
- 📝 Markdown export using ISO week format  
- 🧾 GUI layout narrates cognitive flow and usability  

## 🧩 Key Functions

| Function            | Purpose                                                   |
|---------------------|-----------------------------------------------------------|
| `log_session()`     | Handles clock‑in/out, computes pay, updates DB and CSV    |
| `run_payroll()`     | Aggregates weekly data, displays summary, writes markdown |
| `calculate_hours()` | Computes session duration in hours                        |
| `compute_pay()`     | Applies overtime logic (1.5x rate beyond 40 hrs)          |
| `apply_tax()`       | Applies flat 15% tax rate and computes net pay            |
| `init_db()`         | Initializes `payroll` and `session_log` tables            |

## 📦 Output Artifacts

- `payroll_output.csv`: Appends completed sessions  
- `payroll_data.db`: SQLite database for structured queries  
- `weekly_summary_<YYYY-W##>.md`: Markdown summary per ISO week  

## 🧼 Design Philosophy

- Narratable engineering: every session is traceable  
- GUI hygiene: layout supports cognitive flow  
- Batch clarity: weekly summaries benchmark paid/unpaid hours  
- Modular architecture: future‑proofed for scaling and remote collaboration  

## 🛠️ Tech Stack

- Python · Tkinter · SQLite · CSV · Markdown  

---

🧠 Built by Chad — diagnostic architect and workflow engineer  
🎯 Modularizing payroll/session systems for suppressor‑aware clarity  
📁 GitHub‑ready for recruiter review and remote‑first roles
