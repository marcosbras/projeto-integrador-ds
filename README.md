# Gestao-de-Inventario-para-pequenos-varejistas
Desenvolvimento de um Sistema Web de Gestão de Inventário e Fidelização de Clientes para o Pequeno Varejo de Tintas

## Preparar e executar o projeto

Este projeto é uma aplicação Django. Não há uma etapa de compilação que gere um executável; para preparar os arquivos estáticos para publicação, use o comando `collectstatic` descrito abaixo.

### Requisitos

- Python 3.10 ou superior
- PowerShell no Windows (ou terminal equivalente)

### Instalação local

Abra o PowerShell na pasta raiz do projeto e crie o ambiente virtual:

```powershell
py -m venv .venv
```

Ative o ambiente e instale as dependências:

```powershell
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Com o ambiente ativo, o prompt do PowerShell começa com `(.venv)`. Se a ativação for bloqueada por uma política de execução de scripts, permita scripts locais para o seu usuário:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

Confirme a alteração quando solicitado e execute novamente `.\.venv\Scripts\Activate.ps1`. Essa configuração vale para o usuário atual do Windows. Como alternativa, use `.\.venv\Scripts\python.exe` para executar o Python do ambiente sem ativá-lo.

### Migrações e execução

O comando `migrate` aplica ao banco as migrações que ainda não foram executadas.
Migrações são arquivos Python que descrevem mudanças na estrutura do banco, como
criar tabelas ou adicionar e alterar colunas. Neste projeto, elas ficam em
`inventario/migrations/`: `0001_initial.py` cria as tabelas iniciais e `0002`,
`0003` e `0004` registram mudanças posteriores. O Django segue as dependências
entre esses arquivos e registra os que já aplicou na tabela `django_migrations`.

No comando `python manage.py migrate`, `python` inicia o interpretador,
`manage.py` carrega as configurações de `jb_sistema/settings.py` e encaminha
`migrate` ao Django. O banco atualizado é o arquivo SQLite configurado em
`dados/jb_tintas.db`. O comando não cria arquivos de migração: depois de alterar
os modelos, use `python manage.py makemigrations` para criá-los e, em seguida,
`python manage.py migrate` para aplicá-los.

Para preparar o banco e iniciar o servidor de desenvolvimento:

```powershell
python manage.py migrate
python manage.py runserver
```

A aplicação estará disponível em <http://127.0.0.1:8000/>.

Faça uma cópia do banco antes de aplicar migrações se precisar preservar os
dados existentes: uma migração pode alterar ou remover dados conforme as
operações definidas.

Para encerrar o servidor, pressione `Ctrl+C`. Para sair do ambiente virtual, execute:

```powershell
deactivate
```

### Preparar arquivos estáticos

Para reunir os arquivos estáticos do projeto e do Django na pasta `staticfiles`, execute:

```powershell
python manage.py collectstatic --noinput
```

Essa etapa é normalmente usada no processo de publicação. O servidor de desenvolvimento (`runserver`) não substitui a configuração de um servidor de produção.

### Executar os testes automatizados

Com o ambiente virtual ativo, execute os testes de regras de negócio:

```powershell
python manage.py test inventario.tests
```

Nesse comando, `manage.py` encaminha a solicitação ao Django, `test` inicia o
executor de testes e `inventario.tests` indica a pasta do aplicativo onde os
testes são procurados. O Django descobre os arquivos `test_*.py` e executa os
métodos com nomes iniciados por `test_`. Os testes atuais verificam regras de
vendas, pontos, processamento de XML e métricas do painel.

O executor do Django prepara um banco de dados temporário, aplica nele as
migrações e remove esse banco ao terminar. Assim, os testes não alteram o banco
local em `dados/jb_tintas.db`. `OK` significa que os testes encontrados
passaram; `F` indica uma falha de verificação e `E`, um erro durante a execução.
Os testes cobrem os cenários programados, não todas as situações possíveis.

Antes de publicar em produção, configure pelo menos `DEBUG=False`, uma `SECRET_KEY` segura carregada de variável de ambiente e os domínios em `ALLOWED_HOSTS`. Os valores atuais de desenvolvimento em `jb_sistema/settings.py` não devem ser usados como configuração de produção.
