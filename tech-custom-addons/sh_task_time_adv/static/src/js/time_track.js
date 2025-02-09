odoo.define("sh_task_time_adv.time_track", function (require) {
    "use strict";
    var AbstractField = require("web.AbstractField");
    var core = require("web.core");
    var field_registry = require("web.field_registry");
    var time = require("web.time");
    var Widget = require("web.Widget");
    var _t = core._t;
    var TimeCounter = AbstractField.extend({
        supportedFieldTypes: [],

        willStart: function () {
            var self = this;
            var def = this._rpc({
                model: "account.analytic.line",
                method: "search_read",
                domain: [
                    ["task_id", "=", this.record.data.id],
                    ["end_date", "=", false],
                    ["start_date", "!=", false],
                ],
            }).then(function (result) {
                if (self.mode === "readonly") {
                    var currentDate = new Date();
                    self.duration = 0;
                    _.each(result, function (data) {
                        self.duration += data.end_date ? self._getDateDifference(data.start_date, data.end_date) : self._getDateDifference(time.auto_str_to_date(data.start_date), currentDate);
                    });
                }
            });
            return $.when(this._super.apply(this, arguments), def);
        },

        destroy: function () {
            this._super.apply(this, arguments);
            clearTimeout(this.timer);
        },

        isSet: function () {
            return true;
        },

        _getDateDifference: function (dateStart, dateEnd) {
            return moment(dateEnd).diff(moment(dateStart));
        },

        _render: function () {
            console.log("render");
            this._startTimeCounter();
        },

        _startTimeCounter: function () {
            var self = this;
            this.timer = "";
            clearTimeout(this.timer);
            if (this.record.data.is_user_working) {
                this.timer = setTimeout(function () {
                    self.duration += 1000;
                    self._startTimeCounter();
                }, 1000);
            } else {
                clearTimeout(this.timer);
            }
            this.$el.html($("<span>" + moment.utc(this.duration).format("HH:mm:ss") + "</span>"));
        },
    });

    field_registry.add("task_time_counter", TimeCounter);
});

odoo.define("sh_task_time_adv.TaskTimerTemplate", function (require) {
    var core = require("web.core");
    var Dialog = require("web.Dialog");
    var Widget = require("web.Widget");
    var rpc = require("web.rpc");
    var SystrayMenu = require("web.SystrayMenu");

    var _t = core._t;
    var QWeb = core.qweb;

    var TimerMenu = Widget.extend({
        template: "TaskTimerTemplate",
        events: {
            "click #timer_start": "_start_timer",
            "click #timer_stop": "_stop_timer",
            "click #user_task_link": "_open_task_form",
        },
        init: function () {
            this._super.apply(this, arguments);
            var self = this;
            this._rpc({
                model: "res.users",
                method: "search_read",
                fields: ["task_id"],
                domain: [["id", "=", this.getSession().uid]],
            }).then(function (data) {
                if (data) {
                    _.each(data, function (user) {
                        if (user.task_id) {
                            self.$("#timer_start").css("display", "none");
                            self.$("#timer_stop").css("display", "flex");
                            self.$("#user_task").html(
                                $('<a>', {
                                    id: 'user_task_link',
                                    href: '#',
                                    text: user.task_id[1],
                                    'data-task-id': user.task_id[0],
                                    style: 'color: inherit; text-decoration: none;'
                                })
                            );
                            self._rpc({
                                model: "project.task",
                                method: "get_duration",
                                args: [user.task_id[0]],
                            }).then(function (duration) {
                                self.$("#task_timer").html($("<span>" + moment.utc(duration).format("HH:mm:ss") + "</span>"));
                                self._startTimeCounter(duration);
                            });
                        } else {
                            self.$("#timer_stop").css("display", "none");
                            self.$("#task_timer").css("display", "none");
                            self.$("#timer_start").css("display", "flex");
                           // self.$("#user_task").parent("li").css("display", "none");
                        }
                    });
                }
            });
        },
        _startTimeCounter: function (duration) {
            var self = this;
            setTimeout(function () {
                console.log("\n\n\ndurationdfkl",duration)
                duration += 1000;
                self.$("#task_timer").html($("<span>" + moment.utc(duration).format("HH:mm:ss") + "</span>"));
                self._startTimeCounter(duration);
            }, 1000);
        },
        _start_timer: function (e) {
            e.preventDefault();
            this.do_action({
                type: "ir.actions.act_window",
                view_type: "form",
                view_mode: "form",
                views: [[false, "form"]],
                res_model: "sh.start.timesheet",
                target: "new",
                context: {
                    form_view_ref: "sh_task_time_adv.start_timesheet_form",
                },
            });
        },
        _stop_timer: function (e) {
            e.preventDefault();
            var self = this;

            this._rpc({
                model: "res.users",
                method: "search_read",
                fields: ["task_id"],
                domain: [["id", "=", this.getSession().uid]],
            }).then(function (data) {
                if (data) {
                    _.each(data, function (user) {
                        if (user.task_id) {
                            self._rpc({
                                model: "project.task",
                                method: "search_read",
                                fields: ["start_time", "end_time", "total_time"],
                                domain: [["id", "=", user.task_id[0]]],
                            }).then(function (task) {
                                self.do_action({
                                    type: "ir.actions.act_window",
                                    view_type: "form",
                                    view_mode: "form",
                                    views: [[false, "form"]],
                                    res_model: "sh.task.time.account.line",
                                    target: "new",
                                    context: {
                                        // default_start_date: task[0]["start_time"],
                                        default_start_date: user.start_time,
                                        active_id: user.task_id[0],
                                        active_model: "project.task",
                                    },
                                });
                            });
                        }
                    });
                }
            });
        },

        // Add method to handle opening the task form view
        _open_task_form: function (e) {
            e.preventDefault();
            var task_id = $(e.currentTarget).data('task-id');
            this.do_action({
                type: "ir.actions.act_window",
                view_type: "form",
                view_mode: "form",
                res_model: "project.task",
                res_id: task_id,
                views: [[false, "form"]],
                target: "current"
            });
        },
    });
    TimerMenu.prototype.sequence = 3;
    SystrayMenu.Items.push(TimerMenu);

    return {
        TimerMenu: TimerMenu,
    };
});

odoo.define("sh_task_time_adv.QuicklyTaskCreateTemplate", function (require) {
    var core = require("web.core");
    var Widget = require("web.Widget");
    var SystrayMenu = require("web.SystrayMenu");

    var QuickTask = Widget.extend({
        template: "QuicklyTaskCreateTemplate",

        events: {
            "click #task_start": "_create_task_start",
        },

        start: function () {
            this.$el.addClass("o_task_button");
            return this._super.apply(this, arguments);
        },

        _create_task_start: function (e) {
            e.preventDefault();
            this.do_action({
                type: "ir.actions.act_window",
                view_type: "form",
                view_mode: "form",
                views: [[false, "form"]],
                res_model: "quick.task.wizard",
                target: "new",
                context: {
                    form_view_ref: "sh_task_time_adv.QuicklyTaskCreateTemplate",
                },
            });
        },

        
    });

    QuickTask.prototype.sequence = 3;
    SystrayMenu.Items.push(QuickTask);

    return {
        QuickTask: QuickTask,
    };
});
