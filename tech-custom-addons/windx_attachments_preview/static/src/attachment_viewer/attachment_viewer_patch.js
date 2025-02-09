/* @odoo-module */

import { AttachmentViewer } from "@mail/components/attachment_viewer/attachment_viewer";
import { useRef, useEffect } from "@odoo/owl";
//const { useRef, useEffect } = owl;
import { patch } from "@web/core/utils/patch";

patch(AttachmentViewer.prototype, 'windx_attachments_preview.AttachmentViewer', {
    setup() {
        this._super(...arguments);
        this.viewerMsOfficeRef = useRef("ViewerMsOffice");
        this.instancePreviewOffice = null;
    },

    _mounted() {
        this._super.apply();
        // Preview Office file: docx, pptx, xlsx
        this.onPreviewMsOffice();
    },

    /**
     * When a new image is displayed, show a spinner until it is loaded.
     */
    _patched() {
        this._super.apply();
        // Preview Office file: docx, pptx, xlsx
        this.onPreviewMsOffice();
    },

    /**
     * @see 'onPreviewMsOffice'
     *
     * @private
     */
    onPreviewMsOffice() {
        if (this.viewerMsOfficeRef.el) {
            this.previewMsOffice(this.viewerMsOfficeRef.el);
        }
    },

    /**
     * @see 'getFileFromUrl'
     *
     * @private
     */
    async getFileFromUrl(url, name, defaultType = 'image/jpeg'){
        const blob = await (await fetch(url)).blob();
        return new File([blob], name, { type: blob.type || defaultType });
    },

    /**
     * @see 'previewMsOffice'
     *
     * @private
     */
    async previewMsOffice(rootElement) {
        var self = this;
        if (!this.attachmentViewer.attachmentViewerViewable.isOfficeFile || !$.isFunction(window.createDocxJS)
            || !$.isFunction(window.createCellJS) || !$.isFunction(window.createSlideJS)) {
            this.attachmentViewer.onClickClose();
            return;
        }

        if (this.attachmentViewer.attachmentViewerViewable.isDocx) {
            this.instancePreviewOffice = window.docxJS = window.createDocxJS();
        } else if (this.attachmentViewer.attachmentViewerViewable.isXLSX) {
            this.instancePreviewOffice = window.cellJS = window.createCellJS();
        } else if (this.attachmentViewer.attachmentViewerViewable.isPPTX) {
            this.instancePreviewOffice = window.slideJS = window.createSlideJS();
        }

        if (this.instancePreviewOffice) {
            var file = await this.getFileFromUrl(this.attachmentViewer.attachmentViewerViewable.defaultSource,
                                                 this.attachmentViewer.attachmentViewerViewable.displayName);
            this.instancePreviewOffice.parse(
                file,
                function () {
                    self.afterRender(file, rootElement);
                }, function (e) {
                    if(e.isError && e.msg){
                        alert(e.msg);
                    }
                    self.instancePreviewOffice.destroy(function(){
                        self.instancePreviewOffice = null;
                    });
                }, null
            );
        }
    },

    /**
     * @see 'afterRender'
     *
     * @private
     */
    afterRender(file, element) {
        if (!$('#' + element.getAttribute('id')).length) {
            return;
        }
        $(element).css('height','calc(100% - 55px)');

        var endCallBackFn = function(result){
            if (result.isError) {
                // console.log("Error Render");
            } else {
                // console.log("Success Render");
            }
        };

        if (this.attachmentViewer.attachmentViewerViewable.isDocx) {
            window.docxAfterRender(element, endCallBackFn);
        } else if (this.attachmentViewer.attachmentViewerViewable.isXLSX) {
            window.cellAfterRender(element, endCallBackFn);
        } else if (this.attachmentViewer.attachmentViewerViewable.isPPTX) {
            window.slideAfterRender(element, endCallBackFn, 0);
        }
    },

});
