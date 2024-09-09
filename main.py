import datetime
from tkinter import *
import tkinter.messagebox as mb
import tkinter.ttk as ttk
import tkinter as tk
from tkcalendar import DateEntry
from pymongo import MongoClient
from bson import ObjectId


# Connect to MongoDB
client = MongoClient('mongodb+srv://gadhesaurabh74:Dkkvn487xvdiTuvz@expense.65hxyyp.mongodb.net/?retryWrites=true&w=majority&appName=expense')
db = client['expense_tracker']
collection = db['expenses']

# Functions
def list_all_expenses():
    table.delete(*table.get_children())
    for expense in collection.find():
        expenditure_date = datetime.datetime.strptime(expense['Date'], '%Y-%m-%d').date()
        table.insert('', END, values=(expense['_id'], expenditure_date.strftime('%m/%d/%y'), expense['Payee'], expense['Description'], expense['Amount'], expense['ModeOfPayment']))

def view_expense_details():
    global table, date, payee, desc, amnt, MoP

    if not table.selection():
        mb.showerror('No expense selected', 'Please select an expense from the table to view its details')
        return

    current_selected_expense = table.item(table.focus())
    values = current_selected_expense['values']

    expenditure_date = datetime.datetime.strptime(values[1], '%m/%d/%y').date()

    date.set_date(expenditure_date)
    payee.set(values[2])
    desc.set(values[3])
    amnt.set(values[4])
    MoP.set(values[5])

def clear_fields():
    global desc, payee, amnt, MoP, date, table

    today_date = datetime.datetime.now().date()

    desc.set('')
    payee.set('')
    amnt.set(0.0)
    MoP.set('Cash')
    date.set_date(today_date)
    table.selection_remove(*table.selection())

def remove_expense():
    if not table.selection():
        mb.showerror('No record selected!', 'Please select a record to delete!')
        return

    current_selected_expense = table.item(table.focus())
    expense_id = current_selected_expense['values'][0]

    surety = mb.askyesno('Are you sure?', f'Are you sure that you want to delete the record of ID: {expense_id}?')

    if surety:
        try:
            result = collection.delete_one({'_id': ObjectId(expense_id)})  # Assuming 'ObjectId' is used for MongoDB
            if result.deleted_count == 1:
                mb.showinfo('Record deleted successfully!', f'The record with ID: {expense_id} has been deleted successfully')
                list_all_expenses()
            else:
                mb.showerror('Deletion Error', f'No record found with ID: {expense_id}.')
        except Exception as e:
            mb.showerror('Error', f'An error occurred while deleting the record: {str(e)}')
    else:
        mb.showinfo('Deletion Cancelled', f'Deletion of record with ID: {expense_id} cancelled by user')


def remove_all_expenses():
    surety = mb.askyesno('Are you sure?', 'Are you sure that you want to delete all the expense items from the database?', icon='warning')

    if surety:
        collection.delete_many({})
        clear_fields()
        list_all_expenses()
        mb.showinfo('All Expenses deleted', 'All the expenses were successfully deleted')
    else:
        mb.showinfo('Ok then', 'The task was aborted and no expense was deleted!')

def add_another_expense():
    global date, payee, desc, amnt, MoP

    if not date.get() or not payee.get() or not desc.get() or not amnt.get() or not MoP.get():
        mb.showerror('Fields empty!', "Please fill all the missing fields before pressing the add button!")
        return

    expense = {
        'Date': date.get_date().strftime('%Y-%m-%d'),
        'Payee': payee.get(),
        'Description': desc.get(),
        'Amount': amnt.get(),
        'ModeOfPayment': MoP.get()
    }

    collection.insert_one(expense)

    clear_fields()
    list_all_expenses()
    mb.showinfo('Expense added', 'The expense whose details you just entered has been added to the database')

edit_btn = None  
btn_font = ('Helvetica', 9)
hlb_btn_bg='blue'

