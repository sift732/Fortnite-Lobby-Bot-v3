
function saveVisual(reload = false) {
    const form = document.getElementById('visual_form');
    const formData = new FormData(form);
    const request = new XMLHttpRequest();
    if (reload) {
        request.open('POST', location.pathname + '/save?reload=true');
    } else {
        request.open('POST', location.pathname + '/save');
    }
    request.send(formData);
    request.onload = function (ev) {
        const data = JSON.parse(request.responseText);
        console.log(data);
        const res = document.getElementById('res');
        res.style.color = data.color;
        res.style.transform = 'translateX(-50%) translateY(0%)';
        res.innerText = data.text;

        res.ontransitionend = function () {
            setTimeout(function () {
                res.style.transform = 'translateX(-50%) translateY(-200px)';
            }, 1500);
        }

        editor.setValue(JSON.stringify(data.data, null, 4));

        for (let [key, value] of Object.entries(data.flat_data)) {
            const valueElement = document.getElementById(key);
            if (valueElement) {
                if (valueElement.tagName == 'INPUT' || valueElement.tagName == 'TEXTAREA') {
                    valueElement.value = value;
                } else {
                    Array.from(valueElement.children).forEach(select => {
                        if (value === null) {
                            if (select.value == 'null') {
                                select.selected = true;
                            }
                        } else if (typeof(value) === Boolean) {
                            if (select.value == value.toString()) {
                                select.selected = true;
                            }
                        } else {
                            if (select.value == value) {
                                select.selected = true;
                            }
                        }
                    });
                }
                valueElement.style.color = null;

                const label = valueElement.previousElementSibling;
                if (label) {
                    label.style.color = null;
                }

                if (key.indexOf("['clients']") != -1) {
                    const h1 = valueElement.parentElement.parentElement.firstElementChild;
                    if (h1) {
                        h1.style.color = null;
                    }

                    const client = h1.parentElement.parentElement.firstElementChild;
                    if (client) {
                        client.style.color = null;
                    }
                }
            }
        }

        if (data.errors.length > 0) {
            const shake = document.getElementById('shake');
            shake.style.animation = 'shake 400ms';
            setTimeout(function () {
                shake.style.animation = '';
            }, 400);
        }
        for (let key of data.errors) {
            const valueElement = document.getElementById(key);
            if (valueElement) {
                valueElement.style.backgroundColor = '#F04747';
                valueElement.ontransitionend = function() {
                    setTimeout(function () {
                        if (valueElement) {
                            valueElement.style.backgroundColor = '';
                        }
                    }, 700);
                }
            }
            const label = valueElement.previousElementSibling;
            if (label) {
                label.style.color = '#F04747';
            }

            if (key.indexOf("['clients']") != -1) {
                const h1 = valueElement.parentElement.parentElement.firstElementChild;
                if (h1) {
                    h1.style.color = '#F04747';
                }

                const client = h1.parentElement.parentElement.firstElementChild;
                if (client) {
                    client.style.color = '#F04747';
                }
            }
        }
    }
}

function replaceAttr(element, attr, before, after) {
    element.setAttribute(attr, element.getAttribute(attr).replace(before, after));
}

function fixId(items, id_before, id_after) {
    items.forEach(item => {
        if (item.classList.contains('editor_h')) {
            Array.from(item.children).forEach(child => {
                if (child.tagName == 'DIV') {
                    const item_items = Array.from(child.lastElementChild.children).filter(
                        child => child.tagName == 'DIV'
                    );
                    fixId(item_items, id_before, id_after);

                    child.classList.remove('open');
                    child.firstElementChild.onclick = function () {
                        child.classList.toggle('open');
                    }
                }
            })
        } else {
            let label, input;
            [label, input] = item.children;
            if (input !== undefined) {
                if (input.classList.contains('value')) {
                    replaceAttr(label, 'for', id_before, id_after);
                    replaceAttr(input, 'id', id_before, id_after);
                    replaceAttr(input, 'name', id_before, id_after);
                } else {
                    const button = Array.from(input.children).slice(-1)[0];
                    button.onclick = function () {
                        addListList(button, button.getAttribute('key').replace(id_before, id_after));
                    }
                    replaceAttr(button, 'key', id_before, id_after);

                    Array.from(input.children).forEach(item_child => {
                        if (item_child.tagName == 'DIV') {
                            replaceAttr(label, 'for', id_before, id_after);
                            const textarea = item_child.firstElementChild;
                            replaceAttr(textarea, 'id', id_before, id_after);
                            replaceAttr(textarea, 'name', id_before, id_after);
                        }
                    });
                }
            }
        }
    });
}

function removeListList(element) {
    element.parentNode.parentNode.removeChild(element.parentNode.nextElementSibling);
    element.parentNode.parentNode.removeChild(element.parentNode);
}

