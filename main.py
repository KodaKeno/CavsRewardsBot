import csv
import os
import time
import random
import pandas as pd
from faker import Faker
from datetime import datetime, timedelta
from playwright.sync_api import Playwright, sync_playwright

def load_proxies(csv_file):
    """Load proxies from a CSV file."""
    if not os.path.exists(csv_file):
        print(f"Error: The file '{csv_file}' does not exist.")
        return []

    proxies = []
    with open(csv_file, 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            if len(row) == 4:
                proxies.append({
                    "server": f"http://{row[0]}:{row[1]}",
                    "username": row[2],
                    "password": row[3]
                })
    time.sleep(1.5)
    return proxies

def get_proxy_config(proxies):
    """Get a random proxy configuration if proxies are provided."""
    time.sleep(1.5)
    if proxies:
        proxy = random.choice(proxies)
        return {
            "server": proxy["server"],
            "username": proxy["username"],
            "password": proxy["password"]
        }
    return None

def log_stats_to_excel(email, password, success, alr_processed, human_rev):
    """Log or update stats in the account stats Excel file."""
    time.sleep(1.5)
    file_name = "account_stats.xlsx"

    # Calculate completion rate
    total_attempts = alr_processed + human_rev
    comp_rate = 0 if total_attempts == 0 else success / total_attempts

    # Create or update the Excel file
    if os.path.exists(file_name):
        df = pd.read_excel(file_name)
        # Check if account already exists
        if email in df["Email"].values:
            # Update existing stats
            df.loc[df["Email"] == email, "Success"] += success
            df.loc[df["Email"] == email, "Already Processed"] += alr_processed
            df.loc[df["Email"] == email, "Human Review"] += human_rev
            # Recalculate completion rate
            updated_success = df.loc[df["Email"] == email, "Success"].values[0]
            updated_alr_processed = df.loc[df["Email"] == email, "Already Processed"].values[0]
            updated_human_rev = df.loc[df["Email"] == email, "Human Review"].values[0]
            df.loc[df["Email"] == email, "Completion Rate"] = 0 if (updated_alr_processed + updated_human_rev) == 0 else updated_success / (updated_alr_processed + updated_human_rev)
        else:
            # Add new account stats
            new_row = {
                "Email": email,
                "Password": password,
                "Success": success,
                "Already Processed": alr_processed,
                "Human Review": human_rev,
                "Completion Rate": comp_rate
            }
            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    else:
        # Create new file with initial stats
        df = pd.DataFrame([{  
            "Email": email,
            "Password": password,
            "Success": success,
            "Already Processed": alr_processed,
            "Human Review": human_rev,
            "Completion Rate": comp_rate
        }])

    df.to_excel(file_name, index=False)

def escape_latex(text):
    """Escape LaTeX special characters."""
    return text.replace("#", "\\#")

def generate_random_receipt():
    """Generate random receipt details."""
    tc_number = escape_latex(f"TC# {random.randint(1000, 9999)} {random.randint(1000, 9999)} {random.randint(1000, 9999)} {random.randint(1000, 9999)}")
    st_number = escape_latex(f"ST# {random.randint(1000, 9999)} OP# {random.randint(1000, 9999)} TE# {random.randint(1, 20)} TR# {random.randint(1000, 9999)}")
    random_date = (datetime.now() - timedelta(days=random.randint(0, 15))).strftime("%m/%d/%y %H:%M:%S")
    amex_number = escape_latex(f"{random.randint(1000, 9999)}")

    items_dict = {
        "OILSPRAY": "002639599991 F",
        "PLSBY ELF": "001800011925 F",
        "BEEF RIBEYE": "026039400000 F",
        "CHILL 12PK": "004900055539 F",
        "CAKE": "007432309524 F",
        "B J ICECRM": "007684040007 F",
        "GV HF HF": "060538818715 F",
        "GV CK MJ 8Z": "007874203972 F"
    }

    fixed_item = ("MMZ LEMONADE", "002500012052 F", random.uniform(2.50, 4.50))
    selected_items = random.sample(list(items_dict.items()), 4)
    items_with_prices = [(name, number, round(random.uniform(10.0, 30.0), 2)) for name, number in selected_items]
    items = items_with_prices[:2] + [fixed_item] + items_with_prices[2:]

    subtotal = round(sum(price for _, _, price in items), 2)
    tax1 = round(0.07 * subtotal, 2)
    total = round(subtotal + tax1, 2)

    return tc_number, st_number, random_date, amex_number, items, subtotal, tax1, total

def create_receipt_latex(tc_number, st_number, random_date, amex_number, items, subtotal, tax1, total, logo_path, barcode_path):
    """Create LaTeX receipt."""
    time.sleep(1.5)
    items_tabbed = r"""
    \begin{tabbing}
        \hspace{2.5cm} \= \hspace{3.7cm} \= \kill
    """
    for name, number, price in items:
        items_tabbed += f"        \\textbf{{{name}}} \\> \\textbf{{{number}}} \\> \\textbf{{{price:.2f}}}\\\\n"
    items_tabbed += r"    \end{tabbing}"

    receipt_template = r"""
\documentclass{article}
\usepackage{geometry}
\geometry{paperwidth=100mm, paperheight=150mm, left=5mm, top=5mm, right=5mm, bottom=5mm}
\usepackage{courier}
\renewcommand{\familydefault}{\ttdefault}
\usepackage{array}
\usepackage{graphicx}
\usepackage{multicol}
\usepackage{xcolor}
\pagecolor{white}
\usepackage{adjustbox}

\begin{document}
\pagestyle{empty}

\newcommand{\receiptfontsize}{\fontsize{10}{9}\selectfont}
\receiptfontsize

\begin{center}
    \includegraphics[width=\linewidth]{{{logo_path}}} % Walmart logo
    \textbf{WAL*MART}\\
    \textbf{33062990 Mgr. MIRANDA}\\
    \textbf{905 SINGLETARY DR}\\
    \textbf{STREETSBORO, OH}\\
    \textbf{{{st_number}}}\\
    \vspace{1mm}
""" + items_tabbed + r"""
    \vspace{-9mm}
    \hspace{2.5cm}\begin{tabbing}
        \hspace{2cm} \= \hspace{2.4cm} \= \kill
        \textbf{\hspace{4cm}SUBTOTAL} \> \textbf{\hspace{4.3cm} {{{subtotal}}}} \\\\
        \textbf{\hspace{2.5cm}TAX} \hspace{-0.25mm} \textbf{1} \> \textbf{\hspace{2.5cm}7\%} \> \textbf{\hspace{1.90cm} {{{tax1}}}} \\\\
        \textbf{\hspace{2.5cm}TAX 12} \> \textbf{\hspace{2.5cm}0\%} \> \textbf{\hspace{2.1cm}0.00} \\\\
        \textbf{\hspace{4.75cm}TOTAL} \> \textbf{\hspace{4.3cm} {{{total}}}} \\\\
        \textbf{\hspace{2.45cm}AMEX CREDIT TEND} \> \textbf{\hspace{4.3cm} {{{total}}}} \\\\
        \textbf{\hspace{2.7cm}AMEX} \textbf{**** **** **** {{{amex_number}}}} \\\\
        \textbf{\hspace{3.7cm}CHANGE DUE} \> \textbf{\hspace{4.7cm}0.00} \\\\
    \end{tabbing}
    \vspace{-2mm}
    \textbf{\huge{\# ITEMS SOLD 5}}\\
    \vspace{0.5cm}
    \textbf{{{tc_number}}}\\
    \includegraphics[width=\linewidth]{{{barcode_path}}} % Barcode
    \vspace{0.5cm}
    \textbf{{{random_date}}}
\end{center}  
\end{document}
"""
    with open("receipt.tex", "w") as f:
        f.write(receipt_template)

def compile_latex_to_png():
    """Compile LaTeX to PDF and convert to PNG."""
    try:
        time.sleep(1.5)
        os.system("pdflatex receipt.tex")
        os.system("convert -density 200 receipt.pdf -quality 100 receipt.png")
    except Exception as e:
        print(f"Error during compilation: {e}")
        return False
    return True

def generate_receipt():
    """Generate and compile receipt to PNG."""
    time.sleep(1.5)
    tc_number, st_number, random_date, amex_number, items, subtotal, tax1, total = generate_random_receipt()
    logo_path = "Header.png"
    barcode_path = "barcode.png"

    # Check if required files exist
    if not os.path.exists(logo_path):
        print(f"Error: '{logo_path}' is missing!")
        return None
    if not os.path.exists(barcode_path):
        print(f"Error: '{barcode_path}' is missing!")
        return None

    create_receipt_latex(tc_number, st_number, random_date, amex_number, items, subtotal, tax1, total, logo_path, barcode_path)
    if compile_latex_to_png():
        for ext in ["aux", "log", "pdf", "tex"]:
            if os.path.exists(f"receipt.{ext}"):
                os.remove(f"receipt.{ext}")
        return "receipt.png"
    return None

def create_account(playwright: Playwright, accounts: list):
    """Create an account on Cavs Rewards."""
    time.sleep(1.5)
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()

    # Navigate and fill in account creation steps
    page.goto("https://www.cavsrewards.com/")
    time.sleep(1.5)
    email = f"{Faker().last_name()}{random.randint(1000, 9999)}@example.com"
    password = f"Pass{random.randint(1000, 9999)}!"

    # Simulate account creation steps here
    accounts.append({"email": email, "password": password})

    context.close()
    browser.close()
    print(f"Account created: {email}")

def login_and_upload_receipt(playwright, account, receipt_path):
    """Log into an account and upload receipt."""
    time.sleep(1.5)
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()

    # Simulated login and receipt upload logic
    time.sleep(1.5)
    success, alr_processed, human_rev = random.randint(0, 1), random.randint(0, 1), random.randint(0, 1)

    context.close()
    browser.close()
    return success, alr_processed, human_rev

def main():
    """Main function to create accounts, generate receipts, and log statistics."""
    time.sleep(1.5)
    accounts = []

    with sync_playwright() as playwright:
        # Step 1: Create 5 accounts
        for _ in range(5):
            create_account(playwright, accounts)

        while True:
            # Step 2: Iterate through accounts
            for account in accounts:
                email = account["email"]
                password = account["password"]

                receipt_path = generate_receipt()
                if receipt_path:
                    success, alr_processed, human_rev = login_and_upload_receipt(
                        playwright, account, receipt_path
                    )

                    print(f"Processing account {email}: Success={success}, Already Processed={alr_processed}, Human Review={human_rev}")

                    log_stats_to_excel(email, password, success, alr_processed, human_rev)

if __name__ == "__main__":
    main()
