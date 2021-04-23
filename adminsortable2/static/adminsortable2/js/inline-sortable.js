// make tabular- and stacked inlines sortable
django.jQuery(function($) {
	$('div.inline-group.sortable').each(function () {
		var $order_div = $(this).nextUntil('div.default_order_field').next()
		var default_order_field = $order_div.attr('default_order_field');
		var default_order_direction = $order_div.attr('default_order_direction');
		var order_input_field = 'input[name$="-' + default_order_field + '"]';
		// first, try with tabluar inlines
		var tabular_inlines = $(this).find('div.tabular table');
		tabular_inlines.sortable({
			handle: $(this).find('tbody .drag'),
			items: 'tr.form-row.has_original',
			axis: 'y',
			scroll: true,
			cursor: 'ns-resize',
			containment: $(this).find('tbody'),
			stop: function (event, dragged_rows) {
				var $result_list = $(this);
				$result_list.find('tbody tr').each(function (index) {
					$(this).removeClass('row1 row2').addClass(index % 2 ? 'row2' : 'row1');
				});
				var originals = $result_list.find('tbody tr.has_original').get()
				if (default_order_direction === '-') {
					originals.reverse();
				}
				$(originals).each(function (index) {
					$(this).find(order_input_field).val(index + 1);
				});
			}
		});
		if (tabular_inlines.length)
			return true;
		// else, try with stacked inlines
		$(this).sortable({
			handle: 'h3',
			items: 'div.inline-related.has_original',
			axis: 'y',
			scroll: true,
			cursor: 'ns-resize',
			containment: $(this),
			stop: function (event, dragged_rows) {
				var $result_list = $(this);
				var originals = $result_list.find('div.inline-related.has_original').get()
				if (default_order_direction === '-') {
					originals.reverse();
				}
				$(originals).each(function (index) {
					$(this).find(order_input_field).val(index + 1);
				});
			}
		});
	});
});
