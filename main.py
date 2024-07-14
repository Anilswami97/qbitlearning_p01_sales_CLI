"""
Main.py: Business logic
======
- This file provides all the basic to advance functionlities to CRM CLI s/w.
"""

import os
import uuid 
import string 
import sqlite3
import numpy as np 
import pandas as pd 
import plotly.offline as py
from datetime import datetime
import plotly.graph_objs as go
from __init__ import create_db
from plotly.subplots import make_subplots



# File Handling
def to_csv(df, path):
    df.to_csv(path, index=False)


def read_csv(path):
    return pd.read_csv(path)


# Data Preprocessing
def generate_leads():
    leads_no = np.random.randint(10, 50)
    numbers = [int("".join(np.random.choice(list(string.digits), 10))) for _ in range(leads_no)]
    names = ["".join(np.random.choice(list(string.ascii_letters), 7)).strip() for _ in range(leads_no)]
    status = [0]*leads_no
    result = ["Unhandled"]*leads_no

    df = pd.DataFrame({"Name":names, "Number":numbers, "Status":status, "Result":result})


    df.to_csv("leads.csv", index=False)

    return True


def load_data():
    df = read_csv('sales.csv')
    handled_leads = df.loc[df['lead_status'] == 1]
    unhandled_leads = df.loc[df['lead_status'] == 0]
    return df, handled_leads, unhandled_leads


def get_data(bda_id):
    return cursor.execute("SELECT * FROM sales WHERE bda_id = ?",(bda_id,)).fetchall()


# Database Interaction
def upload_to_db(bda_id):
    df = read_csv("sales.csv")

    values = [(row['lead_result'], row['lead_status'], row['id'], bda_id) for _, row in df.iterrows()]

    conn = sqlite3.connect("crm.db")
    cursor = conn.cursor()

    cursor.executemany("UPDATE sales SET lead_result =  ?, lead_status = ? WHERE id = ? AND bda_id = ?", values)
    conn.commit()
    conn.close()


def payouts(util_args):
    cursor = util_args.get("cursor")
    bda_id = util_args.get("bda_id")
    rate = util_args.get("rate")

    sales_data = cursor.execute("SELECT lead_result, lead_status FROM sales WHERE bda_id = \'{}\'".format(bda_id)).fetchall()
    salary_status = cursor.execute("SELECT remarks FROM bda_payouts WHERE bda_id = ?", (bda_id,)).fetchone()[0]

    sales_df = pd.DataFrame({
        "lead_result" : [i[0] for i in sales_data],
        "lead_status" : [i[1] for i in sales_data]
    })

    data = sales_df['lead_result'].value_counts()

    print()
    print("+=====================+============================+")
    print("               Payout Details")
    print("+=====================+============================+")
    print()
    print("Here is the Work Done by You: ")
    print("---------------------------------------")
    print("Total Leads: ", len(sales_df))
    print("Total Handled Leads: ", len(sales_df.loc[sales_df['lead_status'] == '1']))
    print("Total Converted Leads: ", data.get('Interested', 0))
    print("Total Unconverted Leads: ", data.get('Not Interested', 0))
    print("Total Call Back Again Leads: ", data.get("Call Back Later", 0) + data.get("Did Not Pick", 0))
    print("Total Spam Leads: ", data.get('Wrong Number/Spam', 0))
    print("---------------------------------------")
    total_amount = rate * data.get('Interested', 0)
    print(f"Total Amount 2000 * {data.get('Interested', 0)} : {total_amount} Rs.")
    print("#===================================================#")
    if salary_status == "Unpaid":
        print("NOTE: HANDLE ALL THE LEADS, AND PAYMENT WILL FOLLOW.")
    else:
        input("Press enter to check your Salary Status... ")
        print(f"Salary Status: {salary_status}")
        
    print()
    input("Press enter to Continue... ")
    clear_scr()
    return total_amount


