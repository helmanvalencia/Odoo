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
from openerp.tools.translate import _
import os

class Partner(orm.Model):
	"""docstring for modification to res_partner"""
	_name = 'res.partner'
	_inherit = 'res.partner'
	_columns = {
		'membership':fields.boolean('Asociado'),
		'cc_afiliado':fields.char('Cedula del afiliado', size=20, readonly=False, help='Numero de cedula del afiliado'),
		'fec_afiliacion':fields.date('Fecha de afiliacion'),
		'state':fields.selection([('draft','Por aprobar'),('confirmed','Afiliado'),('cancel','No pago'),('death','Muerto'),('retired','Retiro Voluntario')], 'Estado Afiliacion', readonly=True),
		'regional':fields.selection([('1','Bogota'),('10','Armenia'),('13','Barranquilla'),('16','Bucaramanga'),('20','Cali'),('22','Cartagena'),('28','Cucuta'),
			('35','Florencia'),('40','Girardot'),('45','Honda'),('47','Ibague'),('50','Ipiales'),('56','Manizales'),('58','Medellin'),('60','Monteria'),
			('62','Neiva'),('65','Pasto'),('67','Pereira'),('69','Popayan'),('75','Rioacha'),('78','Santa Marta'),('80','Sincelejo'),('85','Tunja'),('86','Valledupar'),
			('87','Villavicencio'),('88','San Andres')], 'Regional'),
		'vinculados_ids': fields.one2many('asocia2.vinculados', 'afiliado_id','Vinculados'),
		'hist_afiliacion_ids': fields.one2many('asocia2.hist_afiliacion', 'afiliado_id','Historia de afiliacion'),
		'excedentes_ids': fields.one2many('asocia2.excedentes', 'afiliado_id','Excedentes'),
		'conv_servicio_ids': fields.one2many('asocia2.conv_servicio', 'proveedor_id','Convenio de Servicios'),
		'conv_prestamo_ids': fields.one2many('asocia2.conv_prestamo', 'proveedor_id','Convenio de Prestamos'),
		'conv_pago_ids': fields.one2many('asocia2.conv_pago', 'proveedor_id','Convenio de Pagos'),
		'servicio_generico_ids': fields.one2many('asocia2.servicio_generico', 'afiliado_id','Servicio Generico'),
		'servicio_credito_ids': fields.one2many('asocia2.servicio_credito', 'afiliado_id','Servicio Credito'),
		'servicio_prestamo_ids': fields.one2many('asocia2.servicio_prestamo', 'afiliado_id','Servicio Prestamo'),
		'servicio_pago_ids': fields.one2many('asocia2.servicio_pago', 'afiliado_id','Servicio Pago'),
		'servicio_aportes_ids': fields.one2many('asocia2.servicio_aportes', 'afiliado_id','Servicio Aportes'),
	}
	_defaults = {
		'membership': False,
		'fec_afiliacion': datetime.now().strftime('%Y-%m-%d'),
		'state': 'draft',
	}

	def confirm(self, cr, uid, ids, context=None):
		self.write(cr, uid, ids, {'state':'confirmed'}, context=None)
		asocia2_obj = self.pool.get('asocia2.hist_afiliacion')
		asocia2_data = {
			'afiliado_id': self.browse(cr, uid, ids).id, 
			'estado': self.browse(cr, uid, ids).state, 
			'fecha': datetime.now().strftime('%Y-%m-%d'),
		}
		asocia2_id = asocia2_obj.create(cr, uid, asocia2_data, context=context)
		return True

	def cancel(self, cr, uid, ids, context=None):
		self.write(cr, uid, ids, {'state':'cancel'}, context=None)
		asocia2_obj = self.pool.get('asocia2.hist_afiliacion')
		asocia2_data = {
			'afiliado_id': self.browse(cr, uid, ids).id, 
			'estado': self.browse(cr, uid, ids).state, 
			'fecha': datetime.now().strftime('%Y-%m-%d'),
		}
		asocia2_id = asocia2_obj.create(cr, uid, asocia2_data, context=context)
		return True

	def death(self, cr, uid, ids, context=None):
		self.write(cr, uid, ids, {'state':'death'}, context=None)
		asocia2_obj = self.pool.get('asocia2.hist_afiliacion')
		asocia2_data = {
			'afiliado_id': self.browse(cr, uid, ids).id, 
			'estado': self.browse(cr, uid, ids).state, 
			'fecha': datetime.now().strftime('%Y-%m-%d'),
		}
		asocia2_id = asocia2_obj.create(cr, uid, asocia2_data, context=context)
		return True

	def retired(self, cr, uid, ids, context=None):
		self.write(cr, uid, ids, {'state':'retired'}, context=None)
		asocia2_obj = self.pool.get('asocia2.hist_afiliacion')
		asocia2_data = {
			'afiliado_id': self.browse(cr, uid, ids).id, 
			'estado': self.browse(cr, uid, ids).state, 
			'fecha': datetime.now().strftime('%Y-%m-%d'),
		}
		asocia2_id = asocia2_obj.create(cr, uid, asocia2_data, context=context)
		return True

class PurchaseOrder(orm.Model):
	"""docstring for modification to purchase_order"""
	_name = 'purchase.order'
	_inherit = 'purchase.order'
	_columns = {
		'cobro':fields.boolean('Cobro asociados'),
		'periodo':fields.char('Periodo', size=7, required=True ,help="Indique el periodo con el formato AAAA-PP (Vigencia y periodo)"),
	}
	_defaults = {
	}

class SaleOrder(orm.Model):
	"""docstring for modification to sale_order"""
	_name = 'sale.order'
	_inherit = 'sale.order'
	_columns = {
		'cobro':fields.boolean('Cobro asociados'),
		'periodo':fields.char('Periodo', size=7, required=True ,help="Indique el periodo con el formato AAAA-PP (Vigencia y periodo)"),
	}
	_defaults = {
	}

class AccountInvoiceOrder(orm.Model):
	"""docstring for modification to account_invoice"""
	_name = 'account.invoice'
	_inherit = 'account.invoice'
	_columns = {
		'cobro':fields.boolean('Cobro asociados'),
		'periodo':fields.char('Periodo', size=7, help="Indique el periodo con el formato AAAA-PP (Vigencia y periodo)"),
	}
	_defaults = {
	}

