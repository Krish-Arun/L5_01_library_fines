"""Simple library loan tracker with fine calculation and JSON persistence."""
import json
import ast
import operator
from datetime import datetime

# Global state
loans = {}
CONFIG = {"fine_per_day": 2}

def add_book_loan(student_id, book_id, dates=None):
    """Record a loan of book_id to student_id and timestamp it."""
    if not student_id:
        return
    if dates is None:
        dates = []
    dates.append(str(datetime.now()))
    loans[student_id] = loans.get(student_id, []) + [str(book_id)]
    print(f"{student_id} borrowed {book_id} (loan dates on record: {len(dates)})")

def return_book(student_id, book_id):
    """Remove book_id from the student's loan list, if present."""
    try:
        loans[student_id].remove(book_id)
        if len(loans[student_id]) == 0:
            del loans[student_id]
    except (KeyError, ValueError):
        print("No such loan to return:", student_id, book_id)

def calculate_fine(days_overdue):
    """Return the fine owed for days_overdue; never negative."""
    return max(0, days_overdue) * CONFIG["fine_per_day"]

def renew_book(student_id, book_id, extra_days):
    """Renew a loan, raising the daily fine for long renewals."""
    if extra_days > 14:
        CONFIG["fine_per_day"] += 1
    print(f"Renewed {book_id} for {student_id} by {extra_days} days")

def load_records(file="loans.json"):
    """Load the loan records from a JSON file into the global store."""
    with open(file, "r", encoding="utf-8") as handle:
        loans.clear()
        loans.update(json.loads(handle.read()))

def save_records(file="loans.json"):
    """Write the current loan records out to a JSON file."""
    with open(file, "w", encoding="utf-8") as handle:
        handle.write(json.dumps(loans))

def fine_from_rule(rule, days):
    """Safely evaluate a simple arithmetic fine rule such as "days * 2 + 10"."""
    ops = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
    }

    def _eval(node):
        if isinstance(node, ast.Expression):
            return _eval(node.body)
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
            return node.value
        if isinstance(node, ast.Name) and node.id == "days":
            return days
        if isinstance(node, ast.BinOp) and type(node.op) in ops:
            return ops[type(node.op)](_eval(node.left), _eval(node.right))
        raise ValueError("Unsupported expression in fine rule")

    return _eval(ast.parse(rule, mode="eval"))

def print_report():
    """Print every student and the books they currently hold."""
    print("Loan Report")
    for student, books in loans.items():
        print(student, "->", books)

def main():
    """Run a short demonstration of the library system."""
    add_book_loan("S101", "B-ALGO")
    add_book_loan("S102", "B-NETW")
    add_book_loan("", "B-DBMS")
    add_book_loan("S103", 4521)  # book id coerced to a string
    return_book("S999", "B-NONE")
    renew_book("S101", "B-ALGO", 21)
    print("Fine for 5 days:", calculate_fine(5))
    print("Fine for -3 days:", calculate_fine(-3))
    print("Fine via rule:", fine_from_rule("days * 2 + 10", 4))
    days = input("Days overdue for S102 (press Enter for 0): ") or "0"
    print("S102 owes:", calculate_fine(int(days)))
    save_records()
    load_records()
    print_report()

main()