# Utility methods
def choose_role():
    print("+--------------------------------+")
    while True:
        print()
        print("1. Already a User?")
        print("2. New User?")
        print("0. Exit")
        print()
        print("------------------------")
        try:
            option = int(input("Choose an option > "))
            if option not in (0, 1, 2):
                print("Invalid option. Please try again.")
            
            elif option == 0:
                print("Thank you for using our CRM system.")
                clear_scr()
                exit()

            else:
                return option
            
        except Exception:
            print("Invalid input. Please try again!")


def create_bda(cursor):
    id = str(uuid.uuid4())

    def is_unique(column, value):
        cursor.execute(f"SELECT 1 FROM bda WHERE {column} = ?", (value,))
        return cursor.fetchone() is None

    while True:
        name = input("Enter your name:")
        if is_unique("name", name):
            break
        else:
            print("this name already taken.")
            print()
    
    while True:
        mobile = input("Phone no.: ")
        if is_unique("mobile", mobile):
            break
        else:
            print("this phone no. already taken.")
            print()
    
    while True:
        email = input("Email ID: ")
        if is_unique("email", email):
            break
        else:
            print("this email already taken.")
            print()

    cursor.execute("INSERT INTO bda VALUES (?, ?, ?, ?)", (id, name, mobile, email))
    conn.commit()
    cursor.execute("INSERT INTO bda_payouts VALUES(?, ?, ?, ?, ?)", (str(uuid.uuid4())[:6], id, "00-00-0000 00:00", "Unpaid", 0))
    conn.commit()

    return id, name 


def assign_leads_to_bda(bda_id):
    generate_leads()
    df = pd.read_csv("leads.csv")

    values = [(str(uuid.uuid4())[:8], bda_id, row["Name"], row["Number"], row["Result"], row["Status"], datetime.now().strftime("%d %b %Y  %H:%M")) for _, row in df.iterrows()]

    cursor.executemany("INSERT INTO sales VALUES(?, ?, ?, ?, ?, ?, ?)", values)
    conn.commit()

    os.remove("leads.csv")
    
    print("--------------------------")
    print("We've assigned some leads to you. You can start working on them now.")
    print()
    input("Press Enter to continue...")
    clear_scr()


def visualize(util_args):
    try:
        # Load data and get the count of each lead result
        data, _, _= load_data()
        data= data['lead_result'].value_counts()

    except Exception:
        # raise an error if data loading fails
        raise ValueError("Error druing loading the data") 

    # Extract labels and values for the charts
    labels, values = (data.index.to_list(), data.to_list())

    # Create a Pie chart
    pie = go.Pie(
        labels=labels,
        values=values,
        text=labels,
        hole = 0.2,
        name = "Pie Chart",
        showlegend=True,
        hovertemplate='<b>%{label}</b><br>Leads: %{value}<extra></extra>'
    )

    # Create a Bar chart
    colors = ['#636EFA', '#FFA15A', '#AB63FA',  '#00CC96', '#EF553B', '#34c7c4']
    bar = go.Bar(
        x=labels,
        y=values,
        marker = dict(color = colors[:len(labels)]),
        name="Bar Plot",
        showlegend=True,
        hovertemplate='<b>%{x}</b><br>Leads: %{y}<extra></extra>',
    )

    # Create a subplot layout with a Pie chart and a Bar chart
    fig = make_subplots(rows=1, cols=2, specs=[[{'type': 'domain'}, {'type': 'xy'}]], subplot_titles=("Pie Chart", "Bar Plot"))

    # Add the Pie chart to the first column
    fig.add_trace(pie, row=1, col=1)
    # Add the Bar chart to the second column
    fig.add_trace(bar, row=1, col=2)

    fig.update_layout(
        title_text=f"Visualization of Leads Assigned to '{util_args.get("name")}'", 
        template = "plotly_dark", 
    )

    # Render the plot
    py.plot(fig)


