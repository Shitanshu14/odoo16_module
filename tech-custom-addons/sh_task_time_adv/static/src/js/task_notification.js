odoo.define("sh_task_time_adv.task_notification", function (require) {
    "use strict";

    var rpc = require("web.rpc");
    var shownPopups = {};
    var session = require('web.session');

    // setInterval(function() {
    //     rpc.query({
    //          model: 'account.analytic.line',
    //          method: 'show_pop',
    //          args: [[],session.uid],
    //     }).then(function (result) {
    //         if (result !== false && !shownPopups[result]) {
    //             console.log(JSON.stringify(result));
    //             alert(`Your Timer on the Task '${result}' has Ended. Kindly Restart it if you're still working on it.`);
    //             shownPopups[result] = true;
    //         }
    //     });
    // }, 40 * 1000);
});