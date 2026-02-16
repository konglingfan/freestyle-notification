from datetime import date, timedelta
import calendar

def get_first_sunday_of_next_month(from_date: date = None) -> date:
    """
    Calculates the date of the first Sunday of the next month relative to the given date.
    If no date is provided, uses the current date.
    """
    if from_date is None:
        from_date = date.today()

    # Calculate first day of next month
    if from_date.month == 12:
        next_month_year = from_date.year + 1
        next_month_month = 1
    else:
        next_month_year = from_date.year
        next_month_month = from_date.month + 1

    first_day_of_next_month = date(next_month_year, next_month_month, 1)

    # Find the first Sunday
    # weekday(): Monday=0, Sunday=6
    weekday = first_day_of_next_month.weekday()
    
    # Days to add to reach Sunday (6)
    # If weekday is 6 (Sunday), add 0
    # If weekday is 0 (Monday), add 6
    days_to_add = (6 - weekday + 7) % 7
    
    first_sunday = first_day_of_next_month + timedelta(days=days_to_add)
    return first_sunday

if __name__ == "__main__":
    # verification
    print(f"Today: {date.today()}")
    print(f"Target: {get_first_sunday_of_next_month()}")
    
    # Test cases
    test_dates = [
        date(2026, 2, 16), # Next month March 2026. 1st is Sunday. Target: 2026-03-01
        date(2023, 12, 1), # Next month Jan 2024. 1st is Monday. Target: 2024-01-07
        date(2024, 1, 1),  # Next month Feb 2024. 1st is Thursday. Target: 2024-02-04
    ]
    
    for d in test_dates:
        print(f"Input: {d} -> Result: {get_first_sunday_of_next_month(d)}")
