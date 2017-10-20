django.jQuery(function ($) {
	$("script.inline-stacked-config").each(function(i, config_element) {
		try {
			var config = JSON.parse(config_element.textContent);
			$("#"+ config["prefix"] + "-group .inline-related").stackedFormset(config);
		}
		catch (parse_error) {
			console.error("Configuration for a django-adminsortable2 inline-stacked form is invalid.");
		}
	});
});
