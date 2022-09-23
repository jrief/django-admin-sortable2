import Sortable, { MoveEvent, MultiDrag, SortableEvent } from 'sortablejs';

Sortable.mount(new MultiDrag());

class ListSortable {
	private readonly tableBody: HTMLTableSectionElement;
	private readonly config: any;
	private readonly sortable: Sortable;
	private readonly observer: MutationObserver;
	private firstOrder: number | undefined;
	private orderDirection: number | undefined;

	constructor(table: HTMLTableElement, config: any) {
		this.tableBody = table.querySelector('tbody')!;
		this.config = config;
		this.sortable = Sortable.create(this.tableBody, {
			animation: 150,
			handle: '.handle',
			draggable: 'tr',
			selectedClass: 'selected',
			multiDrag: true,
			onStart: event => this.onStart(event),
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

	private async onStart(evt: SortableEvent) {
		evt.oldIndex;  // element index within parent
		const firstOrder = this.tableBody.querySelector('tr:first-child')?.querySelector('.handle')?.getAttribute('order');
		const lastOrder = this.tableBody.querySelector('tr:last-child')?.querySelector('.handle')?.getAttribute('order');
		if (firstOrder && lastOrder) {
			this.firstOrder = parseInt(firstOrder);
			this.orderDirection = parseInt(lastOrder) > this.firstOrder ? 1 : -1;
		}
	}

	private async onEnd(evt: SortableEvent) {
		if (typeof evt.newIndex !== 'number' || typeof evt.oldIndex !== 'number'
			|| typeof this.firstOrder !== 'number'|| typeof this.orderDirection !== 'number'
			|| !(evt.item instanceof HTMLTableRowElement))
			return;

		let firstChild: number, lastChild: number;
		if (evt.items.length === 0) {
			// single dragged item
			if (evt.newIndex < evt.oldIndex) {
				// drag up
				firstChild = evt.newIndex;
				lastChild = evt.oldIndex;
			} else if (evt.newIndex > evt.oldIndex) {
				// drag down
				firstChild = evt.oldIndex;
				lastChild = evt.newIndex;
			} else {
				return;
			}
		} else {
			// multiple dragged items
			firstChild = this.tableBody.querySelectorAll('tr').length;
			lastChild = 0;
			evt.oldIndicies.forEach(item => {
				firstChild = Math.min(firstChild, item.index)
				lastChild = Math.max(lastChild, item.index)
			});
			evt.newIndicies.forEach(item => {
				firstChild = Math.min(firstChild, item.index)
				lastChild = Math.max(lastChild, item.index)
			});
		}

		const updatedRows = this.tableBody.querySelectorAll(`tr:nth-child(n+${firstChild + 1}):nth-child(-n+${lastChild + 1})`);
		if (updatedRows.length === 0)
			return;

		let order;
		if (firstChild === 0) {
			order = this.firstOrder;
		} else {
			order = this.tableBody.querySelector(`tr:nth-child(${firstChild}) .handle`)?.getAttribute('order');
			if (!order)
				return;
			order = parseInt(order) + this.orderDirection;
		}
 		const updatedItems = new Map<string, number>();
		for (let row of updatedRows) {
			const pk = row.querySelector('.handle')?.getAttribute('pk');
			if (pk) {
				row.querySelector('.handle')?.setAttribute('order', String(order));
				updatedItems.set(pk, order);
				order += this.orderDirection;
			}
		}

		const response = await fetch(this.config.update_url, {
			method: 'POST',
			headers: this.headers,
			body: JSON.stringify({
				updatedItems: Array.from(updatedItems.entries()),
			})
		});
		if (response.status === 200) {
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
		const elem = document.getElementById('action-toggle');
		if (elem instanceof HTMLInputElement) {
			elem.checked = false;
		}
		// @ts-ignore
		window.Actions(actionsEls);
	}

	public get headers(): Headers {
		const headers = new Headers();
		headers.append('Accept', 'application/json');
		headers.append('Content-Type', 'application/json');

		const inputElement = this.tableBody.closest('form')?.querySelector('input[name="csrfmiddlewaretoken"]') as HTMLInputElement;
		if (inputElement) {
			headers.append('X-CSRFToken', inputElement.value);
		}
		return headers;
	}
}


class ActionForm {
	private readonly selectElement: HTMLSelectElement;
	private readonly config: any;
	private readonly stepInput: HTMLInputElement;
	private readonly pageInput: HTMLInputElement;

	constructor(formElement: HTMLElement, config: any) {
		formElement.setAttribute('novalidate', 'novalidate');
		this.selectElement = formElement.querySelector('select[name="action"]')!;
		this.config = config;
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
				onEnd: event => this.onEnd(),
				onMove: event => this.onMove(event),
			});
		} else {
			// stacked inline
			this.itemSelectors = '.inline-related.has_original'
			this.sortable = Sortable.create(inlineFieldSet, {
				animation: 150,
				handle: 'h3',
				draggable: '.inline-related.has_original',
				onEnd: event => this.onEnd(),
			});
		}
		inlineFieldSet.querySelectorAll('.inline-related .sort i.move-begin').forEach(
			elem => elem.addEventListener('click', event => this.move(event.target, 'begin'))
		);
		inlineFieldSet.querySelectorAll('.inline-related .sort i.move-end').forEach(
			elem => elem.addEventListener('click', event => this.move(event.target, 'end'))
		);
	}

	private onEnd() {
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

	private onMove(event: MoveEvent) {
		return event.related.classList.contains("has_original");
	}

	private move(target: EventTarget | null, direction: 'begin' | 'end') {
		if (!(target instanceof HTMLElement))
			return;
		const inlineRelated = target.closest(this.itemSelectors);
		if (!inlineRelated)
			return;
		const inlineRelatedList = this.sortable.el.querySelectorAll(this.itemSelectors);
		if (inlineRelatedList.length < 2)
			return;
		if (direction === 'begin') {
			inlineRelatedList[0].insertAdjacentElement('beforebegin', inlineRelated);
		} else {
			inlineRelatedList[inlineRelatedList.length - 1].insertAdjacentElement('afterend', inlineRelated);
		}
		this.onEnd();
	}
}


window.addEventListener('load', (event) => {
	const configElem = document.getElementById('admin_sortable2_config');
	if (configElem instanceof HTMLScriptElement && configElem.textContent) {
		const adminSortableConfig = JSON.parse(configElem.textContent);

		const table = document.getElementById('result_list');
		if (table instanceof HTMLTableElement) {
			new ListSortable(table, adminSortableConfig);
		}

		const changelistForm = document.getElementById('changelist-form');
		if (changelistForm) {
			new ActionForm(changelistForm, adminSortableConfig);
		}
	}

	for (let inlineFieldSet of document.querySelectorAll('fieldset.sortable')) {
		new InlineSortable(inlineFieldSet as HTMLFieldSetElement);
	}
});
