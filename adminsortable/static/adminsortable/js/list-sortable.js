"use strict";

jQuery.extend({
	getQueryParams: function() {
		var vars = [], hash, i;
		var hashes = window.location.href.slice(window.location.href.indexOf('?') + 1).split('&');
		for (i = 0; i < hashes.length; i++) {
			hash = hashes[i].split('=');
			vars.push(hash[0]);
			vars[hash[0]] = hash[1];
		}
		return vars;
	},
	getQueryParam: function(name) {
		return jQuery.getQueryParams()[name];
	}
});

// make list view sortable
jQuery(function($) {
	var sortable_update_url = $('#adminsortable_update_url').attr('href') || 'adminsortable_update/';
	var startorder, endorder;
	var csrfvalue = $('#changelist-form').find('input[name="csrfmiddlewaretoken"]').val();

	$('#result_list').sortable({
		handle: 'div.drag',
		items: 'tr',
		axis: 'y',
		scroll: true,
		cursor: 'ns-resize',
		containment: $('#result_list tbody'),
		start: function(event, dragged_rows) {
			$(this).find('thead tr th').each(function(index) {
				$(dragged_rows.item.context.childNodes[index]).width($(this).width() - 10);
			});
			startorder = parseInt($(dragged_rows.item.context).find('div.drag').attr('order'));
		},
		stop: function(event, dragged_rows) {
			var $result_list = $(this);
			$result_list.find('tbody tr').each(function(index) {
				$(this).removeClass('row1 row2').addClass(index % 2 ? 'row2' : 'row1');
			}).each(function() {
				var untilorder = parseInt($(this).find('div.drag').attr('order'));
				if (startorder === untilorder)
					return false;
				endorder = untilorder;
			});
			if (startorder === endorder + 1)
				return;
			$.ajax({
				url: sortable_update_url,
				type: 'POST',
				data: {
					o: $.getQueryParam('o'),
					startorder: startorder,
					endorder: endorder,
					csrfmiddlewaretoken: csrfvalue
				},
				success: function(moved_items) {
					$.each(moved_items, function(index, item) {
						$result_list.find('tbody tr input.action-select[value=' + item.pk + ']').parents('tr').each(function() {
							$(this).find('div.drag').attr('order', item.order);
						});
					});
				},
				error: function(response) {
					console.error('The server responded: ' + response.responseText);
				}
			});
		}
	});
	$('#result_list, tbody, tr, td, th').disableSelection();
});
