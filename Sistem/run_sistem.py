import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import cv2
import os
from PIL import Image
import numpy as np
from datetime import datetime
import time
import mysql.connector
import csv

#################### Fungsi Clear ######################
def clear():
    txt.delete(0, 'end')

def clear2():
    txt2.delete(0, 'end')

############################ Tanggal ##################
ts = time.time()
date = datetime.fromtimestamp(ts).strftime('%d-%m-%Y')
day, month, year = date.split("-")

mont = {'01':'Januari',
        '02':'Febuari',
        '03':'Maret',
        '04':'April',
        '05':'Mei',
        '06':'Juni',
        '07':'Juli',
        '08':'Agustus',
        '09':'September',
        '10':'Oktober',
        '11':'November',
        '12':'Desember'
       }

############################### Fungsi CLock #####################
def clk():
    time_string = time.strftime('%H:%M:%S')
    clock.config(text=time_string)
    clock.after(200,clk)

    
############################## Fungsi Absensi ##########################

def markAttendance(name, nim, status) :
    ts = time.time()
    date = datetime.fromtimestamp(ts).strftime('%d-%m-%Y')
    with open('Absen_'+date+'.csv','r+') as f :
        myDataList = f.readlines()
        nameList = []
        nimList = []
        statusList = []
            
        for line in myDataList :
            entry = line.split(',')
            nameList.append(entry[0])
        if name not in nameList :
            nimList.append(entry[0])
            statusList.append(entry[0])
            ts = time.time()
            date = datetime.fromtimestamp(ts).strftime('%d-%m-%Y')
            day, month, year = date.split("-")

            mont = {'01':'Januari',
                    '02':'Febuari',
                    '03':'Maret',
                    '04':'April',
                    '05':'Mei',
                    '06':'Juni',
                    '07':'Juli',
                    '08':'Agustus',
                    '09':'September',
                    '10':'Oktober',
                    '11':'Novemver',
                    '12':'Desember'
                    }
            now = datetime.now()
            dtString = now.strftime('%H:%M:%S')
            f.writelines(f'\n{name}, {nim}, {status}, {day+"-"+mont[month]+"-"+year}, {dtString}')
            # kalau \n dihilangin akan menyebabkan error
            
############################# Training - Face Recognition ##########################

def train_classifier():
    data_dir = "DataSet"
    path = [os.path.join(data_dir, f) for f in os.listdir(data_dir)]
    
    faces = []
    ids = []
    
    for image in path:
        img = Image.open(image).convert('L')
        imageNp = np.array(img, 'uint8')
        id = int(os.path.split(image)[1].split(".")[1])
        
        faces.append(imageNp)
        ids.append(id)
        
    ids = np.array(ids)
    
    # Train and save classifier
    clf = cv2.face.LBPHFaceRecognizer_create()
    clf.train(faces,ids)
    clf.write("training.xml")
    messagebox.showinfo("Jendela", "Data Telah Berhasil Anda Dilatih")
    
    

############################# Detect - Face Recognition ##########################

def detect_face():
    
    head = [str('Nama'), str('NIM'), str('Status'), str('Tanggal'), str('Jam')]
    ts = time.time()
    date = datetime.fromtimestamp(ts).strftime('%d-%m-%Y')
    exists = os.path.isfile('Absen_'+date+'.csv')

    if exists is False:
        with open('Absen_'+date+'.csv','a+') as csvFile1:
            writer=csv.writer(csvFile1)
            writer.writerow(head)
        csvFile1.close()
    else : 
        None
    
    i=0
    #camera = 0
    #video = cv2.VideoCapture('http://192.168.37.124:4747/mjpegfeed')
    video = cv2.VideoCapture(1)
    
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    recognizer.read('training.xml')
    faceDetect = cv2.CascadeClassifier("data/haarcascade_frontalface_default.xml")
    a = 0
    fontFace = cv2.FONT_HERSHEY_SIMPLEX
    fontScale = 1
    fontColor = (255,255,255)
    Thickness = 2
    
    while True :
        a = a+1
        check, frame = video.read()
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = faceDetect.detectMultiScale(gray, 1.3, 5)
        for (x,y,w,h) in faces :
            cv2.rectangle(frame, (x,y), (x+w, y+h), (0,255,0),2)
            id, distance = recognizer.predict(gray[y:y+h,x:x+w])
            
            mydb=mysql.connector.connect(
            host = "localhost",
            user = "root",
            password = "",
            database = "rincian_user"
            ) 
            mycursor= mydb.cursor()
            mycursor.execute("select Nama from my_table where id="+str(id))
            s = mycursor.fetchone()
            s = ''+''.join(s)
            mycursor_1= mydb.cursor()
            mycursor_1.execute("select NIM from my_table where id="+str(id))
            s_1 = mycursor.fetchone()
            s_1 = ''+''.join(s_1)
            mycursor_2= mydb.cursor()
            mycursor_2.execute("select Status from my_table where id="+str(id))
            s_2 = mycursor.fetchone()
            s_2 = ''+''.join(s_2)
            #(1,20)
            #(1,470)
            cv2.putText(frame,"Similarity"+":"+str(distance), (1,470), cv2.FONT_HERSHEY_SIMPLEX, 0.5,(255,255,255),1)

            if (distance<=50):
                cv2.putText(frame,s,(x,y+h),fontFace,fontScale,fontColor,Thickness)
                markAttendance(s,s_1,s_2)
            else :
                cv2.putText(frame,"Tidak Diketahui",(x,y+h),fontFace,fontScale,fontColor, Thickness)
            
        
        cv2.imshow("wajah",frame)
        if (cv2.waitKey(1)==ord('q')):
            break
            
    with open("Absen_"+date+".csv",'r') as csvFile2 :
        reader = csv.reader(csvFile2)
    
        for lines in reader:
            i = i+1
            if (i > 1):
                tv.insert('',0,values=lines)

    video.release()
    cv2.destroyAllWindows()

