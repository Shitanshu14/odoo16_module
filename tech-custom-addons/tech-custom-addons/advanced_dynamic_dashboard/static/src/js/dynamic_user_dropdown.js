//odoo.define('advanced_dynamic_dashboard.populate_users', function (require) {
//    "use strict";
//
//    const rpc = require('web.rpc');
//    const core = require('web.core');
//    const Widget = require('web.Widget');
//    const SystrayMenu = require('web.SystrayMenu');
//
//    var QuickTask = Widget.extend({
//        template: 'UserNamesTemplate',
//
//        start: function () {
//            this._super.apply(this, arguments);
//            this.populateUserNames();
//        },
//
//        populateUserNames: function () {
//            rpc.query({
//                model: 'res.users',
//                method: 'search_read',
//                args: [[], ['id','name']],
//            }).then(users => {
//                console.log("----------------users", users)
//                const userDropdownElement = document.getElementById('user-names-list');
//                if (userDropdownElement) {
//                    userDropdownElement.innerHTML = '';
//
//                    users.forEach(user => {
//                        console.log("----------------user", user)
//                        const option = document.createElement('option');
//                        option.value = user.id;
//                        option.textContent = user.name;
//                        userDropdownElement.appendChild(option);
//                    });
//                }
//            });
//        }
//    });
//
//    SystrayMenu.Items.push(QuickTask);
//
//    core.bus.on('web_client_ready', null, function () {
//        new QuickTask().appendTo($('body'));
//    });
//});









//import { Component } from "@odoo/owl";
//import { registry } from "@web/core/registry";
//
////const { xml } = owl.tags;
//
////import { Component, xml } from 'owl';
//
////import { Component, xml, owl } from 'owl';
////import { registry } from '@web/core/registry';
//
//class UserSelectionWidget extends Component {
//    setup() {
//        super.setup();
//        this.state = {};
//    }
//
//    async willUpdateProps(nextProps) {
//        const { resModel, record } = nextProps;
//        const users = await record.env[resModel].search([]);
//        this.state.options = users.map((user) => ({
//            label: user.name,
//            value: user.id,
//        }));
//    }
//
//    _render() {
//        const { options } = this.state;
//        return `
//            <label for="select-user" style="color: black; margin-right: 5px;">Select User:</label>
//            <select id="select-user" data-model="res.users" data-field="name">
//                 self.${options.map((option) => `
//                    <option value="${option.value}">self.${option.label}</option>
//                `).join('')}
//            </select>
//        `;
//    }
//}
//
//UserSelectionWidget.template = xml`
//    <t t-name="UserSelectionWidget">
//        <t t-call="web.FieldSelectionWidget"/>
//    </t>
//`;
//
//registry.category("fields").add("user_selection", UserSelectionWidget);









//console.log("My widget code is loaded!");

//
//import { Widget } from "@web/core/framework";
//
//console.log("My widget code is loaded22222222222222!");
//
//export class DynamicUserDropdown extends Widget {
//console.log("My widget code is loaded3333333333333333!");
//    mounted() {
//        super.mounted();
//        this.fetchData();
//    }
//
//    async fetchData() {
//        const users = await this.env.rpc('/fetch_users');
//        this.options = users.map((user) => ({
//            id: user.id,
//            label: user.name,
//        }));
//    }
//
//    static template = xml`
//        <select t-model="record.user_id">
//            <t t-esc="options" for="option in options">
//                <option t-att-value="option.id" t-text="option.label" />
//            </t>
//        </select>
//    `;
//
////     static buttonClick() {} // To comply with the Widget interface (optional in this case)
//}
//
//export default {
//    props: {
//        record: {
//            type: Object,
//            required: true,
//        },
//    },
//};
//
//registry.category("widgets").add("dynamic_user_dropdown", DynamicUserDropdown);
