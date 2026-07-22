# Agenda Médica

Aplicação web simples de agenda médica desenvolvida como desafio técnico. Permite login de um usuário e, após autenticação, exibe os agendamentos médicos em uma tabela com busca por paciente, CPF ou médico.

## Descrição da solução

O projeto é composto por dois serviços Flask:

- **web**: aplicação principal, responsável pelo login, sessão do usuário e pela tela da agenda. Guarda os usuários em um banco SQLite e busca os agendamentos fazendo uma requisição HTTP para o serviço `api`.
- **api**: serviço separado que simula uma API de agendamentos, retornando dados mockados em `/agendamentos`.

O front-end usa apenas HTML e CSS simples, sem frameworks, e a biblioteca [Tabulator](https://tabulator.info/) (carregada via CDN) para exibir a tabela de agendamentos com busca.

## Tecnologias utilizadas

- Python 3 / Flask
- SQLite (via biblioteca padrão `sqlite3`)
- Requests (para comunicação HTTP entre os serviços)
- Tabulator.js (via CDN)
- HTML5 / CSS3
- Docker e Docker Compose
- Pytest (testes automatizados)

## Como executar com Docker

1. Copie o arquivo de variáveis de ambiente de exemplo:

   ```bash
   cp .env.example .env
   ```

2. Suba os serviços:

   ```bash
   docker compose up --build
   ```

3. Acesse a aplicação em [http://localhost:5000](http://localhost:5000).

O banco SQLite é criado e populado automaticamente (usuário de teste incluso) na primeira inicialização do serviço `web`. O serviço `api`, com os dados mockados dos agendamentos, fica disponível em `http://localhost:5001/agendamentos`.

## Credenciais do usuário de teste

- **Usuário/e-mail:** `teste@timesaver.com`
- **Senha:** `teste123`

Esses valores vêm das variáveis de ambiente `TEST_USER_EMAIL` e `TEST_USER_PASSWORD` (ver `.env.example`) e podem ser alterados livremente antes de subir o projeto.

## Exemplos de uso

1. Acesse `http://localhost:5000`, será redirecionado para a tela de login.
2. Informe as credenciais de teste acima e clique em "Entrar".
3. A tela da agenda é exibida com todos os agendamentos disponíveis.
4. Digite um nome de paciente, CPF ou nome de médico no campo de busca (por exemplo, `Maria` ou `Cardiologia` não filtram por especialidade, apenas paciente/CPF/médico) e clique em "Buscar".
5. Se não houver nenhum agendamento correspondente, a tabela exibe a mensagem "Nenhum agendamento encontrado".
6. Clique em "Limpar" para voltar à lista completa.
7. Selecione um ou mais agendamentos pelo checkbox na primeira coluna da tabela e clique no botão de lixeira para excluí-los (uma confirmação é exibida antes da exclusão).
8. Clique em "Novo agendamento" (botão "+") para abrir um formulário em pop-up e cadastrar um novo agendamento.
9. Clique em "Sair" para encerrar a sessão e retornar à tela de login.
10. Ao acessar uma URL inexistente, uma página 404 personalizada é exibida, com um botão para voltar à tela inicial.

## Gerenciamento de agendamentos (criar e excluir)

Além da consulta, a agenda permite:

- **Selecionar e excluir**: cada linha da tabela tem um checkbox; ao selecionar uma ou mais linhas, o botão de lixeira é habilitado. Clicar nele exclui os agendamentos selecionados (após confirmação).
- **Cadastrar**: o botão "+ Novo agendamento" abre um formulário em pop-up (`<dialog>`) com os campos obrigatórios (paciente, CPF, médico, especialidade, data, horário, convênio e status). Ao salvar, o agendamento é criado e a tabela é recarregada.

Essas operações passam pelas rotas `POST /api/agendamentos` e `DELETE /api/agendamentos` do serviço `web`, que fazem proxy para o serviço `api` (`POST`/`DELETE /agendamentos`), validando os campos obrigatórios antes de repassar a chamada.

**Importante:** os agendamentos continuam guardados em uma lista Python em memória no serviço `api` (mesma abordagem dos dados mockados originais), e não em um banco de dados. Isso significa que agendamentos criados ou excluídos pela tela são perdidos se o serviço `api` reiniciar. Só a tabela `users` (login) é persistida em SQLite.

## Página 404 personalizada

Qualquer URL não mapeada pelo Flask exibe uma página de erro 404 customizada (`web/templates/404.html`), com uma mensagem amigável e um botão para voltar à tela inicial, em vez da página de erro padrão do Flask.

## Rodando os testes automatizados

```bash
cd web
pip install -r requirements.txt
pytest tests/ -v
```

Os testes cobrem:

- login com credenciais válidas;
- login com credenciais inválidas;
- busca por um paciente inexistente (retorno vazio);
- indisponibilidade do serviço de agendamentos (API fora do ar).

## Tratamento de erros implementado

- **Credenciais de login inválidas**: mensagem exibida na própria tela de login, sem expor detalhes técnicos.
- **Nenhum agendamento encontrado**: a tabela (Tabulator) mostra a mensagem "Nenhum agendamento encontrado" ao invés de ficar vazia sem explicação.
- **Resposta vazia ou inválida da API**: se o corpo não for uma lista JSON válida, a aplicação retorna uma mensagem amigável ao usuário e registra o erro no log.
- **Indisponibilidade temporária da API**: erros de conexão/timeout ao chamar o serviço `api` são capturados e uma mensagem clara é exibida, sem quebrar a página.
- **Erro de conexão com o banco de dados**: exceções do SQLite durante o login são tratadas e uma mensagem genérica é exibida ao usuário.
- **Campos obrigatórios ausentes na resposta**: registros de agendamento que não possuem todos os campos exigidos (paciente, CPF, médico, especialidade, data, horário, convênio, status) são descartados individualmente e registrados em log, sem interromper a exibição dos demais registros válidos.

Todos esses cenários são registrados via `logging` no console da aplicação (visível com `docker compose logs web`), facilitando a identificação da causa em caso de problema.

## Decisões técnicas e limitações conhecidas

- **SQLite sem container próprio**: por ser um banco de dados embutido em arquivo (não um serviço de rede), o SQLite não precisa de um container dedicado. O arquivo do banco é criado automaticamente pelo serviço `web` em um volume Docker (`agenda_data`), garantindo persistência entre reinicializações.
- **API mockada como serviço separado**: optei por criar a API de agendamentos como um serviço Flask independente (`api/`), para deixar clara a comunicação via requisição HTTP real entre os dois serviços, conforme pedido no desafio.
- **Servidor de desenvolvimento do Flask**: por simplicidade, os dois serviços rodam com o servidor embutido do Flask (`app.run`). Em um cenário de produção real, o recomendado seria usar um servidor WSGI como Gunicorn.
- **Sem cadastro de novos usuários**: o escopo do desafio é login e consulta da agenda, então não há tela de cadastro; o usuário de teste é criado automaticamente por um script de seed (`web/seed.py`).
- **Busca simples**: a busca filtra por correspondência parcial (case-insensitive) nos campos paciente, CPF e médico, feita no lado do servidor após buscar os dados da API.
- **Criação/exclusão de agendamentos em memória**: assim como os dados mockados originais, os agendamentos criados ou excluídos pela tela não são persistidos em banco — ficam em uma lista Python no serviço `api`. Optei por manter a mesma simplicidade do restante do projeto; para persistir entre reinicializações, o próximo passo seria criar uma tabela `agendamentos` no SQLite já usado para `users`.
- **Página 404 customizada**: registrada via `@app.errorhandler(404)` no serviço `web`, cobre automaticamente qualquer URL não mapeada, sem precisar de uma rota "catch-all" manual.
