/** @odoo-module */
import fieldRegistry from 'web.field_registry';
import relationalFields from 'web.relational_fields';
import { registry } from "@web/core/registry";
import { Many2ManyBinaryField } from "@web/views/fields/many2many_binary/many2many_binary_field";
import { useService } from "@web/core/utils/hooks";
import { _t } from "@web/core/l10n/translation";

const { useState, onWillStart, onWillRender } = owl;

const Many2ManyBinaryFieldPreviewMultiFiles = relationalFields.FieldMany2ManyBinaryMultiFiles.extend({});

export class Many2ManyBinaryFieldPreview extends Many2ManyBinaryField {

    setup() {
        super.setup(...arguments);
        this.messaging = useService("messaging");
        this.state = useState({
            attachments: [],
        });
        onWillStart(() => {
            this.getAttachments();
        });
        onWillRender(() => {
            this.getAttachments();
        });
    }

    getAttachments() {
        try {
            if (this.props.value.records.length !== this.state.attachments.length) {
                this.messaging.get().then((messaging) => {
                    var attachments = this.props.value.records.map((record) => {
                        var attachment = messaging.models["Attachment"].insert({
                            id: record.resId,
                            filename: record.data.name,
                            name: record.data.name,
                            mimetype: record.data.mimetype
                        });
                        return {
                            id: record.resId,
                            attachment: attachment
                        };
                    });
                    this.state.attachments = attachments;
                });
            }
        } catch (e) {
            this.state.attachments = [];
        }
    }

    getAttachmentById(id) {
        const attachment = this.state.attachments.find((attachment) => attachment.id === id);
        if (!!attachment)
            return attachment.attachment;
        return false;
    }

    async previewAttachment(attachment) {
        if (attachment && attachment.isViewable) {
            this.messaging.get().then((messaging) => {
                const attachmentList = messaging.models["AttachmentList"].insert({
                    selectedAttachment: attachment,
                });
                this.dialog = messaging.models["Dialog"].insert({
                    attachmentListOwnerAsAttachmentView: attachmentList,
                });
            });
        }
        return;
    }

}

fieldRegistry.add('many2many_preview_attachment', Many2ManyBinaryFieldPreviewMultiFiles);

registry.category("fields").add("many2many_preview_attachment", Many2ManyBinaryFieldPreview);