class AccountVoucher(orm.Model):
	"""docstring for modification to account_voucher"""
	_name = 'account.voucher'
	_inherit = 'account.voucher'
	_columns = {
		'caja':fields.boolean('Caja asociados'),
		'tipo_transaccion':fields.selection([('pago','Pago'),('devolucion','Devolucion'),('condonacion','Condonacion')], 'Tipo de transaccion', readonly=True),
		'metodo_aplicacion':fields.selection([('automatico','Automatico'),('caja','Obligaciones de Caja'),('seleccion','Seleccion')], 'Metodo de aplicacion', readonly=True),
		'vouchers_seleccion_ids': fields.one2many('asocia2.vouchers_seleccion', 'vouchers_seleccion_id','Distribucion del Pago'),
	}
	_defaults = {
	}

	def create(self, cr, uid, vals, context=None):
		print "&&&&&&&& vals-->", vals, self
		voucher=self.pool.get('account.voucher')
		voucher_line=self.pool.get('account.voucher.line')
		raise RuntimeError(vals)
		per = str(vals['fecha_pago1'])[0:4] + '-' + str(vals['fecha_pago1'])[5:7]
		datos = {}
		datos['partner_id'] = afil.id
		datos['date'] = datetime.strptime(vals['fecha_pago1'],'%Y-%m-%d').date()
		datos['name'] = vals['tipo_transaccion']
		datos['reference'] = per + '-' + datosI['soporte']
		datos['amount'] = datosI['valor_aplicar']
		datos['type'] = 'receipt'
		datos['account_id'] = account.search(cr, uid, [('type','=','liquidity'),('name','=','Banco')])[0]
		# 1 Crea el pago
		voucher_id = super(voucher, self).create(cr, uid, vals, context)
		v = voucher.browse(cr, uid, voucher_id)
		res = voucher.browse(cr, uid, voucher_id).recompute_voucher_lines(afil.id, v.journal_id.id, 0, v.currency_id.id, v.type, v.date, context=context)
		if vals['metodo_aplicacion'] == 'automatico':
			Deuda = self.AplicacionAutomatica(cr, uid, afil, conv, vals, AplicaCortesias, voucher_id, context=None)
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
		return 

class asocia2_vouchers_seleccion(osv.osv):
	"""docstring for asocia2_vouchers_seleccion"""
	_name = 'asocia2.vouchers_seleccion'
	_description = 'Distribucion del Pago'
	_columns = {
		'vouchers_seleccion_id':fields.many2one('account.voucher', 'Id Voucher'),
		'product_id':fields.many2one('product.product', 'ID producto'),
		'valor': fields.float('Valor a pagar'),
		'metodo_aplicacion':fields.selection([('capital','Capital'),('cuotas','Cuotas')], 'Metodo de aplicacion', readonly=True),
	}
	_defaults = {
	}

class asocia2_invoice_line_prestamo(osv.osv):
	"""docstring for asocia2_invoice_line_prestamo"""
	_name = 'asocia2.invoice.line.prestamo'
	_description = 'Información causacion y pago prestamo'
	_columns = {
		'invoice_line_id':fields.many2one('account.invoice.line', 'ID invoice line'),
		'capital_causado': fields.float('Capital causado'),
		'interes_causado': fields.float('Interes causado'),
		'capital_pagado': fields.float('Capital pagado'),
		'interes_pagado': fields.float('Interes pagado'),
	}
	_defaults = {
	}

class asocia2_vinculados(osv.osv):
	"""docstring for asocia2_vinculados"""
	_name = 'asocia2.vinculados'
	_description = 'Asociados vinculados'
	_columns = {
		'afiliado_id':fields.many2one('res.partner', 'ID afiliado'),
		'cc_afiliado_vinculado':fields.char('Cedula afiliado vinculado', size=20, required=True),
	}
	_defaults = {
	}

class asocia2_hist_afiliacion(osv.osv):
	"""docstring for asocia2_hist_afiliacion"""
	_name = 'asocia2.hist_afiliacion'
	_description = 'Historico de afiliacion'
	_columns = {
		'afiliado_id':fields.many2one('res.partner', 'ID afiliado'),
		'estado':fields.selection([('draft','Por aprobar'),('confirmed','Afiliado'),('cancel','No pago'),('death','Muerto'),('retired','Retiro Voluntario')], 'Estado Afiliacion', required=True),
		'fecha':fields.date('Fecha de cambio de estado', required=True),
	}
	_defaults = {
	}

class asocia2_excedentes(osv.osv):
	"""docstring for asocia2_excedentes"""
	_name = 'asocia2.excedentes'
	_description = 'Saldo de excedentes'
	_columns = {
		'afiliado_id':fields.many2one('res.partner', 'ID afiliado'),
		'saldo': fields.float('Saldo', required=True),
		'excedentes_vouchers_ids': fields.one2many('asocia2.excedentes_vouchers', 'excedentes_vouchers_id','Vouchers con excedentes'),
	}
	_defaults = {
	}

class asocia2_excedentes_vouchers(osv.osv):
	"""docstring for asocia2_excedentes_vouchers"""
	_name = 'asocia2.excedentes_vouchers'
	_description = 'Vouchers con excedentes'
	_columns = {
		'excedentes_vouchers_id':fields.many2one('asocia2.excedentes', 'ID excedentes'),
		'voucher_id':fields.many2one('account.voucher', 'Voucher'),
		'valor': fields.float('Valor excedente', required=True),
	}
	_defaults = {
	}

class asocia2_servicio_generico(osv.osv):
	"""docstring for asocia2_servicio_generico"""
	_name = 'asocia2.servicio_generico'
	_description = 'Servicios genericos'
	_columns = {
		'afiliado_id':fields.many2one('res.partner', 'ID afiliado'),
		'product_id': fields.many2one('product.template','Producto', required=True, change_default=True, help="Seleccione el producto asociado al servicio"),
		'categ_id': fields.many2one('product.category','Categoria del servicio', required=True, change_default=True, domain="[('type','=','normal')]" ,help="Seleccione la categoria para el servicio actual"),
		'valor_cuota': fields.float('Valor cuota', required=True),
		'vlr_pag_caja': fields.float('Valor caja', required=True),
		'valor_cortesia_asociacion': fields.float('Cortesia de asociacion', required=True),
		'valor_cortesia_proveedor': fields.float('Cortesia de proveedor', required=True),
		'periodicidad':fields.selection([('mensual','Mensual'),('trimestral','Trimestral'),('semestral','Semestral'),('anual','Anual')], 'Periodicidad de pago', required=True),
		'cuotas_anio':fields.integer('Cuotas por anio', required=True),
		'estado':fields.selection([('active','Activo'),('finished','Finalizado')], 'Estado de Servicio', required=True),
		'fecha':fields.date('Fecha inicio', required=True),
		'hist_servicio_generico_ids': fields.one2many('asocia2.hist_servicio_generico', 'servicio_generico_id','Historia del servicio'),
	}
	_defaults = {
		'vlr_pag_caja': 0,
		'valor_cortesia_asociacion': 0,
		'valor_cortesia_proveedor': 0,
		'periodicidad': 'mensual',
		'cuotas_anio': 12,
		'estado': 'active',
	}

class asocia2_hist_servicio_generico(osv.osv):
	"""docstring for asocia2_hist_servicio_generico"""
	_name = 'asocia2.hist_servicio_generico'
	_description = 'Historico del Servicio'
	_columns = {
		'servicio_generico_id':fields.many2one('asocia2.servicio_generico', 'ID servicio'),
		'estado':fields.selection([('active','Activo'),('finished','Finalizado')], 'Estado de Servicio', required=True),
		'fecha':fields.date('Fecha de cambio de estado', required=True),
	}
	_defaults = {
	}

