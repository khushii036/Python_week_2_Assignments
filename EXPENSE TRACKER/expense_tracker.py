import csv
from dataclasses import asdict, dataclass
from datetime import datetime
import os

# --- Step 1: Data Model ---
@dataclass
class Expense:
    amount: float
    category: str
    description: str
    date: str  # Format: YYYY-MM-DD

    def to_dict(self):
        return asdict(self)


class ExpenseTracker:
    def __init__(self, filename="expenses.csv"):
        self.filename = filename
        self.expenses = []
        self.load_from_csv()

    # --- Step 2: File Persistence ---
    def save_to_csv(self):
        try:
            with open(self.filename, mode="w", newline="", encoding="utf-8") as file:
                fieldnames = ["amount", "category", "description", "date"]
                writer = csv.DictWriter(file, fieldnames=fieldnames)
                writer.writeheader()
                for exp in self.expenses:
                    writer.writerow(exp.to_dict())
        except IOError as e:
            print(f"Error saving data: {e}")

    def load_from_csv(self):
        if not os.path.exists(self.filename):
            return
        try:
            with open(self.filename, mode="r", encoding="utf-8") as file:
                reader = csv.DictReader(file)
                self.expenses = []
                for row in reader:
                    self.expenses.append(
                        Expense(
                            amount=float(row["amount"]),
                            category=row["category"].strip(),
                            description=row["description"].strip(),
                            date=row["date"].strip()
                        )
                    )
        except (IOError, ValueError) as e:
            print(f"Error loading data: {e}. Starting with an empty tracker.")

    # --- Step 3: Add Expense with Validation ---
    def add_expense(self, amount_str, category, description, date_str):
        try:
            amount = float(amount_str)
            if amount <= 0:
                raise ValueError("Amount must be greater than zero.")
        except ValueError:
            print("Invalid amount. Please enter a valid positive number.")
            return False

        category = category.strip().capitalize()
        if not category:
            print("Category cannot be empty.")
            return False

        try:
            # Validate date format
            valid_date = datetime.strptime(date_str, "%Y-%m-%d").date()
            date_str = valid_date.strftime("%Y-%m-%d")
        except ValueError:
            print("Invalid date format. Use YYYY-MM-DD.")
            return False

        new_expense = Expense(amount, category, description.strip(), date_str)
        self.expenses.append(new_expense)
        self.save_to_csv()
        print("Expense added successfully!")
        return True

    # --- Step 4: Tabulated View ---
    def view_expenses(self, data_list=None):
        target = data_list if data_list is not None else self.expenses
        if not target:
            print("\nNo expense records found.")
            return

        print(f"\n{'ID':<5} | {'Date':<12} | {'Category':<15} | {'Amount ($)':<12} | {'Description'}")
        print("-" * 70)
        for idx, exp in enumerate(target, start=1):
            print(f"{idx:<5} | {exp.date:<12} | {exp.category:<15} | {exp.amount:<12.2f} | {exp.description}")
        print("-" * 70)

    # --- Step 5: Filtering ---
    def filter_by_category(self, category):
        category = category.strip().capitalize()
        filtered = [e for e in self.expenses if e.category == category]
        self.view_expenses(filtered)

    def filter_by_date_range(self, start_str, end_str):
        try:
            start_date = datetime.strptime(start_str, "%Y-%m-%d").date()
            end_date = datetime.strptime(end_str, "%Y-%m-%d").date()
        except ValueError:
            print("Invalid date boundaries. Use YYYY-MM-DD.")
            return

        filtered = []
        for e in self.expenses:
            try:
                exp_date = datetime.strptime(e.date, "%Y-%m-%d").date()
                if start_date <= exp_date <= end_date:
                    filtered.append(e)
            except ValueError:
                continue
        self.view_expenses(filtered)

    # --- Step 6 & 7: Summaries & Breakdowns ---
    def generate_monthly_summary(self):
        if not self.expenses:
            print("\nNo data available to summarize.")
            return

        # Group by Year-Month and Category
        monthly_data = {}
        for e in self.expenses:
            try:
                month_key = e.date[:7]  # Extracts YYYY-MM
                if month_key not in monthly_data:
                    monthly_data[month_key] = {}
                monthly_data[month_key][e.category] = monthly_data[month_key].get(e.category, 0.0) + e.amount
            except Exception:
                continue

        for month, categories in sorted(monthly_data.items(), reverse=True):
            print(f"\n--- Summary for Month: {month} ---")
            total_month_spend = sum(categories.values())
            print(f"{'Category':<15} | {'Total Spend ($)':<15} | {'Percentage'}")
            print("-" * 45)
            for cat, amount in categories.items():
                percentage = (amount / total_month_spend) * 100
                print(f"{cat:<15} | {amount:<15.2f} | {percentage:.1f}%")
            print("-" * 45)
            print(f"{'TOTAL':<15} | {total_month_spend:<15.2f} | 100.0%")

    # --- Step 10 (Optional): Matplotlib Visualizer ---
    def plot_pie_chart(self):
        if not self.expenses:
            print("No data available to plot.")
            return
        try:
            import matplotlib.pyplot as plt
            
            cat_totals = {}
            for e in self.expenses:
                cat_totals[e.category] = cat_totals.get(e.category, 0.0) + e.amount
                
            labels = list(cat_totals.keys())
            sizes = list(cat_totals.values())
            
            plt.figure(figsize=(8, 6))
            plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140)
            plt.title("Spending Distribution by Category")
            plt.axis('equal')
            plt.show()
        except ImportError:
            print("Matplotlib is not installed. Run 'pip install matplotlib' to enable visual charts.")


# --- Step 8: Main Menu Loop ---
def main():
    tracker = ExpenseTracker()

    while True:
        print("\n===== EXPENSE TRACKER MENU =====")
        print("1. Add Expense")
        print("2. View All Expenses")
        print("3. Filter Expenses by Category")
        print("4. Filter Expenses by Date Range")
        print("5. Generate Monthly Category Summary")
        print("6. Plot Spending Pie Chart (Optional)")
        print("7. Exit")
        
        choice = input("Select an option (1-7): ").strip()
        
        if choice == "1":
            amount = input("Enter amount ($): ")
            category = input("Enter category (e.g., Food, Transport, Rent): ")
            description = input("Enter brief description: ")
            date = input("Enter date (YYYY-MM-DD) [Leave blank for today]: ").strip()
            if not date:
                date = datetime.today().strftime("%Y-%m-%d")
            tracker.add_expense(amount, category, description, date)
            
        elif choice == "2":
            tracker.view_expenses()
            
        elif choice == "3":
            cat = input("Enter category name to filter: ")
            tracker.filter_by_category(cat)
            
        elif choice == "4":
            start = input("Enter start date (YYYY-MM-DD): ")
            end = input("Enter end date (YYYY-MM-DD): ")
            tracker.filter_by_date_range(start, end)
            
        elif choice == "5":
            tracker.generate_monthly_summary()
            
        elif choice == "6":
            tracker.plot_pie_chart()
            
        elif choice == "7":
            print("Exiting Expense Tracker. Goodbye!")
            break
        else:
            print("Invalid choice. Please select a valid number between 1 and 7.")

if __name__ == "__main__":
    main()