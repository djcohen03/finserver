var FLASH = (() => {
    var container = $('#flash-messages');


    var _makeAlert = (message, type) => {
        // Helper method to make the actual alert element:
        return $(`
            <div class="alert alert-${ type } animated fadeInRight">
                ${ message }
                <button type="button" class="close" data-dismiss="alert" aria-hidden="true">&times;</button>
            </div>
        `);
    }

    var _flash = (message, type, timeout=15) => {
        // Helper method to make the alert and flash it:

        // Make the alert:
        var item = _makeAlert(message, type);
        container.append(item);

        // Fade out the item after some time:
        setTimeout(() => {
            item.removeClass('animated').fadeOut()
        }, timeout * 1000);
    }

    // Flash Methods:
    var methods = {};
    methods.success = (message) => _flash(message, 'success');
    methods.error = (message) => _flash(message, 'danger');
    methods.info = (message) => _flash(message, 'info');

    return methods;
})();

// Flash Flask Messages:
$(() => flaskMessges.forEach(item => FLASH[item.category](item.message)))