class asocia2_servicio_credito(osv.osv):
	"""docstring for asocia2_servicio_credito"""
	_name = 'asocia2.servicio_credito'
	_description = 'Servicios de credito'
	_columns = {
		'afiliado_id':fields.many2one('res.partner', 'ID afiliado'),
		'product_id': fields.many2one('product.template','Producto', required=True, change_default=True, help="Seleccione el producto asociado al servicio"),
		'categ_id': fields.many2one('product.category','Categoria del servicio', required=True, change_default=True, domain="[('type','=','normal')]" ,help="Seleccione la categoria para el servicio actual"),
		'plazo':fields.integer('Plazo en meses', required=True),
		'saldo': fields.float('saldo reportado', required=True),
		'cuotas_pag_reportado':fields.integer('Cuotas pagadas reportado', required=True),
		'cuotas_pag_calculado':fields.integer('Cuotas pagadas calculado', required=True),
		'valor_cuota': fields.float('Valor cuota', required=True),
		'vlr_pag_caja': fields.float('Valor caja', required=True),
		'valor_cortesia_asociacion': fields.float('Cortesia de asociacion', required=True),
		'valor_cortesia_proveedor': fields.float('Cortesia de proveedor', required=True),
		'periodicidad':fields.selection([('mensual','Mensual'),('trimestral','Trimestral'),('semestral','Semestral'),('anual','Anual')], 'Periodicidad de pago', required=True),
		'cuotas_anio':fields.integer('Cuotas por anio', required=True),
		'estado':fields.selection([('active','Activo'),('finished','Finalizado')], 'Estado de Servicio', required=True),
		'fecha':fields.date('Fecha inicio', required=True),
		'hist_servicio_credito_ids': fields.one2many('asocia2.hist_servicio_credito', 'servicio_credito_id','Historia del servicio'),
	}
	_defaults = {
		'vlr_pag_caja': 0,
		'valor_cortesia_asociacion': 0,
		'valor_cortesia_proveedor': 0,
		'periodicidad': 'mensual',
		'cuotas_anio': 12,
		'estado': 'active',
	}

class asocia2_hist_servicio_credito(osv.osv):
	"""docstring for asocia2_hist_servicio_credito"""
	_name = 'asocia2.hist_servicio_credito'
	_description = 'Historico del Servicio'
	_columns = {
		'servicio_credito_id':fields.many2one('asocia2.servicio_credito', 'ID servicio'),
		'estado':fields.selection([('active','Activo'),('finished','Finalizado')], 'Estado de Servicio', required=True),
		'fecha':fields.date('Fecha de cambio de estado', required=True),
	}
	_defaults = {
	}

