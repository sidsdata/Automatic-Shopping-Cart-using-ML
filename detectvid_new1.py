from tkinter import *
from tkinter import filedialog
from PIL import ImageTk, Image
import time
import mysql.connector
import sys

from absl import app,  flags, logging
from absl.flags import FLAGS
import cv2
import tensorflow as tf
from yolov3_tf2.models import (
    YoloV3, YoloV3Tiny
)
from yolov3_tf2.dataset import transform_images
from yolov3_tf2.utils import draw_outputs
import pdfkit 


# global i 
# pname = ''



class Product:

    def __init__(self, frame_left, row_num, product_id, product, price, index):
        self.frame_left = frame_left
        self.row_num = row_num
        self.product_id = product_id
        self.product = product
        self.price = price
        self.index = index
        self.subtotal = price
        self.qty = 1
        
    def create_row(self):
        print('row created')
        label = {}
        idlabel = Label(self.frame_left, text=self.product_id, width=20)
        idlabel.grid(row=self.row_num, column=0, padx=20, pady=20)
        label[self.product_id] = idlabel

        product_label = Label(self.frame_left, text=self.product, width=20)
        product_label.grid(row=self.row_num, column=1, padx=20, pady=20)
        label[self.product] = product_label

        price_label = Label(self.frame_left, text=self.price, width=20)
        price_label.grid(row=self.row_num, column=2, padx=20, pady=20)
        label[self.price] = price_label

        optionlist = [1,2,3,4,5]
        dropVar = IntVar()
        dropVar.set(self.qty)

        click_adv = OptionMenu(self.frame_left, dropVar, *optionlist, command=self.calc_subtotal)
        click_adv.grid(row=self.row_num, column=3, padx=20,pady=20)

        subtotal_label=Label(self.frame_left, text=self.subtotal, width=20)
        subtotal_label.grid(row=self.row_num, column=4, padx=20, pady=20)




    def calc_subtotal(self, qty):
        self.qty = qty
        self.subtotal = self.price * self.qty
        print("{} : {} * {} = {}".format(self.product, self.price, qty, self.subtotal))
        subtotal_label=Label(self.frame_left, text=self.subtotal, width=20)
        subtotal_label.grid(row=self.row_num, column=4, padx=20, pady=20)
        myshop.cal_total()
        # myshop.printTohtml()

    

