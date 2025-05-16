# import base64
# import boto3
# from odoo import models, fields, api
# from odoo.exceptions import UserError
# from botocore.exceptions import NoCredentialsError
#
# class IrAttachment(models.Model):
#     _inherit = 'ir.attachment'
#
#     s3_url = fields.Char("S3 URL", readonly=True)
#     is_s3 = fields.Boolean("Stored in S3", compute='_compute_storage_location', store=True)
#
#     @api.depends('s3_url')
#     def _compute_storage_location(self):
#         for rec in self:
#             rec.is_s3 = bool(rec.s3_url)
#
#     @api.model
#     def create(self, vals):
#         if vals.get('datas') and vals.get('name'):
#             file_name = vals['name']
#             file_content = base64.b64decode(vals['datas'])
#             s3_url = self._upload_to_s3(file_name, file_content)
#             if s3_url:
#                 vals['url'] = s3_url
#                 vals['s3_url'] = s3_url
#                 vals['type'] = 'url'
#                 vals.pop('datas', None)
#                 vals.pop('db_datas', None)
#                 print(f"[UPLOAD] S3 URL: {s3_url} (STORED IN S3)")
#             else:
#                 print("[UPLOAD] STORED LOCALLY in Odoo database/filestore.")
#         return super(IrAttachment, self).create(vals)
#
#     def _upload_to_s3(self, file_name, file_content):
#         try:
#             s3 = boto3.client('s3',
#                 aws_access_key_id='YOUR_ACCESS_KEY',
#                 aws_secret_access_key='YOUR_SyECRET_KEY',
#                 region_name='YOUR_REGION'  # Example: 'ap-south-1'
#             )
#             bucket_name = 'YOUR_BUCKET_NAME'
#             s3_key = f"odoo_attachments/{file_name}"
#             s3.put_object(Bucket=bucket_name, Key=s3_key, Body=file_content)
#             s3_url = f"https://{bucket_name}.s3.{s3.meta.region_name}.amazonaws.com/{s3_key}"
#             return s3_url
#         except NoCredentialsError:
#             raise UserError("AWS credentials not available.")
#         except Exception as e:
#             print(f"[S3 ERROR] {e}")
#             return None


import boto3
import os
from odoo import fields, models, api
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta


class IrAttachment(models.Model):
    _inherit = 'ir.attachment'

    @api.model
    def create(self, vals):
        res = super(IrAttachment, self).create(vals)
        res.send_to_bucket()
        return res

    def send_to_bucket(self):
        try:
            client = boto3.client(
                's3',
                aws_access_key_id=self.env['ir.config_parameter'].get_param('amazon_s3_connector.amazon_access_key'),
                aws_secret_access_key=self.env['ir.config_parameter'].get_param('amazon_s3_connector.amazon_secret_key')
            )
            bucket_name = self.env['ir.config_parameter'].get_param('amazon_s3_connector.amazon_bucket_name')

            date_string = self.create_date.strftime("%d-%m-%y")
            file_path = self._full_path(self.store_fname)

            with open(file_path, 'rb') as file_data:
                response = client.put_object(
                    Bucket=bucket_name,
                    Key=f"{date_string}/{self.name}",
                    Body=file_data
                )

            if response['ResponseMetadata']['HTTPStatusCode'] == 200:
                file_url = f"https://{bucket_name}.s3.amazonaws.com/{date_string}/{self.name}"

                if self.res_model and self.res_id:
                    related_record = self.env[self.res_model].browse(self.res_id)
                    if related_record:
                        related_record.message_post(
                            body=f"File uploaded: <a href='{file_url}'>{self.name}</a>",
                            subtype_xmlid='mail.mt_note'
                        )

        except Exception as e:
            print(f"Failed to upload {self.name} to S3: {e}")

    @api.model
    def delete_old_attachments_cron(self):
        try:
            three_months_ago = datetime.now() - timedelta(days=90)

            attachments = self.env['ir.attachment'].sudo().search([
                ('create_date', '<', three_months_ago.strftime('%Y-%m-%d %H:%M:%S')),
                ('res_model', '=', 'project.task')
            ])

            for attachment in attachments:
                try:
                    file_path = attachment._full_path(attachment.store_fname)
                    if os.path.isfile(file_path):
                        os.remove(file_path)

                    attachment.unlink()

                    print(f"Attachment {attachment.name} deleted after 3 months from project.")

                except Exception as e:
                    print(f"Failed to delete {attachment.name}: {e}")

        except Exception as e:
            print(f"Failed to execute cron job: {e}")


    @api.model
    def check_attachments_in_s3(self):
        try:
            client = boto3.client(
                's3',
                aws_access_key_id=self.env['ir.config_parameter'].get_param('amazon_s3_connector.amazon_access_key'),
                aws_secret_access_key=self.env['ir.config_parameter'].get_param('amazon_s3_connector.amazon_secret_key')
            )
            bucket_name = self.env['ir.config_parameter'].get_param('amazon_s3_connector.amazon_bucket_name')

            attachments = self.env['ir.attachment'].sudo().search([])

            s3_objects = client.list_objects_v2(Bucket=bucket_name)

            s3_files = {obj['Key'] for obj in s3_objects.get('Contents', [])}

            for attachment in attachments:
                date_string = attachment.create_date.strftime("%d-%m-%y")
                expected_key = f"{date_string}/{attachment.name}"

                if expected_key not in s3_files:
                    print(f"Attachment {attachment.name} is missing in S3, uploading...")
                    attachment.send_to_bucket()
                else:
                    print(f"Attachment {attachment.name} already exists in S3.")

        except Exception as e:
            print(f"Failed to check attachments in S3: {e}")

    @api.model
    def sync_attachments_to_s3(self):
        try:
            client = boto3.client(
                's3',
                aws_access_key_id=self.env['ir.config_parameter'].get_param('amazon_s3_connector.amazon_access_key'),
                aws_secret_access_key=self.env['ir.config_parameter'].get_param('amazon_s3_connector.amazon_secret_key')
            )
            bucket_name = self.env['ir.config_parameter'].get_param('amazon_s3_connector.amazon_bucket_name')

            attachments = self.env['ir.attachment'].sudo().search([])

            for attachment in attachments:
                date_string = attachment.create_date.strftime("%d-%m-%y")
                expected_key = f"{date_string}/{attachment.name}"

                s3_objects = client.list_objects_v2(Bucket=bucket_name, Prefix=expected_key)
                s3_files = {obj['Key'] for obj in s3_objects.get('Contents', [])}

                if expected_key not in s3_files:
                    print(f"Attachment {attachment.name} is missing in S3, uploading...")
                    attachment.send_to_bucket()
                else:
                    print(f"Attachment {attachment.name} already exists in S3.")

        except Exception as e:
            print(f"Failed to sync attachments to S3: {e}")
