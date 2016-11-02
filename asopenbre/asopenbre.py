# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
#    Coded by: Helman Valencia (helmanvalencia@gmail.com)
##############################################################################

from openerp.osv import fields, osv, orm
from datetime import time, datetime, date
from decimal import *
from openerp.tools.translate import _
import os, re

class asocia2_procesos(osv.osv):
	"""docstring for modification to asocia2_procesos"""
	_name = 'asocia2.procesos'
	_inherit = 'asocia2.procesos'

	def ProximoPeriodo(self, periodo):
		""" Devuelve el proximo periodo """
		anioi = int(periodo[0:4])
		mesi = int(periodo[5:7])
		if mesi == 12:
			aniof = anioi + 1
			mesf = 1
		else:
			aniof = anioi
			mesf = mesi + 1
		return str(aniof)+'-'+str(mesf).zfill(2)

	def causa_credito(self, cr, uid, ids, context=None):
		""" Procesa archivo convenios de credito """
		partner=self.pool.get('res.partner')
		product=self.pool.get('product.product')
		servicio_credito=self.pool.get('asocia2.servicio_credito')
		hist_servicio_credito=self.pool.get('asocia2.hist_servicio_credito')
		hist_procesos=self.pool.get('asocia2.hist_procesos')
		purchase = self.pool.get('purchase.order')
		invoice = self.pool.get('account.invoice')
		periodo = self.ProximoPeriodo(self.browse(cr, uid, ids[0]).periodos_id.control_procesos_id.periodo_actual)
		print "&&&&&&&& periodo -->", periodo
		if os.name == 'posix':
			Directorio = '/home/helman/Procesos/' + self.browse(cr, uid, ids[0]).periodos_id.control_procesos_id.periodo_actual +'/'
		else:
			Directorio = 'c:\Procesos\\' + self.browse(cr, uid, ids[0]).periodos_id.control_procesos_id.periodo_actual +'\\'
		Log = []
		ArchivoE = []
		Convenio = self.browse(cr, uid, ids[0]).categ_id.name
		p = self.browse(cr, uid, ids[0]).proveedor_id
		if os.name == 'posix':
			Directorio = Directorio + Convenio + ' - ' + p.name + '/'
		else:
			Directorio = Directorio + Convenio + ' - ' + p.name + '\\'
		print "&&&&&&&& Directorio -->", Directorio
		nProceso = self.browse(cr, uid, ids[0]).nombre_proceso
		Archivo = nProceso + '.csv'
		if not os.access(Directorio+Archivo, os.F_OK):
			raise osv.except_osv(_('Error!'), _('El archivo '+Archivo + ' no existe en el directorio ' + Directorio))
		f = open(Directorio+Archivo,"rU")
		linea = f.readline()
		ArchivoE.append(linea)
		campos = re.split(";",linea)
		campos.append('Mensaje de error')
		Log.append(campos)
		linea = f.readline()
		# 0. Crea purchase del proveedor
		asocia2_data = {
			'partner_id': p.id,
			'location_id': 17,
			'pricelist_id': 2,
			'cobro': True,
			'periodo': periodo,
		}
		purchase_id = purchase.create(cr, uid, asocia2_data, context=context)
		AlgunError = False
		while linea:
			campos = re.split(";",linea)
			datos = {}
			datos['cedula'] = campos[0]
			datos['id_credito'] = campos[2]
			datos['saldo'] = campos[3]
			datos['cuota'] = campos[4]
			datos['plazo'] = campos[5]
			datos['cuotas_pagadas'] = campos[6]
			datos['capital'] = 0
			datos['interes'] = 0
			datos['fuente'] = Archivo
			datos['periodo'] = periodo
			#datos['soporte'] = Nro
			datos['fecha_procesado'] = date.today().strftime('%Y/%m/%d')
			Correcto = True
			# 1. Valida que la fecha de causacion sea formato 'mm/dd/aaaa'
			try:
				datos['fecha_causado'] = date(int(campos[8][6:10]),int(campos[8][3:5]),int(campos[8][0:2])).strftime('%Y/%m/%d')
			except:
				Correcto = False
				datos['mensaje'] = "El formato de la fecha de causacion '%s' debe ser 'dd/mm/aaaa'"% campos[8][0:10]
			if Correcto:
				# 2. Valida que la fecha de causacion corresponda al periodo que se procesa (siguiente mes)
				Periodo = datos['fecha_causado'][0:4] + '-' + datos['fecha_causado'][5:7]
				if not Periodo == periodo:
					Correcto = False
					datos['mensaje'] = "La fecha de causacion '%s' no corresponde al siguiente mes '%s' del mes que se procesa '%s'"% (campos[8][0:10],periodo,self.browse(cr, uid, ids[0]).periodos_id.control_procesos_id.periodo_actual)
			if Correcto:
				# 3. Valida que el afiliado exista y este activo
				resultado = partner.search(cr, uid, [('membership','=',True),('cc_afiliado','=',datos['cedula'])])
				print "&&&&&&&& afiliados -->", resultado
				if not resultado:
					Correcto = False
					datos['mensaje'] = "El afiliado con cédula '%s' no existe"% datos['cedula']
				else:
					afil=partner.browse(cr, uid, resultado[0])
					if not afil.state=='confirmed':
						Correcto = False
						datos['mensaje'] = "El afiliado con cédula '%s' no esta activo"% datos['cedula']
			if Correcto:
				# 4. Procesa la informacion
				#if datos['id_credito']=='801763385':
					#raise RuntimeError('Si llegue')
				# 4.1 Novedad "" - Normal
				if not campos[7]:
					# 4.1.1 Valida que exista este servicio de credito y este activo
					resultado = servicio_credito.search(cr, uid, [('afiliado_id','=',afil.id),('product_id','=',product_id)])
					if not resultado:
						Correcto = False
						datos['mensaje'] = "El servicio de crédito con id '%s' no existe y la novedad es normal"% datos['id_credito']
					else:
						cred=servicio_credito.browse(cr, uid, resultado)
						if not cred.estado=='active':
							Correcto = False
							datos['mensaje'] = "El servicio de crédito con id '%s' no esta activo"% datos['id_credito']
						else:
							# 4.1.2. Valida que no venga modificado cuota,plazo o cuotas pagadas
							if not cred.valor_cuota==float(datos['cuota']):
								Correcto = False
								datos['mensaje'] = "El valor de la cuota fué modificado '%s' y la novedad es normal"% str(cred.valor_cuota)
							else:
								#raise RuntimeError(cred.plazo,datos['plazo'])
								if not cred.plazo==int(datos['plazo']):
									Correcto = False
									datos['mensaje'] = "El plazo fué modificado '%s' y la novedad es normal"% str(cred.plazo)
								else:
									if not cred.cuotas_pag_calculado==int(datos['cuotas_pagadas']):
										Correcto = False
										datos['mensaje'] = "El contador de cuotas pagadas del banco difiere del contador de la asociación '%s'"% str(cred.cuotas_pag_calculado)
									# Log de cambios 1.1.2
									else:
										if int(datos['cuotas_pagadas']) > cred.plazo:
											Correcto = False
											datos['mensaje'] = "El numero de cuotas pagadas '%s' no puede ser mayor al plazo '%s'"% (datos['cuotas_pagadas'],str(cred.plazo))
										else:
											# 4.1.3. Graba la causacion y actualiza saldo, cuotas pagadas reportado y calculado
											contador_cuotas = cred.cuotas_pag_calculado + 1
											cred.write(cr, uid, ids, {
												'saldo':datos['saldo'],
												'cuotas_pag_reportado':datos['cuotas_pagadas'],
												'cuotas_pag_calculado':contador_cuotas,
												}, context=None)
											datos['purchase_id'] = purchase_id
											datos['afiliado_id'] = afil.id
											datos['producto_id'] = cred.product_id
											self.GrabaCausacion(cr, uid, ids, servicio, datos, context=None)
				#raise RuntimeError(datos,cred.Title())
				# 4.2 Novedad "0" - Nuevo
				if campos[7]=='0':
					# 4.2.1. Valida que no exista este producto
					resultado = product.search(cr, uid, [('default_code','=',datos['id_credito']),('categ_id','=',self.browse(cr, uid, ids[0]).categ_id.id)])
					print "&&&&&&&& productos -->", resultado
					if resultado:
						Correcto = False
						datos['mensaje'] = "El producto con id '%s' existe y la novedad es nuevo"% datos['id_credito']
					else:
						# 4.2.2. Crea el producto
						asocia2_data = {
							'name': Convenio + ' - ' + p.name + ' ' + datos['id_credito'],
							'categ_id': self.browse(cr, uid, ids[0]).categ_id.id, 
							'list_price': datos['cuota'], 
							'standard_price': datos['cuota'], 
							'type': 'service', 
							'default_code': datos['id_credito'],
						}
						product_id = product.create(cr, uid, asocia2_data, context=context)
						# 4.2.3. Valida que no exista este servicio de credito para el afiliado
						resultado = servicio_credito.search(cr, uid, [('afiliado_id','=',afil.id),('product_id','=',product_id)])
						print "&&&&&&&& servicio_credito -->", resultado
						if resultado:
							Correcto = False
							datos['mensaje'] = "El servicio de credito con id '%s' existe y la novedad es nuevo"% datos['id_credito']
						else:
							# 4.2.4. Crea el servicio de credito
							asocia2_data = {
								'afiliado_id':afil.id,
								'product_id': product_id,
								'categ_id': self.browse(cr, uid, ids[0]).categ_id.id, 
								'plazo': datos['plazo'],
								'saldo': datos['saldo'],
								'cuotas_pag_reportado': datos['cuotas_pagadas'],
								'cuotas_pag_calculado': int(datos['cuotas_pagadas']) + 1,
								'valor_cuota': datos['cuota'],
								'fecha': datos['fecha_procesado'],
							}
							servicio_credito_id = servicio_credito.create(cr, uid, asocia2_data, context=context)
							asocia2_data = {
								'servicio_credito_id':servicio_credito_id,
								'estado': 'active',
								'fecha': datos['fecha_procesado'],
							}
							hist_servicio_credito_id = hist_servicio_credito.create(cr, uid, asocia2_data, context=context)
							servicio = servicio_credito.browse(cr, uid, servicio_credito_id)
							# 4.2.5. Graba la causacion
							datos['purchase_id'] = purchase_id
							datos['afiliado_id'] = afil.id
							datos['producto_id'] = product_id
							self.GrabaCausacion(cr, uid, ids, servicio, datos, context=None)
				# 4.3 Novedad "1" - Cancela
				if campos[7]=='1':
					# 4.3.1 Valida que exista este servicio de credito y este activo
					resultado = servicio_credito.search(cr, uid, [('afiliado_id','=',afil.id),('product_id','=',product_id)])
					if not resultado:
						Correcto = False
						datos['mensaje'] = "El servicio de crédito con id '%s' no existe y la novedad es cancelar"% datos['id_credito']
					else:
						cred=servicio_credito.browse(cr, uid, resultado)
						if not cred.estado=='active':
							Correcto = False
							datos['mensaje'] = "El servicio de crédito con id '%s' no esta activo y se esta solicitando cancelar"% datos['id_credito']
						else:
							# 4.3.2. Actualiza los datos que vienen en la novedad sin grabar causacion
							cred.write(cr, uid, ids, {
								'saldo':datos['saldo'],
								'cuotas_pag_reportado':datos['cuotas_pagadas'],
								'estado':'finished',
								}, context=None)
							asocia2_data = {
								'servicio_credito_id':cred.id,
								'estado': 'finished',
								'fecha': datos['fecha_procesado'],
							}
							hist_servicio_credito_id = hist_servicio_credito.create(cr, uid, asocia2_data, context=context)
				# 4.4 Novedad "2" - Modifica
				if campos[7]=='2':
					# 4.4.1 Valida que exista este servicio de credito y este activo
					resultado = servicio_credito.search(cr, uid, [('afiliado_id','=',afil.id),('product_id','=',product_id)])
					if not resultado:
						Correcto = False
						datos['mensaje'] = "El servicio de crédito con id '%s' no existe y la novedad es modificar"% datos['id_credito']
					else:
						cred=servicio_credito.browse(cr, uid, resultado)
						if not cred.estado=='active':
							Correcto = False
							datos['mensaje'] = "El servicio de crédito con id '%s' no esta activo"% datos['id_credito']
						else:
							# 4.4.2. Graba la causacion y actualiza datos y contador cuotas pagadas y calculado
							contador_cuotas = cred.cuotas_pag_calculado + 1
							cred.write(cr, uid, ids, {
								'saldo':datos['saldo'],
								'plazo':datos['plazo'],
								'valor_cuota':datos['cuota'],
								'cuotas_pag_reportado':datos['cuotas_pagadas'],
								'cuotas_pag_calculado':contador_cuotas,
								}, context=None)
							datos['purchase_id'] = purchase_id
							datos['afiliado_id'] = afil.id
							datos['producto_id'] = cred.product_id
							self.GrabaCausacion(cr, uid, ids, servicio, datos, context=None)
				# 4.5 Novedad diferente es un error
				if campos[7] and campos[7] not in ('0','1','2'):
					Correcto = False
					datos['mensaje'] = "La novedad reportada '%s' no es valida, los valores correctos son: vacio,0,1,2"% campos[7]
			print "&&&&&&&& datos -->", datos
			# 5. Agrega al Log si es necesario
			if not Correcto:
				ArchivoE.append(linea)
				campos.append(datos['mensaje'])
				Log.append(campos)
				AlgunError = True
			linea = f.readline()
		# 6. Procesos finales
		f.close()
		# 6.1 Crea el Log
		resultado = purchase.browse(cr, uid, purchase_id).wkf_confirm_order()
		resultado = purchase.browse(cr, uid, purchase_id).wkf_approve_order()
		invoice_id = purchase.browse(cr, uid, purchase_id).action_invoice_create()
		invoice.write(cr, uid, invoice_id, {'date_invoice':datos['fecha_causado']}, context=None)
		resultado = invoice.browse(cr, uid, invoice_id).invoice_validate()
		print "&&&&&&&& resultado -->", resultado
		print "&&&&&&&& Log -->", Log
		Loghtml = self.CreaLog(Log, nProceso)
		print "&&&&&&&& Loghtml -->", Loghtml
		# 6.2 Crea registro de historia procesos
		if AlgunError:
			resultado = 'Con errores'
		else:
			resultado = 'Sin errores'
		asocia2_data = {
			'procesos_id': ids[0],
			'fecha': date.today(),
			'resultado': resultado,
		}
		hist_procesos_id = hist_procesos.create(cr, uid, asocia2_data, context=context)
		# 6.3 Renombra el archivo de causaciones
		os.chdir(Directorio)
		i = 0
		NArchivo = nProceso + date.today().strftime('%Y-%m-%d') + str(i) + '.csv'
		NLog = nProceso + date.today().strftime('%Y-%m-%d') + str(i) + '.htm'
		while os.access(NArchivo, os.F_OK):
			i = i + 1
			NArchivo = nProceso + date.today().strftime('%Y-%m-%d') + str(i) + '.csv'
			NLog = nProceso + date.today().strftime('%Y-%m-%d') + str(i) + '.htm'
		Archivo = nProceso + '.csv'
		print "&&&&&&&& Archivo -->", Archivo, NArchivo
		os.rename(Archivo, NArchivo)
		# 6.4 Crea el Archivo de errores y Log
		self.CreaArchivo(ArchivoE,Archivo,Directorio)
		NLog = 'Log-' + NLog
		self.CreaArchivo(Loghtml,NLog,Directorio)
		return 'Fin del proceso'

	def causa_salud(self, cr, uid, ids, context=None):
		""" Procesa archivo convenios de Salud """
		a = self.causa_Convenio(cr, uid, ids, 'salud', context=None)
		return 'Fin del proceso'

	def causa_seguro_auto(self, cr, uid, ids, context=None):
		""" Procesa archivo convenios de Seguro de Auto """
		a = self.causa_Convenio(cr, uid, ids, 'seguro_auto', context=None)
		return 'Fin del proceso'

	def causa_seguro_vida(self, cr, uid, ids, context=None):
		""" Procesa archivo convenios de Seguro de Vida """
		a = self.causa_Convenio(cr, uid, ids, 'seguro_vida', context=None)
		return 'Fin del proceso'

	def causa_seguro_hogar(self, cr, uid, ids, context=None):
		""" Procesa archivo convenios de Seguro de Hogar """
		a = self.causa_Convenio(cr, uid, ids, 'seguro_hogar', context=None)
		return 'Fin del proceso'

	def causa_seguro_funerario(self, cr, uid, ids, context=None):
		""" Procesa archivo convenios de Seguro Funerario """
		a = self.causa_Convenio(cr, uid, ids, 'seguro_funerario', context=None)
		return 'Fin del proceso'

	def causa_telefonia(self, cr, uid, ids, context=None):
		""" Procesa archivo convenios de Telefonia """
		a = self.causa_Convenio(cr, uid, ids, 'telefonia', context=None)
		return 'Fin del proceso'

	def causa_Convenio(self, cr, uid, ids, TipoServicio, context=None):
		""" Procesa archivos de convenios """
		partner=self.pool.get('res.partner')
		product=self.pool.get('product.product')
		servicio_generico=self.pool.get('asocia2.servicio_generico')
		hist_servicio_generico=self.pool.get('asocia2.hist_servicio_generico')
		hist_procesos=self.pool.get('asocia2.hist_procesos')
		purchase = self.pool.get('purchase.order')
		invoice = self.pool.get('account.invoice')
		periodo = self.ProximoPeriodo(self.browse(cr, uid, ids[0]).periodos_id.control_procesos_id.periodo_actual)
		if os.name == 'posix':
			Directorio = '/home/helman/Procesos/' + self.browse(cr, uid, ids[0]).periodos_id.control_procesos_id.periodo_actual +'/'
		else:
			Directorio = 'c:\Procesos\\' + self.browse(cr, uid, ids[0]).periodos_id.control_procesos_id.periodo_actual +'\\'
		Log = []
		ArchivoE = []
		Convenio = self.browse(cr, uid, ids[0]).categ_id.name
		p = self.browse(cr, uid, ids[0]).proveedor_id
		if os.name == 'posix':
			Directorio = Directorio + Convenio + ' - ' + p.name + '/'
		else:
			Directorio = Directorio + Convenio + ' - ' + p.name + '\\'
		print "&&&&&&&& Directorio -->", Directorio
		nProceso = self.browse(cr, uid, ids[0]).nombre_proceso
		Archivo = nProceso + '.csv'
		if not os.access(Directorio+Archivo, os.F_OK):
			raise osv.except_osv(_('Error!'), _('El archivo '+Archivo + ' no existe en el directorio ' + Directorio))
		f = open(Directorio+Archivo,"rU")
		linea = f.readline()
		ArchivoE.append(linea)
		campos = re.split(";",linea)
		campos.append('Mensaje de error')
		Log.append(campos)
		linea = f.readline()
		# 0. Crea purchase del proveedor
		asocia2_data = {
			'partner_id': p.id,
			'location_id': 17,
			'pricelist_id': 2,
			'cobro': True,
			'periodo': periodo,
		}
		purchase_id = purchase.create(cr, uid, asocia2_data, context=context)
		AlgunError = False
		while linea:
			campos = re.split(";",linea)
			datos = {}
			datos['regional'] = campos[0]
			datos['cedula'] = campos[1]
			datos['identificador'] = campos[3]
			datos['cuota'] = campos[4]
			datos['fuente'] = Archivo
			datos['periodo'] = periodo
			datos['fecha_procesado'] = date.today().strftime('%Y/%m/%d')
			if TipoServicio == 'telefonia':
				datos['capital'] = str(float(campos[7])+float(campos[8]))
				datos['interes'] = campos[9]
				datos['cuota'] = str(float(campos[7])+float(campos[8])+float(campos[9]))
			else:
				datos['capital'] = 0
				datos['interes'] = 0
			Correcto = True
			# 1. Valida que la fecha de causacion sea formato 'dd/mm/aaaa'
			try:
				datos['fecha_causado'] = date(int(campos[6][6:10]),int(campos[6][3:5]),int(campos[6][0:2])).strftime('%Y/%m/%d')
			except:
				Correcto = False
				datos['mensaje'] = "El formato de la fecha de causacion '%s' debe ser 'dd/mm/aaaa'"% campos[6][0:10]
			if Correcto:
				# 2. Valida que la fecha de causacion corresponda al periodo que se procesa
				Periodo = datos['fecha_causado'][0:4] + '-' + datos['fecha_causado'][5:7]
				if not Periodo == self.browse(cr, uid, ids[0]).periodos_id.control_procesos_id.periodo_actual:
					Correcto = False
					datos['mensaje'] = "La fecha de reporte '%s' no corresponde al mes que se procesa '%s'"% (campos[6][0:10],periodo,self.browse(cr, uid, ids[0]).periodos_id.control_procesos_id.periodo_actual)
			if Correcto:
				# 3. Valida que el afiliado exista y este activo
				resultado = partner.search(cr, uid, [('membership','=',True),('cc_afiliado','=',datos['cedula'])])
				print "&&&&&&&& afiliados -->", resultado
				if not resultado:
					Correcto = False
					datos['mensaje'] = "El afiliado con cédula '%s' no existe"% datos['cedula']
				else:
					afil=partner.browse(cr, uid, resultado[0])
					if not afil.state=='confirmed':
						Correcto = False
						datos['mensaje'] = "El afiliado con cédula '%s' no esta activo"% datos['cedula']
			if Correcto:
				# 4. Procesa la informacion
				# 4.1 Novedad "" - Normal
				if not campos[5]:
					# 4.1.1 Valida que exista este servicio generico y este activo
					resultado = servicio_generico.search(cr, uid, [('afiliado_id','=',afil.id),('product_id','=',product_id)])
					if not resultado:
						Correcto = False
						datos['mensaje'] = "El servicio tipo '%s' con id '%s' no existe y la novedad es normal"% (TipoServicio,datos['identificador'])
					else:
						cred=servicio_generico.browse(cr, uid, resultado)
						if not cred.estado=='active':
							Correcto = False
							datos['mensaje'] = "El servicio tipo '%s' con id '%s' no esta activo"% (TipoServicio,datos['identificador'])
						else:
							# 4.1.2. Valida que no venga modificado cuota,regional
							if not TipoServicio == 'telefonia':
								if not cred.valor_cuota==float(datos['cuota']):
									Correcto = False
									datos['mensaje'] = "El valor de la cuota fué modificado '%s' y la novedad es normal"% str(cred.valor_cuota)
								else:
									if not regional==datos['regional']:
										Correcto = False
										datos['mensaje'] = "La regional fue modificada '%s' y la novedad es normal"% str(regional)
									else:
										# 4.1.3. Graba la causacion
										datos['purchase_id'] = purchase_id
										datos['afiliado_id'] = afil.id
										datos['producto_id'] = cred.product_id
										self.GrabaCausacion(cr, uid, ids, servicio, datos, context=None)
							else:
								if not cred.valor_cuota==float(datos['cuota']):
									Correcto = False
									datos['mensaje'] = "El valor fijo fué modificado '%s' y la novedad es normal"% str(cred.valor_cuota)
								else:
									# 4.1.3. Graba la causacion
									datos['purchase_id'] = purchase_id
									datos['afiliado_id'] = afil.id
									datos['producto_id'] = cred.product_id
									self.GrabaCausacion(cr, uid, ids, servicio, datos, context=None)
				# 4.2 Novedad "0" - Nuevo
				if campos[5]=='0':
					# 4.2.1. Valida que no exista este producto
					resultado = product.search(cr, uid, [('default_code','=',datos['identificador']),('categ_id','=',self.browse(cr, uid, ids[0]).categ_id.id)])
					print "&&&&&&&& productos -->", resultado
					if resultado:
						Correcto = False
						datos['mensaje'] = "El producto con id '%s' existe y la novedad es nuevo"% datos['identificador']
					else:
						# 4.2.2. Crea el producto
						if TipoServicio == 'telefonia':
							val_cuota = datos['capital']
						else:
							val_cuota = datos['cuota']
						asocia2_data = {
							'name': Convenio + ' - ' + p.name + ' ' + datos['identificador'],
							'categ_id': self.browse(cr, uid, ids[0]).categ_id.id, 
							'list_price': val_cuota, 
							'standard_price': val_cuota, 
							'type': 'service', 
							'default_code': datos['identificador'],
						}
						product_id = product.create(cr, uid, asocia2_data, context=context)
						# 4.2.3. Valida que no exista este servicio generico para el afiliado
						resultado = servicio_generico.search(cr, uid, [('afiliado_id','=',afil.id),('product_id','=',product_id)])
						print "&&&&&&&& servicio generico -->", resultado
						if resultado:
							Correcto = False
							datos['mensaje'] = "El servicio generico con id '%s' existe y la novedad es nuevo"% datos['identificador']
						else:
							# 4.2.4. Crea el servicio generico
							asocia2_data = {
								'afiliado_id':afil.id,
								'product_id': product_id,
								'categ_id': self.browse(cr, uid, ids[0]).categ_id.id, 
								'valor_cuota': val_cuota,
								'fecha': datos['fecha_procesado'],
							}
							servicio_generico_id = servicio_generico.create(cr, uid, asocia2_data, context=context)
							asocia2_data = {
								'servicio_generico_id':servicio_generico_id,
								'estado': 'active',
								'fecha': datos['fecha_procesado'],
							}
							hist_servicio_generico_id = hist_servicio_generico.create(cr, uid, asocia2_data, context=context)
							servicio = servicio_generico.browse(cr, uid, servicio_generico_id)
							# 4.2.5. Graba la causacion
							datos['purchase_id'] = purchase_id
							datos['afiliado_id'] = afil.id
							datos['producto_id'] = product_id
							self.GrabaCausacion(cr, uid, ids, servicio, datos, context=None)
				# 4.3 Novedad "1" - Cancela
				if campos[5]=='1':
					# 4.3.1 Valida que exista este servicio generico y este activo
					resultado = servicio_generico.search(cr, uid, [('afiliado_id','=',afil.id),('product_id','=',product_id)])
					if not resultado:
						Correcto = False
						datos['mensaje'] = "El servicio de generico con id '%s' no existe y la novedad es cancelar"% datos['identificador']
					else:
						cred=servicio_generico.browse(cr, uid, resultado)
						if not cred.estado=='active':
							Correcto = False
							datos['mensaje'] = "El servicio de generico con id '%s' no esta activo y se esta solicitando cancelar"% datos['identificador']
						else:
							# 4.3.2. Actualiza los datos que vienen en la novedad sin grabar causacion
							cred.write(cr, uid, ids, {
								'estado':'finished',
								}, context=None)
							asocia2_data = {
								'servicio_generico_id':cred.id,
								'estado': 'finished',
								'fecha': datos['fecha_procesado'],
							}
							hist_servicio_generico_id = hist_servicio_generico.create(cr, uid, asocia2_data, context=context)
				# 4.4 Novedad "2" - Modifica
				if campos[5]=='2':
					# 4.4.1 Valida que exista este servicio de generico y este activo
					resultado = servicio_generico.search(cr, uid, [('afiliado_id','=',afil.id),('product_id','=',product_id)])
					if not resultado:
						Correcto = False
						datos['mensaje'] = "El servicio de generico con id '%s' no existe y la novedad es modificar"% datos['identificador']
					else:
						cred=servicio_generico.browse(cr, uid, resultado)
						if not cred.estado=='active':
							Correcto = False
							datos['mensaje'] = "El servicio generico con id '%s' no esta activo"% datos['identificador']
						else:
							# 4.4.2. Graba la causacion y actualiza datos
							if TipoServicio == 'telefonia':
								val_cuota = datos['capital']
							else:
								val_cuota = datos['cuota']
							cred.write(cr, uid, ids, {
								'valor_cuota':val_cuota,
								}, context=None)
							datos['purchase_id'] = purchase_id
							datos['afiliado_id'] = afil.id
							datos['producto_id'] = cred.product_id
							self.GrabaCausacion(cr, uid, ids, servicio, datos, context=None)
				# 4.5 Novedad diferente es un error
				if campos[5] and campos[5] not in ('0','1','2'):
					Correcto = False
					datos['mensaje'] = "La novedad reportada '%s' no es valida, los valores correctos son: vacio,0,1,2"% campos[5]
			print "&&&&&&&& datos -->", datos
			# 5. Agrega al Log si es necesario
			if not Correcto:
				ArchivoE.append(linea)
				campos.append(datos['mensaje'])
				Log.append(campos)
				AlgunError = True
			linea = f.readline()
		# 6. Procesos finales
		f.close()
		# 6.1 Crea el Log
		resultado = purchase.browse(cr, uid, purchase_id).wkf_confirm_order()
		resultado = purchase.browse(cr, uid, purchase_id).wkf_approve_order()
		invoice_id = purchase.browse(cr, uid, purchase_id).action_invoice_create()
		invoice.write(cr, uid, invoice_id, {'date_invoice':datos['fecha_causado']}, context=None)
		resultado = invoice.browse(cr, uid, invoice_id).invoice_validate()
		print "&&&&&&&& resultado -->", resultado
		print "&&&&&&&& Log -->", Log
		Loghtml = self.CreaLog(Log, nProceso)
		print "&&&&&&&& Loghtml -->", Loghtml
		# 6.2 Crea registro de historia procesos
		if AlgunError:
			resultado = 'Con errores'
		else:
			resultado = 'Sin errores'
		asocia2_data = {
			'procesos_id': ids[0],
			'fecha': date.today(),
			'resultado': resultado,
		}
		hist_procesos_id = hist_procesos.create(cr, uid, asocia2_data, context=context)
		# 6.3 Renombra el archivo de causaciones
		os.chdir(Directorio)
		i = 0
		NArchivo = nProceso + date.today().strftime('%Y-%m-%d') + str(i) + '.csv'
		NLog = nProceso + date.today().strftime('%Y-%m-%d') + str(i) + '.htm'
		while os.access(NArchivo, os.F_OK):
			i = i + 1
			NArchivo = nProceso + date.today().strftime('%Y-%m-%d') + str(i) + '.csv'
			NLog = nProceso + date.today().strftime('%Y-%m-%d') + str(i) + '.htm'
		Archivo = nProceso + '.csv'
		print "&&&&&&&& Archivo -->", Archivo, NArchivo
		os.rename(Archivo, NArchivo)
		# 6.4 Crea el Archivo de errores y Log
		self.CreaArchivo(ArchivoE,Archivo,Directorio)
		NLog = 'Log-' + NLog
		self.CreaArchivo(Loghtml,NLog,Directorio)
		return 'Fin del proceso'

	def causa_prestamo(self, cr, uid, ids, context=None):
		""" Procesa causacion de prestamos asociacion """
		""" genera causaciones para el proximo periodo """
		partner=self.pool.get('res.partner')
		product=self.pool.get('product.product')
		servicio_prestamo=self.pool.get('asocia2.servicio_prestamo')
		hist_servicio_prestamo=self.pool.get('asocia2.hist_servicio_prestamo')
		hist_procesos=self.pool.get('asocia2.hist_procesos')
		purchase = self.pool.get('purchase.order')
		invoice = self.pool.get('account.invoice')
		invoice_line = self.pool.get('account.invoice.line')
		linea_pres = self.pool.get('asocia2.invoice.line.prestamo')
		periodo = self.ProximoPeriodo(self.browse(cr, uid, ids[0]).periodos_id.control_procesos_id.periodo_actual)
		if os.name == 'posix':
			Directorio = '/home/helman/Procesos/' + self.browse(cr, uid, ids[0]).periodos_id.control_procesos_id.periodo_actual +'/'
		else:
			Directorio = 'c:\Procesos\\' + self.browse(cr, uid, ids[0]).periodos_id.control_procesos_id.periodo_actual +'\\'
		Log = []
		ArchivoE = []
		Convenio = self.browse(cr, uid, ids[0]).categ_id.name
		p = self.browse(cr, uid, ids[0]).proveedor_id
		if os.name == 'posix':
			Directorio = Directorio + Convenio + ' - ' + p.name + '/'
		else:
			Directorio = Directorio + Convenio + ' - ' + p.name + '\\'
		print "&&&&&&&& Directorio -->", Directorio
		nProceso = self.browse(cr, uid, ids[0]).nombre_proceso
		# 0. Crea purchase del proveedor
		asocia2_data = {
			'partner_id': p.id,
			'location_id': 17,
			'pricelist_id': 2,
			'cobro': True,
			'periodo': periodo,
		}
		purchase_id = purchase.create(cr, uid, asocia2_data, context=context)
		# 1. Crea titulos del Log
		campos = []
		campos.append('Cédula')
		campos.append('Nro. préstamo')
		campos.append('Valor Cuota')
		campos.append('Capital')
		campos.append('Interes')
		Log.append(campos)
		# 2. Busca los prestamos del mismo tipo (categ_id) activos
		categ_id = self.browse(cr, uid, ids[0]).categ_id.id
		resultado = servicio_prestamo.search(cr, uid, [('categ_id','=',categ_id),('estado','=','active')])
		AlgunError = False
		if resultado:
			for prestamo_id in resultado:
				pres = servicio_prestamo.browse(cr, uid, prestamo_id)
				tasa_interes = Decimal(str(pres.tasa_interes)) / Decimal('100')
				ValorCuota = Decimal(pres.valor_cuota).quantize(Decimal('1'))
				ValorPrestamo = Decimal(pres.vlr_prestamo)
				if self.HayCausacion(cr, uid, pres, periodo):
					pass
				else:
					datosp = self.DatosActuales(cr, uid, pres, periodo, True)
					if datosp[0] > 0:
						# 4. Si no hay causacion para el periodo y tiene deuda capital crea la causacion
						ValorInteres = (datosp[0] * tasa_interes).quantize(Decimal('1'))
						ValorCapital = ValorCuota - ValorInteres
						if ValorCapital > datosp[0]:
							#Si la deuda de capital es menor que lo que se va a causar. Cobrar solo la deuda de capital
							ValorCapital = datosp[0]
						CuotasCausadas = ((ValorPrestamo - datosp[0]) / ValorCuota).quantize(Decimal('1'))
						datos = {}
						ValorCuota = ValorCapital + ValorInteres
						datos['cuota'] = str(float(ValorCuota))
						#datos['fuente'] = Archivo
						datos['periodo'] = periodo
						#datos['soporte'] = Nro
						datos['fecha_procesado'] = date.today().strftime('%Y/%m/%d')
						datos['capital'] = str(float(ValorCapital))
						datos['interes'] = str(float(ValorInteres))
						print "&&&&&&&& fecha_pago1 -->", pres.fecha_pago1
						datos['fecha_causado'] = pres.ProximaFecha(datetime.strptime(pres.fecha_pago1,'%Y-%m-%d').date(),'mensual',12,CuotasCausadas)
						# 4.1.1. Graba la causacion
						datos['purchase_id'] = purchase_id
						datos['afiliado_id'] = pres.afiliado_id.id
						datos['producto_id'] = pres.product_id.id
						creados = self.GrabaCausacion(cr, uid, ids, pres, datos, context=None)
						invoice_line_id = invoice_line.search(cr, uid, [('invoice_id','=',creados['invoice_id']),('product_id','=',pres.product_id.id)])
						print "&&&&&&&& datos -->", datos, creados, invoice_line_id[0]
						# 4.1.2. Graba causacion detalles prestamo
						asocia2_data = {
							'invoice_line_id': invoice_line_id[0],
							'capital_causado': datos['capital'],
							'interes_causado': datos['interes'],
						}
						linea_pres_id = linea_pres.create(cr, uid, asocia2_data, context=context)
				datosp = self.DatosActuales(cr, uid, pres, periodo, True)
				# 5 Si ya fue cancelado marca el prestamo como finalizado y graba historia
				# Log de cambios 1.2.5
				if not(datosp[0] + datosp[1]) > 0:
					#raise RuntimeError(datosp,pres.Title())
					pres.edit(estado_servicio = 'finalizado')
					h_ref = {}
					h_ref['evento'] = 'desactivado'
					h_ref['fecha'] = date.today().strftime('%Y/%m/%d')
					h_ref['tipo'] = 'Pago completo'
					h_retiro_reing = pres.hist_activ_cancel + (h_ref,)
					pres.edit(hist_activ_cancel= h_retiro_reing)
		# Log de cambios 1.3.1 ====OOOOJJJJOOOO==== pendiente hasta que se creen los estados en otros conceptos y excedentes
		# 6 Cancela cuotas admon ya pagadas
		#resultado= self.portal_catalog.searchResults(path=Path_local,
		#                                             portal_type="otros_conceptos",)
		#if resultado:
		#  self.cancela_cuotas_admon(resultado)
		# 7.1 Actualiza fecha de proceso
		resultado = purchase.browse(cr, uid, purchase_id).wkf_confirm_order()
		resultado = purchase.browse(cr, uid, purchase_id).wkf_approve_order()
		invoice_id = purchase.browse(cr, uid, purchase_id).action_invoice_create()
		invoice.write(cr, uid, invoice_id, {'date_invoice':datos['fecha_causado']}, context=None)
		resultado = invoice.browse(cr, uid, invoice_id).invoice_validate()
		# 7.2 Crea registro de historia procesos
		if AlgunError:
			resultado = 'Con errores'
		else:
			resultado = 'Sin errores'
		asocia2_data = {
			'procesos_id': ids[0],
			'fecha': date.today(),
			'resultado': resultado,
		}
		hist_procesos_id = hist_procesos.create(cr, uid, asocia2_data, context=context)
		return 'Fin del proceso'

	def causa_Convenio_pago(self, cr, uid, ids, context=None):
		""" Procesa causacion (cobros) de convenios de pago """

		partner=self.pool.get('res.partner')
		product=self.pool.get('product.product')
		product_template=self.pool.get('product.template')
		product_category=self.pool.get('product.category')
		servicio_aportes=self.pool.get('asocia2.servicio_aportes')
		servicio_prestamo=self.pool.get('asocia2.servicio_prestamo')
		servicio_credito=self.pool.get('asocia2.servicio_credito')
		servicio_generico=self.pool.get('asocia2.servicio_generico')
		hist_procesos=self.pool.get('asocia2.hist_procesos')
		asoc_vinculados=self.pool.get('asocia2.vinculados')
		periodo = self.ProximoPeriodo(self.browse(cr, uid, ids[0]).periodos_id.control_procesos_id.periodo_actual)
		p = self.browse(cr, uid, ids[0]).proveedor_id
		if os.name == 'posix':
			Directorio = '/home/helman/Procesos/' + self.browse(cr, uid, ids[0]).periodos_id.control_procesos_id.periodo_actual +'/'
		else:
			Directorio = 'c:\Procesos\\' + self.browse(cr, uid, ids[0]).periodos_id.control_procesos_id.periodo_actual +'\\'
		if periodo[5:7] == '06':
		#if periodo[5:7] == '05':
			Prima = True
		else:
			Prima = False
		if os.name == 'posix':
			Directorio = Directorio + 'Convenio_pago' + ' - ' + p.name.decode('utf-8') + '/'
		else:
			Directorio = Directorio + 'Convenio_pago' + ' - ' + p.name.decode('utf-8') + '\\'
		if not os.access(Directorio, os.F_OK):
			raise RuntimeError('El directorio ' + Directorio + ' no existe o no es accesible')
		# 1. Busca los aportes de este convenio de pago
		convenio_pago_id = self.browse(cr, uid, ids[0]).proveedor_id.conv_pago_ids.id
		resultado = servicio_aportes.search(cr, uid, [('convenio_pago_id','=',convenio_pago_id),('estado','=','active')])
		print "&&&&&&&& periodo -->", periodo, Prima, self, ids, Directorio, resultado, convenio_pago_id
		if resultado:
			TNormal = Decimal('0')
			TPrima = Decimal('0')
			CNormal = 0
			CPrima = 0
			DNormal = []
			DPrima = []
			for aporte in resultado:
				apor = servicio_aportes.browse(cr, uid, aporte)
				afil=apor.afiliado_id
				deuda = Decimal('0')
				cuotas = Decimal('0')
				# 1.1. Acumula el total de cuotas y deuda del afiliado
				datosp = self.DatosActuales(cr, uid, apor, periodo, False)
				# Log de cambios 1.2.3
				cuotaServicio = Decimal(datosp[1])
				deudaServicio = Decimal(datosp[0]) - Decimal(datosp[1])
				if deudaServicio > 0:
					deuda = deuda + deudaServicio
				else:
					if cuotaServicio + deudaServicio > 0:
						cuotaServicio = cuotaServicio + deudaServicio
					else:
						cuotaServicio = Decimal('0')
				cuotas = cuotas + cuotaServicio
				pres = servicio_prestamo.search(cr, uid, [('afiliado_id','=',afil.id)])
				for p in pres:
					datosp = self.DatosActuales(cr, uid, servicio_prestamo.browse(cr, uid, p), periodo, True)
					#if p.numero_prestamo == '6012003':
					#  raise RuntimeError(datosp,p.Title(),p.numero_prestamo)
					# Log de cambios 1.2.3
					cuotaServicio = Decimal(datosp[4]) + Decimal(datosp[3]) - Decimal(datosp[6]) - Decimal(datosp[8]) - Decimal(datosp[10])
					if Prima:
						deudaServicio = Decimal(datosp[1]) + Decimal(datosp[2]) - Decimal(datosp[5]) - Decimal(datosp[7]) - Decimal(datosp[9]) - cuotaServicio
					else:
						deudaServicio = Decimal(datosp[1]) + Decimal(datosp[2]) - Decimal(datosp[5]) - Decimal(datosp[7]) - Decimal(datosp[9])
					print "&&&&&&&& cuotaServicio -->", cuotaServicio, deudaServicio
					if deudaServicio > cuotaServicio:
						deuda = deuda + deudaServicio - cuotaServicio
					else:
						if deudaServicio < cuotaServicio:
							if deudaServicio > 0:
								cuotaServicio = deudaServicio
							else:
								cuotaServicio = Decimal('0')
					cuotas = cuotas + cuotaServicio
				creds = servicio_credito.search(cr, uid, [('afiliado_id','=',afil.id)])
				for cre in creds:
					datosp = self.DatosActuales(cr, uid, servicio_credito.browse(cr, uid, cre), periodo, False)
					# Log de cambios 1.2.3
					cuotaServicio = Decimal(datosp[4]) - Decimal(datosp[6]) - Decimal(datosp[8]) - Decimal(datosp[10])
					if Prima:
						deudaServicio = Decimal(datosp[1]) - Decimal(datosp[5]) - Decimal(datosp[7]) - Decimal(datosp[9]) - cuotaServicio
					else:
						deudaServicio = Decimal(datosp[1]) - Decimal(datosp[5]) - Decimal(datosp[7]) - Decimal(datosp[9])
					print "&&&&&&&& cuotaServicio -->", cuotaServicio, deudaServicio
					if deudaServicio > cuotaServicio:
						deuda = deuda + deudaServicio - cuotaServicio
					else:
						if deudaServicio < cuotaServicio:
							if deudaServicio > 0:
								cuotaServicio = deudaServicio
							else:
								cuotaServicio = Decimal('0')
					cuotas = cuotas + cuotaServicio
				servs = servicio_generico.search(cr, uid, [('afiliado_id','=',afil.id)])
				for s in servs:
					datosp = self.DatosActuales(cr, uid, servicio_generico.browse(cr, uid, s), periodo, False)
					# Log de cambios 1.2.3
					cuotaServicio = Decimal(datosp[4]) - Decimal(datosp[6]) - Decimal(datosp[8]) - Decimal(datosp[10])
					if Prima:
						deudaServicio = Decimal(datosp[1]) - Decimal(datosp[5]) - Decimal(datosp[7]) - Decimal(datosp[9]) - cuotaServicio
					else:
						deudaServicio = Decimal(datosp[1]) - Decimal(datosp[5]) - Decimal(datosp[7]) - Decimal(datosp[9])
					print "&&&&&&&& cuotaServicio -->", cuotaServicio, deudaServicio
					if deudaServicio > cuotaServicio:
						deuda = deuda + deudaServicio - cuotaServicio
					else:
						if deudaServicio < cuotaServicio:
							if deudaServicio > 0:
								cuotaServicio = deudaServicio
							else:
								cuotaServicio = Decimal('0')
					cuotas = cuotas + cuotaServicio
				cat_id = product_category.search(cr, uid, [('name','=','Otros')])
				pts = product_template.search(cr, uid, [('categ_id','=',cat_id)])
				if pts:
					for p in pts:
						otrs = product.search(cr, uid, [('product_tmpl_id','=',p)])
						print "&&&&&&&& otrs -->", otrs, cat_id, pts
						datosp = self.DatosActualesProducto(cr, uid, product.browse(cr, uid, p), afil, periodo)
						# Log de cambios 1.2.3
						cuotaServicio = Decimal(datosp[4]) - Decimal(datosp[6]) - Decimal(datosp[8]) - Decimal(datosp[10])
						if Prima:
							deudaServicio = Decimal(datosp[1]) - Decimal(datosp[5]) - Decimal(datosp[7]) - Decimal(datosp[9]) - cuotaServicio
						else:
							deudaServicio = Decimal(datosp[1]) - Decimal(datosp[5]) - Decimal(datosp[7]) - Decimal(datosp[9])
						print "&&&&&&&& cuotaServicio -->", cuotaServicio, deudaServicio
						if deudaServicio > cuotaServicio:
							deuda = deuda + deudaServicio - cuotaServicio
						else:
							if deudaServicio < cuotaServicio:
								if deudaServicio > 0:
									cuotaServicio = deudaServicio
								else:
									cuotaServicio = Decimal('0')
						cuotas = cuotas + cuotaServicio
				"""
				# 1.2. Resta excedentes de cuotas
				excs = afil.objectValues(['excedentes'])
				if excs:
					for e in excs:
						datosp = e.DatosActuales(periodo)
						#if afil.cedula == 6751896:
						#  raise RuntimeError(datosp,afil.Title(),afil.cedula)
						ValorExcedente = Decimal(datosp[0])
						if ValorExcedente > deuda:
							deuda = Decimal('0')
							ValorExcedente = ValorExcedente - deuda
						else:
							deuda = deuda - ValorExcedente
							ValorExcedente = Decimal('0')
						if ValorExcedente > cuotas:
							cuotas = Decimal('0')
						else:
							cuotas = cuotas - ValorExcedente
				"""
				# 1.3. Acumula y agrega a lista de datos
				TNormal = TNormal + cuotas.quantize(Decimal('1'))
				TPrima = TPrima + deuda.quantize(Decimal('1'))
				# Log de cambios 1.2.6
				sustitucion = asoc_vinculados.search(cr, uid, [('afiliado_id','=',afil.id)])
				if sustitucion:
					cedula_br = afil.convierte_cedula_BR()
					#raise RuntimeError(afil.cedula,cedula_br)
					if cedula_br == 'NO':
						raise RuntimeError('La cédula ' + afil.cedula + ' no tiene el formato solicitado para sustitucion (12 digitos y los dos primeros 99')
				else:
					cedula_br = str(afil.cc_afiliado)
				print "&&&&&&&& cuotas -->", cuotas, deuda
				if Prima:
					if cuotas > 0:
						desc_requerido = {'cedula':cedula_br,'concepto':'825','valor':str(float(cuotas.quantize(Decimal('1')))),'tipo_proceso':'070'}
						DNormal.append(desc_requerido)
						CNormal = CNormal + 1
					if deuda > 0:
						 desc_requerido = {'cedula':cedula_br,'concepto':'825','valor':str(float(deuda.quantize(Decimal('1')))),'tipo_proceso':'074'}
						 DPrima.append(desc_requerido)
						 CPrima = CPrima + 1
				else:
					if cuotas + deuda > 0:
						desc_requerido = {'cedula':cedula_br,'concepto':'825','valor':str(float(cuotas.quantize(Decimal('1')) + deuda.quantize(Decimal('1')))),'tipo_proceso':'070'}
						DNormal.append(desc_requerido)
						CNormal = CNormal + 1
				"""
			# 2. Graba mvto_pago
			proveed = a.objectValues(['proveedores'])
			proveedores = proveed[0].objectValues(['proveedor'])
			for p in proveedores:
			  convenios = p.objectValues(['convenio_pago'])
			  if convenios:
				for conv in convenios:
				  if conv.Title() == Convapor:
					mvts = conv.objectValues(['mvto_pago'])
					CreaMvto = True
					if mvts:
					  for m in mvts:
						if m.periodo == periodo:
						  # 2.1 Actualiza datos de mvto_pago
						  a = CNormal
						  datos = DNormal
						  if Prima:
							a = a + CPrima
							datos.extend(DPrima)
						  m.Schema()['requeridos'].resize(a,m)
						  m.update(requeridos = datos)
						  m.Schema()['requeridos'].Schema().fields()[0].set(m,a)
						  x = m.getRequeridos()
						  CreaMvto = False
						  #raise RuntimeError('Modifica',m,datos,a,DNormal,DPrima)
					if CreaMvto:
					  # 2.2 Crea el objeto mvto_pago
					  id = 'Movimiento ' + periodo
					  conv.invokeFactory("mvto_pago", id)
					  m = conv[id]
					  m.edit(periodo = periodo)
					  m.editMetadata(title = id)
					  a = CNormal
					  datos = DNormal
					  if Prima:
						a = a + CPrima
						datos.extend(DPrima)
					  m.Schema()['requeridos'].resize(a,m)
					  m.update(requeridos = datos)
					  m.Schema()['requeridos'].Schema().fields()[0].set(m,a)
				"""
			# 3. Crea archivo de novedades segun formato Banrepublica
			Archivo = 'Nov07000-' + periodo + '.dat'
			Novedades = []
			if Prima:
				linea = '070     00' + str(int(TNormal)).rjust(10) + '00' + str(CNormal).rjust(5) + ' 01' + periodo[5:7] + periodo[0:4] + '00\n'
			else:
				linea = '070     00' + str(int(TNormal+TPrima)).rjust(10) + '00' + str(CNormal).rjust(5) + ' 01' + periodo[5:7] + periodo[0:4] + '00\n'
			#raise RuntimeError(TNormal,TPrima,CNormal,linea)
			Novedades.append(linea)
			for d in DNormal:
				if d:
					linea = str(d['cedula']).rjust(11) + '825     00' + str(int(round(float(d['valor'])))).rjust(10) + '0001' + periodo[5:7] + periodo[0:4] + '\n'
					Novedades.append(linea)
			self.CreaArchivo(Novedades,Archivo,Directorio)
			if Prima:
				Archivo = 'Nov07400-' + periodo + '.dat'
				Novedades = []
				# Log de cambios 1.2.3
				linea = '074 00' + str(int(TPrima)).rjust(10) + '00' + str(CPrima).rjust(5) + ' 15' + periodo[5:7] + periodo[0:4] + '00\n'
				Novedades.append(linea)
				for d in DPrima:
					if d:
						linea = str(d['cedula']).rjust(11) + '825     00' + str(int(round(float(d['valor'])))).rjust(10) + '0015' + periodo[5:7] + periodo[0:4] + '\n'
						Novedades.append(linea)
				self.CreaArchivo(Novedades,Archivo,Directorio)
			# 4 Actualiza fecha de proceso
			asocia2_data = {
				'procesos_id': ids[0],
				'fecha': date.today(),
				'resultado': 'Sin errores',
			}
			hist_procesos_id = hist_procesos.create(cr, uid, asocia2_data, context=context)
		return 'Fin del proceso'

	def pago_Convenio_pago(self, cr, uid, ids, context=None):
		""" Procesa los pagos de convenios de pago """

		partner=self.pool.get('res.partner')
		servicio_aportes=self.pool.get('asocia2.servicio_aportes')
		purchase = self.pool.get('purchase.order')
		hist_procesos=self.pool.get('asocia2.hist_procesos')
		voucher=self.pool.get('account.voucher')
		voucher_line=self.pool.get('account.voucher.line')
		excedentes=self.pool.get('asocia2.excedentes')
		excedentes_vouchers=self.pool.get('asocia2.excedentes_vouchers')
		p = self.browse(cr, uid, ids[0]).proveedor_id
		if os.name == 'posix':
			Directorio = '/home/helman/Procesos/' + self.browse(cr, uid, ids[0]).periodos_id.control_procesos_id.periodo_actual +'/'
		else:
			Directorio = 'c:\Procesos\\' + self.browse(cr, uid, ids[0]).periodos_id.control_procesos_id.periodo_actual +'\\'
		if os.name == 'posix':
			Directorio = Directorio + 'Convenio_pago' + ' - ' + p.name.decode('utf-8') + '/'
		else:
			Directorio = Directorio + 'Convenio_pago' + ' - ' + p.name.decode('utf-8') + '\\'
		if not os.access(Directorio, os.F_OK):
			raise RuntimeError('El directorio ' + Directorio + ' no existe o no es accesible')
		nProceso = self.browse(cr, uid, ids[0]).nombre_proceso
		Archivo = nProceso + '.csv'
		if not os.access(Directorio+Archivo, os.F_OK):
			raise osv.except_osv(_('Error!'), _('El archivo '+Archivo + ' no existe en el directorio ' + Directorio))
		f = open(Directorio+Archivo,"rU")
		# 0. Crea purchase del proveedor
		asocia2_data = {
			'partner_id': p.id,
			'location_id': 17,
			'pricelist_id': 2,
			'cobro': True,
			'periodo': self.browse(cr, uid, ids[0]).periodos_id.control_procesos_id.periodo_actual,
		}
		purchase_id = purchase.create(cr, uid, asocia2_data, context=context)
		# 1. Busca convenio de pago para obtener porcentaje para aportes
		cnv_porce = Decimal(str(self.browse(cr, uid, ids[0]).proveedor_id.conv_pago_ids.porcentaje_para_aportes))
		conv = self.browse(cr, uid, ids[0]).proveedor_id.conv_pago_ids
		# 2. Realiza la aplicacion automatica de pagos de cortesias
		self.pago_cortesias(cr, uid, ids, context=None)
		CNormal = 0
		DNormal = []
		linea = f.readline()
		linea = f.readline()
		while linea:
			campos = re.split(";",linea)
			datos = {}
			datos['mensaje'] = ''
			# Log de cambios 1.2.6
			datos['cedula'] = self.interpreta_cedula_BR(campos[1])
			print "&&&&&&&& campos -->", campos
			# Log de cambios 1.1.3
			if campos[1]:
				if campos[9][-1:] == ' ':
					q = 4
				else:
					q = 3
				#raise RuntimeError(campos[11],'-',campos[11][-1:],'-',q)
				if '.' in campos[9][:-q]:
					raise RuntimeError('Verifique el formato regional del equipo (windows). El separador de miles debe ser ,(coma) y en el archivo se tiene este:'+campos[12])
				else:
					datos['cuota'] = campos[8][:-q].replace(',', '')+'.00'
					datos['capital'] = 0
					datos['interes'] = 0
					datos['fuente'] = 'Convenio_pago' + ' - ' + p.name.decode('utf-8')
					datos['periodo'] = self.browse(cr, uid, ids[0]).periodos_id.control_procesos_id.periodo_actual
					datos['soporte'] = campos[4]
					datos['fecha_procesado'] = date.today().strftime('%Y/%m/%d')
					datos['fecha_causado'] = date.today().strftime('%Y/%m/%d')
				if campos[11][:-3] == '1':
					datos['tipo_proceso'] = '070'
				else:
					datos['tipo_proceso'] = '074'
				resultado= partner.search(cr, uid, [('membership','=',True),('cc_afiliado','=',datos['cedula'])])
				if not resultado:
					Correcto = False
					datos['mensaje'] = "El afiliado con cedula '%s' no existe"% datos['cedula']
					#raise RuntimeError(datos['mensaje'])
				else:
					afil=partner.browse(cr, uid, resultado[0])
					regional=afil.regional
					if not afil.state=='confirmed':
						Correcto = False
						datos['mensaje'] = "El afiliado con cedula '%s' no esta activo"% datos['cedula']
						#raise RuntimeError(datos['mensaje'])
					if campos[4] == '820':
						# 1. Actualiza valor pension , aporte y regional
						apors = servicio_aportes.search(cr, uid, [('afiliado_id','=',afil.id),('convenio_pago_id','=',self.browse(cr, uid, ids[0]).proveedor_id.conv_pago_ids.id),('estado','=','active')])
						for a in apors:
							asocia2_data = {
								'regional':campos[0],
							}
							partner.write(cr, uid, afil.id, asocia2_data, context=None)
							pension = Decimal(datos['cuota']) * Decimal(100) / cnv_porce
							asocia2_data = {
								'valor_pension':pension,
								'valor_cuota':datos['cuota'],
							}
							servicio_aportes.write(cr, uid, a, asocia2_data, context=None)
							apor = servicio_aportes.browse(cr, uid, a)
							# 2. Causa aportes del periodo si no existen
							if self.HayCausacion(cr, uid, apor, datos['periodo']):
								pass
							else:
								datos['purchase_id'] = purchase_id
								datos['afiliado_id'] = afil.id
								datos['producto_id'] = apor.product_id.id
								print "&&&&&&&& datos -->", datos
								self.GrabaCausacion(cr, uid, ids, apor, datos, context=None)
					datos['cuota'] = campos[9][:-q].replace(',', '')+'.00'
					# 3. Aplicar pago segun orden descuentos de nomina
					if Decimal(datos['cuota']) > 0:
						datos['valor_aplicar'] = Decimal(datos['cuota'])
						Deuda = self.AplicaPagoNomina(cr, uid, afil, conv, datos, False, context=None)
					# 4. Aplicar automaticamente excedente si hay deuda
					if Deuda > 0:
						resultado = excedentes.search(cr, uid, [('afiliado_id','=',afil.id)])
						for r in resultado:
							saldoExcedentes = excedentes.browse(cr, uid, r).saldo
							if saldoExcedentes > 0:
								resultado1 = excedentes_vouchers.search(cr, uid, [('excedentes_vouchers_id','=',r)])
								if resultado1:
									for r1 in resultado1:
										datos['valor_aplicar'] = excedentes_vouchers.browse(cr, uid, r).valor
										voucher_id = excedentes_vouchers.browse(cr, uid, r).voucher_id
										v = voucher.browse(cr, uid, voucher_id)
										res = voucher.browse(cr, uid, voucher_id).recompute_voucher_lines(afil.id, v.journal_id.id, 0, v.currency_id.id, v.type, v.date, context=context)
										Deuda1 = self.AplicacionAutomatica(cr, uid, afil, conv, datos, False, voucher_id, context=None)
										for rc in res['value']['line_cr_ids']:
											print "&&&&&&&& OJO rc inicial -->", rc
											rc['voucher_id'] = voucher_id
											print "&&&&&&&& rc final -->", rc
											vouc_line_id = voucher_line.create(cr, uid, rc, context=context)
										for rd in res['value']['line_dr_ids']:
											print "&&&&&&&& OJO rd inicial -->", rd
											rd['voucher_id'] = voucher_id
											print "&&&&&&&& rd final -->", rd
											vouc_line_id = voucher_line.create(cr, uid, rd, context=context)
										resultado = voucher.browse(cr, uid, voucher_id).action_move_line_create()
					"""
					# 5. Agrega datos a la lista de reportado convenio de pago
					desc_realizado = {'cedula':campos[1],'regional':campos[0],'concepto':campos[4],'valor_reportado':campos[8][:-q].replace(',', '')+'.00','valor_aplicado':campos[9][:-q].replace(',', '')+'.00','valor_devuelto':campos[10][:-q].replace(',', '')+'.00','tipo_proceso':datos['tipo_proceso'],'nombres':datos['mensaje']}
					DNormal.append(desc_realizado)
					CNormal = CNormal + 1
					"""
			linea = f.readline()
		"""
		# 6. Graba reportado en mvto_pago
		mvts = conv.objectValues(['mvto_pago'])
		CreaMvto = True
		if mvts:
			for m in mvts:
			  if m.periodo == datos['periodo']:
				# 6.1 Actualiza datos de mvto_pago
				a = CNormal
				m.Schema()['realizados'].resize(a,m)
				m.update(realizados = DNormal)
				m.Schema()['realizados'].Schema().fields()[0].set(m,a)
				x = m.getRealizados()
				CreaMvto = False
		if CreaMvto:
			raise RuntimeError('Error grave, no existe el objeto mvto_pago para este convenio:',conv.Title(),datos['periodo'])
		"""
		# 7. Actualiza fecha de proceso
		asocia2_data = {
			'procesos_id': ids[0],
			'fecha': date.today(),
			'resultado': 'Sin errores',
		}
		hist_procesos_id = hist_procesos.create(cr, uid, asocia2_data, context=context)
		return 'Fin del proceso'

	def pago_cortesias(self, cr, uid, ids, context=None):
		""" Procesa los pagos de cortesias para todos los afiliados """

		servicio_aportes=self.pool.get('asocia2.servicio_aportes')
		servicio_prestamo=self.pool.get('asocia2.servicio_prestamo')
		servicio_credito=self.pool.get('asocia2.servicio_credito')
		servicio_generico=self.pool.get('asocia2.servicio_generico')
		periodo = self.browse(cr, uid, ids[0]).periodos_id.control_procesos_id.periodo_actual
		# 1. Busca los servicios activos con cortesias mayores que cero
		resultado= servicio_aportes.search(cr, uid, [('estado','=','active'),'|',('valor_cortesia_asociacion','>',0),('valor_cortesia_proveedor','>',0)])
		# Ojo----- Falta incluir todos los servicios en esta busqueda
		if resultado:
			for serv in resultado:
				afil = afiliado.getObject()
				if afil.estado_afil=='activo':
					# 2. Aplica cortesias a los servicios activos con cortesia
					serv = afil.objectValues(['convenio_de_credito']) + afil.objectValues(['convenio_comercial']) + afil.objectValues(['prestamo'])
					if serv:
						for s in serv:
							if s.estado_servicio=='activo':
								datosp = s.DatosActuales(periodo)
								if s.portal_type=='prestamo':
									if (Decimal(datosp[7]) > 0 or Decimal(datosp[9]) > 0):
										#raise RuntimeError(afil.Title(),s.Title(),periodo,datosp)
										afil.AplicaCortesiaPrestamo(s, periodo, datosp)
								else:
									if (Decimal(datosp[4]) > 0 or Decimal(datosp[6]) > 0):
										#raise RuntimeError(afil.Title(),s.Title(),periodo,datosp)
										afil.AplicaCortesiaGeneral(s, periodo, datosp)
		return

	def CreaLog(self, log, nProceso):
		""" Crea el log del proceso en formato html """
		fecha = date.today()
		titulo = nProceso + ' ' + str(fecha)
		#Agrega titulo
		textlog = '<h3>LOG DE ERRORES DEL PROCESO</h3><br><h3>' + titulo + '</h3><br>'
		#Almacena el contenido del log en el documento
		datos = '<table border="""1""" cellspacing="""0""" bordercolor="""navy""" width="""100%"""><tbody>'
		for linea in log:
			renglon = ''
			for dato in linea:
				renglon = renglon + '<td>' + str(dato) + '</td>'
			datos = datos + '<tr>' + renglon + '</tr>'
		datos = datos + '</tbody></table>'
		textlog = textlog + datos
		return textlog
		
	def CreaArchivo(self, contenido, nombre, directorio):
		""" Crea el archivo con los registros no procesados """
		f = open(directorio+nombre,"w")
		for linea in contenido:
			f.write(linea)
		f.close()
		return

	def GrabaCausacion(self, cr, uid, ids, obj, datos, context=None):
		""" Crea Purchase line y Sale """
		p_order_line = self.pool.get('purchase.order.line')
		sale = self.pool.get('sale.order')
		s_order_line = self.pool.get('sale.order.line')
		invoice = self.pool.get('account.invoice')
		creados = {}
		# 1. Crea Purchase line
		asocia2_data = {
			'order_id': datos['purchase_id'],
			'product_id': datos['producto_id'],
			'product_qty': 1.0,
			'price_unit': datos['cuota'],
			'name': ' ',
			'date_planned': datos['fecha_causado'],
		}
		purchase_line_id = p_order_line.create(cr, uid, asocia2_data, context=context)
		creados['purchase_line_id'] = purchase_line_id
		# 2. Crea Sale para afiliado
		asocia2_data = {
			'partner_id': datos['afiliado_id'],
			'cobro': True,
			'periodo': datos['periodo'],
		}
		sale_id = sale.create(cr, uid, asocia2_data, context=context)
		creados['sale_id'] = sale_id
		asocia2_data = {
			'order_id': sale_id,
			'product_id': datos['producto_id'],
			'product_uom_qty': 1.0,
			'product_uos_qty': 1.0,
			'price_unit': datos['cuota'],
		}
		sale_line_id = s_order_line.create(cr, uid, asocia2_data, context=context)
		creados['sale_line_id'] = sale_line_id
		resultado = sale.browse(cr, uid, sale_id).action_button_confirm()
		invoice_id = sale.browse(cr, uid, sale_id).action_invoice_create()
		creados['invoice_id'] = invoice_id
		asocia2_data = {
			'date_invoice':datos['fecha_causado'],
			'cobro': True,
			'periodo': datos['periodo'],
		}
		invoice.write(cr, uid, invoice_id, asocia2_data, context=None)
		resultado = invoice.browse(cr, uid, invoice_id).action_move_create()
		resultado = invoice.browse(cr, uid, invoice_id).invoice_validate()
		return creados

	def GrabaCausacionPropia(self, cr, uid, ids, obj, datos, context=None):
		""" Crea Sale """
		sale = self.pool.get('sale.order')
		s_order_line = self.pool.get('sale.order.line')
		invoice = self.pool.get('account.invoice')
		# 1. Crea Sale para afiliado
		asocia2_data = {
			'partner_id': datos['afiliado_id'],
			'cobro': True,
			'periodo': datos['periodo'],
		}
		sale_id = sale.create(cr, uid, asocia2_data, context=context)
		asocia2_data = {
			'order_id': sale_id,
			'product_id': datos['producto_id'],
			'product_uom_qty': 1.0,
			'product_uos_qty': 1.0,
			'price_unit': datos['cuota'],
		}
		print "&&&&&&&& asocia2_data -->", asocia2_data
		sale_line_id = s_order_line.create(cr, uid, asocia2_data, context=context)
		resultado = sale.browse(cr, uid, sale_id).action_button_confirm()
		invoice_id = sale.browse(cr, uid, sale_id).action_invoice_create()
		asocia2_data = {
			'date_invoice':datos['fecha_causado'],
			'cobro': True,
			'periodo': datos['periodo'],
		}
		invoice.write(cr, uid, invoice_id, asocia2_data, context=None)
		resultado = invoice.browse(cr, uid, invoice_id).action_move_create()
		resultado = invoice.browse(cr, uid, invoice_id).invoice_validate()
		return

	def HayCausacion(self, cr, uid, obj, periodo):
		""" Devuelve True si hay causaciones (invoice) para ese periodo """
		HayCausacion = False
		sale = self.pool.get('account.invoice')
		s_order_line = self.pool.get('account.invoice.line')
		print "&&&&&&&& self -->", self, obj, obj.afiliado_id.id, periodo
		Causado = sale.search(cr, uid, [('partner_id','=',obj.afiliado_id.id),('periodo','=',periodo)])
		print "&&&&&&&& Causado -->", Causado
		for c in Causado:
			resultado = s_order_line.search(cr, uid, [('invoice_id','=',sale.browse(cr, uid, c).id)])
			print "&&&&&&&& resultado -->", c, resultado, obj.product_id.id, s_order_line.browse(cr, uid, resultado).product_id.id
			if obj.product_id.id == s_order_line.browse(cr, uid, resultado).product_id.id:
				HayCausacion = True
		return HayCausacion
		
	def interpreta_cedula_BR(self,cedula_br):
		""" Esta funcion convierte la cedula del formato BR"""
		if  cedula_br[:1]=='0':
			cedula_tem =  990000000000+int(cedula_br)
			return cedula_tem
		else:
			return int(cedula_br)

	def DatosActuales(self, cr, uid, obj, periodo, prestamo):
		""" Devuelve DeudaTotal, DeudaCaja, DeudaCortesiaAsociacion, DeudaCortesiaProveedor, PrimerPeriodoDeuda
			Si es Prestamo ademas devuelve SaldoCapital, DeudaCapital, DeudaInteres, ValorInteres, ValorCapital """
		#tasa_interes = Decimal(str(self.getTasa_interes())) / Decimal('100')
		#ValorCuota = Decimal(self.getValor_cuota()).quantize(Decimal('1'))
		#c = 0
		#p = 0
		#NCuota = 1
		#per = periodoi
		Datos = []
		sale = self.pool.get('sale.order')
		s_order_line = self.pool.get('sale.order.line')
		s_order_line_invoice_rel = self.pool.get('sale.order.invoice_rel')
		account_invoice_line = self.pool.get('account.invoice.line')
		account_invoice = self.pool.get('account.invoice')
		invoice_prestamo = self.pool.get('asocia2.invoice.line.prestamo')
		print "&&&&&&&& self -->", self, obj, periodo
		print "&&&&&&&& self1 -->", obj.afiliado_id.id, obj.product_id.id
		DeudaCaja = Decimal('0')
		CuotaCaja = Decimal('0')
		DeudaAsociacion = Decimal('0')
		CuotaAsociacion = Decimal('0')
		DeudaProveedor = Decimal('0')
		CuotaProveedor = Decimal('0')
		DeudaCapital = Decimal('0')
		DeudaInteres = Decimal('0')
		ValorInteres = Decimal('0')
		ValorCapital = Decimal('0')
		SaldoCapital = Decimal('0')
		PrimerPeriodoDeuda = ''
		ControlInicioDeuda = True
		if prestamo:
			periodod = datetime.strptime(obj.fec_desembolso,'%Y-%m-%d').strftime('%Y-%m')
			if periodod > periodo:
				SaldoCapital = Decimal('0')
			else:
				SaldoCapital = Decimal(obj.vlr_prestamo)
			print "&&&&&&&& SaldoCapital -->", SaldoCapital
		#resultado = s_order_line.search(cr, uid, [('product_id','=',obj.product_id.id)])
		resultado = account_invoice_line.search(cr, uid, [('product_id','=',obj.product_id.id),('partner_id','=',obj.afiliado_id.id)])
		print "&&&&&&&& resultado -->", resultado
		for r in resultado:
			"""
			Tablas a utilizar para ver deuda
			sale_order_line_invoice_rel (linea que le corresponde en invoice a este producto)
			account_invoice_line (lineas de invoice - invoice_id)
			account_invoice (residual_numeric corresponde al valor por pagar de esta factura)
			"""
			#cr.execute('SELECT rel.invoice_id ' \
			#	'FROM sale_order_line_invoice_rel AS rel WHERE rel.order_line_id = ' + str(r))
			#invoice_line_id = cr.fetchall()[0][0]
			#invoice = account_invoice_line.browse(cr, uid, invoice_line_id).invoice_id
			invoice = account_invoice_line.browse(cr, uid, r).invoice_id
			#res = account_invoice.search(cr, uid, [('id','=',invoice_id)])
			#print "&&&&&&&& r -->", r, invoice_line_id, invoice, invoice.residual, invoice.amount_total
			print "&&&&&&&& r -->", r, invoice, invoice.residual, invoice.amount_total, periodo, invoice.periodo
			if not invoice.periodo > periodo:
				if prestamo:
					res = invoice_prestamo.search(cr, uid, [('invoice_line_id','=',r)])
					inv_pres = invoice_prestamo.browse(cr, uid, res[0])
					print "&&&&&&&& inv_pres -->", inv_pres, inv_pres.id, inv_pres.capital_causado, inv_pres.interes_causado, inv_pres.capital_pagado, inv_pres.interes_pagado
					SaldoCapital = SaldoCapital - Decimal(inv_pres.capital_causado)
					DeudaCapital = DeudaCapital + Decimal(inv_pres.capital_causado - inv_pres.capital_pagado)
					DeudaInteres = DeudaInteres + Decimal(inv_pres.interes_causado - inv_pres.interes_pagado)
					ValorCapital = ValorCapital + Decimal(inv_pres.capital_causado - inv_pres.capital_pagado)
					ValorInteres = ValorInteres + Decimal(inv_pres.interes_causado - inv_pres.interes_pagado)
					print "&&&&&&&& valores finales -->", SaldoCapital, DeudaCapital, DeudaInteres, ValorCapital, ValorInteres
					# Pendiente de manejar los valores de Caja, Asociacion y Proveedores
				else:
					valor_pagado = Decimal(invoice.amount_total - invoice.residual)
					if valor_pagado > 0:
						DeudaCapital = DeudaCapital - valor_pagado
						if self.pago_x_caja:
							if p['tipo_documento'] == 'Caja':
								if Decimal(str(self.getVlr_pag_caja())) > Decimal(p['valor_pagado']):
									DeudaCaja = DeudaCaja - Decimal(p['valor_pagado'])
								else:
									DeudaCaja = DeudaCaja - Decimal(str(self.getVlr_pag_caja()))
						# Log de cambios 1.2.1
						if invoice.periodo == periodo:
							ValorCapital = ValorCapital - Decimal(p['capital_pagado'])
							ValorInteres = ValorInteres - Decimal(p['interes_pagado'])
							if p['tipo_documento'] == 'Caja':
								CuotaCaja = CuotaCaja - Decimal(p['valor_pagado'])
							if p['tipo_documento'] == 'Cortesia asociacion':
								CuotaAsociacion = CuotaAsociacion - Decimal(p['valor_pagado'])
							if p['tipo_documento'] == 'Cortesia proveedor':
								CuotaProveedor = CuotaProveedor - valor_pagado
					DeudaCapital = DeudaCapital + Decimal(invoice.amount_total)
					Deuda = DeudaInteres + DeudaCapital
					if Deuda > 0 and ControlInicioDeuda:
						PrimerPeriodoDeuda = invoice.periodo
						ControlInicioDeuda = False
					if obj.vlr_pag_caja > 0:
						if Decimal(str(self.getVlr_pag_caja())) > Decimal(c['valor_causado']):
							DeudaCaja = DeudaCaja + Decimal(c['valor_causado'])
						else:
							DeudaCaja = DeudaCaja + Decimal(str(self.getVlr_pag_caja()))
					# Log de cambios 1.2.1
					if invoice.periodo == periodo:
						ValorCapital = ValorCapital + Decimal(invoice.amount_total)
						if obj.vlr_pag_caja > 0:
							CuotaCaja = CuotaCaja + Decimal(vlr_pag_caja)
						if obj.valor_cortesia_asociacion > 0:
							CuotaAsociacion = CuotaAsociacion + Decimal(valor_cortesia_asociacion)
						if obj.valor_cortesia_proveedor > 0:
							CuotaProveedor = CuotaProveedor + Decimal(valor_cortesia_proveedor)
			#raise RuntimeError(periodo,SaldoCapital,DeudaCapital,DeudaInteres,ValorInteres,ValorCapital,PrimerPeriodoDeuda)
			if DeudaCaja > DeudaCapital + DeudaInteres:
				DeudaCaja = DeudaCapital + DeudaInteres
			# Log de cambios 1.2.1
			if obj.valor_cortesia_asociacion > 0:
				if Deuda < Decimal(obj.valor_cortesia_asociacion):
					DeudaAsociacion = Deuda
				else:
					DeudaAsociacion = Decimal(obj.valor_cortesia_asociacion)
			if obj.valor_cortesia_proveedor > 0:
				if Deuda < Decimal(obj.valor_cortesia_proveedor):
					DeudaProveedor = Deuda
				else:
					DeudaProveedor = Decimal(obj.valor_cortesia_proveedor)
		Datos.append(SaldoCapital)
		Datos.append(DeudaCapital)
		Datos.append(DeudaInteres)
		Datos.append(ValorInteres)
		Datos.append(ValorCapital)
		Datos.append(DeudaCaja)
		Datos.append(CuotaCaja)
		Datos.append(DeudaAsociacion)
		Datos.append(CuotaAsociacion)
		Datos.append(DeudaProveedor)
		Datos.append(CuotaProveedor)
		Datos.append(PrimerPeriodoDeuda)
		print "&&&&&&&& Datos -->", Datos
		return Datos

	def DatosActualesProducto(self, cr, uid, prod, afil, periodo):
		""" Devuelve DeudaTotal, DeudaCaja, DeudaCortesiaAsociacion, DeudaCortesiaProveedor, PrimerPeriodoDeuda
			Si es Prestamo ademas devuelve SaldoCapital, DeudaCapital, DeudaInteres, ValorInteres, ValorCapital """
		Datos = []
		sale = self.pool.get('sale.order')
		s_order_line = self.pool.get('sale.order.line')
		s_order_line_invoice_rel = self.pool.get('sale.order.invoice_rel')
		account_invoice_line = self.pool.get('account.invoice.line')
		account_invoice = self.pool.get('account.invoice')
		invoice_prestamo = self.pool.get('asocia2.invoice.line.prestamo')
		print "&&&&&&&& self -->", self, prod, periodo
		print "&&&&&&&& self1 -->", afil.id, prod.id
		DeudaCaja = Decimal('0')
		CuotaCaja = Decimal('0')
		DeudaAsociacion = Decimal('0')
		CuotaAsociacion = Decimal('0')
		DeudaProveedor = Decimal('0')
		CuotaProveedor = Decimal('0')
		DeudaCapital = Decimal('0')
		DeudaInteres = Decimal('0')
		ValorInteres = Decimal('0')
		ValorCapital = Decimal('0')
		SaldoCapital = Decimal('0')
		PrimerPeriodoDeuda = ''
		ControlInicioDeuda = True
		#resultado = s_order_line.search(cr, uid, [('product_id','=',obj.product_id.id)])
		resultado = account_invoice_line.search(cr, uid, [('product_id','=',prod.id),('partner_id','=',afil.id)])
		print "&&&&&&&& resultado -->", resultado
		for r in resultado:
			"""
			Tablas a utilizar para ver deuda
			sale_order_line_invoice_rel (linea que le corresponde en invoice a este producto)
			account_invoice_line (lineas de invoice - invoice_id)
			account_invoice (residual_numeric corresponde al valor por pagar de esta factura)
			"""
			#cr.execute('SELECT rel.invoice_id ' \
			#	'FROM sale_order_line_invoice_rel AS rel WHERE rel.order_line_id = ' + str(r))
			#invoice_line_id = cr.fetchall()[0][0]
			#invoice = account_invoice_line.browse(cr, uid, invoice_line_id).invoice_id
			invoice = account_invoice_line.browse(cr, uid, r).invoice_id
			#res = account_invoice.search(cr, uid, [('id','=',invoice_id)])
			#print "&&&&&&&& r -->", r, invoice_line_id, invoice, invoice.residual, invoice.amount_total
			print "&&&&&&&& r -->", r, invoice, invoice.residual, invoice.amount_total, periodo, invoice.periodo
			if not invoice.periodo > periodo:
				valor_pagado = Decimal(invoice.amount_total - invoice.residual)
				if valor_pagado > 0:
					DeudaCapital = DeudaCapital - valor_pagado
					if self.pago_x_caja:
						if p['tipo_documento'] == 'Caja':
							if Decimal(str(self.getVlr_pag_caja())) > Decimal(p['valor_pagado']):
								DeudaCaja = DeudaCaja - Decimal(p['valor_pagado'])
							else:
								DeudaCaja = DeudaCaja - Decimal(str(self.getVlr_pag_caja()))
					# Log de cambios 1.2.1
					if invoice.periodo == periodo:
						ValorCapital = ValorCapital - Decimal(p['capital_pagado'])
						ValorInteres = ValorInteres - Decimal(p['interes_pagado'])
						if p['tipo_documento'] == 'Caja':
							CuotaCaja = CuotaCaja - Decimal(p['valor_pagado'])
						if p['tipo_documento'] == 'Cortesia asociacion':
							CuotaAsociacion = CuotaAsociacion - Decimal(p['valor_pagado'])
						if p['tipo_documento'] == 'Cortesia proveedor':
							CuotaProveedor = CuotaProveedor - valor_pagado
				DeudaCapital = DeudaCapital + Decimal(invoice.amount_total)
				Deuda = DeudaInteres + DeudaCapital
				if Deuda > 0 and ControlInicioDeuda:
					PrimerPeriodoDeuda = invoice.periodo
					ControlInicioDeuda = False
				if invoice.periodo == periodo:
					ValorCapital = ValorCapital + Decimal(invoice.amount_total)
			#raise RuntimeError(periodo,SaldoCapital,DeudaCapital,DeudaInteres,ValorInteres,ValorCapital,PrimerPeriodoDeuda)
			if DeudaCaja > DeudaCapital + DeudaInteres:
				DeudaCaja = DeudaCapital + DeudaInteres
		Datos.append(SaldoCapital)
		Datos.append(DeudaCapital)
		Datos.append(DeudaInteres)
		Datos.append(ValorInteres)
		Datos.append(ValorCapital)
		Datos.append(DeudaCaja)
		Datos.append(CuotaCaja)
		Datos.append(DeudaAsociacion)
		Datos.append(CuotaAsociacion)
		Datos.append(DeudaProveedor)
		Datos.append(CuotaProveedor)
		Datos.append(PrimerPeriodoDeuda)
		print "&&&&&&&& Datos -->", Datos
		return Datos

	def AplicaPagoNomina(self, cr, uid, afil, conv, datosI, AplicaCortesias, context=None):
		""" Aplica pago por proceso de nomina """

		voucher=self.pool.get('account.voucher')
		voucher_line=self.pool.get('account.voucher.line')
		per = datosI['periodo']
		datos = {}
		datos['partner_id'] = afil.id
		datos['date'] = datosI['fecha_causado']
		datos['name'] = datosI['fuente']
		datos['reference'] = per + '-' + datosI['soporte']
		datos['amount'] = datosI['valor_aplicar']
		datos['type'] = 'receipt'
		datos['account_id'] = account.search(cr, uid, [('type','=','liquidity'),('name','=','Banco')])[0]
		# 1 Crea el pago
		voucher_id = voucher.create(cr, uid, datos, context=context)
		Deuda = self.AplicacionAutomatica(cr, uid, afil, conv, datosI, AplicaCortesias, voucher_id, context=None)
		# 2 Graba la aplicación del pago
		for rc in res['value']['line_cr_ids']:
			rc['voucher_id'] = voucher_id
			print "&&&&&&&& rc -->", rc
			vouc_line_id = voucher_line.create(cr, uid, rc, context=context)
		for rd in res['value']['line_dr_ids']:
			rd['voucher_id'] = voucher_id
			print "&&&&&&&& rd -->", rd
			vouc_line_id = voucher_line.create(cr, uid, rd, context=context)
		resultado = voucher.browse(cr, uid, voucher_id).action_move_line_create()
		return Deuda

	def AplicacionAutomatica(self, cr, uid, afil, conv, datosI, AplicaCortesias, voucher_id, context=None):
		""" Aplicacion automatica utilizando la prioridad de pago del convenio """

		product=self.pool.get('product.product')
		product_template=self.pool.get('product.template')
		product_category=self.pool.get('product.category')
		prioridad_pago = self.pool.get('asocia2.prioridad_de_pago')
		servicio_aportes=self.pool.get('asocia2.servicio_aportes')
		servicio_prestamo=self.pool.get('asocia2.servicio_prestamo')
		servicio_credito=self.pool.get('asocia2.servicio_credito')
		servicio_generico=self.pool.get('asocia2.servicio_generico')
		account=self.pool.get('account.account')
		account_invoice_line = self.pool.get('account.invoice.line')
		invoice_prestamo = self.pool.get('asocia2.invoice.line.prestamo')
		voucher=self.pool.get('account.voucher')
		voucher_line=self.pool.get('account.voucher.line')
		excedentes=self.pool.get('asocia2.excedentes')
		excedentes_vouchers=self.pool.get('asocia2.excedentes_vouchers')
		PorAplicar = datosI['valor_aplicar']
		interes = Decimal('0')
		capital = Decimal('0')
		Pagar = Decimal('0')
		Deuda = Decimal('0')
		v = voucher.browse(cr, uid, voucher_id)
		#res = voucher.browse(cr, uid, voucher_id).recompute_voucher_lines(afil.id, v.journal_id.id, v.amount, v.currency_id.id, v.type, v.date, context=context)
		res = voucher.browse(cr, uid, voucher_id).recompute_voucher_lines(afil.id, v.journal_id.id, 0, v.currency_id.id, v.type, v.date, context=context)
		resultado = prioridad_pago.search(cr, uid, [('conv_pago_id','=',conv.id)])
		print "&&&&&&&& resultado -->", resultado, datosI, res
		for c in resultado:
			if PorAplicar > 0:
				cn = prioridad_pago.browse(cr, uid, c).categ_id.name
				print "&&&&&&&& categoria -->", c, cn
				if cn == 'Aportes':
					# Ordenar por periodo esta pendiente
					apors = servicio_aportes.search(cr, uid, [('afiliado_id','=',afil.id),('estado','=','active')])
					for a in apors:
						#datosp = self.DatosActuales(cr, uid, obj, per, True)
						obj = servicio_aportes.browse(cr, uid, a)
						if AplicaCortesias and (obj.valor_cortesia_asociacion > 0 or obj.valor_cortesia_proveedor > 0):
							afil.AplicaCortesia(p, per, datosp)
						resultado = account_invoice_line.search(cr, uid, [('product_id','=',obj.product_id.id),('partner_id','=',obj.afiliado_id.id)])
						for r in resultado:
							invoice = account_invoice_line.browse(cr, uid, r).invoice_id
							for rc in res['value']['line_cr_ids']:
								if rc['name'] == invoice.number:
									Pagar = rc['amount_unreconciled']
									if Pagar > 0:
										if Pagar > PorAplicar:
											Deuda = Deuda + Pagar - PorAplicar
											Pagar = PorAplicar
										PorAplicar = float(PorAplicar) - float(Pagar)
										rc['amount'] = str(float(Pagar))
								print "&&&&&&&& rc -->", rc
							for rd in res['value']['line_dr_ids']:
								print "&&&&&&&& rd -->", rd
						print "&&&&&&&& PorAplicar -->", PorAplicar, Pagar
				else:
					if cn == 'Prestamos':
						# Ordenar por periodo esta pendiente
						pres = servicio_prestamo.search(cr, uid, [('afiliado_id','=',afil.id),('estado','=','active')])
						for p in pres:
							#datosp = self.DatosActuales(cr, uid, obj, per, True)
							obj = servicio_prestamo.browse(cr, uid, p)
							if AplicaCortesias and (obj.valor_cortesia_asociacion > 0 or obj.valor_cortesia_proveedor > 0):
								afil.AplicaCortesiaPrestamo(p, per, datosp)
							resultado = account_invoice_line.search(cr, uid, [('product_id','=',obj.product_id.id),('partner_id','=',obj.afiliado_id.id)])
							for r in resultado:
								invoice = account_invoice_line.browse(cr, uid, r).invoice_id
								for rc in res['value']['line_cr_ids']:
									if rc['name'] == invoice.number:
										resu = invoice_prestamo.search(cr, uid, [('invoice_line_id','=',r)])
										inv_pres = invoice_prestamo.browse(cr, uid, resu[0])
										DeudaInteres = inv_pres.interes_causado - inv_pres.interes_pagado
										Pagar = rc['amount_unreconciled']
										if Pagar > 0:
											if Pagar > PorAplicar:
												Deuda = Deuda + Pagar - PorAplicar
												Pagar = PorAplicar
											PorAplicar = float(PorAplicar) - float(Pagar)
											if not Pagar > DeudaInteres:
												interes = Pagar
												capital = Decimal('0')
											else:
												interes = DeudaInteres
												capital = float(Pagar) - interes
											rc['amount'] = str(float(Pagar))
											capital_pagado = inv_pres.capital_pagado + capital
											interes_pagado = inv_pres.interes_pagado + interes
											asocia2_data = {
												'capital_pagado': capital_pagado,
												'interes_pagado': interes_pagado,
											}
											invoice_prestamo.write(cr, uid, resu[0], asocia2_data, context=None)
									print "&&&&&&&& rc -->", rc
								for rd in res['value']['line_dr_ids']:
									print "&&&&&&&& rd -->", rd
							print "&&&&&&&& PorAplicar -->", PorAplicar, Pagar
					else:
						if cn == 'Credito':
							# Ordenar por periodo esta pendiente
							creds = servicio_credito.search(cr, uid, [('afiliado_id','=',afil.id),('estado','=','active')])
							for c in creds:
								#datosp = self.DatosActuales(cr, uid, obj, per, True)
								obj = servicio_credito.browse(cr, uid, c)
								if AplicaCortesias and (obj.valor_cortesia_asociacion > 0 or obj.valor_cortesia_proveedor > 0):
									afil.AplicaCortesia(p, per, datosp)
								resultado = account_invoice_line.search(cr, uid, [('product_id','=',obj.product_id.id),('partner_id','=',obj.afiliado_id.id)])
								for r in resultado:
									invoice = account_invoice_line.browse(cr, uid, r).invoice_id
									for rc in res['value']['line_cr_ids']:
										if rc['name'] == invoice.number:
											Pagar = rc['amount_unreconciled']
											if Pagar > 0:
												if Pagar > PorAplicar:
													Deuda = Deuda + Pagar - PorAplicar
													Pagar = PorAplicar
												PorAplicar = float(PorAplicar) - float(Pagar)
												rc['amount'] = str(float(Pagar))
										print "&&&&&&&& rc -->", rc
									for rd in res['value']['line_dr_ids']:
										print "&&&&&&&& rd -->", rd
								print "&&&&&&&& PorAplicar -->", PorAplicar, Pagar
						else:
							# Ordenar por periodo esta pendiente
							servs = servicio_generico.search(cr, uid, [('afiliado_id','=',afil.id),('estado','=','active')])
							for s in servs:
								#datosp = self.DatosActuales(cr, uid, obj, per, True)
								obj = servicio_generico.browse(cr, uid, s)
								print "&&&&&&&& tipo servicio -->", cn, s, obj.categ_id.name
								if cn == obj.categ_id.name:
									if AplicaCortesias and (obj.valor_cortesia_asociacion > 0 or obj.valor_cortesia_proveedor > 0):
										afil.AplicaCortesia(p, per, datosp)
									resultado = account_invoice_line.search(cr, uid, [('product_id','=',obj.product_id.id),('partner_id','=',obj.afiliado_id.id)])
									for r in resultado:
										invoice = account_invoice_line.browse(cr, uid, r).invoice_id
										for rc in res['value']['line_cr_ids']:
											if rc['name'] == invoice.number:
												Pagar = rc['amount_unreconciled']
												if Pagar > 0:
													if Pagar > PorAplicar:
														Deuda = Deuda + Pagar - PorAplicar
														Pagar = PorAplicar
													PorAplicar = float(PorAplicar) - float(Pagar)
													rc['amount'] = str(float(Pagar))
											print "&&&&&&&& rc -->", rc
										for rd in res['value']['line_dr_ids']:
											print "&&&&&&&& rd -->", rd
									print "&&&&&&&& PorAplicar -->", PorAplicar, Pagar
		if PorAplicar > 0:
			# Aplicar pago a otros conceptos
			cat_id = product_category.search(cr, uid, [('name','=','Otros')])
			pts = product_template.search(cr, uid, [('categ_id','=',cat_id)])
			if pts:
				for p in pts:
					otrs = product.search(cr, uid, [('product_tmpl_id','=',p)])
					print "&&&&&&&& otrs -->", otrs, cat_id, pts
					resultado = account_invoice_line.search(cr, uid, [('product_id','=',otrs[0]),('partner_id','=',obj.afiliado_id.id)])
					for r in resultado:
						invoice = account_invoice_line.browse(cr, uid, r).invoice_id
						for rc in res['value']['line_cr_ids']:
							if rc['name'] == invoice.number:
								Pagar = rc['amount_unreconciled']
								if Pagar > 0:
									if Pagar > PorAplicar:
										Deuda = Deuda + Pagar - PorAplicar
										Pagar = PorAplicar
									PorAplicar = float(PorAplicar) - float(Pagar)
									rc['amount'] = str(float(Pagar))
							print "&&&&&&&& rc -->", rc
						for rd in res['value']['line_dr_ids']:
							print "&&&&&&&& rd -->", rd
					print "&&&&&&&& PorAplicar -->", PorAplicar, Pagar
		if PorAplicar > 0:
			# Adiciona PorAplicar a excedentes
			resultado = excedentes.search(cr, uid, [('afiliado_id','=',afil.id)])
			if resultado:
				for r in resultado:
					saldoExcedentes = excedentes.browse(cr, uid, r).saldo + PorAplicar
					excedentes_id = r
					asocia2_data = {
						'saldo':saldoExcedentes,
					}
					excedentes.write(cr, uid, excedentes_id, asocia2_data, context=None)
			else:
				datos = {}
				datos['afiliado_id'] = afil.id
				datos['saldo'] = PorAplicar
				excedentes_id = excedentes.create(cr, uid, datos, context=context)
			resultado = excedentes_vouchers.search(cr, uid, [('voucher_id','=',voucher_id)])
			if resultado:
				for r in resultado:
					asocia2_data = {
						'valor':PorAplicar,
					}
					excedentes_vouchers.write(cr, uid, r, asocia2_data, context=None)
			else:
				datos = {}
				datos['voucher_id'] = voucher_id
				datos['valor'] = PorAplicar
				excedentes_id = excedentes_vouchers.create(cr, uid, datos, context=context)
		return Deuda
