(() => {
    const data = JSON.parse(document.getElementById('{{ data_id|safe|escapejs }}').textContent);
    editor.registerEditor('{{ editor_id|safe|escapejs }}', '{{ hidden_field_id|safe|escapejs }}', data);
})();