def login(cursor):
    while True:
        print()

        print("------------------------")
        print('--- Enter ".exit" to exit ---')
        username = input("Enter Username: ")
        if username == ".exit":
            exit()   # Exit the program if the user enters ".exit"

        print("------------------------------------")
        try:
            # Query the database for the entered username
            result = cursor.execute("SELECT * FROM bda WHERE name = ?",(username,)).fetchone()

            if result:
                # If username is found, return their ID and name
                print(f"Welcome '{username}' to the CRM Panel.")
                print()
                input("Press Enter to continue...")
                clear_scr()    # Clear the screen for better User-Experience(UX)
                return result[0], result[1]  # return bda_id, and name

            else:
                # If username is not found, prompt the user to try again
                print("Username not found. Please try again.")
                print()
                continue

        # Handling any unexpected errors during the database query
        except Exception:
            raise ValueError("An Unexpected Error occurred. Please try again.")

 
def display_menu(handled_leads, unhandled_leads, util_args):
    # Display Menu options
    print()
    print("+------------------------------------------------------+")
    print(f'Username: {util_args.get("name")}           User ID: {util_args.get("bda_id")}')
    print()
    print("1. Handle Next Lead.")
    print("2. Show Handled Leads.")
    print("3. Show Unhandled Leads")
    print("4. Payouts")
    print("5. Visualize Your Work")
    print("0. Exit")
    print()
    # Show the counts of handled and unhandled leads.
    print(f"Handled Leads: {len(handled_leads)}    Unhandled Leads: {len(unhandled_leads)}")
    print("+---------------------------------------------------+")


def display_leads(status):
    # Load data and split into handled and unhandled leads
    _, handled_leads, unhandled_leads = load_data()
    print()
    if status == 1:            # If status is 1, display handled Leads
        if len(handled_leads) != 0:
            print("#===============================================#")
            print("|   Name    |   Phone no.   |   Result   |")
            print("#===============================================#")
            for _, row in handled_leads.iterrows():
                print(f'|  {row["lead_name"]}  |  {row["lead_mobile"]}   | {row["lead_result"]}  |')
                print("+-----------------------------------------------+")
        else:
            print()
            print("No handled leads found.")
            print()

    # Otherwise, display unhandled Leads
    else:
        if len(unhandled_leads) != 0:
            print("#===============================================#")
            print("|   Name    |   Phone no.   |   Result   |")
            print("#===============================================#")
            for _, row in unhandled_leads.iterrows():
                print(f'|  {row["lead_name"]}  |  {row["lead_mobile"]}   | {row["lead_result"]}  |')
                print("+-----------------------------------------------+")
        else:
            print()
            print("No unhandled leads found.")
            print()

    print()
    input("Press Enter to continue...")
    clear_scr()

    print()


def handle_next_lead(unhandled_leads, util_args):
    cursor = util_args.get("cursor")

    # Check if there are any unhandled leads
    if len(unhandled_leads) == 0:
        print()
        print("No more Unhandled Leads! Thank you for your work!")
        return

    else:
        # Select the first unhandled lead
        lead = unhandled_leads.iloc[0]
        print()
        print("#===================================================#")
        print()
        print("----- Make a Call, and Enter the Result -----")
        print()
        print("+-------------------------+")
        print("|    Name   |   Phone no. |")
        print("+-------------------------+")
        print(f'|  {lead["lead_name"]}  |  {lead["lead_mobile"]}  |')
        print("+-------------------------+")
        print()

        while True:
            # Display options for lead result
            print("0. Not Interested")
            print("1. Interested")
            print("2. Call Back Later")
            print("3. Did Not Pick")
            print("4. Wrong Number/Spam")
            print()
            print("        ----- Enter 5 to Skip -----")                   
            print()
            print("#=====================================#")

            try: 
                # Get user input for lead result
                option = int(input("Enter Result Option>"))
                if option not in [0, 1, 2, 3, 4, 5]:
                    print()
                    print("!! Invalid Option !!")
                    print()
                    continue
                
                elif option == 5:
                    print("Skipping...")
                    break
                
                else:
                    # Map input to lead result
                    result_map = {
                        0 : "Not Interested",
                        1 : "Interested",
                        2 : "Call Back Later",
                        3 : "Did Not Pick",
                        4 : "Wrong Number/Spam",
                    }

                    # Update lead result and status in the sales DataFrame
                    sales_df = read_csv("sales.csv")
                    sales_df.loc[sales_df['lead_mobile'] == lead['lead_mobile'], 'lead_result'] = result_map[option]
                    sales_df.loc[sales_df['lead_mobile'] == lead['lead_mobile'], 'lead_status'] = 1

                    print()
                    # Save updated DataFrame back to CSV


                    print("|| SAVED ||")
                    print()
                    input("Press Enter to continue...")


                    # Make Payment when there is no unhandled leads remaining.
                    if len(sales_df.loc[sales_df['lead_result'] == 'Unhandled', 'lead_result']) == 0:
                        update_query = """
                            UPDATE bda_payouts 
                            SET paydate = ?, remarks = ?, amount = ? 
                            WHERE bda_id = ?
                            """
                        
                        cursor.execute(update_query, (datetime.now().strftime("%d %b %Y  %H:%M"), "Salary Paid", util_args.get("total_amount"), util_args.get("bda_id")))
                        conn.commit()

                    to_csv(sales_df, "sales.csv")  # update CSV file to keep tracking which one was handled and which one not.
                    
                    clear_scr()
                    break


            except Exception as e:
                print()
                print("!! Invalid Option. Please choose from the given options !!")
                print()


