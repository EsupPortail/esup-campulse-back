document.addEventListener('DOMContentLoaded', function () {
    const checkbox = document.querySelector('#id_use_json_import');
    if (!checkbox) return;

    const jsonFileRow = document.querySelector('.field-json_file');
    const allRows = document.querySelectorAll('.form-row');

    function toggleForm() {
        const isChecked = checkbox.checked;

        allRows.forEach(row => {
            const hasError = row.classList.contains('errors') || row.querySelector('.errorlist');

            if (!row.classList.contains('field-use_json_import') && !row.classList.contains('field-json_file')) {
                if (isChecked && !hasError) {
                    row.style.display = 'none';
                } else {
                    row.style.display = '';
                }
            }
        });

        if (jsonFileRow) {
            jsonFileRow.style.display = isChecked ? '' : 'none';
        }
    }

    checkbox.addEventListener('change', toggleForm);
    toggleForm();
});