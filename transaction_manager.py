import sqlite3
import shutil
import os
from datetime import datetime

def connect_db():
    """Establish a connection to the SQLite database."""
    return sqlite3.connect('finance_manager.db')

def add_transaction(user_id, transaction_type, amount, category):
    """Add a new transaction to the database."""
    conn = connect_db()
    cursor = conn.cursor()
    
    try:
        date = datetime.now().strftime("%Y-%m-%d")
        cursor.execute("INSERT INTO transactions (user_id, type, amount, category, date) VALUES (?, ?, ?, ?, ?)",
                       (user_id, transaction_type, amount, category, date))
        conn.commit()
        print("Transaction added successfully!")
        return cursor.lastrowid
    
    except Exception as e:
        print(f"Error adding transaction: {e}")
        return None
    
    finally:
        conn.close()

def update_transaction():
    """Update an existing transaction in the database."""
    conn = connect_db()
    cursor = conn.cursor()
    
    try:
        transaction_id = int(input("Enter transaction ID to update: "))
        cursor.execute("SELECT * FROM transactions WHERE id=?", (transaction_id,))
        transaction = cursor.fetchone()

        if not transaction:
            print("Transaction ID not found. Please try again.")
            return
        
        transaction_type = input("Enter new transaction type (income/expense): ").strip().lower()
        if transaction_type not in ['income', 'expense']:
            print("Invalid transaction type. Use 'income' or 'expense'.")
            return
        
        amount = float(input("Enter new amount: "))
        category = input("Enter new category: ")
        date = input("Enter new date (YYYY-MM-DD) or press Enter to keep the same: ")
        
        sql = "UPDATE transactions SET type=?, amount=?, category=?, date=? WHERE id=?"
        cursor.execute(sql, (transaction_type, amount, category, date or transaction[5], transaction_id))
        conn.commit()
        print("Transaction updated successfully!")
    
    except ValueError:
        print("Invalid input. Please enter numeric values for amount.")
    
    except Exception as e:
        print(f"Error updating transaction: {e}")
    
    finally:
        conn.close()

def delete_transaction():
    """Delete a transaction from the database."""
    conn = connect_db()
    cursor = conn.cursor()
    
    try:
        transaction_id = int(input("Enter transaction ID to delete: "))
        cursor.execute("SELECT * FROM transactions WHERE id=?", (transaction_id,))
        transaction = cursor.fetchone()

        if not transaction:
            print("Transaction ID not found. Please try again.")
            return
        
        cursor.execute("DELETE FROM transactions WHERE id=?", (transaction_id,))
        conn.commit()
        print("Transaction deleted successfully!")
    
    except Exception as e:
        print(f"Error deleting transaction: {e}")
    
    finally:
        conn.close()

def list_transactions(user_id):
    """List all transactions for a specific user."""
    conn = connect_db()
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT * FROM transactions WHERE user_id=?", (user_id,))
        transactions = cursor.fetchall()
        
        if not transactions:
            print("No transactions found for this user.")
            return []
        
        print("\nTransactions:")
        for transaction in transactions:
            print(f"ID: {transaction[0]}, Type: {transaction[2]}, Amount: {transaction[3]}, "
                  f"Category: {transaction[4]}, Date: {transaction[5]}")
        return transactions
    
    except Exception as e:
        print(f"Error listing transactions: {e}")
        return None
    
    finally:
        conn.close()

def generate_monthly_report(user_id, month, year):
    """Generate a monthly financial report for a user."""
    conn = connect_db()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT SUM(amount) FROM transactions 
        WHERE user_id=? AND type='income' AND strftime('%Y', date)=? AND strftime('%m', date)=?
    """, (user_id, year, month))
    total_income = cursor.fetchone()[0] or 0
    
    cursor.execute("""
        SELECT SUM(amount) FROM transactions 
        WHERE user_id=? AND type='expense' AND strftime('%Y', date)=? AND strftime('%m', date)=?
    """, (user_id, year, month))
    total_expenses = cursor.fetchone()[0] or 0
    
    savings = total_income - total_expenses
    print(f"\nMonthly Report for {month}/{year}:")
    print(f"Total Income: ${total_income:.2f}")
    print(f"Total Expenses: ${total_expenses:.2f}")
    print(f"Savings: ${savings:.2f}")
    
    conn.close()

def generate_yearly_report(user_id, year):
    """Generate a yearly financial report for a user."""
    conn = connect_db()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT SUM(amount) FROM transactions 
        WHERE user_id=? AND type='income' AND strftime('%Y', date)=?
    """, (user_id, year))
    total_income = cursor.fetchone()[0] or 0
    
    cursor.execute("""
        SELECT SUM(amount) FROM transactions 
        WHERE user_id=? AND type='expense' AND strftime('%Y', date)=?
    """, (user_id, year))
    total_expenses = cursor.fetchone()[0] or 0
    
    savings = total_income - total_expenses
    print(f"\nYearly Report for {year}:")
    print(f"Total Income: ${total_income:.2f}")
    print(f"Total Expenses: ${total_expenses:.2f}")
    print(f"Savings: ${savings:.2f}")
    
    conn.close()