# Method to Clear the Screen
def clear_scr():
    # Checking for the OS you are using to assign correct value to os.system()
    os.system('cls' if os.name == 'nt' else 'clear')



# Origin of the Entire CLI s/w : Main Function
if __name__ == "__main__":
    if not os.path.exists("crm.db"):
        create_db()
    
    # Connect the SQLite Database
    conn = sqlite3.connect("crm.db")
    cursor = conn.cursor()


    # Determine user role (existing or new user)
    option = choose_role()
    if option == 1:  
        bda_id, name = login(cursor)      # Login for existing user
    else:   
        bda_id, name = create_bda(cursor) # Create a new BDA (Business Development Associate)
        assign_leads_to_bda(bda_id) # assign leads to new BDA

    # Upload CSV data to database if exists (in case when program closed directly without saving)
    if os.path.exists("sales.csv"):
        upload_to_db(bda_id)

    # now retrieve the sales data for the current BDA
    data = get_data(bda_id)

    sales_df = pd.DataFrame({
        "id" : [i[0] for i in data],
        "bda_id" : [i[1] for i in data],
        "lead_name" : [i[2] for i in data],
        "lead_mobile" : [i[3] for i in data],
        "lead_result" : [i[4] for i in data],
        "lead_status" : [i[5] for i in data],
        "lead_date" : [i[6] for i in data],
    })
    to_csv(sales_df, "sales.csv")


    # make a dictionary to store some basic utilities
    util_args = {
        "rate" : 2000,   # price amount per converted lead
        "bda_id" : bda_id,
        "name" : name,
        "cursor" : cursor
    }


    while True:
        
        _, handled_leads, unhandled_leads = load_data()

        util_args['total_amount'] = util_args.get("rate")*len(handled_leads.loc[handled_leads['lead_result'] == 'Interested'])

        display_menu(handled_leads, unhandled_leads, util_args)


        try:
            option = int(input("Choose your Option: "))    

            match(option):
                case 1:
                    handle_next_lead(unhandled_leads, util_args)
                    continue
                
                case 2:
                    display_leads(1)
                    continue

                case 3:
                    display_leads(0)
                    continue
                

                case 4:
                    upload_to_db(bda_id)
                    payouts(util_args)
                    continue
                

                case 5:
                    print("Processing...")
                    visualize(util_args)
                    clear_scr()
                    continue
                
                case 0:
                    if input("Are you sure? (y/n) default y > ").lower() in ('y', ''):
                        upload_to_db(bda_id)
                        os.remove("sales.csv")
                        conn.close()
                        clear_scr()
                        break

                    else:
                        clear_scr()
                        continue
                        
                case _:
                    print()
                    print("!! Invalid Option. Please choose from the given options !!")
                    continue


        except Exception as e:
            print("!! Invalid input, please choose a valid option !!")


