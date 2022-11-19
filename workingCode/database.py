from flask import Flask, redirect, render_template, request, session
from flask_session import Session
from flask_mysqldb import MySQL
#from mysql import connector
#import mysql.connector as mysql
#import mysql.connector as connector
#from mysql.connector.errors import Error

app = Flask(__name__)
mysql = MySQL(app)
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'gms'

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"



cursor = mysql.connection.cursor()
#cursor = mysql.connector.connect()
cursor.execute(
        "insert into plantdata(creation_dateTime, temp,humidity,ph,moisture) values (%s, %s, %s, %s, %s, %s)",
        'time ', 24, 56, 5.5, "wet")
mysql.connection.commit()
cursor.close()
