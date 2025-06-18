#this is the three inputs stored in String variables that the program will recieve
loan_amount = float(input("What is the loan Amount? "))
annual_Interest_Rate = float(input("What is the interest rate per year? "))
loan_term_year = int(input("What is the loan term in terms of years? "))

if loan_amount < 0:
            print("The Loan Amount is less than 0, please check your inputs")


#I need to calculate the monthly interest rate
monthly_interest_rate = (annual_Interest_Rate/100) / 12
#I need to get the loan term in months
loan_term_month = loan_term_year * 12
#this is the montly payment an integer that I am getting from using the following formula
monthly_payment = loan_amount * (monthly_interest_rate * (1 + monthly_interest_rate) ** loan_term_month) / ((1 + monthly_interest_rate) ** loan_term_month - 1)

schedule = []
#Now that I have all my variables it's time to get to work on the logic
Month = 0
def Amortization(loan_amount, monthly_payment, loan_term_month):
    for Month in range(1, loan_term_month + 1):
        interest_payment = loan_amount * monthly_interest_rate
        principal_payment = monthly_payment - interest_payment
        loan_amount -= principal_payment

        

        payment_info = {
            "Month" : Month,
            "Monthly Payment" : monthly_payment,
            "Interest per month" : interest_payment,
            "Principal per month" : principal_payment,
            "Updated balance" : loan_amount
        }

        schedule.append(payment_info)
        
        if loan_amount == 0:
            print("The Loan Amount has been paid off")
            break
    return schedule

schedule = Amortization(loan_amount, monthly_payment, loan_term_month)
# Print the amortization schedule
for payment in schedule:
    print(payment)