class asocia2_servicio_prestamo(osv.osv):
	"""docstring for asocia2_servicio_prestamo"""
	_name = 'asocia2.servicio_prestamo'
	_description = 'Servicios de prestamo'
	_columns = {
		'afiliado_id':fields.many2one('res.partner', 'ID afiliado'),
		'product_id': fields.many2one('product.template','Producto', change_default=True, help="Seleccione el producto asociado al servicio"),
		'categ_id': fields.many2one('product.category','Categoria del servicio', required=True, change_default=True, domain="[('type','=','normal')]" ,help="Seleccione la categoria para el servicio actual"),
		'vlr_prestamo': fields.float('Valor prestado', required=True),
		'plazo':fields.integer('Plazo en meses', required=True),
		'fec_desembolso':fields.date('Fecha desembolso', required=True),
		'comprobante_egreso_desembolso':fields.char('Documento soporte egreso', size=20),
		'fecha_pago1':fields.date('Fecha primer pago', required=True),
		'fecha_cancelacion':fields.date('Fecha cancelacion'),
		'tasa_interes': fields.float('Tasa de interes', required=True),
		'valor_cuota': fields.float('Valor cuota', required=True),
		'vlr_pag_caja': fields.float('Valor caja', required=True),
		'valor_cortesia_asociacion': fields.float('Cortesia de asociacion', required=True),
		'valor_cortesia_proveedor': fields.float('Cortesia de proveedor', required=True),
		'periodicidad':fields.selection([('mensual','Mensual'),('trimestral','Trimestral'),('semestral','Semestral'),('anual','Anual')], 'Periodicidad de pago', required=True),
		'cuotas_anio':fields.integer('Cuotas por anio', required=True),
		'estado':fields.selection([('active','Activo'),('finished','Finalizado')], 'Estado de Servicio', required=True),
		'fecha':fields.date('Fecha inicio'),
		'hist_servicio_prestamo_ids': fields.one2many('asocia2.hist_servicio_prestamo', 'servicio_prestamo_id','Historia del servicio'),
		'prestamos_refinancia_ids': fields.one2many('asocia2.prestamos_refinancia', 'servicio_prestamo_id','Prestamos que refinancia'),
	}
	_defaults = {
		'vlr_pag_caja': 0,
		'valor_cortesia_asociacion': 0,
		'valor_cortesia_proveedor': 0,
		'periodicidad': 'mensual',
		'cuotas_anio': 12,
		'estado': 'active',
	}

	def create(self, cr, uid, vals, context=None):
		print "&&&&&&&& vals-->", vals, self
		conv_prestamo = self.pool.get('asocia2.conv_prestamo')
		product=self.pool.get('product.product')
		hist_servicio_prestamo=self.pool.get('asocia2.hist_servicio_prestamo')
		resultado = conv_prestamo.search(cr, uid, [('categ_id','=',vals['categ_id'])])
		if not resultado:
			raise osv.except_osv(_('Error!'), _('No hay convenio de prestamo para esta categoria: '+vals['categ_id']))
		conv_pres=conv_prestamo.browse(cr, uid, resultado[0])
		Convenio = conv_pres.categ_id.name
		p = conv_pres.proveedor_id
		# 1. Valida plazo y vlr_prestamo
		if (vals['plazo'] < conv_pres.plazo_minimo) or (vals['plazo'] > conv_pres.plazo_maximo):
			raise osv.except_osv(_('Error!'), _('El plazo ' + str(vals['plazo']) + ' es menor de ' + str(conv_pres.plazo_minimo) + ' o es mayor de ' + str(conv_pres.plazo_maximo)))
		if (vals['vlr_prestamo'] < conv_pres.valor_minimo) or (vals['vlr_prestamo'] > conv_pres.valor_maximo):
			raise osv.except_osv(_('Error!'), _('El valor del prestamo ' + str(vals['vlr_prestamo']) + ' es menor de ' + str(conv_pres.valor_minimo) + ' o es mayor de ' + str(conv_pres.valor_maximo)))
		# 2. Asigna valores para interes, numero prestamo, valor de la cuota y fecha de cancelacion
		tasa_interes = float(conv_pres.tasa_interes)
		cuota_admon = float(conv_pres.cuota_admon)
		if conv_pres.cns_prestamo:
			cns_prestamo = conv_pres.cns_prestamo + 1
		else:
			cns_prestamo = 1
		vals.update({'tasa_interes': tasa_interes})
		tasa_interes = tasa_interes / 100
		vlr_prestamo = float(vals['vlr_prestamo'])
		if tasa_interes > 0:
			valor_cuota = vlr_prestamo*(tasa_interes*(1+tasa_interes)**vals['plazo'])/((1+tasa_interes)**vals['plazo']-1)
		else:
			valor_cuota = vlr_prestamo/vals['plazo']
		vals.update({'valor_cuota': valor_cuota})
		MesesCobro = vals['plazo']-1
		fecha_cancelacion = self.ProximaFecha(datetime.strptime(vals['fecha_pago1'],'%Y-%m-%d').date(),vals['periodicidad'],vals['cuotas_anio'],MesesCobro)
		vals.update({'fecha_cancelacion': fecha_cancelacion})
		print "&&&&&&&& vals 2-->", vals
		# 3. Modifica el consecutivo en los parametros del prestamo
		conv_prestamo.write(cr, uid, resultado, {'cns_prestamo':cns_prestamo}, context=None)
		# 4.Si hay cuota de administracion la causa
		proces = self.pool.get('asocia2.procesos')
		if cuota_admon > 0:
			#raise RuntimeError(cuota_admon,e.Title(),e.tipo_concepto,str(self.fecha_pago1),str(self.fecha_pago1)[0:4],str(self.fecha_pago1)[5:7])
			datos = {}
			datos['periodo'] = str(vals['fecha_pago1'])[0:4] + '-' + str(vals['fecha_pago1'])[5:7]
			datos['fecha_procesado'] = date.today().strftime('%Y/%m/%d')
			datos['fecha_causado'] = datetime.strptime(vals['fecha_pago1'],'%Y-%m-%d').date()
			datos['cuota'] = str(cuota_admon)
			datos['capital'] = 0
			datos['interes'] = 0
			datos['fuente'] = ''
			datos['soporte'] = cns_prestamo
			datos['producto_id'] = conv_pres.id_producto_cuota_admon.id
			datos['afiliado_id'] = vals['afiliado_id']
			print "&&&&&&&& datos -->", datos, p, self
			proces.GrabaCausacionPropia(cr, uid, p, self, datos, context=None)
		"""
	  # 5.En caso de refinanciacion aplica el pago automaticamente
	  for p in self.num_cred_que_refinancia:
		if p:
		  for pres in prestamos:
			if pres.Title() == p:
			  # 5.1.Acumula capital causado de periodos posteriores
			  causad0 = pres.getCausados()
			  CapitalCausado = 0
			  for c in causad0:
				if c['anio_mes'] > per:
				  CapitalCausado = CapitalCausado + float(c['capital_causado'])
			  # 5.2.Graba el pago
			  datosp = pres.DatosActuales(per)
			  datos = {}
			  datos['periodo'] = per
			  datos['fecha_pago'] = date.today().strftime('%Y/%m/%d')
			  datos['tipo_documento'] = 'Refinanciacion ' + self.Title()
			  datos['n_documento'] = self.numero_prestamo
			  datos['valor'] = str(float(datosp[0] + datosp[1] + datosp[2]) - CapitalCausado)
			  datos['capital'] = str(float(datosp[0] + datosp[1]) - CapitalCausado)
			  datos['interes'] = str(float(datosp[2]))
			  pres.GrabaPago(datos)
			  # 5.3.Causa el saldo de capital
			  if float(datosp[0]) - CapitalCausado > 0:
				datos['cuota'] = str(float(datosp[0]) - CapitalCausado)
				datos['fuente'] = 'Causa saldo capital'
				datos['soporte'] = self.numero_prestamo
				datos['fecha_procesado'] = date.today().strftime('%Y/%m/%d')
				datos['capital'] = str(float(datosp[0]) - CapitalCausado)
				datos['interes'] = str(float(0))
				datos['fecha_causado'] = date.today().strftime('%Y/%m/%d')
				pres.GrabaCausacion(datos)
			  # 5.4.Marca el prestamo como finalizado, cambia fecha de cancelacion y graba historia
			  pres.edit(estado_servicio = 'finalizado')
			  pres.edit(fecha_cancelacion = self.fec_desembolso)
			  h_ref = {}
			  h_ref['evento'] = 'desactivado'
			  h_ref['fecha'] = str(pres.fecha_cancelacion)
			  h_ref['tipo'] = datos['tipo_documento']
			  h_retiro_reing = pres.hist_activ_cancel + (h_ref,)
			  pres.edit(hist_activ_cancel= h_retiro_reing)
		"""
		# 6. Crea el producto
		asocia2_data = {
			'name': Convenio + ' - ' + p.name + ' ' + str(cns_prestamo),
			'categ_id': vals['categ_id'], 
			'list_price': valor_cuota, 
			'standard_price': valor_cuota, 
			'type': 'service', 
			'default_code': str(cns_prestamo),
		}
		product_id = product.create(cr, uid, asocia2_data, context=context)
		vals.update({'product_id': product_id})
		servicio_prestamo_id = super(asocia2_servicio_prestamo, self).create(cr, uid, vals, context)
		asocia2_data = {
			'servicio_prestamo_id':servicio_prestamo_id,
			'estado': 'active',
			'fecha': vals['fec_desembolso'],
		}
		hist_servicio_prestamo_id = hist_servicio_prestamo.create(cr, uid, asocia2_data, context=context)
		return 

	def ProximaFecha(self,fechai,periodicidad,perxanio,plazo):
		""" Devuelve la proxima fecha al final del plazo en periodos """
		#fechai = datetime.strptime(fechai,'%Y-%m-%d').date()
		anioi = fechai.year
		mesi = fechai.month
		diai = fechai.day
		anios = plazo // perxanio
		meses = plazo % perxanio
		if periodicidad == 'mensual':
			aniof = anioi + anios
			mesf = mesi + meses
			diaf = diai
			if mesf > 12:
				aniof = aniof + 1
				mesf = mesf - 12
		if periodicidad == 'trimestral':
			aniof = anioi + anios
			mesf = mesi + meses * 3
			diaf = diai
			if mesf > 12:
				aniof = aniof + 1
				mesf = mesf - 12
		if periodicidad == 'semestral':
			aniof = anioi + anios
			mesf = mesi + meses * 6
			diaf = diai
			if mesf > 12:
				aniof = aniof + 1
				mesf = mesf - 12
		if periodicidad == 'anual':
			aniof = anioi + anios + meses
			mesf = mesi
			diaf = diai
		return datetime(aniof,mesf,diaf).date()

