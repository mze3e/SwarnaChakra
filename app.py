import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import random


# Set page configuration for a wide layout and add an icon
st.set_page_config(
    page_title="SwarnaChakra: Financial Planning Companion",
    page_icon="💰",  # Use any emoji as an icon
    layout="wide"  # Makes the page layout wide
)

# Title with Icon
st.markdown(
    """
    <h1 style="text-align: center; font-size: 3rem;">
        💰 SwarnaChakra: Your Financial Planning Companion
    </h1>
    """,
    unsafe_allow_html=True
)
# Inputs
st.header("Step 1: Enter Your Financial Details")
col1, col2, col3, col4 = st.columns(4)

with col1:
    current_age = st.number_input("Current age:", min_value=18, max_value=100, value=25)
with col2:
    retirement_age = st.number_input("Retirement age:", min_value=18, max_value=100, value=60)
with col3:
    monthly_income = st.number_input("Monthly income (INR):", min_value=0, value=50000)
with col4:
    monthly_expenses = st.number_input("Monthly expenses (INR):", min_value=0, value=30000)

annual_income = monthly_income * 12
annual_expenses = monthly_expenses * 12  # Correctly calculate annual expenses

col1, col2, col3 = st.columns(3)

with col1:
    gst_rate = st.slider("GST Rate (%):", min_value=0, max_value=20, value=18)
with col2:
    investment_rate = st.slider("Projected Growth (% per annum):", min_value=0.0, max_value=15.0, value=8.0)
with col3:
    inflation_rate = st.slider("Projected Inflation (% per annum):", min_value=0.0, max_value=15.0, value=6.0)

def calculate_tax(income):
    """Calculate tax based on Indian tax laws."""
    tax = 0
    if income <= 250000:
        tax = 0
    elif income <= 500000:
        tax = (income - 250000) * 0.05
    elif income <= 1000000:
        tax = 12500 + (income - 500000) * 0.2
    else:
        tax = 112500 + (income - 1000000) * 0.3
    return tax

# Goals Section
st.header("Step 2: Add Your Financial Goals")
goals = []

if "goal_types" not in st.session_state:
    # Initialize session state for goal types
    st.session_state.goal_types = ["House", "Car", "Traveling", "Emergency Fund", "Add Goal"]

# Divide goal inputs into 3 columns dynamically
columns = st.columns(3)

for i, goal in enumerate(st.session_state.goal_types):
    with columns[i % 3]:  # Rotate through columns dynamically
        st.subheader(f"{goal}")
        if goal == "Add Goal":
            # Form to add a new goal
            with st.form("Add Goal"):
                new_goal = st.text_input("New Goal:")
                submitted = st.form_submit_button("Add")

            # Handle form submission
            if submitted:
                if new_goal.strip():  # Ensure the new goal is not empty
                    st.session_state.goal_types.append(new_goal.strip())  # Add new goal
                    st.success(f"Goal '{new_goal}' added successfully!")
                else:
                    st.error("Goal name cannot be empty.")

        else:
            if 'default_value' not in st.session_state:
                st.session_state.default_value = {}
            if goal not in st.session_state.default_value:
                st.session_state.default_value[goal] = current_age + random.randrange(5,retirement_age)

            cost = st.number_input(f"Estimated cost for {goal} (INR):", min_value=0, value=70000000 if "House" in goal else 5000000, key=f"cost_{goal}")
            target_year = st.slider(f"By which year do you want to achieve your {goal}?", 
                                    min_value=current_age, 
                                    max_value=current_age + 50, 
                                    value=st.session_state.default_value[goal], 
                                    key=f"year_{goal}")
            goals.append({"type": goal, "cost": cost, "year": target_year})

# Projection
st.header("Step 3: Projection and Analysis")
years = st.slider("Projection Period (Years):", min_value=1, max_value=50, value=retirement_age)
ages = list(range(current_age, current_age + years))

# Calculate expenses with inflation and savings projection
projection_data = []
current_savings = 0
goal_deductions = {goal["year"]: {"amount" : goal["cost"], "type": goal["type"]} for goal in goals}
projected_expenses = annual_expenses  # Initialize expenses with inflation applied
projected_income = annual_income
projected_salary_increment = 0

for i, age in enumerate(ages):
    projected_tax = calculate_tax(projected_income)
    annual_gst_paid = projected_expenses * gst_rate / 100
    net_income = projected_income - projected_tax
    annual_savings = max(0, net_income - projected_expenses)
    growth = current_savings * (1 + investment_rate / 100) + annual_savings
    try: goal_cost = goal_deductions[age]['amount']
    except: goal_cost = 0
    try: goal_type = goal_deductions[age]['type']
    except: goal_type = ''

    growth -= goal_cost
    
    # Append to data for the table
    projection_data.append({
        "Age": age,
        "Year": i + 1,
        "Projected Income": round(projected_income,2),
        "Projected Tax": round(projected_tax,2),
        "Projected Tax %": f"{round(projected_tax/projected_income*100,2)}%",
        "Salary Increment": f"{projected_salary_increment}%",
        "Inflation": f"{inflation_rate}%",
        "Projected Expenses": round(projected_expenses,2),
        "Net Income": round(net_income,2),
        "Annual Savings": round(annual_savings,2),
        "Projected Savings (with Growth)": max(0, growth),
        "Goal Deduction": goal_type,
        "Goal Cost": round(goal_cost,2),
        "Annual GST Paid": round(annual_gst_paid,2),
    })
    
    # Update variables for the next year
    current_savings = max(0, growth)
    projected_salary_increment = random.randrange(3, int(inflation_rate))
    projected_income *= (1 + projected_salary_increment / 100)
    projected_expenses *= (1 + inflation_rate / 100)

# Convert to DataFrame
df_projection = pd.DataFrame(projection_data)

# Display Results
st.subheader("Projected Financial Table")
st.write(df_projection)

# Visualizations
st.subheader("Savings and Goal Achievement Over Time")
fig, ax = plt.subplots()
ax.plot(ages, df_projection["Projected Savings (with Growth)"], label="Projected Savings", color="green")
ax.plot(ages, df_projection["Projected Expenses"], label="Projected Expenses", color="red", linestyle="--")
for goal in goals:
    ax.axvline(x=goal["year"], color="blue", linestyle="--", label=f"{goal['type']} Goal Year" if goal["year"] == ages[0] else "")
ax.set_title("Savings, Expenses, and Goal Milestones")
ax.set_xlabel("Age")
ax.set_ylabel("INR")
ax.legend()
st.pyplot(fig)

# st.subheader("Income Breakdown")
# labels = ["Gross Income", "Income Tax", "GST", "Net Savings"]
# values = [annual_income, annual_tax, df_projection["Annual GST Paid"].iloc[0], df_projection["Annual Savings"].iloc[0]]
# fig, ax = plt.subplots()
# ax.pie(values, labels=labels, autopct='%1.1f%%', startangle=90)
# st.pyplot(fig)
