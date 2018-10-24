django.jQuery(function($) {
	$("script.inline-stacked-config").each(function (i, config_element) {
		try {
			var config = JSON.parse(config_element.textContent);
		}
		catch (parse_error) {
			console.error("Configuration for a django-adminsortable2 inline-stacked form is invalid.");
		}

		// Note: This function signature changed in Django 2.1.
		if ($.fn.stackedFormset.length === 1) {  // Django < 2.1
			$("#" + config["prefix"] + "-group .inline-related").stackedFormset(config);
		} else {  // Django 2.1+
			$("#" + config["prefix"] + "-group .inline-related").stackedFormset($('this').selector, config);
		}

	});
});