class asocia2_hist_servicio_prestamo(osv.osv):
	"""docstring for asocia2_hist_servicio_prestamo"""
	_name = 'asocia2.hist_servicio_prestamo'
	_description = 'Historico del Servicio'
	_columns = {
		'servicio_prestamo_id':fields.many2one('asocia2.servicio_prestamo', 'ID servicio'),
		'estado':fields.selection([('active','Activo'),('finished','Finalizado')], 'Estado de Servicio', required=True),
		'fecha':fields.date('Fecha de cambio de estado', required=True),
	}
	_defaults = {
	}

class asocia2_prestamos_refinancia(osv.osv):
	"""docstring for asocia2_prestamos_refinancia"""
	_name = 'asocia2.prestamos_refinancia'
	_description = 'Prestamos refinanciados'
	_columns = {
		'servicio_prestamo_id':fields.many2one('asocia2.servicio_prestamo', 'ID servicio'),
		'id_prestamo_refinancia':fields.many2one('asocia2.servicio_prestamo', 'Prestamo que refinancia'),
		'valor_que_refinancia': fields.float('Valor refinanciado', required=True),
	}
	_defaults = {
	}

class asocia2_servicio_pago(osv.osv):
	"""docstring for asocia2_servicio_pago"""
	_name = 'asocia2.servicio_pago'
	_description = 'Servicios de pago'
	_columns = {
		'afiliado_id':fields.many2one('res.partner', 'ID afiliado'),
		'product_id': fields.many2one('product.template','Producto', required=True, change_default=True, help="Seleccione el producto asociado al servicio"),
		'categ_id': fields.many2one('product.category','Categoria del servicio', required=True, change_default=True, domain="[('type','=','normal')]" ,help="Seleccione la categoria para el servicio actual"),
		'valor_base_aporte': fields.float('Valor base para aportes', required=True),
		'valor_cuota': fields.float('Valor cuota', required=True),
		'vlr_pag_caja': fields.float('Valor caja', required=True),
		'valor_cortesia_asociacion': fields.float('Cortesia de asociacion', required=True),
		'valor_cortesia_proveedor': fields.float('Cortesia de proveedor', required=True),
		'periodicidad':fields.selection([('mensual','Mensual'),('trimestral','Trimestral'),('semestral','Semestral'),('anual','Anual')], 'Periodicidad de pago', required=True),
		'cuotas_anio':fields.integer('Cuotas por anio', required=True),
		'estado':fields.selection([('active','Activo'),('finished','Finalizado')], 'Estado de Servicio', required=True),
		'fecha':fields.date('Fecha inicio', required=True),
		'hist_servicio_pago_ids': fields.one2many('asocia2.hist_servicio_pago', 'servicio_pago_id','Historia del servicio'),
	}
	_defaults = {
		'vlr_pag_caja': 0,
		'valor_cortesia_asociacion': 0,
		'valor_cortesia_proveedor': 0,
		'periodicidad': 'mensual',
		'cuotas_anio': 12,
		'estado': 'active',
	}

class asocia2_hist_servicio_pago(osv.osv):
	"""docstring for asocia2_hist_servicio_pago"""
	_name = 'asocia2.hist_servicio_pago'
	_description = 'Historico del Servicio'
	_columns = {
		'servicio_pago_id':fields.many2one('asocia2.servicio_pago', 'ID servicio'),
		'estado':fields.selection([('active','Activo'),('finished','Finalizado')], 'Estado de Servicio', required=True),
		'fecha':fields.date('Fecha de cambio de estado', required=True),
	}
	_defaults = {
	}

class asocia2_servicio_aportes(osv.osv):
	"""docstring for asocia2_servicio_aportes"""
	_name = 'asocia2.servicio_aportes'
	_description = 'Servicios aportes'
	_columns = {
		'afiliado_id':fields.many2one('res.partner', 'ID afiliado'),
		'product_id': fields.many2one('product.template','Producto', required=True, change_default=True, help="Seleccione el producto asociado al servicio"),
		'categ_id': fields.many2one('product.category','Categoria del servicio', required=True, change_default=True, domain="[('type','=','normal')]" ,help="Seleccione la categoria para el servicio actual"),
		'convenio_pago_id':fields.many2one('asocia2.conv_pago', 'ID convenio pago'),
		'valor_pension': fields.float('Valor pension', required=True),
		'valor_cuota': fields.float('Valor cuota', required=True),
		'vlr_pag_caja': fields.float('Valor caja', required=True),
		'valor_cortesia_asociacion': fields.float('Cortesia de asociacion', required=True),
		'valor_cortesia_proveedor': fields.float('Cortesia de proveedor', required=True),
		'periodicidad':fields.selection([('mensual','Mensual'),('trimestral','Trimestral'),('semestral','Semestral'),('anual','Anual')], 'Periodicidad de pago', required=True),
		'cuotas_anio':fields.integer('Cuotas por anio', required=True),
		'estado':fields.selection([('active','Activo'),('finished','Finalizado')], 'Estado de Servicio', required=True),
		'fecha':fields.date('Fecha inicio', required=True),
		'hist_servicio_aportes_ids': fields.one2many('asocia2.hist_servicio_aportes', 'servicio_aportes_id','Historia del servicio'),
	}
	_defaults = {
		'vlr_pag_caja': 0,
		'valor_cortesia_asociacion': 0,
		'valor_cortesia_proveedor': 0,
		'periodicidad': 'mensual',
		'cuotas_anio': 12,
		'estado': 'active',
	}

class asocia2_hist_servicio_aportes(osv.osv):
	"""docstring for asocia2_hist_servicio_aportes"""
	_name = 'asocia2.hist_servicio_aportes'
	_description = 'Historico del Servicio'
	_columns = {
		'servicio_aportes_id':fields.many2one('asocia2.servicio_aportes', 'ID servicio'),
		'estado':fields.selection([('active','Activo'),('finished','Finalizado')], 'Estado de Servicio', required=True),
		'fecha':fields.date('Fecha de cambio de estado', required=True),
	}
	_defaults = {
	}

class asocia2_conv_servicio(osv.osv):
	"""docstring for asocia2_conv_servicio"""
	_name = 'asocia2.conv_servicio'
	_description = 'Convenio de Servicios'
	_columns = {
		'proveedor_id':fields.many2one('res.partner', 'ID proveedor'),
		'tipo_servicio':fields.selection([('credito','Credito'),('salud','Salud'),('seg_auto','Seguro de Auto'),('seg_vida','Seguro de Vida'),('seg_hogar','Seguro de Hogar'),('seg_funerario','Seguro Funerario'),('telefonia','Telefonia')], 'Tipo de Servicio', required=True),
		'categ_id': fields.many2one('product.category','Categoria del servicio', required=True, change_default=True, domain="[('type','=','normal')]" ,help="Seleccione la categoria para el servicio actual"),
		'causacion':fields.boolean('Causacion'),
		'pago':fields.boolean('Pago'),
		'estado':fields.selection([('active','Activo'),('finished','Finalizado')], 'Estado de Convenio', required=True),
		'fecha_inicio':fields.date('Fecha de inicio convenio', required=True),
		'hist_conv_servicio_ids': fields.one2many('asocia2.hist_conv_servicio', 'conv_servicio_id','Historia de convenio'),
	}
	_defaults = {
	}

