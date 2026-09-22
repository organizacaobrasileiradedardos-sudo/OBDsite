const { prepararParaOEditor } = require('../obd/core/static/core/admin_noticia_editor.js');

function conferir(rotulo, entrada, esperado) {
    const obtido = prepararParaOEditor(entrada);
    const ok = obtido === esperado;
    console.log(`  ${ok ? 'ok  ' : 'FALHOU'} ${rotulo}`);
    if (!ok) { console.log('        esperado:', JSON.stringify(esperado)); console.log('        obtido  :', JSON.stringify(obtido)); }
    return ok;
}

let falhas = 0;

console.log('### texto puro de notícia antiga — o caso que quebrou');
falhas += !conferir('dois parágrafos separados por linha em branco',
    'Primeiro parágrafo.\n\nSegundo parágrafo.',
    '<p>Primeiro parágrafo.</p><p>Segundo parágrafo.</p>');
falhas += !conferir('quebra simples vira <br> dentro do mesmo parágrafo',
    'Linha um\nLinha dois',
    '<p>Linha um<br>Linha dois</p>');
falhas += !conferir('quebras do Windows (\\r\\n)',
    'Um\r\n\r\nDois',
    '<p>Um</p><p>Dois</p>');
falhas += !conferir('linha em branco com espaços no meio',
    'Um\n   \nDois',
    '<p>Um</p><p>Dois</p>');

console.log('\n### texto puro com sinais que não podem virar etiqueta');
falhas += !conferir('menor, maior e e-comercial são escapados',
    'Média > 60 & < 70',
    '<p>Média &gt; 60 &amp; &lt; 70</p>');

console.log('\n### conteúdo que já veio do editor — não pode ser mexido');
falhas += !conferir('HTML passa intacto',
    '<p>Com <strong>negrito</strong>.</p><p>Outro.</p>',
    '<p>Com <strong>negrito</strong>.</p><p>Outro.</p>');

console.log('\n### vazio');
falhas += !conferir('string vazia', '', '');
falhas += !conferir('só espaços', '   \n  ', '');

console.log('\nRESULTADO:', falhas === 0 ? 'todos os casos passaram' : `${falhas} falha(s)`);
process.exit(falhas === 0 ? 0 : 1);