############################# Generate - Face Recognition ##########################

def generate_dataset():
    if var.get()==1:
        s1="Mahasiswa"
    elif var.get()==2:
        s1="Dosen"
    elif var.get()==3:
        s1="Karyawan"
    else:
        s1=""
    
    if (txt.get()=="" or txt2.get()=="" or s1==""):
        messagebox.showinfo("Hasil", "Tolong lengkapi data diri anda")
    else :
        mydb = mysql.connector.connect(
        host = "localhost",
        user = "root",
        password = "",
        database = "rincian_user"
        )
        mycursor = mydb.cursor()
        mycursor.execute("SELECT * FROM my_table")
        myresult = mycursor.fetchall()
        id = 1
        for x in myresult :
            id+=1
        sql = "INSERT INTO my_table(id, Nama, NIM, Status) values(%s,%s,%s,%s)"
        val = (id, txt.get(), txt2.get(), s1)
        mycursor.execute(sql, val)
        mydb.commit()
        
        #camera = 0
        #cam =cv2.VideoCapture('http://192.168.37.124:4747/mjpegfeed')
        cam =cv2.VideoCapture(1)
        a = 0
        face_classifier = cv2.CascadeClassifier('data/haarcascade_frontalface_default.xml')

        while True :
            check, frame = cam.read()
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            face = face_classifier.detectMultiScale(gray, scaleFactor=1.3, minNeighbors = 5)
            for (x,y,w,h) in face :
                a = a+1
                cv2.imwrite("DataSet/User."+str(id)+"."+str(a)+".jpg", gray[y:y+h,x:x+w])
                cv2.rectangle(frame, (x,y), (x+w,y+h), (0,255,0), thickness = 2)
            
            

            cv2.imshow('tangkap wajah', frame)
            key = cv2.waitKey(1)
            if key == ord('q') or int(a) == 200 :
                break

        cam.release()
        cv2.destroyAllWindows()
        messagebox.showinfo("Jendela", "Data Anda Telah Berhasil Diinput")


############################## GUI Front-End ###########################

window = tk.Tk()
window.geometry("1280x720")
window.resizable(True, False)
window.title("My System")
window.configure(background = "#101C21")

frame1 = tk.Frame(window, bg = "#546EBE")
frame1.place(relx=0.11, rely=0.17, relwidth=0.39, relheight=0.80)

frame2 = tk.Frame(window, bg = "#546EBE")
frame2.place(relx=0.51, rely=0.17, relwidth=0.38, relheight=0.80)

header1 = tk.Label(window, text = "Sistem Absensi Berbasis Wajah", fg = "#FEFEFE", bg="#101C21", width=55, height=1, font=('times',29,'bold'))
header1.place(x=10, y=10)

frame3 = tk.Frame(window, bg = "#101C21")
frame3.place(relx= 0.52, rely = 0.09, relwidth=0.15, relheight=0.07)

frame4 = tk.Frame(window, bg = "#101C21")
frame4.place(relx=0.36, rely=0.09, relwidth=0.19, relheight=0.07)

date = tk.Label(frame4, text = day+"-"+mont[month]+"-"+year+"  |  ", fg="#DC6730",bg="#101C21" ,width=55 ,height=1,font=('times', 22, ' bold '))
date.pack(fill='both',expand=1)

clock = tk.Label(frame3, fg = "#DC6730", bg = "#101C21", width=55, height=1, font=('times',22,'bold'))
clock.pack(fill='both', expand=1)
clk()

