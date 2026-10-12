(() => {
  'use strict';

  const CHOICE_FIELD_TYPES = new Set([
    'SingleChoice',
    'MultipleChoice',
  ]);

  const updateOptionsVisibility = (select) => {
    if (!select) {
      return;
    }

    const fieldGroup = select.closest(
      'sdoc-form-field-group[data-custom-field="true"]'
    );

    if (!fieldGroup) {
      return;
    }

    const optionsContainer = fieldGroup.querySelector(
      '[data-custom-field-options]'
    );

    if (!optionsContainer) {
      return;
    }

    const isChoiceField = CHOICE_FIELD_TYPES.has(select.value);

    optionsContainer.hidden = !isChoiceField;
  };


  /*
   * Initial state
   *
   * This is important when the page is loaded with an existing
   * SingleChoice or MultipleChoice field.
   */
  const initialize = () => {
    document
      .querySelectorAll(
        'sdoc-form-field-group[data-custom-field="true"] [data-custom-field-type]'
      )
      .forEach(updateOptionsVisibility);
  };


  /*
   * Event delegation
   *
   * This also works for custom fields that are added dynamically
   * after the page has already loaded.
   */
  document.addEventListener('change', (event) => {
    const select = event.target.closest(
      'sdoc-form-field-group[data-custom-field="true"] [data-custom-field-type]'
    );

    if (!select) {
      return;
    }

    updateOptionsVisibility(select);
  });


  /*
   * Initialize existing fields.
   */
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initialize);
  } else {
    initialize();
  }
})();