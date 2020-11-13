from tkinter import *
import mysql.connector
import atest

window=Tk()
window.geometry("470x700")
window.title("Automatic Shopping Cart")
window.configure(background="")

# global op, op2, lb4, lb5, frame_left
mydb = mysql.connector.connect(host = 'localhost', user = 'root', password = '', database = 'automatic_shopping_cart')
mycursor = mydb.cursor()


sql = 'SELECT * FROM login;'

mycursor.execute(sql)

result = mycursor.fetchall()
for values in result:
    username = values[0]
    password = values[1]

    print(username)
    print(password)


backgroundImage = PhotoImage(file = "bgimglogin2.gif")

label = Label(master=window,
          image = backgroundImage,
          text='This is a test ',
          height = 2
          )
label.place(x=0, y=0, relwidth=1, relheight=1)

frame_left = Frame(window,bg="LightBlue1")
frame_left.grid(row=3,column=0,padx=55,pady=220)
lb1=Label(frame_left,text="USERNAME",font="times 10 bold", fg="Black",  bd=4, bg="White",)
lb1.grid(row=0,column=0,padx=20,pady=20)
e1=Entry(frame_left,width=30)
e1.grid(row=0,column=1,padx=20,pady=20)
# print(username1)

lb2=Label(frame_left,text="PASSWORD",font="times 10 bold", fg="Black",   bd=4, bg="White",)
lb2.grid(row=1,column=0,padx=20,pady=20)
e2=Entry(frame_left,width=30,)
e2.grid(row=1,column=1,padx=20,pady=20)
# print(password1)



# global op2

def login():
    username1 = e1.get()
    password1 = e2.get()

    if ((username == username1) and (password == password1)):
        # print('login successful')
        op = "Login successful"
        lb4=Label(frame_left,text=op,font="times 10 bold", fg="Black",   bd=4, bg="White",)
        lb4.grid(row=4,column=0,columnspan=2,padx=20,pady=20)
        atest.cart()

    else:
        op2 = "Wrong Credentials"
        lb4=Label(frame_left,text=op2,font="times 10 bold", fg="Black",   bd=4, bg="White",)
        lb4.grid(row=4,column=0,columnspan=2,padx=20,pady=20)
        # print("wrong credentials")

bt1=Button(frame_left, text="LOGIN",width=42, fg="Black", padx=5, pady=5,  bd=4, bg="Light green",command = login)
bt1.grid(row=3,column=0,columnspan=2,padx=20,pady=20)

window.mainloop()