import Sortable, { MultiDrag, SortableEvent } from 'sortablejs';

Sortable.mount(new MultiDrag());

class SortableBase {
	protected readonly config: any;

	constructor() {
		this.config = JSON.parse(document.getElementById('admin_sortable2_config')?.textContent ?? '');
	}
}


class ListSortable extends SortableBase {
	private readonly tableBody: HTMLTableSectionElement;
	private readonly sortable: Sortable;
	private readonly observer: MutationObserver;

	constructor(table: HTMLTableElement) {
		super();
		this.tableBody = table.querySelector('tbody')!;
		this.sortable = Sortable.create(this.tableBody, {
			animation: 150,
			handle: '.handle',
			draggable: 'tr',
			selectedClass: 'selected',
			multiDrag: true,
			onEnd: event => this.onEnd(event),
		});
		this.observer = new MutationObserver(mutationsList => this.selectActionChanged(mutationsList));
		const tableRows = this.tableBody.querySelectorAll('tr');
		tableRows.forEach(tableRow => this.observer.observe(tableRow, {attributes: true}));
	}

	private selectActionChanged(mutationsList: Array<MutationRecord>) {
		for (const mutation of mutationsList) {
			if (mutation.type === 'attributes' && mutation.attributeName === 'class') {
				const tableRow = mutation.target as HTMLTableRowElement;
				if (tableRow.classList.contains('selected')) {
					Sortable.utils.select(tableRow);
				} else {
					Sortable.utils.deselect(tableRow);
				}
			}
		}
	}

	private async onEnd(evt: SortableEvent) {
		if (typeof evt.newIndex !== 'number' || typeof evt.oldIndex !== 'number' || !(evt.item instanceof HTMLTableRowElement))
			return;

		let endorder;
		if (evt.newIndex < evt.oldIndex) {
			// drag up
			if (evt.items.length > 0) {
				endorder = evt.items[evt.items.length - 1].nextElementSibling?.querySelector('.handle')?.getAttribute('order');
			} else {
				endorder = evt.item.nextElementSibling?.querySelector('.handle')?.getAttribute('order');
			}
		} else if (evt.newIndex > evt.oldIndex) {
			// drag down
			if (evt.items.length > 0) {
				endorder = evt.items[0].previousElementSibling?.querySelector('.handle')?.getAttribute('order');
			} else {
				endorder = evt.item.previousElementSibling?.querySelector('.handle')?.getAttribute('order');
			}
		} else {
			return;
		}
		const draggedItems = new Array<string>();
		if (evt.items.length > 0) {
			evt.items.forEach(elem => {
				const pk = elem?.querySelector('.handle')?.getAttribute('pk');
				if (pk) {
					draggedItems.push(pk);
				}
			});
		} else {
			const pk = evt.item?.querySelector('.handle')?.getAttribute('pk');
			if (pk) {
				draggedItems.push(pk);
			}
		}
		if (draggedItems.length === 0)
			return;
		const response = await fetch(this.config.update_url, {
			method: 'POST',
			headers: this.headers,
			body: JSON.stringify({
				draggedItems: draggedItems,
				endorder: endorder,
			})
		});
		if (response.status === 200) {
			const movedItems = await response.json();
			movedItems.forEach((item: any) => {
				const tableRow = this.tableBody.querySelector(`tr td.field-_reorder_ div[pk="${item.pk}"]`)?.closest('tr');
				tableRow?.querySelector('.handle')?.setAttribute('order', item.order);
			});
			this.resetActions();
		} else {
			console.error(`The server responded: ${response.statusText}`);
		}
	}

	private resetActions() {
		// reset default action checkboxes behaviour
		if (!window.hasOwnProperty('Actions'))
			return;
		const actionsEls = this.tableBody.querySelectorAll('tr input.action-select');
		actionsEls.forEach(elem => {
			const tableRow = elem.closest('tr');
			// @ts-ignore
			Sortable.utils.deselect(tableRow);
			tableRow?.classList.remove('selected');
			(elem as HTMLInputElement).checked = false;
		});
		// @ts-ignore
		window.Actions(actionsEls);
	}

