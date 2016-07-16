# -*- coding: utf-8 -*-
# codigo genérico del conector
import xmlrpclib
import configparser
from datetime import datetime

config = configparser.ConfigParser()
try:
    config.read('config.ini')
except:
    print """
    
    ERROR: No pudo leer archivo de configuracion. config.ini.
    Revise si se encuentra en el directorio  de instalacion de 
    prnfiscal.
    

    """
    raise SystemExit(0)

max_lineas = {}
try:
    max_lineas['BOLETA'] = config['BOLETA']['maxlineas']
except:
    print """
    ERROR: No está definida en el archivo config.ini la 
    cantidad de lineas de las boletas.
    """
    raise SystemExit(0)
try:
    max_lineas['FACTURA'] = config['FACTURA']['maxlineas']
except:
    print """
    ERROR: No está definida en el archivo config.ini la 
    cantidad de lineas de las facturas.
    """
    raise SystemExit(0)
try:
    max_lineas['GUIA DE DESPACHO'] = config['GUIA DE DESPACHO']['maxlineas']
except:
    print """
    ERROR: No está definida en el archivo config.ini la 
    cantidad de lineas de las guias de despacho.
    """
    raise SystemExit(0)

try:
    max_lineas['NV-T'] = config['NV-T']['maxlineas']
except:
    print """
    ERROR: No está definida en el archivo config.ini la 
    cantidad de lineas de las NOTAS DE VENTA.
    """
    raise SystemExit(0)



try:
    username = config['DEFAULT']['username']
    pwd = config['DEFAULT']['password']
    dbname = config['DEFAULT']['database']
    odoourl = config['DEFAULT']['url']
except:
    print """

    ERROR:
    No se pudieron obtener parámetros de acceso. 
    Por favor revise que el archivo \"config.ini\" contenga la
    información de acceso.
        TIPS: la seccion \"[DEFAULT]\" debe existir.
            Dentro de ella deben estar los siguientes parametros:
            username, password, database y url.


    """
    raise SystemExit(0)


class i_data(object):
    sock_common = xmlrpclib.ServerProxy (odoourl + '/xmlrpc/common')
    sock = xmlrpclib.ServerProxy (odoourl + '/xmlrpc/object')
    uid = sock_common.login(dbname, username, pwd)

    def get_invoice(self, dbname=dbname, uid=uid, pwd=pwd, sock=sock, max_lineas=max_lineas):

        args = [
            ('invoice_printed', '=', False),
            ('type', '=', 'out_invoice'),
            ('state', 'not in', ['draft', 'cancel']),
        ]

        account_invoice_fields = [
            'id',
            'date_invoice',
            'date_due',
            'sii_document_class_id',
            'sii_document_number',
            'state', 
            'amount_tax',
            'amount_untaxed',
            'amount_total',
            'partner_id',
            'vat_discriminated',
            'responsability_id',
            'seller_id',
        ]

        res_partner_fields = [
            'name',
            'street',
            'vat',
            'city',
            'phone',
            'state_id',
        ]

        account_invoice_line_fields = [
            'sequence',
            #'invoice_id',
            'price_unit',
            'price_subtotal',
            'discount',
            #'product_id',
            'quantity',
            'name'
        ]

        #empty_line = {'product_id': ['', ''], 'sequence': 40, 'invoice_id': ['', u''], 'price_unit': '', 'price_subtotal': '', 'discount': '', 'quantity': '', 'id': '', 'name': ''}
        empty_line = {'product_id': ['', ''], 'sequence': 40, 'price_unit': '', 'price_subtotal': '', 'discount': '', 'quantity': '', 'id': '', 'name': ''}
        
        try:
            print "consumiendo primer ws..."
            invoice_id = sock.execute(dbname, uid, pwd, 'account.invoice', 'search', args)
            print invoice_id
        except:
            print """

            ERROR:
            No se pudo efectuar la consulta. Revise si los parametros de 
            ingreso a su sistema en \"config.ini\" son los correctos.
            Serciorese de haber instalado el modulo \"invoice_printed\" 
            en su sistema Odoo.


            """
            raise SystemExit(0)

        invoices = sock.execute(dbname, uid, pwd, 'account.invoice', 'read', invoice_id, account_invoice_fields)
        invoice_data = {}
        for invoice in invoices:
            invoice_data["head"] = invoice

            #print invoice['partner_id'][0]
            #print invoice['sii_document_number']
            partner = sock.execute(dbname, uid, pwd, 'res.partner', 'read', invoice['partner_id'][0], res_partner_fields)
            
            
            #partner['city'] = partner['city'].encode("cp1252")
            #partner['street'] = partner['street'].encode("cp1252")
            #partner['name'] = partner['name'].encode("cp1252")
            #partner['state_id'][1] = partner['state_id'][1].encode("cp1252")
            #print partner['state_id'][1] 
            #raise SystemExit[0]
            
            
            invoice_data["partner"] = partner
            
            invoice_lines_args = [
                ('invoice_id', '=', invoice['id']),
            ]

            invoice_lines_ids = sock.execute(dbname, uid, pwd, 'account.invoice.line', 'search', invoice_lines_args)
            #print invoice_lines_ids
            i = 0
            invoice_data["lines"] = []
            for invoice_line_id in invoice_lines_ids:
                invoice_line = sock.execute(dbname, uid, pwd, 'account.invoice.line', 'read', invoice_line_id, account_invoice_line_fields)
                #incorporar un proceso para cambiar la codificacion de las lineas
                # 'sequence',
                ##'invoice_id',
                # print invoice_line['price_unit']
                # print invoice_line['price_subtotal']
                # print invoice_line['discount']
                # print invoice_line['product_id']
                # print invoice_line['quantity']
                invoice_line['name'] = invoice_line['name'].encode("cp1252")
                # print invoice_line['name']
                #encode("cp1252")
                invoice_data["lines"].append(invoice_line)
                i += 1

            try:
                if config['PRINTER']['seguridad'] == "ON":
                    j = input (("PRNFISCAL: Por imprimir {} {}. Presione \"s\" para continuar.").format(invoice_data["head"]["sii_document_class_id"][1], invoice_data["head"]["sii_document_number"]))
                    if j[0] != "s":
                        print "Saliendo... Ingrese nuevamente para continuar operando."
                        raise SystemExit(0)
            except:
                pass
            print ("PRNFISCAL: {} Imprimiendo {} {}....").format(datetime.now().strftime("%Y-%m-%d %H:%M:%S"),invoice_data["head"]["sii_document_class_id"][1], invoice_data["head"]["sii_document_number"])
            print invoice_data["head"]["sii_document_class_id"]
            print max_lineas[invoice_data["head"]["sii_document_class_id"][1]]
           
            for x in range( i, int(max_lineas[invoice_data["head"]["sii_document_class_id"][1]]) ):
                invoice_data["lines"].append(empty_line)

        return invoice_data
    def update_invoice(self, id, dbname=dbname, uid=uid, pwd=pwd, sock=sock):
    
        ids = [id]
        values = {'invoice_printed': 'printed'}
        
        return sock.execute(dbname, uid, pwd, 'account.invoice', 'write', ids, values)