class Shop:
    pname = None
    product_id = None
    product = None
    price = 0
    frame_left=None
    products = []
    grand_total = 0.0

    def __init__(self):
        self.grand_total = 0.0
        flags.DEFINE_string('classes', './data/labels/coco.names', 'path to classes file')
        flags.DEFINE_string('weights', './weights/yolov3.tf',
                            'path to weights file')
        flags.DEFINE_boolean('tiny', False, 'yolov3 or yolov3-tiny')
        flags.DEFINE_integer('size', 416, 'resize images to')
        flags.DEFINE_string('video', './data/video/paris.mp4',
                            'path to video file or number for webcam)')
        flags.DEFINE_string('output', None, 'path to output video')
        flags.DEFINE_string('output_format', 'XVID', 'codec used in VideoWriter when saving video to file')
        flags.DEFINE_integer('num_classes', 80, 'number of classes in the model')


    # Open camera and scan for the item
    # If found ? Call dbdata() : continue loop.
    def scanner(self):
        FLAGS(sys.argv)
        self.physical_devices = tf.config.experimental.list_physical_devices('GPU')
        if len(self.physical_devices) > 0:
            tf.config.experimental.set_memory_growth(self.physical_devices[0], True)

        if FLAGS.tiny:
            self.yolo = YoloV3Tiny(classes=FLAGS.num_classes)
        else:
            self.yolo = YoloV3(classes=FLAGS.num_classes)

        self.yolo.load_weights(FLAGS.weights)
        logging.info('weights loaded')

        self.class_names = [c.strip() for c in open(FLAGS.classes).readlines()]
        logging.info('classes loaded')

        times = []

        try:
            self.vid = cv2.VideoCapture((0))
        except:
            self.vid = cv2.VideoCapture(FLAGS.video)

        self.out = None

        if FLAGS.output:
            # by default VideoCapture returns float instead of int
            self.width = int(self.vid.get(cv2.CAP_PROP_FRAME_WIDTH))
            self.height = int(self.vid.get(cv2.CAP_PROP_FRAME_HEIGHT))
            self.fps = int(self.vid.get(cv2.CAP_PROP_FPS))
            self.codec = cv2.VideoWriter_fourcc(*FLAGS.output_format)
            self.out = cv2.VideoWriter(FLAGS.output, self.codec, self.fps, (self.width, self.height))
        self.fps = 0.0
        self.count = 0

        a= True

        while a:
            _, self.img = self.vid.read()

            if self.img is None:
                logging.warning("Empty Frame")
                time.sleep(0.1)
                self.count+=1
                if self.count < 3:
                    continue
                else: 
                    break

            self.img_in = cv2.cvtColor(self.img, cv2.COLOR_BGR2RGB) 
            self.img_in = tf.expand_dims(self.img_in, 0)
            self.img_in = transform_images(self.img_in, FLAGS.size)

            self.t1 = time.time()
            self.boxes, self.scores, self.classes, self.nums = self.yolo.predict(self.img_in)
            
            self.fps  = ( self.fps + (1./(time.time()-self.t1)) ) / 2

            self.img, self.pname = draw_outputs(self.img, (self.boxes, self.scores, self.classes, self.nums), self.class_names)
            pname = self.pname
            print('in main funcion : ', self.pname)
        
            self.img = cv2.putText(self.img, "FPS: {:.2f}".format(self.fps), (0, 30),
                            cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, (0, 0, 255), 2)
                        
            # draw_outputs(img, outputs, class_names)
            if FLAGS.output:
                self.out.write(self.img)

            cv2.namedWindow('Product Scanner')
            cv2.imshow('Product Scanner', self.img)

            if cv2.waitKey(100) &0xFF == ord('e'):
                self.dbdata()
                print('destroying scanner window')
                cv2.destroyWindow('Product Scanner')
                a=False


    # Collect the deails of the product from database
    # Create object of the found product
    # Append to products
    def dbdata(self):
        mydb = mysql.connector.connect(host = 'localhost', user = 'root', password = '', database = 'automatic_shopping_cart')
        mycursor = mydb.cursor()

        print('in db function', self.pname)


        if self.pname:
            sql = 'SELECT * FROM product_info WHERE product = "{}";'.format(self.pname)
            mycursor.execute(sql)
            result = mycursor.fetchall()

            # If product data is found 
            # create an object of the product
            # append to products list
            row = len(self.products) + 1
            for values in result:
                product_id = values[0]
                product = values[1]
                price = values[2]
                self.products.append(Product(self.frame_left, row, product_id, product, price, row-1))

        self.windows_body()

        
    # Draw main window
    def cart(self):
        window = Tk()
        window.title("Automatic Billing System")
        window.configure(background="black")
        window.geometry("1200x750")
        canvas=Canvas(window,width=1200,height=700)
        bimg = Image.open("bgimg.jpg")
        bimg = bimg.resize((1200, 700), Image.ANTIALIAS)
        bimg=ImageTk.PhotoImage(bimg)
        canvas.create_image(0,0,anchor=NW,image=bimg)
        canvas.pack()

        button1 = Button(window, text="Product Scanner ", fg="Black", padx=5, pady=5,  bd=4, bg="Light green", command = self.scanner)
        button1.place(x=500, y=75)
        button1.config(font=("Courier", 12))

        self.frame_left = Frame(window,bg="LightBlue1")
        self.frame_left.place(x=60, y=150)
        
        # 
        self.windows_body()

        window.mainloop()

    def windows_body(self):
        # table headings
        lb1=Label(self.frame_left,text="PRODUCT ID",font="times 10 bold")
        lb1.grid(row=0,column=0,padx=20,pady=20)

        lb2=Label(self.frame_left,text="PRODUCT",font="times 10 bold")
        lb2.grid(row=0,column=1,padx=20,pady=20)

        lb3=Label(self.frame_left,text="PRICE",font="times 10 bold")
        lb3.grid(row=0,column=2,padx=20,pady=20)

        lb4=Label(self.frame_left,text="QUANTITY",font="times 10 bold")
        lb4.grid(row=0,column=3,padx=20,pady=20)
        
        lb5=Label(self.frame_left,text="SUBTOTAL",font="times 10 bold")
        lb5.grid(row=0,column=4,padx=20,pady=20)

        # product listing
        self.list_products()

        # bt1=Button(self.frame_left, text="DELETE",width=10,bg="red", fg="white", bd=4)
        # bt1.grid(row=len(self.products)+1,column=5,padx=20,pady=20,sticky=W)

        lb6=Label(self.frame_left,text="TOTAL:",font="times 10 bold")
        lb6.grid(row=7,column=4,padx=20,pady=20,sticky=E)
        
        
       

        bt1=Button(self.frame_left, text="PRINT BILL",width=30, bd=4,bg="burlywood2",command = self.printTohtml)
        bt1.grid(row=8,column=5,padx=50,pady=70)

        # Product.
    # List all the products in the list products
    def list_products(self):
        print('products')
        for product in self.products:
            product.create_row()
            print(product.row_num, product.product_id, product.product, product.price, product.index, sep=" - ")
        
    # grand total of products
    def cal_total(self):
        self.grand_total = 0.0
        if len(self.products) > 0 :
            for product in self.products:
                self.grand_total = self.grand_total + product.subtotal
        else :
            self.grand_total = 0.0
        print('rang total', self.grand_total)
        total_label=Label(self.frame_left,text = self.grand_total,width=10)
        total_label.grid(row=7,column=5,padx=20,pady=20,sticky=W)


    def printTohtml(self):
        myfile = open('pythonop.html', 'w')

        title = "Automatic Shopping Cart"
        heading =  """<html>
            <head><h1 style = "text-align:center">{htmlText1}</h1></head>
            <body>"""

        row1 = '''<table style="margin-left:auto;margin-right:auto;padding:20px">
                    <tr style= "padding:20px">
                        <th style= "padding:20px">Product Id</th>
                        <th style= "padding:20px">Product</th> 
                        <th style= "padding:20px">Price</th>
                        <th style= "padding:20px">Qty</th>
                        <th style= "padding:20px">Sub Total</th>
                    </tr>'''
                        
        

        footer = '''</table><br><br>
            <h3 style="text-align:center"> Total {grand_total} Rs </h3>
            </body>
            </html>'''
        myfile.write(heading.format(htmlText1 = title))
        myfile.write(row1.format())
        row2=""""""

        for product in self.products:
            row22 =          '''<tr style= "padding:20px" >
                        <td style= "padding:20px">{product_id}  </td>
                        <td style= "padding:20px">{product} </td> 
                        <td style= "padding:20px">{price}  </td>
                        <td style= "padding:20px">{qty}  </td>
                        <td style= "padding:20px">{subtotal} Rs </td>
                    </tr>
            '''.format( product_id=product.product_id, product=product.product, price=product.price, qty= product.qty, subtotal=product.subtotal)
            row2= row2+row22

        myfile.write(row2)
        myfile.write(footer.format(grand_total = self.grand_total))
        myfile.close()    

        pdfkit.from_file('pythonop.html', 'bill.pdf') 

if __name__ == '__main__':
    myshop = Shop()
    myshop.cart()



