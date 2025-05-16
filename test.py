from flask import request, render_template
from datetime import date, timedelta
from models.database import visitors_status

def search_by_date():
    input_date = "2025-05-15"  # e.g., '2025-04-30'
    print(input_date)
    # Convert to datetime object
    # date_obj = datetime.strptime(input_date, '%Y-%m-%d')

    # Define the range: from 00:00:00 to 23:59:59 of that date
    start_dt = input_date
    end_dt = input_date

    # MongoDB query
    results = list(visitors_status.find({
        "Date": {
            "$gte": start_dt,
            "$lte": end_dt
        }
    }))

    # Format for display
    for r in results:
        r["_id"] = str(r["_id"])
        # r["Date"] = r["Date"].strftime("%d-%b-%Y %H:%M")

    # Print to console or return to template
    print(f"results = {results}")

    return "hello"

search_by_date()
