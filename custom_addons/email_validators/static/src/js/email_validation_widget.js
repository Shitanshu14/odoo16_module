/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { FormController } from "@web/views/form/form_controller";

patch(FormController.prototype, 'email_validators.FormControllerPatch', {
    async saveRecord(recordId, options = {}) {
        const res = await this._super(...arguments);

        const emailField = this.model.get(recordId).data.email;
        const isValid = this._validateEmail(emailField);

        const warningElement = this.el.querySelector('.o_email_warning');

        if (warningElement) {
            if (!isValid) {
                warningElement.textContent = "Client-side: Invalid Email Format";
                warningElement.style.backgroundColor = "#ffdddd";
                warningElement.style.color = "#d8000c";
                warningElement.style.padding = "5px";
                warningElement.style.borderRadius = "4px";
                warningElement.style.marginTop = "5px";
            } else {
                warningElement.textContent = "";
                warningElement.style.backgroundColor = "";
            }
        }

        return res;
    },

    _validateEmail(email) {
        if (!email) return false;

        const regex = /^(?!.*\.\.)(?!.*\.$)(?!^\.)[a-zA-Z0-9]+([._%+-]?[a-zA-Z0-9]+)*@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
        return regex.test(email.trim());
    }
});
