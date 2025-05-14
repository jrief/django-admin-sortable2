# CHANGELOG

## Release history of [django-admin-sortable2](https://github.com/jrief/django-admin-sortable2/)

### 2.2.6
- Fix adding new models with inlines: automatically set order of new entries.

### 2.2.5
- Fix sorting in parallel requests.
- Add support for Python 3.13.

### 2.2.4
- Fix: Selected ordering is not always preserved when using "Save as new" in inline admin.

### 2.2.3
- Add compatibility for Django-5.1

### 2.2.2
- Fix: Coalesce type error on `default_ordering_field`.

### 2.2.1
- Fix: With setting `DEBUG = True`, loading the unminimized JavaScript files failed. They now are added during build
  time.

### 2.2
- Add support for Django-5.0
- Add support for Python-3.12
- Drop support for Django-4.1 and lower.
- Drop support for Python-3.8

### 2.1.11
- Upgrade all external dependencies to their latest versions.
- Adopt E2E tests to use Playwright's `locator`.

### 2.1.10
- Do not create sourcemaps in production build.

### 2.1.9
- Folder `testapp` is not published on PyPI anymore.

### 2.1.8
- Fix: In combination with [django-nested-admin](https://github.com/theatlantic/django-nested-admin) integration fails
  with an error in inlien formsets.

### 2.1.7
- Yanked.

### 2.1.6
- Add support for Django-4.2.

### 2.1.5
- Fix: In `SortableInlineAdminMixin.get_fields()`, convert potential tuple to list in order to append extra elements.

### 2.1.4
- Fix: It not is not possible anymore, to move items beyond the last item, i.e. after an empty extra rows for new items
  or even after the row with the "Add another chapter" link.

### 2.1.3
- Fix #328: Replace `uglify` against `terser` to minify JavaScript files.

### 2.1.2
- Fix #320: Adding Jinja2 as template engine didn't work because it is unable to handle file references using `pathlib.Path`.

### 2.1.1
- Enlarge top/down buttons on top of header of `SortableTabularInline`.

### 2.1
- Introduce classes `adminsortable2.admin.SortableStackedInline` and `adminsortable2.admin.SortableTabularInline`
  to resort items to the begin or end of the list of those inlines.
- Add support for Django-4.1.

### 2.0.5
- Fix: When using an `InlineAdmin` with a self defined form, the default ordering
  has been ignored. 
- Fix: Skip instance check, if model used in an `InlineAdmin` is a proxy model.


### 2.0.4
- Fix [\#309](https://github.com/jrief/django-admin-sortable2/issues/309):
  Prevent JavaScrip error when using *InlineAdmin without sortable list view.
- Internally use Python's `pathlib` instead of `os.path`.
- In DEBUG mode, load unminimized JavaScript.


### 2.0.3
- Fix [\#304](https://github.com/jrief/django-admin-sortable2/issues/304):
  ModelAdmin not inheriting from SortableAdminMixin prevented sortable Stacked-/TabluraInlineAdmin be sortable.


### 2.0.2
- Fix [\#303](https://github.com/jrief/django-admin-sortable2/issues/303):
  Use CSRF-Token from input field rather than from Cookie.


### 2.0.1
- Fix [\#302](https://github.com/jrief/django-admin-sortable2/issues/302):
  Django's ManifestStaticFilesStorage references missing file `adminsortable2.js.map`.


### 2.0
- Drop support for Django 3.2 and lower.
- Replace jQuery-UI's [sortable](https://jqueryui.com/sortable/) against
  [Sortable.js](https://sortablejs.github.io/Sortable/).
- Use TypeScript instead of JavaScript for all client side code.
- Remove all extended Django admin templates: This allows a smoother upgrade
  for future Django versions.
- New feature: Select multiple rows and drag them to a new position.


### 1.0.4
- Fix [\#294](https://github.com/jrief/django-admin-sortable2/issues/294):
  issue in 1.0.3 where `install_requires` unintentionally dropped Django 2.2


### 1.0.3
- Adding support for Django 4 and Python 3.10.


### 1.0.2
- Fix regression introduced in 1.0.1, adding double item rows on
  SortableInlineAdminMixin and TabularInline.


### 1.0.1
- Fix CSS classes change introduced in Django-2.1.
- Prepared to run on Django-4.0.
- Ditch Travis-CI in favor of GitHub Actions.


### 1.0
- Drop support for Python-2.7, 3.4 and 3.5.
- Drop support for Django-1.10, 1.11, 2.0 and 2.1.
- Add Python-3.9 to the testing matrix.
- Refactor code base to clean Python-3 syntax.


### 0.7.8
- Fix [\#207](https://github.com/jrief/django-admin-sortable2/issues/207):
  Last item not displayed in stacked- and tabular inline admins, if model doesn\'t have add permission.


### 0.7.7
- Add support for Django-3.1.


### 0.7.6
- Fix [\#241](https://github.com/jrief/django-admin-sortable2/issues/241):
  Move items when the order column is not first.
- Fix [\#242](https://github.com/jrief/django-admin-sortable2/issues/242):
  Bulk move when sorting order is descending.
- Fix [\#243](https://github.com/jrief/django-admin-sortable2/issues/243):
  Bulk move to last page when it is too small.
- Refactor aggregates to use Coalasce for empty querysets.


### 0.7.5
- Add support for Django-3.0.


### 0.7.4
- Fix [\#208](https://github.com/jrief/django-admin-sortable2/issues/208):
  Correctly apply custom css classes from the
  `InlineModelAdmin.classes` attribute then using `StackedInline`.


### 0.7.3
- Fix [\#220](https://github.com/jrief/django-admin-sortable2/issues/220):
  If model admin declares `list_display_links = None`, no link is autogenerated for the detail view.


### 0.7.2
- Fully adopted and tested with Django-2.2


### 0.7.1
- Fix issue with JavaScript loading in Django-2.2.


### 0.7
- Add support for Django-2.0 and Django-2.1.
- Drop support for Django-1.9 and lower.
- Check for changed function signature in Django-2.1.


### 0.6.21
- Added jQuery compatibility layer for Django-2.1.


### 0.6.20
- Dysfunctional.


### 0.6.19
- Fix [\#183](https://github.com/jrief/django-admin-sortable2/issues/183):
  Use `mark_safe` for reorder `div`.


### 0.6.18
- Fix: Method `adminsortable2.admin.SortableInlineAdminMixin.get_fields` always return
  a list instead of sometimes a tuple.


### 0.6.17
- [\#171](https://github.com/jrief/django-admin-sortable2/issues/171):
  Adhere to Content Security Policy best practices by removing inline scripts.
- Adopted to Django-2.0 keeping downwards compatibility until Django-1.9.
- Better explanation what to do in case of sorting inconsistency.


### 0.6.16
- Fixes [\#137](https://github.com/jrief/django-admin-sortable2/issues/137):
  Allow standard collapsible tabular inline.


### 0.6.15
- Fix [\#164](https://github.com/jrief/django-admin-sortable2/issues/164):
  TypeError when `display_list` in admin contains a callable.
- Fix [\#160](https://github.com/jrief/django-admin-sortable2/issues/160):
  Updated ordering values not getting saved in `TabluarInlineAdmin` / `StackedInlineAdmin`.


### 0.6.14
- Fix [\#162](https://github.com/jrief/django-admin-sortable2/issues/162):
  In model admin, setting `actions` to `None` or `[]` breaks the sortable functionality.


### 0.6.13
- Fix [\#159](https://github.com/jrief/django-admin-sortable2/issues/159):
  Make stacked inline\'s header more clear that it is sortable.


### 0.6.12
- Fix [\#155](https://github.com/jrief/django-admin-sortable2/issues/155):
  Sortable column not the first field by default.


### 0.6.11
- Fix [\#147](https://github.com/jrief/django-admin-sortable2/issues/147):
  Use current admin site name instead of `admin`.
- Fix [\#122](https://github.com/jrief/django-admin-sortable2/issues/122):
  Columns expand continuously with each sort.


### 0.6.9 and 0.6.10
- Fix [\#139](https://github.com/jrief/django-admin-sortable2/issues/139):
  Better call of post_save signal.


### 0.6.8
- Fix [\#135](https://github.com/jrief/django-admin-sortable2/issues/135):
  Better call of pre_save signal.
- On `./manage.py reorder ...`, name the model using `app_label.model_name` rather than
  requiring the fully qualified path.
- In `adminsortable2.admin.SortableAdminMixin` renamed method `update` to `update_order`,
  to prevent potential naming conflicts.


### 0.6.7
- Add class `PolymorphicSortableAdminMixin` so that method `get_max_order` references the
  ordering field from the base model.


### 0.6.6
- Fix: Drag\'n Drop reordering now send \[pre\|post\]\_save signals for all updated instances.


### 0.6.5
- Fix: Reorder management command now accepts args.


### 0.6.4
- Drop support for Django-1.5.
- `change_list_template` now is extendible.
- Fixed concatenation if `exclude` is tuple.
- Support reverse sorting in CustomInlineFormSet.


### 0.6.3
- Setup.py ready for Python 3.


### 0.6.2
- Fixed regression from 0.6.0: Multiple sortable inlines are now possible again.


### 0.6.1
- Removed global variables from Javascript namespace.


### 0.6.0
- Compatible with Django 1.9.
- In the list view, it now is possible to move items to any arbitrary page.


### 0.5.0
- Changed the namespace from `adminsortable` to `adminsortable2` to allow both this project and
  [django-admin-sortable](https://github.com/jazzband/django-admin-sortable) to co-exist in
  the same project. This is helpful for projects to transition from one to the other library.
  It also allows existing projects\'s migrations which previously relied on django-admin-sortable
  to continue to work.


### 0.3.2
- Fix [\#42](https://github.com/jrief/django-admin-sortable2/issues/42):
  Sorting does not work when ordering is descending.


### 0.3.2
- Use property method `media()` instead of hard coded `Media` class.
- Use the `verbose_name` from the column used to keep the order of fields instead of a
  hard coded \"Sort\".
- When updating order in change_list_view, use the CSRF protection token.


### 0.3.1
- Fixed issue \#25:
  `admin.TabularInline` problem in Django 1.5.x
- Fixed problem when adding new Inline Form Fields.
- PEP8 cleanup.


### 0.3.0
- Support for Python-3.3.
- Fixed: Add list-sortable.js on changelist only. Issue \#31.


### 0.2.9
- Fixed: StackedInlines do not add an empty field after saving the model.
- Added management command to preset initial ordering.


### 0.2.8
- Refactored documentation for Read-The-Docs


### 0.2.7
- Fixed: MethodType takes only two attributes


### 0.2.6
- Fixed: Unsortable inline models become draggable when there is a sortable inline model


### 0.2.5
- Bulk actions are added only when they make sense.
- Fixed bug when clicking on table header for ordering field.


### 0.2.4
- Fix CustomInlineFormSet to allow customization.


### 0.2.2
- Distinction between different versions of jQuery in case django-cms is installed side by side.

### 0.2.0
- Added sortable stacked and tabular inlines.


### 0.1.2
- Fixed: All field names other than \"order\" are now allowed.


### 0.1.1
- Fixed compatibility issue when used together with django-cms.


### 0.1.0
- First version published on PyPI.


### 0.0.1
- First working release.
