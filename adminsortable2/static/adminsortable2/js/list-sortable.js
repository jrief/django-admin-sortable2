"use strict";

django.jQuery(function($) {
	// make list view sortable
	var startindex, startorder, endindex, endorder;
	var csrfvalue = $('form').find('input[name="csrfmiddlewaretoken"]').val();
	var getQueryParams = function () {
		var vars = [], hash, i;
		var hashes = window.location.href.slice(window.location.href.indexOf('?') + 1).split('&');
		for (i = 0; i < hashes.length; i++) {
			hash = hashes[i].split('=');
			vars.push(hash[0]);
			vars[hash[0]] = hash[1];
		}
		return vars;
	};

	try {
		var config = JSON.parse($("#admin_sortable2_config").text());
	}
	catch (parse_error) {
		return;  // configuration not initialized by change_list.html
	}

	$('#result_list').sortable({
		handle: 'div.drag',
		items: 'tr',
		axis: 'y',
		scroll: true,
		cursor: 'ns-resize',
		containment: $('#result_list tbody'),
		tolerance: 'pointer',
		start: function (event, dragged_rows) {
			$(this).find('thead tr th').each(function (index) {
				$(dragged_rows.item[0].childNodes[index]).width($(this).width() - 10);
			});

			startindex = dragged_rows.item.index();
		},
		stop: function (event, dragged_rows) {
			$(this).find('thead tr th').each(function (index) {
				$(dragged_rows.item[0].childNodes[index]).width('auto');
			});

			var $result_list = $(this);
			$result_list.find('tbody tr').each(function (index) {
				$(this).removeClass('row1 row2').addClass(index % 2 ? 'row2' : 'row1');
			});

			endindex = dragged_rows.item.index();

			if (endindex < startindex) {
				// drag up
				endorder = $(dragged_rows.item[0].nextElementSibling).find('div.drag').attr('order');
			} else if (endindex > startindex) {
				// drag down
				endorder = $(dragged_rows.item[0].previousElementSibling).find('div.drag').attr('order');
			} else {
				return;
			}
			startorder = $(dragged_rows.item[0]).find('div.drag').attr('order');

			$.ajax({
				url: config.update_url,
				type: 'POST',
				data: {
					startorder: startorder,
					endorder: endorder,
					csrfmiddlewaretoken: csrfvalue
				},
				success: function (moved_items) {
					$.each(moved_items, function (index, item) {
						$result_list.find('tbody tr .js-reorder-' + item.pk).parents('tr').each(function () {
							$(this).find('div.drag').attr('order', item.order);
						});
					});
				},
				error: function (response) {
					console.error('The server responded: ' + response.responseText);
				}
			});
		}
	});
	$('#result_list, tbody, tr, td, th').disableSelection();
});

// Show and hide the step input field
django.jQuery(function($) {
	var $step_field = $('#changelist-form-step');
	var $page_field = $('#changelist-form-page');

	try {
		var config = JSON.parse($("#admin_sortable2_config").text());
	}
	catch (parse_error) {
		return;  // configuration not initialized by change_list.html
	}

	if (config.current_page === config.total_pages) {
		$page_field.attr('max', config.total_pages - 1);
		$page_field.val(config.current_page - 1);
	} else {
		$page_field.attr('max', config.total_pages);
		$page_field.val(config.current_page + 1)
	}
	if (config.current_page === 1) {
		$page_field.attr('min', 2);
	} else {
		$page_field.attr('min', 1);
	}

	$step_field.attr('min', 1);

	function display_fields() {
		if (['move_to_back_page', 'move_to_forward_page'].indexOf($(this).val()) != -1) {
			if ($(this).val() === 'move_to_forward_page') {
				$step_field.attr('max', config.total_pages - config.current_page);
			} else {
				$step_field.attr('max', config.current_page - 1);
			}
			$step_field.show();
		} else {
			$step_field.hide();
		}
		if ($(this).val() === 'move_to_exact_page') {
			$page_field.show();
		} else {
			$page_field.hide();
		}
	}

	var $grp_form = $('#grp-changelist-form'); // Grappelli support
	if ($grp_form) {
		$grp_form.attr('novalidate', 'novalidate');
	}
	var $form = $('#changelist-form') || $grp_form;
	$form.find('select[name="action"]').change(display_fields);
});