function addListList(element, key) {
    const parent = element.parentNode;
    const div = document.createElement('div');
    let num = 0;
    Array.from(element.parentNode.children).forEach(child => {
        if (child.tagName == 'DIV') {
            num += 1;
        }
    });
    const textarea = document.createElement('textarea');
    textarea.id = key + `[${num}]`;
    textarea.className = 'value';
    textarea.setAttribute('name', key + `[${num}]`);
    div.appendChild(textarea);

    const input = document.createElement('input');
    input.className = 'remove_button';
    input.type = 'button';
    input.value = texts.remove;
    input.onclick = function () {
        removeListList(input);
    }
    div.appendChild(input);

    parent.insertBefore(div, element);
}

function removeElement(element, prefix) {
    const id_prefix = element.parentElement.parentElement.getAttribute('id');
    const element_num = parseInt(element.parentElement.getAttribute('num'));
    const parent = element.parentElement.parentElement;
    const element_count = Array.from(parent.children).filter(
        child => child.tagName == 'DIV'
    ).length;
    element.parentElement.previousElementSibling.remove();
    element.parentElement.nextElementSibling.remove();
    element.parentElement.remove();
    if (element_count != element_num) {
        let current_num = 0;
        Array.from(parent.children).forEach(child => {
            if (child.tagName == 'DIV') {
                if (element_count >= current_num) {
                    const num = parseInt(child.getAttribute('num'));
                    child.id = `${id_prefix}_${current_num}`;
                    const id_before = `${prefix}[${num}]`;
                    const id_after = `${prefix}[${current_num}]`;
                    replaceAttr(child, 'num', num.toString(), current_num.toString());
                    replaceAttr(child.previousElementSibling, 'name', id_before, id_after);

                    const request = new XMLHttpRequest();
                    request.open('POST', '/l');
                    request.setRequestHeader('Content-Type', 'application/json');
                    request.send(JSON.stringify({
                        text: id_prefix.slice(0, -1),
                        args: [current_num + 1],
                        kwargs: {}
                    }));
                    request.onload = function () {
                        child.children[0].textContent = request.responseText;
                    }

                    const items = Array.from(child.children[child.children.length - 1].children).filter(
                        child => child.tagName == 'DIV'
                    );
                    fixId(items, id_before, id_after);
                }
                current_num += 1
            }
        });
    }
}

function addElement(element, prefix) {
    const id_prefix = element.parentElement.getAttribute('id');
    const parent = element.parentElement;
    let copyElement = null;
    Array.from(parent.childNodes).forEach(child => {
        if (child.tagName == 'DIV') {
            copyElement = child;
        }
    });
    if (copyElement === null) {
        const request = new XMLHttpRequest();
        if (id_prefix == 'ng_names' || id_prefix == 'ng_words') {
            request.open('POST', `${location.pathname}/add-${id_prefix.replace('_', '-').slice(0, -1)}/` + element.parentNode.getAttribute('client_num'));
        } else {
            request.open('POST', `${location.pathname}/add-${id_prefix.replace('_', '-').slice(0, -1)}`);
        }
        request.send(null);
        request.onload = function () {
            console.log(request.responseText);
            if (request.status == 204) {
                window.location.reload();
            }
        }
    } else {
        const newElement = copyElement.cloneNode(true);
        const num = parseInt(newElement.getAttribute('num'));
        newElement.setAttribute('id', `${id_prefix}_${num + 1}`);
        newElement.setAttribute('num', `${num + 1}`);
        const id_before = `${prefix}[${num}]`;
        const id_after = `${prefix}[${num + 1}]`;

        const request = new XMLHttpRequest();
        request.open('POST', '/l');
        request.setRequestHeader('Content-Type', 'application/json');
        request.send(JSON.stringify({
            text: id_prefix.slice(0, -1),
            args: [num + 2],
            kwargs: {}
        }));
        request.onload = function () {
            newElement.firstElementChild.textContent = request.responseText;
        }

        newElement.firstElementChild.onclick = function () {
            newElement.classList.toggle('open');
        }

        const items = Array.from(newElement.lastElementChild.children).filter(
            child => child.tagName == 'DIV'
        );
        items.forEach(item => {
            let label, input;
            [label, input] = item.children;
            if (input !== undefined) {
                if (input.tagName == 'DIV') {
                    while (input.firstChild && (input.firstChild.tagName != 'INPUT' || input.firstChild.getAttribute('type') != 'button')) {
                        input.removeChild(input.firstChild);
                    }
                } else {
                    replaceAttr(label, 'for', id_before, id_after);
                    replaceAttr(input, 'id', id_before, id_after);
                    replaceAttr(input, 'name', id_before, id_after);
                    if (input.tagName == 'INPUT' || input.tagName == 'TEXTAREA') {
                        input.value = '';
                    } else {
                        Array.from(input.children).forEach(select => {
                            select.selected = false;
                        });
                    }
                }
            }
        });
        const input = document.createElement('input');
        input.setAttribute('type', 'hidden');
        input.setAttribute('name', `${prefix}[${num + 1}]`)
        parent.insertBefore(input, element);
        parent.insertBefore(newElement, element);
        parent.insertBefore(document.createElement('br'), element);
    }
}

