#!/usr/bin/env python
"""Guia para iniciantes: os comandos ``migrate`` e ``runserver`` neste projeto.

Este arquivo, ``manage.py``, e o ponto de entrada dos comandos administrativos
do Django. Ele e executado a partir da pasta principal do projeto, por exemplo:

    python manage.py runserver

Leia o comando por partes:
* ``python`` inicia o interpretador Python (de preferencia o de ``.venv``).
* ``manage.py`` e este arquivo, que prepara o projeto para receber um comando.
* ``runserver`` pede ao Django para iniciar o servidor local de desenvolvimento.

CAMINHO DE ``python manage.py runserver`` ATE A PAGINA NO NAVEGADOR

1. O terminal inicia Python e Python executa este arquivo. Como ele foi
   executado diretamente, ``__name__`` vale ``'__main__'``. Por isso, o bloco
   no final chama ``main()``.
2. ``main()`` define ``DJANGO_SETTINGS_MODULE`` como ``jb_sistema.settings``.
   Essa variavel diz ao Django qual arquivo contem as configuracoes do projeto.
3. ``main()`` importa ``execute_from_command_line`` e passa ``sys.argv``. Essa
   lista contem os argumentos do terminal, neste caso o nome deste arquivo e
   ``runserver``. O Django identifica e executa o comando correspondente.
4. O comando de desenvolvimento verifica as configuracoes e inicia um servidor
   HTTP local. Sem endereco informado, ele usa normalmente
   ``http://127.0.0.1:8000/``. Esse servidor serve para desenvolvimento e nao
   substitui um servidor apropriado para producao.
5. A configuracao ``WSGI_APPLICATION`` em ``jb_sistema/settings.py`` aponta
   para ``jb_sistema.wsgi.application``. O arquivo ``jb_sistema/wsgi.py``
   chama ``get_wsgi_application()`` para criar a aplicacao que recebe pedidos
   HTTP e os encaminha ao Django. WSGI e a convencao que conecta o servidor
   Python a uma aplicacao web.
6. Ao abrir o endereco no navegador, o navegador envia um pedido HTTP. Por
   exemplo, ``http://127.0.0.1:8000/`` pede o caminho ``/``. O servidor entrega
   esse pedido a aplicacao WSGI; o Django prepara o objeto ``request`` e passa
   o pedido pela lista ``MIDDLEWARE`` configurada em ``settings.py``. Middlewares
   sao etapas compartilhadas que podem tratar seguranca, sessao e outras partes
   de cada pedido.
7. O Django le ``ROOT_URLCONF``, tambem em ``settings.py``. Neste projeto, ele
   vale ``jb_sistema.urls``. O Django procura em ``jb_sistema/urls.py`` uma rota
   que combine com o caminho pedido. Para ``/``, encontra
   ``path('', autenticacao_views.tela_login, name='login')``.
8. A rota chama a funcao ``tela_login`` em
   ``inventario/views/autenticacao_views.py`` e entrega a ela o ``request``.
   Uma view e uma funcao que decide o que responder a um pedido. Essa view
   verifica se existe um usuario na sessao: se existir, redireciona ao painel;
   se nao, prepara a pagina de login.
9. Para mostrar o login, a view chama
   ``render(request, 'inventario/login.html')``. Como ``APP_DIRS`` esta
   habilitado em ``settings.py``, o Django procura o template dentro dos
   aplicativos e encontra ``inventario/templates/inventario/login.html``.
10. O Django transforma o template em uma resposta HTTP (normalmente status
    ``200`` para a pagina) e a devolve pelo servidor ao navegador. O navegador
    entao apresenta o HTML e pode solicitar separadamente arquivos CSS, imagens
    ou outros recursos usados pela pagina.

Esse fluxo muda conforme o endereco. Por exemplo, ``/admin/`` combina com a
rota do admin em ``jb_sistema/urls.py``; ``/painel/`` combina com a funcao
``painel_principal``. O arquivo de URLs mapeia caminhos para views.

IMPORTANTE: ``runserver`` inicia o servidor, mas nao prepara a estrutura do
banco. Para aplicar ao banco as migracoes que ainda faltam, rode antes:

    python manage.py migrate

Uma migracao e como uma receita/versionamento da estrutura do banco: pode criar
uma tabela, adicionar ou alterar uma coluna, entre outras operacoes. O comando
``migrate`` nao cria arquivos de migracao. Depois de alterar os modelos, use
``python manage.py makemigrations`` para criar os arquivos e
``python manage.py migrate`` para aplica-los. Neste projeto, as migracoes do
aplicativo estao em ``inventario/migrations/`` e o SQLite esta configurado em
``jb_sistema/settings.py`` para ``dados/jb_tintas.db``.

O Django registra migracoes aplicadas em ``django_migrations`` e nao repete as
que ja foram concluidas. Antes de migrar um banco com dados importantes, faca
uma copia: dependendo das operacoes definidas, uma migracao pode alterar ou
remover dados.

CAMINHO DE ``python manage.py test inventario.tests``

Esse comando executa os testes automatizados do projeto. Um teste automatizado
e um pequeno programa que verifica se uma parte do sistema produz o resultado
esperado. Leia o comando por partes:

* ``python`` inicia o interpretador Python escolhido no terminal. Se o ambiente
  virtual ``.venv`` estiver ativado, sera usado o Python desse ambiente.
* ``manage.py`` e o ponto de entrada dos comandos administrativos do Django.
* ``test`` pede ao Django para encontrar e executar testes.
* ``inventario.tests`` diz onde procurar: e o pacote de testes do aplicativo
  ``inventario``, que corresponde a pasta ``inventario/tests/``.

O caminho percorrido e:
1. Python executa este arquivo e o bloco ``if __name__ == '__main__'`` chama
   ``main()``.
2. ``main()`` seleciona ``jb_sistema.settings`` e entrega ``sys.argv`` ao
   ``execute_from_command_line`` do Django. A lista de argumentos, neste caso,
   inclui ``manage.py``, ``test`` e ``inventario.tests``.
3. O Django reconhece ``test`` como seu comando de testes, carrega as
   configuracoes do projeto e procura modulos de teste dentro de
   ``inventario.tests``. Por convencao, os arquivos se chamam ``test_*.py`` e
   os metodos de teste comecam com ``test_``.
4. Neste projeto, os arquivos encontrados incluem ``test_vendas_services.py``,
   ``test_pontos_services.py``, ``test_xml_services.py`` e
   ``test_dashboard_services.py``. Eles verificam regras como calculo de
   pontos e comissoes, vendas e cancelamentos, processamento de XML e metricas
   do painel. Cada classe herda de ``django.test.TestCase``, que oferece
   preparacao e isolamento para testes que usam o Django e o banco.
5. Antes dos testes, o Django cria um banco de dados temporario de teste e
   prepara nele as tabelas necessarias, inclusive aplicando as migracoes. Os
   testes podem criar dados de exemplo sem gravar no banco normal configurado
   em ``dados/jb_tintas.db``. O Django limpa ou recria os dados de teste entre
   os casos e remove o banco temporario ao terminar.
6. O Django executa cada metodo ``test_...``. As verificacoes, como
   ``self.assertEqual(valor_obtido, valor_esperado)``, comparam o resultado do
   programa com o resultado esperado. Se os valores forem diferentes ou ocorrer
   um erro, o teste aparece como falho; se todos passarem, o resultado final
   informa ``OK``.
7. Ao final, o Django encerra o banco temporario e mostra quantos testes foram
   executados e se passaram. O comando testa o comportamento coberto pelos
   testes, mas nao prova sozinho que todas as telas ou situacoes possiveis estao
   corretas.

Um ponto (``.``) impresso no terminal normalmente representa um teste que
passou; ``F`` indica uma verificacao que falhou e ``E`` indica um erro durante
a execucao. Quando houver falha, leia o resumo e o traceback exibidos depois
dos simbolos para encontrar o arquivo, o teste e a linha que precisam de
investigacao.

Para executar todos os testes descobertos pelo Django, pode-se usar
``python manage.py test`` sem informar ``inventario.tests``. Para rodar apenas
um arquivo ou uma classe, o comando aceita um caminho mais especifico, por
exemplo ``python manage.py test inventario.tests.test_vendas_services``.
"""

import os
import sys

def main():
    """Prepara o Django e encaminha os argumentos do terminal ao comando pedido."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'jb_sistema.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError:
        raise ImportError("Erro ao importar o Django.")
    execute_from_command_line(sys.argv)

if __name__ == '__main__':
    main()