class asocia2_hist_conv_servicio(osv.osv):
	"""docstring for asocia2_hist_conv_servicio"""
	_name = 'asocia2.hist_conv_servicio'
	_description = 'Historico de Convenio'
	_columns = {
		'conv_servicio_id':fields.many2one('asocia2.conv_servicio', 'ID convenio'),
		'estado':fields.selection([('active','Activo'),('finished','Finalizado')], 'Estado de Convenio', required=True),
		'fecha':fields.date('Fecha de cambio de estado', required=True),
	}
	_defaults = {
	}

class asocia2_conv_prestamo(osv.osv):
	"""docstring for asocia2_conv_prestamo"""
	_name = 'asocia2.conv_prestamo'
	_description = 'Convenio de Prestamos'
	_columns = {
		'proveedor_id':fields.many2one('res.partner', 'ID proveedor'),
		'tipo_prestamo':fields.char('Tipo de Prestamo', size=20, required=True),
		'categ_id': fields.many2one('product.category','Categoria del prestamo', required=True, change_default=True, domain="[('type','=','normal')]" ,help="Seleccione la categoria para el prestamo actual"),
		'cns_prestamo':fields.integer('Consecutivo de Prestamo', required=True, help="Numero del ultimo prestamo asignado"),
		'plazo_minimo':fields.integer('Plazo minimo en meses', required=True),
		'plazo_maximo':fields.integer('Plazo maximo en meses', required=True),
		'valor_minimo':fields.float('Valor minimo a prestar', digits=(16,2), required=True),
		'valor_maximo':fields.float('Valor maximo a prestar', digits=(16,2), required=True),
		'tasa_interes':fields.float('Tasa de interes (%)', required=True),
		'cuota_admon':fields.float('Valor de la cuota de administracion', digits=(16,2), required=True),
		'id_producto_cuota_admon': fields.many2one('product.template','Producto', required=True, change_default=True, help="Seleccione el producto cuota de administracion asociado al servicio"),
		'cuenta_corto_plazo': fields.many2one('account.account', 'Cuenta contable corto plazo', help="Escoja la cuenta que se va a utilizar para trasladar de largo a corto plazo el capital."),
		'cuenta_interes_d': fields.many2one('account.account', 'Cuenta contable intereses (debito)', help="Escoja la cuenta (debito) que se va a utilizar para manejar los intereses."),
		'cuenta_interes_c': fields.many2one('account.account', 'Cuenta contable intereses (credito)', help="Escoja la cuenta (credito) que se va a utilizar para manejar los intereses."),
		'causacion':fields.boolean('Causacion'),
		'pago':fields.boolean('Pago'),
		'estado':fields.selection([('active','Activo'),('finished','Finalizado')], 'Estado de Convenio', required=True),
		'fecha_inicio':fields.date('Fecha de inicio convenio', required=True),
		'hist_conv_prestamo_ids': fields.one2many('asocia2.hist_conv_prestamo', 'conv_prestamo_id','Historia de convenio'),
	}
	_defaults = {
	}

class asocia2_hist_conv_prestamo(osv.osv):
	"""docstring for asocia2_hist_conv_prestamo"""
	_name = 'asocia2.hist_conv_prestamo'
	_description = 'Historico de Convenio'
	_columns = {
		'conv_prestamo_id':fields.many2one('asocia2.conv_prestamo', 'ID convenio'),
		'estado':fields.selection([('active','Activo'),('finished','Finalizado')], 'Estado de Convenio', required=True),
		'fecha':fields.date('Fecha de cambio de estado', required=True),
	}
	_defaults = {
	}

class asocia2_conv_pago(osv.osv):
	"""docstring for asocia2_conv_pago"""
	_name = 'asocia2.conv_pago'
	_description = 'Convenio de Pagos'
	_columns = {
		'proveedor_id':fields.many2one('res.partner', 'ID proveedor'),
		'categ_id': fields.many2one('product.category','Categoria del pago', required=True, change_default=True, domain="[('type','=','normal')]" ,help="Seleccione la categoria para el pago actual"),
		'porcentaje_para_aportes':fields.float('Porcentaje para aportes (%)', required=True),
		'causacion':fields.boolean('Causacion'),
		'pago':fields.boolean('Pago'),
		'estado':fields.selection([('active','Activo'),('finished','Finalizado')], 'Estado de Convenio', required=True),
		'fecha_inicio':fields.date('Fecha de inicio convenio', required=True),
		'hist_conv_pago_ids': fields.one2many('asocia2.hist_conv_pago', 'conv_pago_id','Historia de convenio'),
		'prioridad_de_pago_ids': fields.one2many('asocia2.prioridad_de_pago', 'conv_pago_id','Prioridad para aplicacion del pago'),
	}
	_defaults = {
	}

class asocia2_hist_conv_pago(osv.osv):
	"""docstring for asocia2_hist_conv_pago"""
	_name = 'asocia2.hist_conv_pago'
	_description = 'Historico de Convenio'
	_columns = {
		'conv_pago_id':fields.many2one('asocia2.conv_pago', 'ID convenio'),
		'estado':fields.selection([('active','Activo'),('finished','Finalizado')], 'Estado de Convenio', required=True),
		'fecha':fields.date('Fecha de cambio de estado', required=True),
	}
	_defaults = {
	}

class asocia2_prioridad_de_pago(osv.osv):
	"""docstring for asocia2_prioridad_de_pago"""
	_name = 'asocia2.prioridad_de_pago'
	_description = 'Prioridad para aplicacion del pago'
	_columns = {
		'conv_pago_id':fields.many2one('asocia2.conv_pago', 'ID convenio'),
		'categ_id': fields.many2one('product.category','Categoria del pago', required=True, change_default=True, domain="[('type','=','normal')]" ,help="Seleccione la categoria para el pago a aplicar"),
	}
	_defaults = {
	}

