# -*- coding: utf-8 -*-
# Powered by Kanak Infosystems LLP.
# © 2020 Kanak Infosystems LLP. (<https://www.kanakinfosystems.com>).

import datetime
import logging
import traceback
from uuid import uuid4
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, _
from odoo.exceptions import AccessError, ValidationError, UserError
from odoo.tools import html_keep_url, is_html_empty

_logger = logging.getLogger(__name__)


class Subscription(models.Model):
    _name = 'subscription.subscription'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Subscription"
    _order = 'name desc'

    def _get_default_pricelist(self):
        return self.env['product.pricelist'].search([('currency_id', '=', self.env.user.company_id.currency_id.id)], limit=1).id

    def _default_journal(self):
        company_id = self.env.context.get('company_id', self.env.user.company_id.id)
        domain = [('type', '=', 'sale'), ('company_id', '=', company_id)]
        return self.env['account.journal'].search(domain, limit=1)

    name = fields.Char(
        required=True, copy=False, readonly=True,
        index='trigram',
        states={'draft': [('readonly', False)]},
        default=lambda self: _('New'))
    company_id = fields.Many2one(
        comodel_name='res.company',
        required=True, index=True,
        default=lambda self: self.env.company)
    partner_id = fields.Many2one(
        comodel_name='res.partner',
        string="Customer",
        required=True, readonly=False, change_default=True, index=True,
        tracking=1,
        domain="[('type', '!=', 'private'), ('company_id', 'in', (False, company_id))]")
    commercial_partner_id = fields.Many2one('res.partner', related='partner_id.commercial_partner_id')
    state = fields.Selection(
        selection=[
            ('draft', "Draft"),
            ('in_progress', "In Progress"),
            ('hold', "Hold"),
            ('closed', "Closed"),
        ],
        compute="compute_state",
        string="Status",
        readonly=True, copy=False, index=True,
        tracking=3)
    code = fields.Char(string="Reference", tracking=True, index=True, copy=False)
    date_order = fields.Datetime(
        string="Order Date",
        required=True, readonly=False, copy=False,
        help="Creation date of subscription orders",
        default=fields.Datetime.now)
    user_id = fields.Many2one(
        comodel_name='res.users',
        string="Salesperson",
        compute='_compute_user_id',
        store=True, readonly=False, precompute=True, index=True,
        tracking=2,
        domain=lambda self: "[('groups_id', '=', {}), ('share', '=', False), ('company_ids', '=', company_id)]".format(
            self.env.ref("sales_team.group_sale_salesman").id
        ))
    fiscal_position_id = fields.Many2one(
        comodel_name='account.fiscal.position',
        string="Fiscal Position",
        compute='_compute_fiscal_position_id',
        store=True, readonly=False, precompute=True, check_company=True,
        help="Fiscal positions are used to adapt taxes and accounts for particular customers or subscriptions/sales orders/invoices. The default value comes from the customer.",
        domain="[('company_id', '=', company_id)]")
    pricelist_id = fields.Many2one(
        comodel_name='product.pricelist',
        string="Pricelist",
        compute='_compute_pricelist_id',
        store=True, readonly=False, precompute=True, check_company=True, required=True,
        tracking=1,
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]",
        help="If you change the pricelist, only newly added lines will be affected.")
    currency_id = fields.Many2one(
        related='pricelist_id.currency_id',
        depends=["pricelist_id"],
        store=True, precompute=True, ondelete="restrict")
    subscription_line_ids = fields.One2many(
        comodel_name='subscription.line',
        inverse_name='subscription_id',
        string="Subscription Lines",
        copy=True, auto_join=True)
    auto_create_pickings = fields.Boolean('Create Delivery Order Automatically ?')
    recurring_total = fields.Float(compute='_compute_recurring_total', string="Recurring Price", store=True, tracking=True)
    payment_token_id = fields.Many2one('payment.token', 'Payment Token', check_company=True, help='If not set, the automatic payment will fail.',
                                       domain="[('partner_id', 'child_of', commercial_partner_id), ('company_id', '=', company_id)]")
    terms_type = fields.Selection(related='company_id.terms_type')
    note = fields.Html(
        string="Terms and conditions",
        compute='_compute_note',
        store=True, readonly=False, precompute=True)
    uuid = fields.Char('Account UUID', default=lambda self: str(uuid4()), copy=False, required=True)
    auto_recurring_payment = fields.Boolean('Auto Recurring Payment')
    sale_order_count = fields.Integer(compute="_compute_sale_order_count")
    invoice_count = fields.Integer(string="Invoice Count", compute='_get_invoiced')
    invoice_ids = fields.Many2many(
        comodel_name='account.move',
        string="Invoices",
        compute='_get_invoiced',
        search='_search_invoice_ids',
        copy=False)
    order_line = fields.One2many('sale.order.line', 'order_id', string='Order Lines', states={'cancel': [('readonly', True)], 'done': [('readonly', True)]}, copy=True, auto_join=True)

    amount_untaxed = fields.Monetary(string="Untaxed Amount", store=True, compute='_compute_amounts', tracking=5)
    amount_tax = fields.Monetary(string="Taxes", store=True, compute='_compute_amounts')
    amount_total = fields.Monetary(string="Total", store=True, compute='_compute_amounts', tracking=4)

    tax_country_id = fields.Many2one(
        comodel_name='res.country',
        compute='_compute_tax_country_id',
        compute_sudo=True)

    suitable_journal_ids = fields.Many2many(
        'account.journal',
        compute='_compute_suitable_journal_ids',
    )
    move_type = fields.Selection(
        selection=[
            ('out_invoice', 'Customer Invoice'),
            ('out_refund', 'Customer Credit Note')
        ],
        string='Type',
        required=True,
        readonly=True,
        tracking=True,
        change_default=True,
        index=True,
        default="out_invoice",
    )
    journal_id = fields.Many2one(
        'account.journal',
        string='Invoice Journal',
        compute='_compute_journal_id', store=True, readonly=False, precompute=True,
        required=True,
        states={'draft': [('readonly', False)]},
        check_company=True,
        domain="[('id', 'in', suitable_journal_ids)]",
    )
    
    #Added by Technians
    # project_id = fields.Many2one(
    #     'project.project',
    #     string = 'Project',
    #     domain="['&',('partner_id', '=', partner_id),('subscription_id', '=', False)]"
        
    # )
    
   

    _sql_constraints = [
        ('uuid_uniq', 'unique (uuid)', """UUID for Subscriptions should be unique!"""),
    ]

    def _get_report_base_filename(self):
        self.ensure_one()
        return self.name

    @api.depends('partner_id')
    def _compute_pricelist_id(self):
        for subscription in self:
            if not subscription.partner_id:
                subscription.pricelist_id = False
                continue
            subscription = subscription.with_company(subscription.company_id)
            subscription.pricelist_id = subscription.partner_id.property_product_pricelist

    @api.depends('partner_id')
    def _compute_user_id(self):
        for subscription in self:
            if not subscription.user_id:
                subscription.user_id = subscription.partner_id.user_id or subscription.partner_id.commercial_partner_id.user_id or \
                    (self.user_has_groups('sales_team.group_sale_salesman') and self.env.user)

    @api.depends('move_type')
    def _compute_journal_id(self):
        for record in self:
            record.journal_id = record._search_default_journal()
            if not record.company_id or record.company_id != record.journal_id.company_id:
                self.env.add_to_compute(self._fields['company_id'], record)
            if not record.currency_id or record.journal_id.currency_id and record.currency_id != record.journal_id.currency_id:
                self.env.add_to_compute(self._fields['currency_id'], record)

    def _search_default_journal(self):
        company_id = (self.company_id or self.env.company).id
        domain = [('company_id', '=', company_id), ('type', '=', 'sale')]

        journal = None
        currency_id = self.currency_id.id or self._context.get('default_currency_id')
        if currency_id and currency_id != self.company_id.currency_id.id:
            currency_domain = domain + [('currency_id', '=', currency_id)]
            journal = self.env['account.journal'].search(currency_domain, limit=1)

        if not journal:
            journal = self.env['account.journal'].search(domain, limit=1)

        if not journal:
            company = self.env['res.company'].browse(company_id)

            error_msg = _(
                "No journal could be found in company %(company_name)s for any of those types: %(journal_types)s",
                company_name=company.display_name,
                journal_types=', '.join('sale'),
            )
            raise UserError(error_msg)

        return journal

    @api.depends('company_id')
    def _compute_suitable_journal_ids(self):
        for m in self:
            company_id = m.company_id.id or self.env.company.id
            domain = [('company_id', '=', company_id), ('type', '=', 'sale')]
            m.suitable_journal_ids = self.env['account.journal'].search(domain)

    @api.depends('partner_id', 'company_id')
    def _compute_fiscal_position_id(self):
        cache = {}
        for subscription in self:
            if not subscription.partner_id:
                subscription.fiscal_position_id = False
                continue
            key = (subscription.company_id.id, subscription.partner_id.id)
            if key not in cache:
                cache[key] = self.env['account.fiscal.position'].with_company(
                    subscription.company_id
                )._get_fiscal_position(subscription.partner_id)
            subscription.fiscal_position_id = cache[key]

    @api.depends('partner_id')
    def _compute_note(self):
        use_invoice_terms = self.env['ir.config_parameter'].sudo().get_param('account.use_invoice_terms')
        if not use_invoice_terms:
            return
        for subscription in self:
            subscription = subscription.with_company(subscription.company_id)
            if subscription.terms_type == 'html' and self.env.company.invoice_terms_html:
                baseurl = html_keep_url(subscription._get_note_url() + '/terms')
                subscription.note = _('Terms & Conditions: %s', baseurl)
            elif not is_html_empty(self.env.company.invoice_terms):
                subscription.note = subscription.with_context(lang=subscription.partner_id.lang).env.company.invoice_terms

    @api.depends('company_id', 'fiscal_position_id')
    def _compute_tax_country_id(self):
        for record in self:
            if record.fiscal_position_id.foreign_vat:
                record.tax_country_id = record.fiscal_position_id.country_id
            else:
                record.tax_country_id = record.company_id.account_fiscal_country_id

    @api.depends('subscription_line_ids')
    def _compute_sale_order_count(self):
        for rec in self:
            try:
                order_count = len(rec.subscription_line_ids.mapped('sale_order_line_ids.order_id'))
            except AccessError:
                order_count = 0
            rec.sale_order_count = order_count

    @api.depends('order_line.invoice_lines')
    def _get_invoiced(self):
        for subscription in self:
            invoices = subscription.subscription_line_ids.mapped('sale_order_line_ids.invoice_lines.move_id')
            filtered_invoices = invoices.filtered(lambda r: r.move_type in ('out_invoice', 'out_refund'))
            subscription.invoice_ids = filtered_invoices
            subscription.invoice_count = len(filtered_invoices)

    def _search_invoice_ids(self, operator, value):
        if operator == 'in' and value:
            self.env.cr.execute("""
                SELECT array_agg(sub.id)
                    FROM subscription_subscription sub
                    JOIN subscription_line subl ON subl.order_id = sub.id
                    JOIN subscription_line_invoice_rel soli_rel ON soli_rel.subscription_line_id = subl.id
                    JOIN account_move_line aml ON aml.id = soli_rel.invoice_line_id
                    JOIN account_move am ON am.id = aml.move_id
                WHERE
                    am.move_type in ('out_invoice', 'out_refund') AND
                    am.id = ANY(%s)
            """, (list(value),))
            so_ids = self.env.cr.fetchone()[0] or []
            return [('id', 'in', so_ids)]
        elif operator == '=' and not value:
            order_ids = self._search([
                ('subscription_line_ids.invoice_lines.move_id.move_type', 'in', ('out_invoice', 'out_refund'))
            ])
            return [('id', 'not in', order_ids)]
        return [
            ('subscription_line_ids.invoice_lines.move_id.move_type', 'in', ('out_invoice', 'out_refund')),
            ('subscription_line_ids.invoice_lines.move_id', operator, value),
        ]

    @api.depends('subscription_line_ids.price_subtotal', 'subscription_line_ids.price_tax', 'subscription_line_ids.price_total','subscription_line_ids.state')
    def _compute_amounts(self):
        for subscription in self:
            # Modified by Technians 
            subscription_lines = subscription.subscription_line_ids.filtered(lambda x: not x.display_type and x.state == 'in_progress')
            # subscription_lines = subscription.subscription_line_ids.filtered(lambda x: not x.display_type)
            subscription.amount_untaxed = sum(subscription_lines.mapped('price_subtotal'))
            subscription.amount_total = sum(subscription_lines.mapped('price_total'))
            subscription.amount_tax = sum(subscription_lines.mapped('price_tax'))

    @api.model
    def _get_note_url(self):
        return self.env.company.get_base_url()

    def action_view_invoice(self):
        invoices = self.mapped('invoice_ids')
        action = self.env["ir.actions.actions"]._for_xml_id("account.action_move_out_invoice_type")
        if len(invoices) > 1:
            action['domain'] = [('id', 'in', invoices.ids)]
        elif len(invoices) == 1:
            form_view = [(self.env.ref('account.view_move_form').id, 'form')]
            if 'views' in action:
                action['views'] = form_view + [(state, view) for state, view in action['views'] if view != 'form']
            else:
                action['views'] = form_view
            action['res_id'] = invoices.id
        else:
            action = {'type': 'ir.actions.act_window_close'}

        context = {
            'default_move_type': 'out_invoice',
        }
        if len(self) == 1:
            context.update({
                'default_partner_id': self.partner_id.id,
                'default_invoice_origin': self.name,
                'default_user_id': self.user_id.id,
            })
        action['context'] = context
        return action

    def action_view_sales_orders(self):
        self.ensure_one()
        orders = self.subscription_line_ids.mapped('sale_order_line_ids.order_id')
        action = {
            "name": _("Sales Orders"),
            "view_mode": "tree,form",
            "res_model": "sale.order",
            "type": "ir.actions.act_window",
            "domain": [("id", "in", orders.ids)],
        }
        if len(orders) == 1:
            action.update({'view_mode': "form", "res_id": orders.id})
        return action

    @api.depends('subscription_line_ids', 'subscription_line_ids.quantity', 'subscription_line_ids.price_unit')
    def _compute_recurring_total(self):
        for account in self:
            account.recurring_total = sum((line.price_unit * line.quantity) for line in account.subscription_line_ids)

    @api.depends('subscription_line_ids.state')
    def compute_state(self):
        for rec in self:
            rec.state = 'draft'
            if rec.subscription_line_ids:
                if any(line.state == 'in_progress' for line in rec.subscription_line_ids):
                    rec.state = 'in_progress'
                if all(line.state == 'closed' for line in rec.subscription_line_ids):
                    rec.state = 'closed'
                if all(line.state == 'hold' for line in rec.subscription_line_ids):
                    rec.state = 'hold'
                if all(line.state == 'draft' for line in rec.subscription_line_ids):
                    rec.state = 'draft'

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        if self.partner_id:
            self.pricelist_id = self.partner_id.property_product_pricelist.id
        if self.partner_id.user_id:
            self.user_id = self.partner_id.user_id

    @api.model
    def get_relative_delta(self, recurring_rule_type, interval):
        if recurring_rule_type == 'daily':
            return relativedelta(days=interval)
        elif recurring_rule_type == 'weekly':
            return relativedelta(weeks=interval)
        elif recurring_rule_type == 'monthly':
            return relativedelta(months=interval)
        elif recurring_rule_type == 'monthlylastday':
            return relativedelta(months=interval, day=31)
        else:
            return relativedelta(years=interval)

    def _prepare_invoice(self, date_invoice, journal=None):
        self.ensure_one()
        if not journal:
            journal = self.env['account.journal'].search([('type', '=', 'sale'), ('company_id', '=', self.company_id.id)], limit=1)
        if not journal:
            raise ValidationError(_("Please define a %s journal for the company '%s'.") % ('sale', self.company_id.name or ''))

        invoice = {
            'company_id': self.company_id.id,
            'partner_id': self.partner_id.id,
            'type': 'out_invoice',
            'invoice_origin': self.code,
            'currency_id': self.currency_id.id,
            'journal_id': journal.id,
            'invoice_user_id': self.user_id.id,
        }
        return invoice

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if 'company_id' in vals:
                self = self.with_company(vals['company_id'])
            if vals.get('name', _("New")) == _("New"):
                seq_date = fields.Datetime.context_timestamp(
                    self, fields.Datetime.to_datetime(vals['date_order'])
                ) if 'date_order' in vals else None
                vals['name'] = self.env['ir.sequence'].next_by_code(
                    'subscription.subscription', sequence_date=seq_date) or _("New")
            subscription = super().create(vals)
            if subscription.partner_id:
                subscription.message_subscribe(subscription.partner_id.ids)
        return subscription

    def write(self, vals):
        if vals.get('partner_id'):
            self.message_subscribe([vals['partner_id']])
        return super().write(vals)

    def _init_column(self, column_name):
        # to avoid generating a single default uuid when installing the module,
        # we need to set the default row by row for this column
        if column_name == "uuid":
            _logger.debug("Table '%s': setting default value of new column %s to unique values for each row",
                          self._table, column_name)
            self.env.cr.execute("SELECT id FROM %s WHERE uuid IS NULL" % self._table)
            acc_ids = self.env.cr.dictfetchall()
            query_list = [{'id': acc_id['id'], 'uuid': str(uuid4())} for acc_id in acc_ids]
            query = 'UPDATE ' + self._table + ' SET uuid = %(uuid)s WHERE id = %(id)s;'
            self.env.cr._obj.executemany(query, query_list)
            self.env.cr.commit()
        else:
            super()._init_column(column_name)

    def _do_payment(self, payment_token, sale_order):
        tx_obj = self.env['payment.transaction']
        values = []
        for subscription in self:
            reference = tx_obj._compute_reference(
                payment_token.provider_id.code, prefix=subscription.code
            )
            values.append({
                'provider_id': payment_token.provider_id.id,
                'sale_order_ids': [(6, 0, [sale_order.id])],
                'amount': sale_order.amount_total,
                'currency_id': sale_order.currency_id.id,
                'partner_id': subscription.partner_id.id,
                'token_id': payment_token.id,
                'operation': 'offline',
                'reference': reference,
            })
        transactions = tx_obj.create(values)
        for tx in transactions:
            tx._send_payment_request()
        return transactions

    def _reconcile_and_send_mail(self, tx, sale_order=False):
        if not sale_order:
            sale_order = tx.sale_order_ids and tx.sale_order_ids[0]
        self.reconcile_pending_transaction(tx, sale_order=sale_order)
        self.send_success_mail(tx, sale_order=sale_order)
        return True

    def send_success_mail(self, tx, sale_order):
        template = self.sudo().env.ref('subscription_kanak.subscription_payment_sucess')
        email_context = self.env.context.copy()
        email_context.update({
            'payment_token': self.payment_token_id.payment_details,
            'total_amount': tx.amount,
            'code': self.name,
            'currency': self.pricelist_id.currency_id.name,
        })
        email_context = {**self.env.context.copy(),
                         **{'payment_token': self.payment_token_id.payment_details,
                            'total_amount': tx.amount,
                            'code': self.name,
                            'subscription_name': self.name,
                            'currency': self.pricelist_id.currency_id.name}}
        _logger.debug("Sending Payment Confirmation Mail to %s for subscription %s", self.partner_id.email, self.id)
        return template.with_context(email_context).send_mail(self.id)

    def reconcile_pending_transaction(self, tx, sale_order=False):
        self.ensure_one()
        if not sale_order:
            sale_order = tx.sale_order_ids and tx.sale_order_ids[0]
        if tx.state in ['done', 'authorized']:
            tx._finalize_post_processing()
            self.env.cr.commit()
        else:
            sale_order.action_cancel()
            sale_order.unlink()

    @api.model
    def sale_get_payment_term(self, partner):
        return (
            partner.property_payment_term_id or
            self.env.ref('account.account_payment_term_immediate', False) or
            self.env['account.payment.term'].sudo().search([('company_id', '=', self.company_id.id)], limit=1)
        ).id

    def _prepare_sale_order_values(self):
        self.ensure_one()
        values = {
            'partner_id': self.partner_id.id,
            'pricelist_id': self.pricelist_id.id,
            'origin': self.name,
            'payment_term_id': self.sale_get_payment_term(self.partner_id),
            'team_id': self.partner_id.parent_id.team_id.id or self.partner_id.team_id.id,
            'partner_invoice_id': self.partner_id.id,
            'user_id': self.user_id.id or False,
        }
        company = self.company_id or self.pricelist_id.company_id
        if company:
            values['company_id'] = company.id
            if self.env['ir.config_parameter'].sudo().get_param('sale.use_sale_note'):
                values['note'] = company.sale_note or ""

        return values

    def _create_sale_orders(self, so_values, subscriptions_lines):
        sale_order = self.env['sale.order'].with_company(self.company_id).create(so_values)
        sale_lines_values_to_create = self._sale_prepare_sale_line_values(sale_order, subscriptions_lines)
        if sale_lines_values_to_create:
            for line in sale_lines_values_to_create:
                sale_order_line = self.env['sale.order.line'].create(line)
                sale_order_line.subscription_line_id.write({'sale_order_line_ids': [(4, sale_order_line.id)]})
        return sale_order

    def _sale_prepare_sale_line_values(self, order, subscriptions_lines):
        self.ensure_one()

        lines = []
        for line in subscriptions_lines:
            partner = order.partner_id
            company_id = line.subscription_id.company_id

            last_so_line = self.env['sale.order.line'].search([('order_id', '=', order.id)], order='sequence desc', limit=1)
            last_sequence = last_so_line.sequence + 1 if last_so_line else 100

            fpos = self.env['account.fiscal.position'].sudo()._get_fiscal_position(partner)
            product_taxes = line.product_id.taxes_id.filtered(lambda t: t.company_id == company_id)
            taxes = fpos.map_tax(product_taxes)

            lines.append({
                'order_id': order.id,
                'name': line.name,
                'sequence': last_sequence,
                'price_unit': line.price_unit,
                'tax_id': [x.id for x in taxes],
                'discount': line.discount,
                'product_id': line.product_id.id,
                'product_uom': line.product_uom.id,
                'product_uom_qty': line.quantity,
                'subscription_line_id': line.id,
                'purchase_option': "subscription",
                'is_subscription': True,
                'subscription_interval': line.subscription_interval.id,
                'subscription_id': line.subscription_id.id,
            })
        return lines

    def write_recurring_next_date(self, lines):
        today = datetime.date.today()
        for line in lines:
            if today == line.date_end and line.duration_cycle != 'unlimited':
                line.action_close_subscription()

            recurring_interval = line.subscription_interval.recurring_interval
            periods = {'daily': 'days', 'weekly': 'weeks', 'monthly': 'months', 'semesterly': 'months', 'quarterly': 'months', 'yearly': 'years'}
            if line.subscription_interval.recurring_rule_type == 'quarterly':
                recurring_interval *= 3
            elif line.subscription_interval.recurring_rule_type == 'semesterly':
                recurring_interval *= 6
            new_date = today + relativedelta(**{periods[line.subscription_interval.recurring_rule_type]: recurring_interval})
            line.write({'recurring_next_date': new_date})

    def _invoice_sale_orders(self, orders):
        if self.env['ir.config_parameter'].sudo().get_param('sale.automatic_invoice'):
            orders._force_lines_to_invoice_policy_order()
            return orders._create_invoices()

    def _recurring_create_sale_order(self, date_ref=False, automatic=False):
        for rec in self:
            so_values = rec._prepare_sale_order_values()
            subscriptions_lines = rec.subscription_line_ids.filtered(lambda x: x.recurring_next_date and x.recurring_next_date <= date_ref and x.state == 'in_progress')
            sale_order = rec._create_sale_orders(so_values, subscriptions_lines)
            sale_order.with_context({'subscription_to_sale': True}).action_confirm()

            payment_token = rec.payment_token_id
            if not payment_token:
                invoice_ids = self._invoice_sale_orders(sale_order)
                msg_body = 'Draft invoice against order <a href=# data-oe-model=sale.order data-oe-id=%d>%s</a> has been created ! <a href=# data-oe-model=account.invoice data-oe-id=%d>View Invoice</a>' % (sale_order.id, sale_order.name, invoice_ids[0])
                rec.message_post(body=msg_body)
            else:
                msg_body = 'Sale order <a href=# data-oe-model=sale.order data-oe-id=%d>%s</a> for current subscription has been created !' % (sale_order.id, sale_order.name)
                rec.message_post(body=msg_body)

            if automatic:
                tx = None
                if payment_token:
                    try:
                        tx = rec._do_payment(payment_token, sale_order)
                        tx = rec._do_payment(payment_token, sale_order)
                        if tx.state in ['done', 'authorized']:
                            rec._reconcile_and_send_mail(tx, sale_order)
                            msg_body = 'Automatic payment succeeded. Payment reference: <a href=# data-oe-model=payment.transaction data-oe-id=%d>%s</a>; Amount: %s. Invoice <a href=# data-oe-model=sale.order data-oe-id=%d>View Sale Order</a>.' % (tx.id, tx.reference, tx.amount, sale_order.id)
                            rec.message_post(body=msg_body)
                            rec.write_recurring_next_date(subscriptions_lines)
                        self.env.cr.commit()
                        if tx is None or tx.state not in ['done', 'authorized']:
                            msg_body = 'Automatic payment failed!'
                            rec.message_post(body=msg_body)
                            sale_order.message_post(body="Automatic payment of this sale order for subscription %s has been failed !" % rec.display_name)
                            sale_order.action_cancel()
                            template = self.sudo().env.ref('subscription_kanak.subscription_payment_failure')
                            _logger.debug("Sending Subscription Payment Failure Mail to %s for subscription %s", rec.partner_id.email, rec.id)
                            template.send_mail(rec.id)
                            self.env.cr.commit()
                    except Exception:
                        self.env.cr.rollback()
                        # we assume that the payment is run only once a day
                        traceback_message = traceback.format_exc()
                        _logger.error(traceback_message)
                        last_tx = self.env['payment.transaction'].search([('reference', 'like', 'SUBSCRIPTION-%s-%s' % (rec.id, datetime.date.today().strftime('%y%m%d')))], limit=1)
                        error_message = "Error during renewal of subscription %s (%s)" % (rec.code, 'Payment recorded: %s' % last_tx.reference if last_tx and last_tx.state == 'done' else 'No payment recorded.')
                        _logger.error(error_message)
                else:
                    rec.write_recurring_next_date(subscriptions_lines)

    @api.model
    def cron_recurring_create_sale_orders(self, date_ref=None):
        if not date_ref:
            date_ref = fields.Date.context_today(self)
        subscriptions_lines = self.env['subscription.line'].search([('recurring_next_date', '<=', date_ref), ('state', '=', 'in_progress')])
        subscriptions_to_invoice = subscriptions_lines.mapped('subscription_id')
        subscriptions_to_invoice._recurring_create_sale_order(date_ref, automatic=True)

    @api.model
    def cron_delivery_reminder_mail_send(self):
        days = int(self.env["ir.config_parameter"].sudo().get_param("subscription_kanak.subscription_before_delivery_reminder_days"))
        if days >= 1:
            mail_date = fields.Date.context_today(self) + relativedelta(days=days)
            subscriptions_lines = self.env['subscription.line'].search([('recurring_next_date', '=', mail_date), ('state', '=', 'in_progress')])
            for subscription in subscriptions_lines.mapped('subscription_id'):
                email_context = self.env.context.copy()
                email_context.update({
                    'delivery_reminder_days': days,
                    'subscriptions_lines': [{'product': line.product_id.name, 'qty': line.quantity} for line in subscription.subscription_line_ids.filtered(lambda x: x in subscriptions_lines)],
                    'subscription': subscription,
                    'commitment_date': subscriptions_lines[0].recurring_next_date
                })
                template = self.sudo().env.ref('subscription_kanak.reminder_mail_for_delivery')
                template.with_context(email_context).send_mail(subscription.id)

    def unlink(self):
        for record in self:
            if record.state in ['in_progress', 'hold']:
                raise UserError(_('You can not delete subscription , if subscription is in "Hold" or "In Progress" state.'))
        return super().unlink()