def edit_expense():
    global table
    
    def edit_existing_expense():
        global date, amnt, desc, payee, MoP, collection
        
        if not table.selection():
            mb.showerror('No expense selected!', 'You have not selected any expense in the table for us to edit; please do that!')
            return
        
        current_selected_expense = table.item(table.focus())
        contents = current_selected_expense['values']
        expense_id = contents[0]  
        
        updated_expense = {
            'Payee': payee.get(),
            'Description': desc.get(),
            'Amount': amnt.get(),
            'ModeOfPayment': MoP.get()
        }

        try:
            
            result = collection.update_one({'_id': ObjectId(expense_id)}, {'$set': updated_expense})
            if result.modified_count == 1:
                clear_fields()  
                list_all_expenses()  
                mb.showinfo('Data edited', 'Expense successfully updated')
                edit_btn.destroy()  
            else:
                mb.showerror('Edit Error', 'Failed to edit the expense.')
        except Exception as e:
            mb.showerror('Error', f'An error occurred while editing the expense: {str(e)}')

   
    if not table.selection():
        mb.showerror('No expense selected!', 'You have not selected any expense in the table for us to edit; please do that!')
        return

    view_expense_details()  
    edit_btn = Button(data_entry_frame, text='Edit expense', command=edit_existing_expense,width=20,height=2,font=('Helvetica', 9,'bold'),bg='blue',fg='white')
    edit_btn.place(x=70, y=470)  

def selected_expense_to_words():
  global table
  if not table.selection():
     mb.showerror('No expense selected!', 'Please select an expense from the table for us to read')
     return
  current_selected_expense = table.item(table.focus())
  values = current_selected_expense['values']
  message = f'Your expense can be read like: \n"You paid {values[4]} to {values[2]} for {values[3]} on {values[1]} via {values[5]}"'
  mb.showinfo('Here\'s how to read your expense', message)



root = Tk()
root.title('Expense Tracker')
root.geometry('1200x550')
root.resizable(0, 0)
root.configure(bg="light blue")

desc = StringVar()
amnt = DoubleVar()
payee = StringVar()
MoP = StringVar(value='Cash')


data_entry_frame = Frame(root,bg="light blue",width=30,height=2)
data_entry_frame.place(x=0, y=30, relheight=0.95, relwidth=0.25)

buttons_frame = Frame(root,bg="light blue",width=30,height=2)
buttons_frame.place(relx=0.25, rely=0.05, relwidth=0.75, relheight=0.21)

tree_frame = Frame(root,bg="light blue",width=30,height=2)
tree_frame.place(relx=0.25, rely=0.26, relwidth=0.75, relheight=0.74)

def create_highlighted_frame(parent, x, y, width, height):
    frame = tk.Frame(parent, bg="dark blue", highlightbackground="dark blue", highlightthickness=2)
    frame.place(x=x, y=y, width=width, height=height)
    return frame


frame_date = create_highlighted_frame(data_entry_frame, x=10, y=5, width=380, height=70)

tk.Label(frame_date, text='Date (M/DD/YY) :', font=('Helvetica', 9), bg="light blue",width=26).grid(row=0, column=0, pady=(5, 5),padx=(50,0), sticky='w')
date = DateEntry(frame_date, date=datetime.datetime.now().date(), font=('Helvetica', 12))
date.grid(row=1, column=0, pady=(5, 0),padx=(50,0))


frame_payee = create_highlighted_frame(data_entry_frame, x=10, y=95, width=380, height=70)

tk.Label(frame_payee, text='Payee\t:', font=('Helvetica', 9), bg="light blue",width=26).grid(row=0, column=0, pady=(5, 0),padx=(50,0), sticky='w')
tk.Entry(frame_payee, textvariable=payee, font=('Helvetica', 15)).grid(row=1, column=0, pady=(5, 0),padx=(32,0))


frame_desc = create_highlighted_frame(data_entry_frame, x=10, y=185, width=380, height=70)

tk.Label(frame_desc, text='Description:', font=('Helvetica', 9), bg="light blue",width=26).grid(row=0, column=0, pady=(5, 0),padx=(50,0), sticky='w')
tk.Entry(frame_desc, textvariable=desc, font=('Helvetica', 15)).grid(row=1, column=0, pady=(5, 0),padx=(32,0))


