// make tabular- and stacked inlines sortable
jQuery(function($) {
	$('div.inline-group.sortable').each(function() {
		var default_order_field = $(this).nextUntil('div.default_order_field').next().attr('default_order_field');
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
			stop: function(event, dragged_rows) {
				var $result_list = $(this);
				$result_list.find('tbody tr').each(function(index) {
					$(this).removeClass('row1 row2').addClass(index % 2 ? 'row2' : 'row1');
				});
				$result_list.find('tbody tr.has_original').each(function(index) {
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
			stop: function(event, dragged_rows) {
				var $result_list = $(this);
				$result_list.find('div.inline-related.has_original').each(function(index) {
					$(this).find(order_input_field).val(index + 1);
				});
			}
		});
	});
});
