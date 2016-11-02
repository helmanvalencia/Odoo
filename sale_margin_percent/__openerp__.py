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

{
    'name': 'Margins (%) in Sales Orders',
    'version':'1.0',
    'category' : 'Sales Management',
    'description': """
This module adds the 'Margin %' on sales order.
===============================================

This gives the profitability in percent (%) by calculating the difference between the Unit
Price and Cost Price.
    """,
    'author':'Helman Valencia',
    'depends':['sale_margin'],
    'demo':['sale_margin_percent_demo.xml'],
    'test': ['test/sale_margin_percent.yml'],
    'data':['security/ir.model.access.csv','sale_margin_percent_view.xml'],
    'auto_install': False,
    'installable': True,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

