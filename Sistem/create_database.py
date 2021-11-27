import mysql.connector

# established host
mydb= mysql.connector.connect(
host = "localhost",
user = "root",
password =""
)

# create database
mycursor = mydb.cursor()
mycursor.execute("CREATE DATABASE rincian_user")

# create table
mydb= mysql.connector.connect(
host = "localhost",
user = "root",
password ="",
database = "rincian_user"
)
mycursor =mydb.cursor()
mycursor.execute("CREATE TABLE my_table(id int primary key, Nama varchar (50), NIM varchar (50), Status varchar(50))")