class asocia2_control_procesos(osv.osv):
	"""docstring for asocia2_control_procesos"""
	_name = 'asocia2.control_procesos'
	_description = 'Control de procesos'
	_columns = {
		'periodo_actual':fields.char('Periodo actual', size=7, required=True ,help="Indique el periodo actual con el formato AAAA-PP (Vigencia y periodo)"),
		'periodos_ids': fields.one2many('asocia2.periodos', 'control_procesos_id','Periodos'),
	}
	_defaults = {
	}

	def cierre(self, cr, uid, ids, context=None):
		""" Acciones para Cierre de un periodo """
		# 1. Valida que se hayan ejecutado todos los procesos del periodo actual
		control_periodo = self.browse(cr, uid, ids)
		periodos=self.pool.get('asocia2.periodos')
		procesos=self.pool.get('asocia2.procesos')
		hist_procesos=self.pool.get('asocia2.hist_procesos')
		partner=self.pool.get('res.partner')
		conv_servicio=self.pool.get('asocia2.conv_servicio')
		conv_prestamo=self.pool.get('asocia2.conv_prestamo')
		conv_pago=self.pool.get('asocia2.conv_pago')
		periodoid = periodos.search(cr, uid, [('periodo','=',control_periodo.periodo_actual)])
		NoEjecutados = ""
		if periodoid:
			#raise RuntimeError(proc_mes,value,instance.periodo_actual)
			print "&&&&&&&& periodoid-->", periodoid , periodoid[0], control_periodo, control_periodo.periodo_actual
			procesosid = procesos.search(cr, uid, [('periodos_id','=',periodoid[0])])
			print "&&&&&&&& procesosid-->", procesosid
			for procesoid in procesosid:
				proceso = procesos.browse(cr, uid, procesoid)
				print "&&&&&&&& procesos del periodo-->", control_periodo.periodo_actual, proceso, procesoid
				if hist_procesos.search(cr, uid, [('procesos_id','=',procesoid)]):
					pass
				else:
					NoEjecutados = NoEjecutados + proceso.nombre_proceso + ', '
		if NoEjecutados:
			raise osv.except_osv(_('Error!'), _(u"En el periodo '%s' no se han ejecutado estos procesos: '%s'"% (control_periodo.periodo_actual, NoEjecutados.decode('utf-8'))))
			#return("En el periodo '%s' no se han ejecutado estos procesos: '%s'"% (instance.periodo_actual, NoEjecutados.decode('utf-8')))
		# 2. Calcula nuevo periodo
		anioi = int(control_periodo.periodo_actual[0:4])
		mesi = int(control_periodo.periodo_actual[5:7])
		if mesi == 12:
			aniof = anioi + 1
			mesf = 1
		else:
			aniof = anioi
			mesf = mesi + 1
		nuevo_periodo = str(aniof)+'-'+str(mesf).zfill(2)
		print "&&&&&&&& periodo actual-->", control_periodo.periodo_actual
		print "&&&&&&&& nuevo periodo-->", nuevo_periodo
		# 2. Crea datos para nuevo periodo
		# 2.1. Crea registro del nuevo periodo
		if periodos.search(cr, uid, [('periodo','=',nuevo_periodo)]):
			raise osv.except_osv(_('Error!'), _('Ya esta creado el nuevo periodo ' + nuevo_periodo + ' en asocia2_periodos'))
		else:
			asocia2_data = {
				'control_procesos_id': control_periodo.id, 
				'periodo': nuevo_periodo, 
			}
			periodon_id = periodos.create(cr, uid, asocia2_data, context=context)
		# 2.2. Crea directorio del nuevo periodo
		if os.name == 'posix':
			DirectorioBase = '/home/helman/Procesos'
		else:
			DirectorioBase = 'c:\Procesos'
		if os.access(DirectorioBase, os.F_OK):
			if os.name == 'posix':
				Directorio = DirectorioBase + '/' + nuevo_periodo
			else:
				Directorio = DirectorioBase + '\\' + nuevo_periodo
			if os.access(Directorio, os.F_OK):
				raise osv.except_osv(_('Error!'), _('Se va a crear el directorio ' + Directorio + ', pero ya existe'))
			else:
				os.mkdir(Directorio)
		else:
			if os.name == 'posix':
				raise osv.except_osv(_('Error!'), _('No existe el directorio /home/helman/Procesos - ' + os.curdir))
			else:
				raise osv.except_osv(_('Error!'), _('No existe el directorio c:\Procesos - ' + os.curdir))
		proveedores = partner.search(cr, uid, [('supplier','=',True),('active','=',True)])
		Proc_mes=[]
		i=1
		for prov in proveedores:
			p = partner.browse(cr, uid, prov)
			convs_s = conv_servicio.search(cr, uid, [('proveedor_id','=',prov)])
			for itemid in convs_s:
				item = conv_servicio.browse(cr, uid, itemid)
				if item.estado == 'active':
					# 2.3. Crea procesos del convenio de servicios
					servicio = item.categ_id.name
					if procesos.search(cr, uid, [('categ_id','=',item.categ_id.id),('periodos_id','=',periodon_id)]):
						raise osv.except_osv(_('Error!'), _('Ya esta creado el proceso ' + item.categ_id.name + ' en asocia2_procesos'))
					else:
						if item.causacion:
							n_proceso = 'causa_' + item.tipo_servicio
							asocia2_data = {
								'periodos_id': periodon_id,
								'proveedor_id': p.id,
								'categ_id': item.categ_id.id, 
								'causacion': True, 
								'pago': False, 
								'nombre_proceso': n_proceso, 
							}
							asocia2_id = procesos.create(cr, uid, asocia2_data, context=context)
						if item.pago:
							n_proceso = 'pago_' + item.tipo_servicio
							asocia2_data = {
								'periodos_id': periodon_id,
								'proveedor_id': p.id,
								'categ_id': item.categ_id.id, 
								'causacion': False, 
								'pago': True, 
								'nombre_proceso': n_proceso, 
							}
							asocia2_id = procesos.create(cr, uid, asocia2_data, context=context)
					# 2.4. Crea directorios del convenio de servicios
					if os.name == 'posix':
						DirectorioConvenio = Directorio + '/' + item.categ_id.name + ' - ' + p.name
					else:
						DirectorioConvenio = Directorio + '\\' + item.categ_id.name + ' - ' + p.name
					if os.access(DirectorioConvenio, os.F_OK):
						pass
					else:
						#raise RuntimeError(Directorio,conv['convenio'],conv['convenio'].decode('utf-8'),conv['convenio'].decode('latin-1'),conv['convenio'].decode('utf-16', 'replace'))
						os.mkdir(DirectorioConvenio)
			convs_pres = conv_prestamo.search(cr, uid, [('proveedor_id','=',prov)])
			for itemid in convs_pres:
				item = conv_prestamo.browse(cr, uid, itemid)
				if item.estado == 'active':
					# 2.5. Crea procesos del convenio de prestamos
					prestamo = item.categ_id.name
					if procesos.search(cr, uid, [('categ_id','=',item.categ_id.id),('periodos_id','=',periodon_id)]):
						raise osv.except_osv(_('Error!'), _('Ya esta creado el proceso ' + item.categ_id.name + ' en asocia2_procesos'))
					else:
						if item.causacion:
							n_proceso = 'causa_prestamo'
							asocia2_data = {
								'periodos_id': periodon_id,
								'proveedor_id': p.id,
								'categ_id': item.categ_id.id, 
								'causacion': True, 
								'pago': False, 
								'nombre_proceso': n_proceso, 
							}
							asocia2_id = procesos.create(cr, uid, asocia2_data, context=context)
						if item.pago:
							n_proceso = 'pago_prestamo'
							asocia2_data = {
								'periodos_id': periodon_id,
								'proveedor_id': p.id,
								'categ_id': item.categ_id.id, 
								'causacion': False, 
								'pago': True, 
								'nombre_proceso': n_proceso, 
							}
							asocia2_id = procesos.create(cr, uid, asocia2_data, context=context)
					# 2.6. Crea directorios del convenio de prestamos
					if os.name == 'posix':
						DirectorioConvenio = Directorio + '/' + item.tipo_prestamo + ' - ' + p.name.decode('utf-8')
					else:
						DirectorioConvenio = Directorio + '\\' + item.tipo_prestamo + ' - ' + p.name.decode('utf-8')
					if os.access(DirectorioConvenio, os.F_OK):
						pass
					else:
						#raise RuntimeError(Directorio,conv['convenio'],conv['convenio'].decode('utf-8'),conv['convenio'].decode('latin-1'),conv['convenio'].decode('utf-16', 'replace'))
						os.mkdir(DirectorioConvenio)
			convs_p = conv_pago.search(cr, uid, [('proveedor_id','=',prov)])
			for itemid in convs_p:
				item = conv_pago.browse(cr, uid, itemid)
				if item.estado == 'active':
					# 2.7. Crea procesos del convenio de pagos
					if procesos.search(cr, uid, [('categ_id','=',item.categ_id.id),('periodos_id','=',periodon_id)]):
						raise osv.except_osv(_('Error!'), _('Ya esta creado el proceso ' + item.categ_id.name + ' en asocia2_procesos'))
					else:
						if item.causacion:
							n_proceso = 'causa_Convenio_pago'
							asocia2_data = {
								'periodos_id': periodon_id,
								'proveedor_id': p.id,
								'categ_id': item.categ_id.id, 
								'causacion': True, 
								'pago': False, 
								'nombre_proceso': n_proceso, 
							}
							asocia2_id = procesos.create(cr, uid, asocia2_data, context=context)
						if item.pago:
							n_proceso = 'pago_Convenio_pago'
							asocia2_data = {
								'periodos_id': periodon_id,
								'proveedor_id': p.id,
								'categ_id': item.categ_id.id, 
								'causacion': False, 
								'pago': True, 
								'nombre_proceso': n_proceso, 
							}
							asocia2_id = procesos.create(cr, uid, asocia2_data, context=context)
					# 2.8. Crea directorios del convenio de pagos
					if os.name == 'posix':
						DirectorioConvenio = Directorio + '/' + 'Convenio_pago' + ' - ' + p.name.decode('utf-8')
					else:
						DirectorioConvenio = Directorio + '\\' + 'Convenio_pago' + ' - ' + p.name.decode('utf-8')
					if os.access(DirectorioConvenio, os.F_OK):
						pass
					else:
						#raise RuntimeError(Directorio,conv['convenio'],conv['convenio'].decode('utf-8'),conv['convenio'].decode('latin-1'),conv['convenio'].decode('utf-16', 'replace'))
						os.mkdir(DirectorioConvenio)
		#raise RuntimeError('Nuevo periodo generado')
		# 3. Actualiza el nuevo periodo
		self.write(cr, uid, ids, {'periodo_actual':nuevo_periodo}, context=None)
		#raise RuntimeError('Ambiente',os.name,os.uname(),sys.platform)
		return

