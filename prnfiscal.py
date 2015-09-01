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

locale.setlocale(locale.LC_ALL,'esp_esp')
#locale.setlocale(locale.LC_ALL,'es_CL.utf-8')
#http://stackoverflow.com/questions/10009753/python-dealing-with-mixed-encoding-files


print """




    Conector para Impresoras Fiscales con sistema Odoo, \"PrnFiscal\".
    Desarrollado por Blanco Martin y Asociados. (c) 2015




"""

# manipulador de la salida del sistema
def signal_handler(signal, frame):
        print """
        Saliendo..."""
        sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

# creacion de filtros para Jinja
def format_currency(value):
    if isinstance(value, str):
        return ' '
    a = str(int(round(value,0)))
    result = ''
    i = -3
    porcion = a[i:]
    result = porcion
    while len(porcion) >= 3:
        j = i
        i -= 3
        porcion = a[i:j]
        if len(porcion) == 0:
            break
        result = porcion + '.' + result
    return result
    #locale.currency(value)

def righted(value,qty):
    return value.rjust(qty)

def integ(value):
    return str(value)

def fixlen(value,qty):
    return value.ljust(qty)[:qty]

def comuna(value):
    value1 = value.split("/")
    return value1[2].strip()

def componer(value):
    x = int(value)

    unidad = ['','uno','dos','tres','cuatro','cinco','seis','siete','ocho','nueve']
    decena = ['diez','once','doce','trece','catorce','quince','dieciseis','dicisiete','dieciocho','diecinueve']
    decadas = {
        2:['veinte','veinti'],
        3:['treinta','treinta y '],
        4:['cuarenta','cuarenta y '],
        5:['cincuenta','cincuenta y '],
        6:['sesenta','sesenta y '],
        7:['setenta','setenta y '],
        8:['ochenta','ochenta y '],
        9:['noventa','noventa y '],
    }
    centena = [
        '',
        'ciento ',
        'doscientos ',
        'trescientos ',
        'cuatrocientos ',
        'quinientos ',
        'seiscientos ',
        'setecientos ',
        'ochocientos ',
        'novecientos '
    ]

    if x < 1000000:
        if x < 1000:
            if x < 100:
                if x < 20:
                    if x < 10:
                        return unidad[x]
                    else:
                        return decena[x - 10]
                else:
                    if (x % 10 == 0):
                        return decadas[x / 10][x % 10]
                    else:
                        return decadas[x / 10][1] + unidad[x % 10]
            else:
                if x == 100:
                    return 'cien '
                else:
                    return centena[x / 100] + componer(x % 100)
        else:
            return componer(x / 1000) + ' mil ' + componer(x % 1000)
            #return 'mil' + componer(x % 1000)
    else:
        if x < 2000000:
            return componer(x / 1000000) + ' millón, ' + componer(x % 1000000)
        else:
            return componer(x / 1000000) + ' millones, ' + componer(x % 1000000)

def part1(value):
    return value[0:30]

def part2(value):
    return value[31:60]

def part3(value):
    return value[61:90]

def days_between(d1, d2):
    d1 = datetime.strptime(d1, "%Y-%m-%d")
    d2 = datetime.strptime(d2, "%Y-%m-%d")
    days = abs((d2 - d1).days)
    if days == 0:
        return 'Contado'
    else:
        return str(days)+ 'días FF'

def mes_enletras(value):
    mes = [
        '',
        'Enero',
        'Febrero',
        'Marzo',
        'Abril',
        'Mayo',
        'Junio',
        'Julio',
        'Agosto',
        'Septiembre',
        'Octubre',
        'Noviembre',
        'Diciembre'
    ]
    return mes[int(value)]
    
def fecha_sep(value,parte):
    if(parte == 'd'):
        return value[8:10]
    elif(parte) == 'm':
        return value[5:7]
    elif(parte) == 'a':
        return value[0:4]

def format_vat(value):
    try:
        return locale.format('%d',int(float(value[2:10])),1)+'-' + value[10:]
    except:
        return "            "

def with_vat(value):
    if isinstance(value, str):
        return ' '
    return round(value * 1.19,0)

templateLoader = jinja2.FileSystemLoader( searchpath="." )
templateEnv = jinja2.Environment( loader=templateLoader )
templateEnv.filters['format_currency'] = format_currency
templateEnv.filters['integ'] = integ
templateEnv.filters['fixlen'] = fixlen
templateEnv.filters['righted'] = righted
templateEnv.filters['componer'] = componer
templateEnv.filters['part1'] = part1
templateEnv.filters['part2'] = part2
templateEnv.filters['part3'] = part3
templateEnv.filters['days_between'] = days_between
templateEnv.filters['format_vat'] = format_vat
templateEnv.filters['with_vat'] = with_vat
templateEnv.filters['fecha_sep'] = fecha_sep
templateEnv.filters['mes_enletras'] = mes_enletras
templateEnv.filters['comuna'] = comuna

try:
    printer_name = config['PRINTER']['printer']
    print "usando la impresora configurada " + printer_name
except:
    printer_name = win32print.GetDefaultPrinter ()
    print "usando la impresora por defecto " + printer_name

timesleep = 0.0
while True:
    print ("PRNFISCAL: {} Esperando nuevo comprobante para imprimir... ").format(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    time.sleep(timesleep)
    timesleep = float(config['DEFAULT']['sleep'])
    from odooconnect import i_data
    i_data = i_data()
    invoice_data = i_data.get_invoice()
    aaaa = 0
    #try:
    if aaaa == 0:
        if invoice_data == {}:
            continue

        invoice_data['cr'] = "\r\n"
        TEMPLATE_FILE = "templates/" + (invoice_data['head']['afip_document_class_id'][1]).lower() + ".txt"
        template = templateEnv.get_template( TEMPLATE_FILE )
        # prueba daniel
        #print invoice_data
        content = template.render( invoice_data )
        print "termina de renderizar"        
        print content
        #raise SystemExit(0)
        print "\n"
        print ("PRNFISCAL: {} Se imprimio {} Numero: {}").format(datetime.now().strftime("%Y-%m-%d %H:%M"), (invoice_data['head']['afip_document_class_id'][1]).lower(), invoice_data['head']['afip_document_number'])
        #raise SystemExit(0)
        
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
        # impresión realizada
        if (i_data.update_invoice(invoice_data['head']['id'])):
            print ("PRNFISCAL: {} Se actualizó el estado del comprobante {} {}... ").format(datetime.now().strftime("%Y-%m-%d %H:%M:%S"),invoice_data["head"]["afip_document_class_id"][1], invoice_data["head"]["afip_document_number"])

        print ("PRNFISCAL: {} Esperando nuevo comprobante para imprimir... ").format(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    else:
    #except:
        print "fallo el renderizado"
        pass
    
