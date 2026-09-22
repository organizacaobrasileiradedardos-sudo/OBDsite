/*
 * Editor visual do conteúdo da notícia, dentro do admin do Django.
 *
 * O campo continua sendo o mesmo `content` de sempre: a caixa de texto original é
 * escondida, o editor aparece no lugar dela, e no momento de salvar o conteúdo
 * formatado é escrito de volta na caixa. Assim nada muda no modelo nem no formulário
 * do Django — se este arquivo deixar de carregar, a caixa de texto simples reaparece e
 * a edição continua possível.
 */
(function () {
    'use strict';

    function iniciarEditor() {
        var caixaOriginal = document.getElementById('id_content');
        if (!caixaOriginal || typeof Quill === 'undefined') {
            return;
        }

        caixaOriginal.style.display = 'none';

        var area = document.createElement('div');
        area.style.minHeight = '320px';
        area.style.backgroundColor = '#fff';
        caixaOriginal.parentNode.insertBefore(area, caixaOriginal);

        var editor = new Quill(area, {
            theme: 'snow',
            placeholder: 'Escreva aqui o conteúdo da notícia…',
            modules: {
                toolbar: [
                    ['bold', 'italic', 'underline'],
                    [{ list: 'ordered' }, { list: 'bullet' }],
                    ['link'],
                    ['clean']
                ]
            }
        });

        // Carrega o que já estava gravado. Para notícias antigas isso é texto puro, e o
        // editor o trata como um parágrafo só — o texto não se perde.
        editor.root.innerHTML = caixaOriginal.value;

        var formulario = caixaOriginal.closest('form');
        if (!formulario) {
            return;
        }

        formulario.addEventListener('submit', function () {
            var html = editor.root.innerHTML;
            // O editor vazio devolve um parágrafo com uma quebra dentro. Gravar isso
            // faria uma notícia sem conteúdo parecer preenchida.
            caixaOriginal.value = (html === '<p><br></p>') ? '' : html;
        });
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', iniciarEditor);
    } else {
        iniciarEditor();
    }
})();