def generate_report(user_id, year, month=None):
    """Generate a financial report for the specified month and year or the whole year."""
    conn = connect_db()
    cursor = conn.cursor()
    
    try:
        if month:
            cursor.execute("""
                SELECT SUM(amount) FROM transactions 
                WHERE user_id=? AND type='income' AND strftime('%Y', date)=? AND strftime('%m', date)=?
            """, (user_id, year, month))
            total_income = cursor.fetchone()[0] or 0
            
            cursor.execute("""
                SELECT SUM(amount) FROM transactions 
                WHERE user_id=? AND type='expense' AND strftime('%Y', date)=? AND strftime('%m', date)=?
            """, (user_id, year, month))
            total_expenses = cursor.fetchone()[0] or 0
        else:
            cursor.execute("""
                SELECT SUM(amount) FROM transactions 
                WHERE user_id=? AND type='income' AND strftime('%Y', date)=?
            """, (user_id, year))
            total_income = cursor.fetchone()[0] or 0
            
            cursor.execute("""
                SELECT SUM(amount) FROM transactions 
                WHERE user_id=? AND type='expense' AND strftime('%Y', date)=?
            """, (user_id, year))
            total_expenses = cursor.fetchone()[0] or 0

        savings = total_income - total_expenses
        if month:
            print(f"Report for {month}/{year} - Income: ${total_income:.2f}, Expenses: ${total_expenses:.2f}, Savings: ${savings:.2f}")
        else:
            print(f"Report for the year {year} - Income: ${total_income:.2f}, Expenses: ${total_expenses:.2f}, Savings: ${savings:.2f}")
    
    except Exception as e:
        print(f"Error generating report: {e}")
    
    finally:
        conn.close()

def set_budget(user_id):
    """Set a budget for a specific category for a user."""
    conn = connect_db()
    cursor = conn.cursor()
    
    try:
        category = input("Enter category: ")
        budget = float(input("Enter budget amount: "))
        
        cursor.execute("""
            INSERT INTO budgets (user_id, category, budget) 
            VALUES (?, ?, ?) 
        """, (user_id, category, budget))
        
        conn.commit()
        print(f"Budget set for {category}: ${budget:.2f}")
    
    except Exception as e:
        print(f"Error setting budget: {e}")
    
    finally:
        conn.close()

def check_budget(user_id):
    """Check if the user's expenses exceed their set budgets."""
    conn = connect_db()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM budgets WHERE user_id=?", (user_id,))
    budgets = cursor.fetchall()
    
    if not budgets:
        print("No budgets set. Please set a budget first.")
        return
    
    print("\nBudget Check:")
    for budget in budgets:
        category = budget[2]
        budget_amount = budget[3]
        
        cursor.execute("""
            SELECT SUM(amount) FROM transactions 
            WHERE user_id=? AND category=? AND type='expense'
        """, (user_id, category))
        
        total_expense = cursor.fetchone()[0] or 0
        if total_expense > budget_amount:
            print(f"Warning: You have exceeded your budget for {category}! Budget: ${budget_amount:.2f}, Expenses: ${total_expense:.2f}")
        else:
            print(f"You are within budget for {category}. Budget: ${budget_amount:.2f}, Expenses: ${total_expense:.2f}")

    conn.close()

def backup_database():
    """Backup the SQLite database to a specified directory."""
    try:
        shutil.copy('finance_manager.db', 'backup/finance_manager_backup.db')
        print("Database backup successful!")
    except Exception as e:
        print(f"Error backing up database: {e}")

def restore_database():
    """Restore the database from a backup."""
    try:
        if os.path.exists('backup/finance_manager_backup.db'):
            shutil.copy('backup/finance_manager_backup.db', 'finance_manager.db')
            print("Database restored successfully!")
        else:
            print("No backup found.")
    except Exception as e:
        print(f"Error restoring database: {e}")
