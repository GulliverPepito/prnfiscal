# -*- coding: utf-8 -*-
import os, sys, decimal
from datetime import datetime
import win32print
import jinja2
import locale
import signal
import time
import locale
from odooconnect import config

reload(sys)
sys.setdefaultencoding('Cp1252')

locale.setlocale(locale.LC_ALL,'esp_esp')
#locale.setlocale(locale.LC_ALL,'es_CL.utf-8')
#http://stackoverflow.com/questions/10009753/python-dealing-with-mixed-encoding-files

try:
    printer_name = config['PRINTER']['printer']
    print "usando la impresora configurada " + printer_name
except:
    printer_name = win32print.GetDefaultPrinter ()
    print "usando la impresora por defecto " + printer_name

content = """hola mundo esta es una impresion de prueba en la oki"""
        
pagebreak = chr(12)

salida = content + pagebreak

if sys.version_info >= (3,):
    raw_data = bytes (salida, "utf-8")
else:
    raw_data = salida

hPrinter = win32print.OpenPrinter (printer_name)
try:
    hJob = win32print.StartDocPrinter (hPrinter, 1, ("test of raw data hjob titulo", None, "RAW"))
    try:
        win32print.StartPagePrinter (hPrinter)
        win32print.WritePrinter (hPrinter, raw_data)
        win32print.EndPagePrinter (hPrinter)
    finally:
        win32print.EndDocPrinter (hPrinter)
finally:
    win32print.ClosePrinter (hPrinter)
    #raise SystemExit(0)
    
