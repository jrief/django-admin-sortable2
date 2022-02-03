import Sortable, { SortableEvent } from 'sortablejs';


class SortableBase {
	protected readonly config: any;

	constructor() {
		this.config = JSON.parse(document.getElementById('admin_sortable2_config')?.textContent ?? '');
	}
}


class ListSortable extends SortableBase {
	private readonly tableBody: HTMLTableSectionElement;
	private readonly sortable: Sortable;

	constructor(table: HTMLTableElement) {
		super();
		this.tableBody = table.querySelector('tbody')!;
		this.sortable = Sortable.create(this.tableBody, {
			animation: 150,
			handle: '.drag',
			draggable: 'tr',
			selectedClass: 'selected',
			onEnd: event => this.onEnd(event),
		});
	}

	private async onEnd(evt: SortableEvent) {
		if (typeof evt.newIndex !== 'number' || typeof evt.oldIndex !== 'number' || !(evt.item instanceof HTMLTableRowElement))
			return;

		let endorder;
		if (evt.newIndex < evt.oldIndex) {
			// drag up
			endorder = evt.item.nextElementSibling?.querySelector('.drag')?.getAttribute('order');
		} else if (evt.newIndex > evt.oldIndex) {
			// drag down
			endorder = evt.item.previousElementSibling?.querySelector('.drag')?.getAttribute('order');
		} else {
			return;
		}
		const startorder = evt.item.querySelector('.drag')?.getAttribute('order');
		const response = await fetch(this.config.update_url, {
			method: 'POST',
			headers: this.headers,
			body: JSON.stringify({
				startorder: startorder,
				endorder: endorder,
			})
		});
		if (response.status === 200) {
			const movedItems = await response.json();
			movedItems.forEach((item: any) => {
				const tableRow = this.tableBody.querySelector(`tr .js-reorder-${item.pk}`)?.closest('tr');
				tableRow?.querySelector('.drag')?.setAttribute('order', item.order);
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
			elem.closest('tr')?.classList.remove('selected');
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

window.addEventListener('load', (event) => {
	const table = document.getElementById('result_list');
	if (table instanceof HTMLTableElement) {
		new ListSortable(table);
	}

	const changelistForm = document.getElementById('changelist-form');
	if (changelistForm) {
		new ActionForm(changelistForm);
	}
});
