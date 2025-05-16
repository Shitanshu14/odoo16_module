/** @odoo-module **/

import { registry } from "@web/core/registry";
import { Component } from "@odoo/owl";

export class HrApplicantEmailValidationWidget extends Component {
    setup() {
        this.record = this.props.record;
    }

    get emailValid() {
        return this.record.data.is_email_valid;
    }

    get showValidateButton() {
        return this.record.data.show_validate_email_button;
    }

    validateEmail() {
        this.env.model.trigger("execute-action", {
            actionName: "action_validate_email_smtp",
            args: [],
            record: this.record,
        });
    }
}

HrApplicantEmailValidationWidget.template = "email_validators.HrApplicantEmailValidationWidget";
registry.category("view_widgets").add("hr_applicant_email_validation_widget", HrApplicantEmailValidationWidget);
