import logging
import re
import smtplib
import dns.resolver

from odoo import models, fields, api
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

class ResPartner(models.Model):
    _inherit = 'res.partner'

    is_email_valid = fields.Boolean(string='Email Valid', compute='_compute_is_email_valid', store=True)
    email_validation_message = fields.Char(string='Email Validation Message')
    show_validate_email_button = fields.Boolean(string="Show Validate Email Button", compute='_compute_show_validate_email_button')

    @api.depends('email')
    def _compute_is_email_valid(self):
        for record in self:
            record.is_email_valid = False
            record.email_validation_message = False

            try:
                if not record.email:
                    record.email_validation_message = "No email provided"
                    continue

                config = self.env['res.config.settings'].sudo().get_values()

                # Validate syntax if enabled in the settings
                if config.get('check_email_syntax', False):
                    self._validate_email_format(record.email)

                domain = self._extract_domain(record.email)

                # DNS check if enabled in settings
                if config.get('check_dns', False):
                    self._get_mx_record(domain)

                # Do not run SMTP here – it's triggered by the button
                record.email_validation_message = "Ready for SMTP Check"

            except Exception as e:
                error_message = str(e)
                _logger.warning(f"Validation error for {record.email}: {error_message}")
                record.email_validation_message = error_message

    @api.depends('email', 'email_validation_message')
    def _compute_show_validate_email_button(self):
        for rec in self:
            config = self.env['res.config.settings'].sudo().get_values()
            rec.show_validate_email_button = False
            if config.get('check_email_syntax', False) and config.get('check_dns', False) and config.get('check_smtp', False):
                if rec.email_validation_message == "Ready for SMTP Check":
                    rec.show_validate_email_button = True

    def action_validate_email_smtp(self):
        for record in self:
            try:
                domain = self._extract_domain(record.email)
                mx_record = self._get_mx_record(domain)
                result = self._smtp_check(record.email, mx_record)
                if not result:
                    record.email_validation_message = "User Does Not Exist"
                    record.is_email_valid = False
                else:
                    record.email_validation_message = "Valid Email"
                    record.is_email_valid = True
            except Exception as e:
                raise UserError(f"SMTP Validation Failed: {e}")

    def _validate_email_format(self, email):
        email = email.strip()

        # Standard pattern allowing only dots (.) in local part
        regex = r"^[a-zA-Z0-9]+(\.?[a-zA-Z0-9]+)*@[a-zA-Z0-9-]+\.[a-zA-Z]{2,}$"
        if not re.match(regex, email):
            raise ValueError("Syntax Error: Invalid email format")

        local_part, domain = email.split('@', 1)
        if '-' in local_part or '_' in local_part:
            raise ValueError("Syntax Error: '-' and '_' are not allowed in local part")

    def _extract_domain(self, email):
        if '@' not in email:
            raise ValueError("Syntax Error: Missing '@'")
        return email.split('@')[1]

    def _get_mx_record(self, domain):
        try:
            answers = dns.resolver.resolve(domain, 'MX')
            return str(answers[0].exchange).rstrip('.')
        except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN):
            raise ValueError(f"Domain not Exist: {domain}")

    def _smtp_check(self, email, mx_record):
        try:
            server = smtplib.SMTP(timeout=10)
            server.connect(mx_record, 25)
            server.helo()
            server.mail('test@example.com')
            code, _ = server.rcpt(email)
            server.quit()
            return code in (250, 251)
        except Exception as e:
            _logger.warning(f"SMTP check failed for {email}: {e}")
            return False

    def action_bulk_validate_email(self):
        config = self.env['res.config.settings'].sudo().get_values()

        for partner in self:
            try:
                partner.is_email_valid = False
                partner.email_validation_message = False

                if not partner.email:
                    partner.email_validation_message = "No email provided"
                    continue

                email = partner.email.strip()

                if config.get('check_email_syntax', False):
                    self._validate_email_format(email)

                domain = self._extract_domain(email)

                mx_record = None
                if config.get('check_dns', False):
                    mx_record = self._get_mx_record(domain)

                if config.get('check_smtp', False) and mx_record:
                    result = self._smtp_check(email, mx_record)
                    partner.is_email_valid = result
                    partner.email_validation_message = "Valid Email" if result else "User Does Not Exist"
                else:
                    partner.email_validation_message = "Ready for SMTP Check" if mx_record else "DNS Skipped"

            except Exception as e:
                _logger.warning(f"Bulk validation error for {partner.email}: {e}")
                partner.email_validation_message = str(e)