var copied_element;
function copy(element) {
    copied_element = element.parentElement;
}

function paste(element, prefix) {
    const id_prefix = element.parentElement.parentElement.getAttribute('id');
    if (copied_element) {
        const parent = element.parentElement.parentElement;
        const next_element = element.parentElement.nextElementSibling.nextElementSibling;
        const element_num = parseInt(element.parentElement.getAttribute('num'));
        const copied_element_num = parseInt(copied_element.getAttribute('num'));
        const element_open = element.parentElement.classList.contains('open');
        const copied_element_open = copied_element.classList.contains('open');
        parent.removeChild(element.parentElement.nextElementSibling);
        parent.removeChild(element.parentElement);

        const child = copied_element.cloneNode(true);
        child.id = `${id_prefix}_${element_num}`;
        const id_before = `${prefix}[${copied_element_num}]`
        const id_after = `${prefix}[${element_num}]`

        const request = new XMLHttpRequest();
        request.open('POST', '/l');
        request.setRequestHeader('Content-Type', 'application/json');
        request.send(JSON.stringify({
            text: id_prefix.slice(0, -1),
            args: [element_num + 1],
            kwargs: {}
        }));
        request.onload = function () {
            child.firstElementChild.textContent = request.responseText;
        }

        child.firstElementChild.onclick = function () {
            child.classList.toggle('open');
        }

        const items = Array.from(child.lastElementChild.children).filter(
            child => child.tagName == 'DIV'
        );
        fixId(items, id_before, id_after);

        if (element_open && !copied_element_open) {
            child.classList.add('open');
        }

        parent.insertBefore(child, next_element);
        parent.insertBefore(document.createElement('br'), next_element);
    }
}

function applyToAll(element, prefix_keys, keys) {
    element = element.previousElementSibling;
    let elements = document.getElementsByClassName('apply_to_all_button');
    if (element.tagName == 'DIV' && element.classList.contains('list_list')) {
        elements = Array.from(elements).filter(e => (
            e.previousElementSibling && e.previousElementSibling.id
            && e.previousElementSibling.id == element.id
            && e.previousElementSibling.tagName == element.tagName
            && e.previousElementSibling != element
        ));
    } else {
        elements = Array.from(elements).filter(e => (
            e.previousElementSibling && e.previousElementSibling.id
            && e.previousElementSibling.id.startsWith(prefix_keys)
            && e.previousElementSibling.id.endsWith(keys)
            && e.previousElementSibling.tagName == element.tagName
            && e.previousElementSibling != element
        ));
    }
    Array.from(elements).forEach(e => {
        const valueElement = e.previousElementSibling;
        if (element.tagName == 'INPUT' || element.tagName == 'TEXTAREA') {
            valueElement.value = element.value;
        } else if (element.tagName == 'DIV' && element.classList.contains('list_list')) {
            const clientNum = parseInt(element.parentElement.parentElement.parentElement.getAttribute('num'));
            const valueClientNum = parseInt(valueElement.parentElement.parentElement.parentElement.getAttribute('num'));
            const id_before = `${prefix_keys}[${clientNum}]`;
            const id_after = `${prefix_keys}[${valueClientNum}]`;
            const newElement = element.cloneNode(true);
            const parent = valueElement.parentElement;
            parent.removeChild(valueElement);
            parent.insertBefore(newElement, e);
            Array.from(newElement.children).forEach(child => {
                if (child.tagName == 'DIV') {
                    replaceAttr(child.firstElementChild, 'id', id_before, id_after);
                    replaceAttr(child.firstElementChild, 'name', id_before, id_after);
                } else {
                    child.onclick = function () {
                        addListList(child, child.getAttribute('key').replace(id_before, id_after));
                    }
                }
            });
        } else {
            for (let i = 0; i < valueElement.children.length; i++) {
                const select = element.children[i];
                const valueSelect = valueElement.children[i];
                valueSelect.selected = select.selected;
            }
        }
    });
}

function OpenReadme(lang, name, key) {
    if (key == 'fortniteparty') {
        key = 'party';
    } else if (key == 'fortniteng_names') {
        key = 'ng_names';
    } else if (key == 'fortniteexec') {
        key = 'exec';
    } else if (name == 'ボット' || name == 'Bots') {
        if (lang == 'ja') {
            name = 'クライアント';
        } else if (lang == 'es') {
            name = 'clientes';
        } else {
            name = 'clients';
        }
    }

    if (location.pathname == '/config-editor') {
        filename = 'config';
    } else if (location.pathname == '/commands-editor') {
        filename = 'commands';
    } else if (location.pathname == '/custom-commands-editor') {
        filename = 'custom_commands';
    } else if (location.pathname == '/replies-editor') {
        filename = 'replies';
    } else {
        filename = 'config';
    }

    open('/docs/' + lang + '/' + filename + '.md', 'readme');
    setTimeout(function() {
        open('/docs/' + lang + '/' + filename + '.md#' + name + '-' + key, 'readme');
    }, 150);
}
