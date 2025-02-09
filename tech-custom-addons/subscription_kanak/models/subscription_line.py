# -*- coding: utf-8 -*-
# Powered by Kanak Infosystems LLP.
# © 2020 Kanak Infosystems LLP. (<https://www.kanakinfosystems.com>).

import logging
from collections import defaultdict
from dateutil.relativedelta import relativedelta

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class SubscriptionLine(models.Model):
    _name = 'subscription.line'
    _description = "Subscription Line"

    subscription_id = fields.Many2one(
        comodel_name='subscription.subscription',
        string="Subscription",
        required=True, ondelete='cascade', index=True, copy=False)
    sequence = fields.Integer(string="Sequence", default=10)
    company_id = fields.Many2one(
        related='subscription_id.company_id',
        store=True, index=True, precompute=True)
    currency_id = fields.Many2one(
        related='subscription_id.currency_id',
        depends=['subscription_id.currency_id'],
        store=True, precompute=True)
    partner_id = fields.Many2one(
        related='subscription_id.partner_id',
        string="Customer",
        store=True, index=True, precompute=True)
    salesman_id = fields.Many2one(
        related='subscription_id.user_id',
        string="Salesperson",
        store=True, precompute=True)
    display_type = fields.Selection(
        selection=[
            ('line_section', "Section"),
            ('line_note', "Note"),
        ],
        default=False)
    product_id = fields.Many2one(
        comodel_name='product.product',
        string="Product",
        change_default=True, ondelete='restrict', check_company=True, index='btree_not_null',
        domain="[('is_subscription', '=', True), '|', ('company_id', '=', False), ('company_id', '=', company_id)]")
    product_template_id = fields.Many2one(
        string="Product Template",
        comodel_name='product.template',
        compute='_compute_product_template_id',
        readonly=False,
        search='_search_product_template_id',
        domain=[('is_subscription', '=', True)])
    product_uom_category_id = fields.Many2one(related='product_id.uom_id.category_id', depends=['product_id'])
    product_uom = fields.Many2one(
        comodel_name='uom.uom',
        string="Unit of Measure",
        compute='_compute_product_uom',
        store=True, readonly=False, precompute=True, ondelete='restrict',
        domain="[('category_id', '=', product_uom_category_id)]")
    product_no_variant_attribute_value_ids = fields.Many2many(
        comodel_name='product.template.attribute.value',
        string="Extra Values",
        compute='_compute_no_variant_attribute_values',
        store=True, readonly=False, precompute=True, ondelete='restrict')

    name = fields.Text(
        string="Description",
        compute='_compute_name',
        store=True, readonly=False, required=True, precompute=True)
    quantity = fields.Float(
        string="Quantity",
        digits='Product Unit of Measure',
        default=1.0,
        required=True)
    tax_id = fields.Many2many(
        comodel_name='account.tax',
        string="Taxes",
        compute='_compute_tax_id',
        store=True, readonly=False, precompute=True,
        context={'active_test': False})
    price_unit = fields.Float(
        string="Unit Price",
        compute='_compute_price_unit',
        digits='Product Price',
        store=True, readonly=False, required=True, precompute=True)
    pricelist_item_id = fields.Many2one(
        comodel_name='product.pricelist.item',
        compute='_compute_pricelist_item_id')
    discount = fields.Float(
        string="Discount (%)",
        compute='_compute_discount',
        digits='Discount',
        store=True, readonly=False, precompute=True)

    price_subtotal = fields.Monetary(
        string="Subtotal",
        compute='_compute_amount',
        store=True, precompute=True)
    price_tax = fields.Float(
        string="Total Tax",
        compute='_compute_amount',
        store=True, precompute=True)
    price_total = fields.Monetary(
        string="Total",
        compute='_compute_amount',
        store=True, precompute=True)

    date_start = fields.Date(string='Start Date', default=fields.Date.today)
    date_end = fields.Date(
        compute='_compute_date_end',
        string='End Date',
        store=True, readonly=False, precompute=True)
    duration_cycle = fields.Selection([
        ('unlimited', 'Forever'),
        ('limited', 'Fixed')
    ], string='Duration', default='unlimited')
    duration_cycle_count = fields.Integer(string="Duration Cycle Count")
    product_subscription_intervals = fields.Many2many(related='product_id.subscription_intervals', string="Product Subscription Intervals", depends=['product_id'])
    subscription_interval = fields.Many2one(
        'subscription.intervals',
        domain="[('id', 'in', product_subscription_intervals)]",
        string='Interval',
    )
    recurring_next_date = fields.Date(string='Next Order Date', store=True)
    sale_order_line_ids = fields.One2many('sale.order.line', 'subscription_line_id', string="Sale Order Line", required=False, copy=False)
    invoice_lines = fields.Many2many(
        comodel_name='account.move.line',
        relation='subscription_line_invoice_rel', column1='subscription_line_id', column2='invoice_line_id',
        string="Invoice Lines",
        copy=False)
    state = fields.Selection([('draft', 'Draft'), ('in_progress', 'In Progress'), ('hold', 'Hold'), ('closed', 'Closed')], string='Status', default='draft')

    # Added by Technians
    project_id = fields.Many2one(
        'project.project',
        string = 'Project',
        # domain=lambda self: self._compute_subscription_line_project()
        # domain="[('partner_id', '=', subscription_id.partner_id)]"
        
    )
    # @api.onchange('subscription_id')
    # def _compute_subscription_line_project(self):
    #     parent_subscription_id = self.subscription_id.id
    #     subscription = self.env['subscription.subscription'].search([('id', '=', parent_subscription_id)])
    #     partner_id = subscription.partner_id.id
    #     domain = [('partner_id', '=', partner_id)]
    #     return domain
    
    # def create(self, vals):
    #     context = self.env.context.copy()
    #     context.update(parent_field=vals.get('parent_id') and self.env['subscription.subscription'].browse(vals['partner_id']).parent_field)
    #     self = self.with_context(context)
    #     return super(SubscriptionLine, self).create(vals)

    # def write(self, vals):
    #     if 'parent_id' in vals:
    #         context = self.env.context.copy()
    #         context.update(parent_field=vals['parent_id'] and self.env['subscription.subscription'].browse(vals['partner_id']).parent_field)
    #         self = self.with_context(context)
    #     return super(SubscriptionLine, self).write(vals)




    
    @api.constrains('duration_cycle_count')
    def _check_duration_cycle_count(self):
        for record in self:
            if record.duration_cycle != 'unlimited' and record.duration_cycle_count <= 0:
                raise ValidationError("Duration Cycle Count must be greater than 0.")

    @api.depends('product_id')
    def _compute_product_template_id(self):
        for line in self:
            line.product_template_id = line.product_id.product_tmpl_id

    def _search_product_template_id(self, operator, value):
        return [('product_id.product_tmpl_id', operator, value)]

    @api.depends('product_id')
    def _compute_product_uom(self):
        for line in self:
            if not line.product_uom or (line.product_id.uom_id.id != line.product_uom.id):
                line.product_uom = line.product_id.uom_id

    @api.depends('product_id')
    def _compute_name(self):
        for line in self:
            if not line.product_id:
                continue
            line.name = line.with_context(lang=line.partner_id.lang)._get_sale_order_line_multiline_description_sale()

    def _get_sale_order_line_multiline_description_sale(self):
        self.ensure_one()
        return self.product_id.get_product_multiline_description_sale()

    @api.depends('product_id')
    def _compute_no_variant_attribute_values(self):
        for line in self:
            if not line.product_id:
                line.product_no_variant_attribute_value_ids = False
                continue
            if not line.product_no_variant_attribute_value_ids:
                continue
            valid_values = line.product_id.product_tmpl_id.valid_product_template_attribute_line_ids.product_template_value_ids
            for ptav in line.product_no_variant_attribute_value_ids:
                if ptav._origin not in valid_values:
                    line.product_no_variant_attribute_value_ids -= ptav

    @api.depends('product_id')
    def _compute_tax_id(self):
        taxes_by_product_company = defaultdict(lambda: self.env['account.tax'])
        lines_by_company = defaultdict(lambda: self.env['subscription.line'])
        cached_taxes = {}
        for line in self:
            lines_by_company[line.company_id] += line
        for product in self.product_id:
            for tax in product.taxes_id:
                taxes_by_product_company[(product, tax.company_id)] += tax
        for company, lines in lines_by_company.items():
            for line in lines.with_company(company):
                taxes = taxes_by_product_company[(line.product_id, company)]
                if not line.product_id or not taxes:
                    # Nothing to map
                    line.tax_id = False
                    continue
                fiscal_position = line.subscription_id.fiscal_position_id
                cache_key = (fiscal_position.id, company.id, tuple(taxes.ids))
                if cache_key in cached_taxes:
                    result = cached_taxes[cache_key]
                else:
                    result = fiscal_position.map_tax(taxes)
                    cached_taxes[cache_key] = result
                # If company_id is set, always filter taxes by the company
                line.tax_id = result

    @api.depends('product_id', 'product_uom', 'quantity')
    def _compute_pricelist_item_id(self):
        for line in self:
            if not line.product_id or line.display_type or not line.subscription_id.pricelist_id:
                line.pricelist_item_id = False
            else:
                line.pricelist_item_id = line.subscription_id.pricelist_id._get_product_rule(
                    line.product_id,
                    line.quantity or 1.0,
                    uom=line.product_uom,
                    date=line.subscription_id.date_order,
                )

    @api.depends('product_id', 'product_uom', 'quantity')
    def _compute_price_unit(self):
        for line in self:
            if not line.product_uom or not line.product_id or not line.subscription_id.pricelist_id:
                line.price_unit = 0.0
            else:
                price = line.with_company(line.company_id)._get_display_price()
                line.price_unit = line.product_id._get_tax_included_unit_price(
                    line.company_id,
                    line.subscription_id.currency_id,
                    line.subscription_id.date_order,
                    'sale',
                    fiscal_position=line.subscription_id.fiscal_position_id,
                    product_price_unit=price,
                    product_currency=line.currency_id
                )

    def _get_display_price(self):
        self.ensure_one()

        pricelist_price = self._get_pricelist_price()

        if self.subscription_id.pricelist_id.discount_policy == 'with_discount':
            return pricelist_price

        if not self.pricelist_item_id:
            # No pricelist rule found => no discount from pricelist
            return pricelist_price

        base_price = self._get_pricelist_price_before_discount()

        # negative discounts (= surcharge) are included in the display price
        return max(base_price, pricelist_price)

    @api.depends('product_id', 'product_uom', 'quantity')
    def _compute_discount(self):
        for line in self:
            if not line.product_id or line.display_type:
                line.discount = 0.0

            if not (
                line.subscription_id.pricelist_id
                and line.subscription_id.pricelist_id.discount_policy == 'without_discount'
            ):
                continue

            line.discount = 0.0

            line = line.with_company(line.company_id)
            pricelist_price = line._get_pricelist_price()
            base_price = line._get_pricelist_price_before_discount()

            if base_price != 0:  # Avoid division by zero
                discount = (base_price - pricelist_price) / base_price * 100
                if (discount > 0 and base_price > 0) or (discount < 0 and base_price < 0):
                    # only show negative discounts if price is negative
                    # otherwise it's a surcharge which shouldn't be shown to the customer
                    line.discount = discount

    def _get_pricelist_price(self):
        self.ensure_one()
        self.product_id.ensure_one()

        pricelist_rule = self.pricelist_item_id
        order_date = self.subscription_id.date_order or fields.Date.today()
        product = self.product_id.with_context(**self._get_product_price_context())
        qty = self.quantity or 1.0
        uom = self.product_uom or self.product_id.uom_id

        price = pricelist_rule._compute_price(
            product, qty, uom, order_date, currency=self.currency_id)

        return price

    def _get_product_price_context(self):
        self.ensure_one()
        res = {}

        no_variant_attributes_price_extra = [
            ptav.price_extra for ptav in self.product_no_variant_attribute_value_ids.filtered(
                lambda ptav:
                    ptav.price_extra and
                    ptav not in self.product_id.product_template_attribute_value_ids
            )
        ]
        if no_variant_attributes_price_extra:
            res['no_variant_attributes_price_extra'] = tuple(no_variant_attributes_price_extra)

        return res

    def _get_pricelist_price_before_discount(self):
        self.ensure_one()
        self.product_id.ensure_one()

        pricelist_rule = self.pricelist_item_id
        order_date = self.subscription_id.date_order or fields.Date.today()
        product = self.product_id.with_context(**self._get_product_price_context())
        qty = self.quantity or 1.0
        uom = self.product_uom

        if pricelist_rule:
            pricelist_item = pricelist_rule
            if pricelist_item.pricelist_id.discount_policy == 'without_discount':
                # Find the lowest pricelist rule whose pricelist is configured
                # to show the discount to the customer.
                while pricelist_item.base == 'pricelist' and pricelist_item.base_pricelist_id.discount_policy == 'without_discount':
                    rule_id = pricelist_item.base_pricelist_id._get_product_rule(
                        product, qty, uom=uom, date=order_date)
                    pricelist_item = self.env['product.pricelist.item'].browse(rule_id)

            pricelist_rule = pricelist_item

        price = pricelist_rule._compute_base_price(
            product,
            qty,
            uom,
            order_date,
            target_currency=self.currency_id,
        )

        return price

    def _convert_to_tax_base_line_dict(self):
        self.ensure_one()
        return self.env['account.tax']._convert_to_tax_base_line_dict(
            self,
            partner=self.subscription_id.partner_id,
            currency=self.subscription_id.currency_id,
            product=self.product_id,
            taxes=self.tax_id,
            price_unit=self.price_unit,
            quantity=self.quantity,
            discount=self.discount,
            price_subtotal=self.price_subtotal,
        )

    @api.depends('quantity', 'discount', 'price_unit', 'tax_id')
    def _compute_amount(self):
        for line in self:
            tax_results = self.env['account.tax']._compute_taxes([line._convert_to_tax_base_line_dict()])
            totals = list(tax_results['totals'].values())[0]
            # amount_untaxed = totals['amount_untaxed']
            # amount_tax = totals['amount_tax']
            if self.state == 'in_progress' :
                amount_untaxed = 0
                amount_tax = 0
            else:
                amount_untaxed = totals['amount_untaxed']
                amount_tax = totals['amount_tax']

            line.update({
                'price_subtotal': amount_untaxed,
                'price_tax': amount_tax,
                'price_total': amount_untaxed + amount_tax,
            })

    @api.depends('date_start', 'subscription_interval', 'duration_cycle', 'duration_cycle_count', 'subscription_interval')
    def _compute_date_end(self):
        for line in self:
            if line.date_start and line.duration_cycle == 'limited' and line.subscription_interval:
                recurring_interval = line.subscription_interval.recurring_interval
                recurring_rule_type = line.subscription_interval.recurring_rule_type
                periods = {'daily': 'days', 'weekly': 'weeks', 'monthly': 'months', 'semesterly': 'months', 'quarterly': 'months', 'yearly': 'years'}
                if recurring_rule_type == 'quarterly':
                    recurring_interval *= 3
                elif recurring_rule_type == 'semesterly':
                    recurring_interval *= 6
                line.date_end = fields.Date.from_string(line.date_start) + relativedelta(**{
                    periods[recurring_rule_type]: line.duration_cycle_count * recurring_interval})
                if line.duration_cycle == 'unlimited':
                    line.date_end = False

    @api.depends('price_unit', 'quantity', 'discount', 'subscription_id.pricelist_id')
    def _compute_price_subtotal(self):
        AccountTax = self.env['account.tax']
        for line in self:
            price = AccountTax._fix_tax_included_price(line.price_unit, line.product_id.sudo().taxes_id, AccountTax)
            price_subtotal = line.quantity * price * (100.0 - line.discount) / 100.0
            taxes = line.tax_id.compute_all(price_subtotal, line.subscription_id.currency_id, line.quantity, product=line.product_id, partner=line.subscription_id.partner_id)
            line.price_subtotal = taxes['total_included']

    def action_draft_subscription(self):
        today = fields.Date.from_string(fields.Date.today())
        for rec in self:
            rec.write({'state': 'draft', 'date_start': today})

    def services_in_project(self):
    # print('---------------------',self.env['project.project'].search([('id','=',self.project_id.id)]).name)
        project = self.env['project.project'].search([('id','=',self.project_id.id)],limit=1)
        if project and hasattr(project, 'project_service_ids'):
            subscription_lines = self.env['subscription.line'].search(
                [('project_id', '=', project.id),('state', '=', 'in_progress')])
            service_ids = []
            for subscription_line in subscription_lines:
                service_id = subscription_line.product_id.id
                service_ids.append(service_id)
            # print('service_idsservice_idsservice_ids',service_ids)
            for service_id in service_ids:
                project.project_service_ids = [(4, service_id)]
            # print('project.project_service_ids',project.project_service_ids.ids)
        else:
            print("Field 'project_service_ids' does not exist in the 'project' model.")




        # if project.project_service_ids:
        #     services = self.env['project.custom.checklist.template'].search([('service_ids.id','in',service_ids)])
        #     print("services----------------------------",services)
        #     template_ids = services.checklist_template_ids.ids
        #
        #     # common_services = list(set(services) & set(service_ids))
        #     # if common_services:
        #     for template_id in template_ids:
        #         lines = self.env['project.custom.checklist.line'].search([('project_id','=', project.id,)]).name.ids
        #         if template_id not in lines:
        #             self.env['project.custom.checklist.line'].create({
        #                 'project_id': project.id,
        #                 'name': template_id,
        #                 'updated_date': fields.Date.from_string(fields.Date.today()),
        #                 'state': 'new',
        #             })



    def action_start_subscription(self):
        today = fields.Date.from_string(fields.Date.today())
        for rec in self:
            rec.write({'state': 'in_progress', 'date_start': today})
            #Added by Technian
            rec.subscription_id.message_post(body="Subscription started for %s." % rec.display_name)
            rec._compute_date_end()
            rec.send_subscription_creation_mail()
            if self.env.context.get('with_button') and not rec.recurring_next_date:
                rec.recurring_next_date = fields.Date.context_today(rec)
            rec.services_in_project()


    def action_hold_subscription(self):
        for rec in self:
            rec.write({'state': 'hold'})
            rec.subscription_id.message_post(body="Subscription has been hold for %s." % rec.display_name)
            rec.services_in_project()

    def action_close_subscription(self):
        for rec in self:
            rec.write({'state': 'closed'})
            rec.subscription_id.message_post(body="Subscription has been closed for %s." % rec.display_name)
            rec.services_in_project()

    def send_subscription_creation_mail(self):
        template = self.sudo().env.ref('subscription_kanak.subscription_creation_alert')
        _logger.debug("Sending Subscription Creation Mail to %s for subscription %s", self.subscription_id.partner_id.email, self.subscription_id.id)
        template.send_mail(self.id)

    def unlink(self):
        for line in self:
            if line.state in ['in_progress', 'hold']:
                raise UserError(_('You can not remove subscription line , if line is in "Hold" or "In Progress" state.'))
        return super(SubscriptionLine, self).unlink()
    #Technians Code 
    @api.onchange('subscription_interval','duration_cycle','product_id','discount','quantity','price_unit','tax_id','date_start')
    def onchange_quantity(self):
        fields_list = ['subscription_interval','duration_cycle','product_id','discount','quantity','price_unit','tax_id','date_start']
        for field_name in fields_list:
            model = self.env['subscription.line']
            field_info = model.fields_get(allfields=[field_name])
            if field_info and field_name in field_info:
                field_label = field_info[field_name]['string']
                field_type = field_info[field_name]['type']
                if field_type == 'many2one':
                    old_value = self._origin[field_name].name if self._origin else False
                    new_value = self[field_name].name 
                else:
                    old_value = self._origin[field_name] if self._origin else False
                    new_value = self[field_name] 

                parent_subscription_id = self._origin.subscription_id.id
                message = f"{field_label} {old_value} <i class='fa fa-long-arrow-right'></i> {new_value} on {self.name}{field_type}"
                self.env['mail.message'].create({
                'model': 'subscription.subscription',
                'res_id': parent_subscription_id,
                'body': message,
                 })
    @api.depends('state')
    def recalculate_total(self):
        parent_subscription_id = self._origin.subscription_id.id
        subscription=self.env['subscription.subscription'].search([('id', '=', parent_subscription_id)])
        for rec in subscription:
            rec._compute_amounts()
        # compute = self.env['subscription.subscription'].parent_subscription_id._compute_amounts()
