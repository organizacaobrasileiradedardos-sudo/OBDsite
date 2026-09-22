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

    var MARCAS_DE_HTML = /<(p|br|ul|ol|li|strong|b|em|i|u|a|h[1-6])\b/i;

    function escapar(texto) {
        return texto
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;');
    }

    /*
     * Prepara o conteúdo gravado para entrar no editor.
     *
     * Notícias escritas antes do editor existir são texto puro, com quebras de linha.
     * Jogar esse texto direto no editor destrói os parágrafos, porque o HTML colapsa
     * quebras de linha em espaços — a notícia inteira vira um bloco único, e é isso que
     * fica gravado no próximo salvamento. Por isso o texto puro é convertido em
     * parágrafos antes: linha em branco separa parágrafo, quebra simples vira <br>.
     */
    function prepararParaOEditor(valor) {
        valor = (valor || '').trim();
        if (!valor) {
            return '';
        }
        if (MARCAS_DE_HTML.test(valor)) {
            return valor;   // já veio do editor
        }
        return valor
            .split(/\r?\n[ \t]*\r?\n/)
            .map(function (paragrafo) {
                return '<p>' + escapar(paragrafo).replace(/\r?\n/g, '<br>') + '</p>';
            })
            .join('');
    }

    // Exposto para o teste automatizado poder exercitar a conversão sem um navegador.
    if (typeof module !== 'undefined' && module.exports) {
        module.exports = { prepararParaOEditor: prepararParaOEditor };
    }

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

        editor.root.innerHTML = prepararParaOEditor(caixaOriginal.value);

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

    if (typeof document !== 'undefined') {
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', iniciarEditor);
        } else {
            iniciarEditor();
        }
    }
})();