	public get headers(): Headers {
		const value = `; ${document.cookie}`;
		const parts = value.split('; csrftoken=');
		const csrfToken = parts.length === 2 ? parts[1].split(';').shift() : null;
		const headers = new Headers();
		headers.append('Accept', 'application/json');
		headers.append('Content-Type', 'application/json');
		if (csrfToken) {
			headers.append('X-CSRFToken', csrfToken);
		}
		return headers;
	}
}


class ActionForm extends SortableBase {
	private readonly selectElement: HTMLSelectElement;
	private readonly stepInput: HTMLInputElement;
	private readonly pageInput: HTMLInputElement;

	constructor(formElement: HTMLElement) {
		super();
		formElement.setAttribute('novalidate', 'novalidate');
		this.selectElement = formElement.querySelector('select[name="action"]')!;
		this.selectElement.addEventListener('change', () => this.actionChanged());

		this.stepInput = document.getElementById('changelist-form-step') as HTMLInputElement;
		this.stepInput.setAttribute('min', '1');
		const max = Math.max(this.config.total_pages - this.config.current_page, this.config.current_page);
		this.stepInput.setAttribute('max', `${max}`);
		this.stepInput.value = '1';

		this.pageInput = document.getElementById('changelist-form-page') as HTMLInputElement;
		this.pageInput.setAttribute('min', '1');
		this.pageInput.setAttribute('max', `${this.config.total_pages}`);
		this.pageInput.value = `${this.config.current_page}`;
	}

	private actionChanged() {
		this.pageInput.style.display = this.stepInput.style.display = 'none';
		switch (this.selectElement?.value) {
			case 'move_to_exact_page':
				this.pageInput.style.display = 'inline-block';
				break;
			case 'move_to_forward_page':
				this.stepInput.style.display = 'inline-block';
				break;
			case 'move_to_back_page':
				this.stepInput.style.display = 'inline-block';
				break;
			case 'move_to_first_page':
				this.pageInput.value = '1';
				break;
			case 'move_to_last_page':
				this.pageInput.value = `${this.config.total_pages + 1}`;
				break;
			default:
				break;
		}
	}
}


class InlineSortable {
	private readonly sortable: Sortable;
	private readonly reversed: boolean;
	private readonly itemSelectors: string;

	constructor(inlineFieldSet: HTMLFieldSetElement) {
		this.reversed = inlineFieldSet.classList.contains('reversed');
		const tBody = inlineFieldSet.querySelector('table tbody') as HTMLTableSectionElement;
		if (tBody) {
			// tabular inline
			this.itemSelectors = 'tr.has_original'
			this.sortable = Sortable.create(tBody, {
				animation: 150,
				handle: 'td.original p',
				draggable: 'tr',
				onEnd: event => this.onEnd(event),
			});
		} else {
			// stacked inline
			this.itemSelectors = '.inline-related.has_original'
			this.sortable = Sortable.create(inlineFieldSet, {
				animation: 150,
				handle: 'h3',
				draggable: '.inline-related.has_original',
				onEnd: event => this.onEnd(event),
			});
		}
	}

	private onEnd(evt: SortableEvent) {
		const originals = this.sortable.el.querySelectorAll(this.itemSelectors);
		if (this.reversed) {
			originals.forEach((element: Element, index: number) => {
				const reorderInputElement = element.querySelector('input._reorder_') as HTMLInputElement;
				reorderInputElement.value = `${originals.length - index}`;
			});
		} else {
			originals.forEach((element: Element, index: number) => {
				const reorderInputElement = element.querySelector('input._reorder_') as HTMLInputElement;
				reorderInputElement.value = `${index + 1}`;
			});
		}
	}
}


window.addEventListener('load', (event) => {
	const table = document.getElementById('result_list');
	if (table instanceof HTMLTableElement) {
		new ListSortable(table);
	}

	const changelistForm = document.getElementById('changelist-form');
	if (changelistForm) {
		new ActionForm(changelistForm);
	}

	for (let inlineFieldSet of document.querySelectorAll('fieldset.sortable')) {
		new InlineSortable(inlineFieldSet as HTMLFieldSetElement);
	}
});