head1 = tk.Label(frame1, text = "                  Bagi Yang Sudah Terdaftar                   ", fg="#101C21", bg="#099940", font=('times',17,'bold'))
head1.grid(row=0,column=0)

head2 = tk.Label(frame2, text = "                 Bagi Yang Belum Terdaftar                  ", fg="#101C21", bg="#099940", font=('times',17,'bold')) 
head2.grid(row = 0, column=0)

lbl = tk.Label(frame2, text="Nama", width=20, height=1, fg="#101C21", bg="#546EBE", font=('times', 17, 'bold') )
lbl.place(x=90,y=55)

txt = tk.Entry(frame2, width=32, fg="#101C21", font=('times',15))
txt.place(x=40, y=88)

lbl2 = tk.Label(frame2, text="Nomor Induk", width=20, fg="#101C21", bg="#546EBE", font=('times',17, 'bold'))
lbl2.place(x=90, y=140)

txt2 = tk.Entry(frame2, width=32, fg="#101C21", font=('times', 15))
txt2.place(x=40, y=173)

lbl3 = tk.Label(frame2, text="Status", width=20, fg="#101C21", bg="#546EBE", font=('times',17,'bold'))
lbl3.place(x=90, y=225)

var = tk.IntVar()
txt3 = tk.Radiobutton(frame2, text="Mahasiswa", fg="#101C21",bg="#546EBE" , font=('times', 15), variable=var, value=1)
txt3.place(x=60, y=265)
txt3 = tk.Radiobutton(frame2, text="Dosen", fg="#101C21",bg="#546EBE" , font=('times', 15), variable=var, value=2)
txt3.place(x=190, y=265)
txt3 = tk.Radiobutton(frame2, text="Karyawan", fg="#101C21",bg="#546EBE" , font=('times', 15), variable=var, value=3)
txt3.place(x=280, y=265)

lbl4 = tk.Label(frame1, text="Absensi", width=20, fg="#101C21", bg="#546EBE", height=1, font=('times', 17, 'bold'))
lbl4.place(x=100, y=115)

################################## TREEVIE ATTENDANCE TABLE ###############################

tv = ttk.Treeview(frame1, height = 13, columns = ('Nama', 'NIM', 'Status', 'Tanggal', 'Jam'))
tv.column('#0', width=0)
tv.column('Nama', width=90)
tv.column('NIM', width=90)
tv.column('Status', width=90)
tv.column('Tanggal', width=100)
tv.column('Jam', width=100)
tv.grid(row=2, column=0, padx=(0,0), pady=(123,0), columnspan=6)
tv.heading('#0')
tv.heading('Nama', text = 'Nama')
tv.heading('NIM', text = 'Nomor Induk')
tv.heading('Status', text = 'Status')
tv.heading('Tanggal', text = 'Tanggal')
tv.heading('Jam', text = 'Jam')


###################################### SCROLL BAR ######################################################
scroll=ttk.Scrollbar(frame1,orient='vertical',command=tv.yview)
scroll.grid(row=2,column=0,padx=(450,0),pady=(126,0),sticky='ns')
tv.configure(yscrollcommand=scroll.set)

######################################### Buttons ####################################################

clearButton = tk.Button(frame2, text="Clear", command=clear, fg="#101C21", bg = "#D02D32", width=10, activebackground = "#FEFEFE", font=('times', 11, 'bold'))
clearButton.place(x=355, y=86)
clearButton2 = tk.Button(frame2, text="Clear", command=clear2, fg="#101C21", bg = "#D02D32", width=10, activebackground = "#FEFEFE", font=('times', 11, 'bold'))
clearButton2.place(x=355, y=172)
takeImg = tk.Button(frame2, text = "Ambil Gambar", command= generate_dataset, fg="#101C21", bg="#2FD99B", width=34, height=1, activebackground= "#FEFEFE", font=('times', 15, ' bold '))
takeImg.place(x=30, y=330)
trainImg = tk.Button(frame2, text="Latih Gambar", command= train_classifier, fg="#101C21", bg="#2FD99B", width=34, height=1, activebackground= "#FEFEFE", font=('times', 15, ' bold '))
trainImg.place(x=30, y=400)
trackImg = tk.Button(frame1, text="Absen", command= detect_face, fg="#101C21", bg="#EBEF24", width=34, height=1, activebackground= "#FEFEFE", font=('times', 15, ' bold '))
trackImg.place(x=30, y=50)
quitWindow = tk.Button(frame1, text="Keluar", command=window.destroy, fg="#101C21", bg = "#D02D32", width=35, height=1, activebackground= "#FEFEFE", font=('times', 15, ' bold '))
quitWindow.place(x=30, y=455)

window.mainloop()