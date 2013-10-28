//make stacked inlines sortable
jQuery(function($) {
	$('.inline-related').sortable({
		items: 'tr.form-row',
		axis: 'y',
		scroll: true,
		cursor: 'ns-resize',
		containment: $('tbody'),
		start: function(event, dragged_rows) {
			console.log('start drag');
			/*
			$(this).find('thead tr th').each(function(index) {
				$(dragged_rows.item.context.childNodes[index]).width($(this).width() - 10);
			});
			startorder = $(dragged_rows.item.context).find('div.drag').attr('order');
			*/
		},
		stop: function(event, dragged_rows) {
			console.log('stop drag');
		}
	});
});