class asocia2_periodos(osv.osv):
	"""docstring for asocia2_periodos"""
	_name = 'asocia2.periodos'
	_description = 'Periodos'
	_columns = {
		'control_procesos_id':fields.many2one('asocia2.control_procesos', 'ID periodo'),
		'periodo':fields.char('Periodo', size=7, required=True ,help="Indique el periodo con el formato AAAA-PP (Vigencia y periodo)"),
		'procesos_ids': fields.one2many('asocia2.procesos', 'periodos_id','Procesos'),
	}
	_defaults = {
	}

class asocia2_procesos(osv.osv):
	"""docstring for asocia2_procesos"""
	_name = 'asocia2.procesos'
	_description = 'Procesos'
	_columns = {
		'periodos_id':fields.many2one('asocia2.periodos', 'ID periodo'),
		'proveedor_id':fields.many2one('res.partner', 'ID proveedor'),
		'categ_id': fields.many2one('product.category','Categoria del proceso', required=True, change_default=True, domain="[('type','=','normal')]" ,help="Seleccione la categoria para el proceso"),
		'causacion':fields.boolean('Causacion'),
		'pago':fields.boolean('Pago'),
		'nombre_proceso':fields.char('Nombre del Proceso', size=20, required=True),
		'hist_procesos_ids': fields.one2many('asocia2.hist_procesos', 'procesos_id','Historia de Procesos'),
	}
	_defaults = {
	}

	def proceso(self, cr, uid, ids, context=None):
		""" Ejecución de los diferentes procesos """
		procesos=self.pool.get('asocia2.procesos')
		item = procesos.browse(cr, uid, ids[0])
		ejecutado = False
		print "&&&&&&&& self-->", item.nombre_proceso, item.categ_id, cr, uid, ids
		if item.nombre_proceso == 'causa_credito':
			a = self.causa_credito(cr, uid, ids, context=None)
			print "&&&&&&&& a -->", a
			ejecutado = True
		if item.nombre_proceso == 'causa_salud':
			a = self.causa_salud(cr, uid, ids, context=None)
			print "&&&&&&&& a -->", a
			ejecutado = True
		if item.nombre_proceso == 'causa_telefonia':
			a = self.causa_telefonia(cr, uid, ids, context=None)
			print "&&&&&&&& a -->", a
			ejecutado = True
		if item.nombre_proceso == 'causa_prestamo':
			a = self.causa_prestamo(cr, uid, ids, context=None)
			print "&&&&&&&& a -->", a
			ejecutado = True
		if item.nombre_proceso == 'causa_Convenio_pago':
			a = self.causa_Convenio_pago(cr, uid, ids, context=None)
			print "&&&&&&&& a -->", a
			ejecutado = True
		if item.nombre_proceso == 'pago_Convenio_pago':
			a = self.pago_Convenio_pago(cr, uid, ids, context=None)
			print "&&&&&&&& a -->", a
			ejecutado = True
		if not ejecutado:
			raise osv.except_osv(_('Error!'), _('No existe el proceso ' + item.nombre_proceso + ' entre los posibles a ejecutar - No codificado'))
		return

class asocia2_hist_procesos(osv.osv):
	"""docstring for asocia2_hist_procesos"""
	_name = 'asocia2.hist_procesos'
	_description = 'Historico de Procesos'
	_columns = {
		'procesos_id':fields.many2one('asocia2.procesos', 'ID proceso'),
		'fecha':fields.date('Fecha de ejecución del proceso', required=True),
		'resultado':fields.char('Resultado del Proceso', size=20, required=True),
	}
	_defaults = {
	}
