import logging
import json
from odoo import http, fields, tools, _
from odoo import http
from odoo.http import request
from odoo.addons.web.controllers.main import ensure_db
from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.exceptions import ValidationError
from werkzeug.exceptions import NotFound
_logger = logging.getLogger(__name__)

class EhaMembershipWebsite(WebsiteSale):
    """
        This route ensures services are displayed on the /membership-service page
        To setup: Kindly go to eha_membership ==> configuration ==> Membership plan and add
        the plan.
        On each plan, select a product to map to it, add related product
        prices list that matches the select product and then the system will
        pick the product price list item and prepares a dictionary to display
        the prices for user
    """
    @http.route(['/find_members'], type='json', auth="public", website=True, methods=["post"])
    def find_members(self, id):
        if id:
            member = request.env['eha.membership'].sudo().search(
                [('partner_id', '=', id)]
            )
            if member:
                vals = {}
                partner = member and member.partner_id
                vals.update({
                    'id': partner.id,
                    'member_id': member.id,
                    'lastname': partner.lastname or '',
                    'firstname': partner.firstname or '',
                    'middlename': partner.lastname2 or '',
                    'gender': partner.sex or '',
                    'lga': partner.lga or '',
                    'dob': partner.dob or '',
                    'email': partner.email or '',
                    'phone': partner.phone or '',
                    'street': partner.street or '',
                    'city': partner.city or '',
                    'state': partner.state_id.id or '',
                })
                return vals
        return False
            
    def get_package_details(self, package_name):
        vals = {
            'pricing':[],
            'products': False,
            'total': 0,
            'type': 'standard',
        }
        if package_name == 'standard':
            products = request.env['product.product'].sudo().search(
                [('default_code', 'in', ['STAND-YOUTH', 'STAND-ADULT', 'STAND-SENIOR'])])
            for rec in products:
                price = rec.list_price
                vals['pricing'].append(price)
            vals['products'] = products.mapped('id') or [0, 0, 0]
            vals['total'] = sum(products.mapped('list_price')) or 0
            vals['type'] = 'standard'
            return vals
        elif package_name == 'premium':
            products = request.env['product.product'].sudo().search(
                [('default_code', 'in', ['PREM-YOUTH', 'PREM-ADULT', 'PREM-SENIOR'])])
            for rec in products:
                price = rec.list_price
                vals['pricing'].append(price)
            vals['products'] = products.mapped('id') or [0, 0, 0]
            vals['total'] = sum(products.mapped('list_price')) or 0
            vals['type'] = 'premium'
            return vals
        elif package_name == 'international':
            products = request.env['product.product'].sudo().search(
                [('default_code', 'in', ['INT-YOUTH', 'INT-ADULT', 'INT-SENIOR'])])
            for rec in products:
                price = rec.list_price
                vals['pricing'].append(price)
            vals['products'] = products.mapped('id') or [0, 0, 0]
            vals['total'] = sum(products.mapped('list_price')) or 0
            vals['type'] = 'international'
            return vals
    
    @http.route('/eha_membership/category', type='http', auth='public', website=True)
    def membership_category(self , **kwargs):
        categories =  request.env['eha.membership.category'].sudo().search([])
        for cat in categories:
            values = {
                'categories': cat
            }
            
        return request.render("eha_membership_website.select_membership_category", values)
    
    @http.route('/shop/plans/compare', type='http', auth="public", website=True)
    def compare_plans(self, **kw):
        return http.request.render('eha_membership_website.compare_plans')
            
    @http.route(
        ['/eha_membership/individual-category/<category_name>', '/eha_membership/family-category/<category_name>', '/eha_membership/group-category'], 
        type='http', auth='public', website=True)
    def membership_plan(self , category_name, **kwargs):
        category_obj = request.env['eha.membership.category'].search([('name', '=', category_name)], limit=1)
        plans_with_products = []
        for plan in request.env['eha.membership.plan'].sudo().search([]):
            d = dict()
            d['name'] = plan.name
            d['code'] = plan.plan_code
            # d['category_obj'] = {'category_id': category_obj.id, 'category_discount': category_obj.discount}
            d['category_discount'] = category_obj.discount_qty
            d['category_id'] = category_obj.id

            # get plan products
            products = plan.mapped('membership_plan_line_ids').filtered(
                lambda s: s.display_on_website) 
            d['products'] = products
            plans_with_products.append(d)

        context = {
            "plans": plans_with_products
        }
        path = request.httprequest.path
        if path == '/eha_membership/individual-category/Individual':
            template = "eha_membership_website.select_individual_membership_plan"
            
        elif path == '/eha_membership/family-category/Family':
            template = "eha_membership_website.select_family_membership_plan"
        _logger.info(f"GET MY PLAN DETAILS ==> {plans_with_products}, == > {context.get('plans')}")
        return request.render(template, qcontext=context)
    
    @http.route('/eha_membership/subscribe/<product_id>', type='http', auth='public', website=True)
    def single_membership_subscription(self , product_id):
        product = request.env['product.product'].sudo().search([('name', '=', product_id)], limit=1)
        context = {
            "products": product
        }
        if product:
            return request.render("eha_membership_website.single_subscription_detail", qcontext=context)
        if not product.can_access_from_current_website():
            raise NotFound()
        
    @http.route(
        ['/family-standard-subscription', '/family-premium-subscription', '/family-premium-international-subscription'],
        type='http', auth='public', website=True, methods=["POST", "GET"])
    def family_membership_subscription(self):
        vals = {
            'pricing':[],
            'products': False,
            'total': 0,
            'type': 'standard',
        }
        path = request.httprequest.path
        if path == '/family-standard-subscription':
            template = 'eha_membership_website.template_family_standard'
            vals = self.get_package_details('standard')
        elif path == '/family-premium-subscription':
            template = 'eha_membership_website.template_family_premium'
            vals = self.get_package_details('premium')
        elif path == '/family-premium-international-subscription':
            template = 'eha_membership_website.template_family_prem_international'
            vals = self.get_package_details('international')
            
        _logger.info(f"GET MY FAMILY PRICE ==> {vals}")
        return request.render(template, vals)
        
    
    