// make tabular inlines sortable
jQuery(function($) {
	$('div.inline-group').each(function() {
		var default_order_field = $(this).nextUntil('div.default_order_field').next().attr('default_order_field');
		var order_input_field = 'input[name$="' + default_order_field + '"]';
		$(this).find(order_input_field).each(function() {
			$(this).clone().attr('type', 'hidden').insertAfter($(this)).prev().remove();
		});
		$(this).find('div.tabular table').sortable({
			items: 'tr.form-row.has_original',
			axis: 'y',
			scroll: true,
			cursor: 'ns-resize',
			containment: $('tbody'),
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
	});
});
