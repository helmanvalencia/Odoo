##############################################################################
#
#    Helman Valencia
#    Copyright (C) 2015.
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

from openerp.osv import fields, osv

class sale_order(osv.osv):
    _inherit = "sale.order"

    def _product_profit(self, cr, uid, ids, field_name, arg, context=None):
        result = {}
        for sale in self.browse(cr, uid, ids, context=context):
            result[sale.id] = 0.0
            amount_untaxed = 0.0
            for line in sale.order_line:
                print "############################## line-->", line
                print "############################## price_subtotal-->", line.price_subtotal
                result[sale.id] += line.margin or 0.0
                amount_untaxed += line.price_subtotal or 0.0
        print "############################## amount_untaxed-->", amount_untaxed
        print "############################## result[sale.id]-->", result[sale.id]
        result[sale.id] = result[sale.id]*100/amount_untaxed
        return result

    _columns = {
        'profit': fields.function(_product_profit, string='Profit(%)', help="It gives profitability in percent.",
                store = True),
    }


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: