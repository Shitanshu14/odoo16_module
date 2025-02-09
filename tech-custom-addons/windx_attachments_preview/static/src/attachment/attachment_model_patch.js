/* @odoo-module */

import { registerPatch } from '@mail/model/model_core';
import { attr } from '@mail/model/model_field';
// dummy import to ensure mail Messaging patches are loaded beforehand
import '@mail/models/attachment';

registerPatch({
    name: 'Attachment',
    fields: {
        /**
         * States id the attachment is an Doc.
         */
        isDoc: attr({
            compute() {
                return this.extension === "doc" && this.mimetype.includes("officedocument");
            },
        }),
        /**
         * States id the attachment is an Docx.
         */
        isDocx: attr({
            compute() {
                return this.extension === "docx" && this.mimetype.includes("officedocument");
            },
        }),
        /**
         * States id the attachment is an ppt.
         */
        isPPT: attr({
            compute() {
                return this.extension === "ppt" && this.mimetype.includes("officedocument");
            },
        }),
        /**
         * States id the attachment is an pptx.
         */
        isPPTX: attr({
            compute() {
                return this.extension === "pptx" && this.mimetype.includes("officedocument");
            },
        }),
        /**
         * States id the attachment is an xlsx.
         */
        isXLS: attr({
            compute() {
                return this.extension === "xls" && this.mimetype.includes("ms-excel");
            },
        }),
        /**
         * States id the attachment is an xlsx.
         */
        isXLSX: attr({
            compute() {
                return this.extension === "xlsx" && this.mimetype.includes("officedocument");
            },
        }),
        isOfficeFile: attr({
            compute() {
                return this.isDocx || this.isPPTX || this.isXLSX;
            },
        }),
        /**
         * @override
         */
        isViewable: {
            compute() {
                return this.isOfficeFile || this._super();
            },
        },
    },
});