frame_amount = create_highlighted_frame(data_entry_frame, x=10, y=280, width=380, height=70)

tk.Label(frame_amount, text='Amount\t:', font=('Helvetica', 9), bg="light blue",width=26).grid(row=0, column=0, pady=(5, 0),padx=(50,0), sticky='w')
tk.Entry(frame_amount, textvariable=amnt, font=('Helvetica', 12)).grid(row=1, column=0, pady=(5, 0),padx=(50,0))

frame_mop = create_highlighted_frame(data_entry_frame, x=10, y=375, width=380, height=70)

tk.Label(frame_mop, text='Mode of Payment:', font=('Helvetica', 9), bg="light blue",width=26).grid(row=0, column=0, pady=(5, 0),padx=(50,0), sticky='w')
ttk.OptionMenu(frame_mop, MoP, *['Cash', 'Cheque', 'Credit Card', 'Debit Card', 'Paytm', 'Google Pay', 'Razorpay']).grid(row=1, column=0, pady=(5, 0),padx=(50,0))


Button(data_entry_frame, text='Add expense', command=add_another_expense,width=20,height=2,font=('Helvetica', 9,'bold'),bg='blue',fg='white').place(x=70, y=470)

Button(buttons_frame, text='Delete Expense', command=remove_expense,width=30,height=2,font=('Helvetica', 9,'bold'),bg='blue',fg='white').place(x=30, y=5)
Button(buttons_frame, text='Clear Fields in DataEntry Frame', command=clear_fields,width=30,height=2,font=('Helvetica', 9,'bold'),bg='blue',fg='white').place(x=335, y=5)
Button(buttons_frame, text='Delete All Expenses', command=remove_all_expenses,width=30,height=2,font=('Helvetica', 9,'bold'),bg='blue',fg='white').place(x=640, y=5)
Button(buttons_frame, text='View Selected Expense\'s Details', command=view_expense_details,width=30,height=2,font=('Helvetica', 9,'bold'),bg='blue',fg='white').place(x=30, y=65)
Button(buttons_frame, text='Edit Selected Expense', command=edit_expense,width=30,height=2,font=('Helvetica', 9,'bold'),bg='blue',fg='white').place(x=335, y=65)
Button(buttons_frame, text='Convert Expense to a sentence',command=selected_expense_to_words,width=30,height=2,font=('Helvetica', 9,'bold'),bg='blue',fg='white').place(x=640, y=65)

table = ttk.Treeview(tree_frame, selectmode=BROWSE, columns=('ID', 'Date', 'Payee', 'Description', 'Amount', 'Mode of Payment'))
X_Scroller = Scrollbar(table, orient=HORIZONTAL, command=table.xview)
Y_Scroller = Scrollbar(table, orient=VERTICAL, command=table.yview)
X_Scroller.pack(side=BOTTOM, fill=X)
Y_Scroller.pack(side=RIGHT, fill=Y)
table.config(yscrollcommand=Y_Scroller.set, xscrollcommand=X_Scroller.set)

table.heading('ID', text='S No.', anchor=CENTER)
table.heading('Date', text='Date', anchor=CENTER)
table.heading('Payee', text='Payee', anchor=CENTER)
table.heading('Description', text='Description', anchor=CENTER)
table.heading('Amount', text='Amount', anchor=CENTER)
table.heading('Mode of Payment', text='Mode of Payment', anchor=CENTER)

table.column('#0', width=0, stretch=NO)
table.column('#1', width=50, stretch=NO)
table.column('#2', width=95, stretch=NO)  
table.column('#3', width=150, stretch=NO)  
table.column('#4', width=325, stretch=NO)  
table.column('#5', width=135, stretch=NO)  
table.column('#6', width=125, stretch=NO)  
table.place(relx=0, y=0, relheight=1, relwidth=1)

list_all_expenses()
root.mainloop()
