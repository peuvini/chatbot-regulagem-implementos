# Chatbot de Regulagem de Implementos Agrícolas

Projeto fullstack para pesquisa aplicada em regulagem de arados, grades e tratores, com validação progressiva, banco PostgreSQL, API FastAPI, frontend React/TypeScript/Tailwind e modelo de machine learning.

## Tecnologias

- Backend: Python, FastAPI, SQLAlchemy, PostgreSQL
- Frontend: React, TypeScript, Tailwind CSS, Vite
- Dados: planilhas `ocr/anuario.xlsx`, `ocr/extracao_arados.xlsx`, `ocr/extracao_grades.xlsx`
- Machine learning: regressão Ridge implementada com `numpy`, treinada sobre os parâmetros técnicos dos implementos

## Estrutura

```text
app/
  backend/
    app/
      core/
      modules/
        implements/
          controller.py
          service.py
          schemas.py
          repository.py
          models.py
        tractors/
        recommendations/
        chat/
        ml/
      scripts/
        load_data.py
        train_model.py
  frontend/
    src/
      components/
      services/
      types/
docs/
  ARQUITETURA_E_TREINAMENTO_ML.md
  GUIA_USO_PLATAFORMA.md
ocr/
  anuario.xlsx
  extracao_arados.xlsx
  extracao_grades.xlsx
```

## 1. Subir PostgreSQL

### Opção recomendada neste Mac: Homebrew

No Mac usado no desenvolvimento, o Docker não estava com o daemon ativo (`/var/run/docker.sock` não existia). Por isso, a forma que funcionou foi subir o PostgreSQL diretamente pelo Homebrew:

```bash
brew install postgresql@16
brew services start postgresql@16
/opt/homebrew/opt/postgresql@16/bin/createdb regulagem_implementos
```

Crie o arquivo de ambiente:

```bash
cd /Users/pedro/Documents/pesquisa-welington/chatbot-regulagem-implementos
cp app/backend/.env.example app/backend/.env
```

Para PostgreSQL via Homebrew, deixe o `DATABASE_URL` assim em `app/backend/.env`:

```text
DATABASE_URL=postgresql+psycopg://pedro@localhost:5432/regulagem_implementos
ENVIRONMENT=development
```

Se o banco já existir, o comando `createdb` pode avisar que ele já foi criado; nesse caso basta seguir para a próxima etapa.

### Opção alternativa: Docker

Se seu Docker tiver o plugin Compose v2:

```bash
cd /Users/pedro/Documents/pesquisa-welington/chatbot-regulagem-implementos
docker compose up -d
```

Se aparecer erro como `unknown shorthand flag: 'd' in -d` ou `unknown command: docker compose`, use o Docker básico com `docker run`:

```bash
docker run --name regulagem-implementos-postgres \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=regulagem_implementos \
  -p 5432:5432 \
  -v regulagem_implementos_pgdata:/var/lib/postgresql/data \
  -d postgres:16
```

Para conferir se o container subiu:

```bash
docker ps
```

Se o container já existir e estiver parado:

```bash
docker start regulagem-implementos-postgres
```

O banco padrão usando Docker será:

```text
postgresql+psycopg://postgres:postgres@localhost:5432/regulagem_implementos
```

## 2. Criar e ativar a venv

Use Python 3.11 ou superior. O projeto usa tipagem moderna e foi organizado para rodar bem com Python 3.12.

```bash
cd /Users/pedro/Documents/pesquisa-welington/chatbot-regulagem-implementos
/opt/homebrew/bin/python3.12 -m venv .venv
source .venv/bin/activate
```

Se o comando `python3` da sua máquina já apontar para Python 3.11+, você pode usar `python3 -m venv .venv`. No Mac atual, prefira `/opt/homebrew/bin/python3.12` para evitar criar a venv com Python 3.9.

## 3. Instalar dependências do backend

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

As dependências antigas de OCR ficaram separadas em `requirements-ocr.txt`. Para rodar o app fullstack, use apenas `requirements.txt`.

Se quiser customizar conexão com PostgreSQL:

```bash
cp app/backend/.env.example app/backend/.env
```

Edite `app/backend/.env` se usuário, senha, host, porta ou nome do banco forem diferentes.

## 4. Rodar migrations do banco

O projeto usa Alembic para versionar alterações estruturais do PostgreSQL, como a tabela de usuários da autenticação.

```bash
cd /Users/pedro/Documents/pesquisa-welington/chatbot-regulagem-implementos/app/backend
alembic upgrade head
```

Se você criar novas alterações de banco futuramente, gere uma nova migration e depois rode `alembic upgrade head`.

## 5. Criar tabelas técnicas e carregar dados

```bash
cd /Users/pedro/Documents/pesquisa-welington/chatbot-regulagem-implementos/app/backend
python -m app.scripts.load_data
```

Esse comando lê:

- `ocr/anuario.xlsx`
- `ocr/extracao_arados.xlsx`
- `ocr/extracao_grades.xlsx`

E grava os dados normalizados no PostgreSQL.

## 6. Treinar o modelo de machine learning

```bash
cd /Users/pedro/Documents/pesquisa-welington/chatbot-regulagem-implementos/app/backend
python -m app.scripts.train_model
```

O modelo será salvo em:

```text
app/artifacts/power_model.json
```

## 7. Rodar a API FastAPI

```bash
cd /Users/pedro/Documents/pesquisa-welington/chatbot-regulagem-implementos/app/backend
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

URLs úteis:

- API: `http://127.0.0.1:8000`
- Swagger: `http://127.0.0.1:8000/docs`
- Healthcheck: `http://127.0.0.1:8000/api/health`

## 8. Rodar o frontend

Em outro terminal:

```bash
cd /Users/pedro/Documents/pesquisa-welington/chatbot-regulagem-implementos/app/frontend
npm install
npm run dev
```

Acesse:

```text
http://127.0.0.1:5173
```

## 9. Publicar com Neon, Render e Vercel

A ordem recomendada é Neon (PostgreSQL), Render (API) e Vercel (frontend).

### Neon

1. Crie um projeto e um banco no Neon.
2. Em **Connect**, habilite a conexão com pool e copie a URL.
3. Troque o prefixo `postgresql://` por `postgresql+psycopg://`, preservando os demais componentes e os parâmetros `sslmode` e `channel_binding`.

Exemplo de formato:

```text
postgresql+psycopg://USUARIO:SENHA@HOST-pooler.REGIAO.aws.neon.tech/BANCO?sslmode=require&channel_binding=require
```

### Render

1. No Render, crie um **Blueprint** usando este repositório. O arquivo `render.yaml` configura build, inicialização, servidor e healthcheck.
2. Quando solicitado, preencha `DATABASE_URL` com a URL SQLAlchemy do Neon.
3. Preencha inicialmente `CORS_ORIGINS` com `http://localhost:5173`. Depois da publicação na Vercel, substitua pelo domínio final, por exemplo `https://arips.vercel.app`, e faça um novo deploy.
4. Confirme o funcionamento em `https://SEU-SERVICO.onrender.com/api/health` e `https://SEU-SERVICO.onrender.com/docs`.

O comando de inicialização aplica as migrations e carrega o banco técnico somente quando ele está vazio. Reinícios e deploys posteriores não apagam recomendações, usuários ou conversas.

### Vercel

1. Importe o mesmo repositório na Vercel.
2. Defina **Root Directory** como `app/frontend` e mantenha o preset Vite.
3. Cadastre a variável `VITE_API_URL` nos ambientes Production e Preview com o endereço do Render, sem barra final:

```text
https://SEU-SERVICO.onrender.com
```

4. Faça o deploy e use o endereço gerado para atualizar `CORS_ORIGINS` no Render.

Como `VITE_API_URL` é incorporada durante o build do Vite, qualquer alteração nessa variável exige um novo deploy na Vercel.

### Primeira conta administrativa

Depois que a aplicação estiver publicada, registre sua conta normalmente. Em seguida, abra o **SQL Editor** do Neon e promova somente essa conta:

```sql
UPDATE users
SET role = 'admin'
WHERE email = 'SEU_EMAIL';
```

Saia e entre novamente na aplicação para que o novo papel seja refletido no token de acesso. As demais contas continuam sendo criadas com o papel `user`.

## Endpoints principais

- `POST /api/auth/register`
- `POST /api/auth/login`
- `GET /api/auth/me`
- `GET /api/implements` - apenas admin
- `GET /api/implements/stats` - apenas admin
- `GET /api/tractors` - apenas admin
- `GET /api/tractors/stats` - apenas admin
- `GET /api/recommendations/dashboard` - apenas admin
- `GET /api/ml/model` - apenas admin
- `POST /api/ml/train` - apenas admin
- `POST /api/recommendations` - usuário autenticado
- `POST /api/operation-planning/calculate` - usuário autenticado
- `POST /api/chat` - usuário autenticado
- `GET /api/chat/conversations` - usuário autenticado
- `GET /api/chat/conversations/{id}` - usuário autenticado

## Planejamento operacional

A tela **Planejamento** dimensiona os conjuntos mecanizados a partir da area e do periodo de trabalho.

Entradas:

- area a ser preparada, em hectares;
- data inicial;
- data final;
- horas de trabalho por dia.

Calculos aplicados:

```text
TD = (data final - data inicial) x horas por dia
TD arado = TD x 2/3
TD grades = TD x 1/3
TD grade destorroadora = TD grades / 2
TD grade niveladora = TD grades / 2
RO arado = area / TD arado
RO grades = area x 2 / TD da operacao
L = RO x 10 / (velocidade x eficiencia de campo)
N equipamentos = teto(RO x 10 / (largura selecionada x velocidade x eficiencia))
```

Velocidades e eficiencias adotadas:

- arado: `5,5 km/h` e eficiencia `0,85`;
- grade destorroadora: `7,0 km/h` e eficiencia `0,90`;
- grade niveladora: `10,0 km/h` e eficiencia `0,90`.

Depois do calculo, o sistema busca no banco arado, grade destorroadora, grade niveladora e tratores compativeis, retornando um relatorio final de conjuntos.

## Autenticação

O usuário pode criar conta informando:

- nome;
- e-mail;
- CPF;
- senha com pelo menos 8 caracteres.

As senhas são salvas como hash PBKDF2 com salt. O login retorna um token assinado, usado pelo frontend para manter a sessão do usuário.

### Tipos de usuário

O sistema possui dois papéis:

- `admin`: acesso completo ao painel, banco técnico, modelo de ML, recomendações, planejamento e chatbot.
- `user`: acesso apenas às áreas de recomendação, planejamento e chatbot.

A migration `20260608_0002` promove o primeiro usuário existente para `admin`. Novos cadastros entram como `user`.

Para promover manualmente um usuário a administrador:

```bash
psql -d regulagem_implementos -c "UPDATE users SET role = 'admin' WHERE email = 'email@exemplo.com';"
```

Para voltar um usuário para comum:

```bash
psql -d regulagem_implementos -c "UPDATE users SET role = 'user' WHERE email = 'email@exemplo.com';"
```

## Histórico do chatbot

Cada usuário autenticado possui seu próprio histórico de conversas. Quando uma mensagem é enviada ao chatbot, o backend:

1. cria uma conversa nova ou continua uma conversa existente;
2. salva a mensagem do usuário;
3. gera a resposta técnica;
4. salva a resposta do assistente;
5. permite recuperar o histórico pela tela de Chatbot.

As conversas ficam nas tabelas:

```text
chat_conversations
chat_messages
```

## Tokenização dos acessos

Após cadastro ou login, a API retorna um `access_token`. Esse token representa a sessão do usuário e deve ser enviado nas rotas protegidas no cabeçalho HTTP:

```text
Authorization: Bearer SEU_TOKEN
```

Fluxo resumido:

1. O usuário cria conta ou faz login.
2. O backend valida as credenciais.
3. O backend gera um token assinado com tempo de expiração.
4. O frontend salva o token no navegador para manter a sessão.
5. Ao acessar uma rota protegida, o token é enviado para a API.
6. A API valida assinatura, expiração e usuário antes de liberar o acesso.

Exemplo de cadastro pela API:

```bash
curl -X POST http://127.0.0.1:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"name":"Pedro","email":"pedro@email.com","cpf":"123.456.789-09","password":"senha12345"}'
```

Exemplo de uso do token:

```bash
curl http://127.0.0.1:8000/api/auth/me \
  -H "Authorization: Bearer SEU_TOKEN"
```

## Como utilizar a plataforma

O guia de uso para apresentação e operação está em:

```text
docs/GUIA_USO_PLATAFORMA.md
```

## Testes automatizados

Instale as dependências de teste e execute a suíte completa:

```bash
python -m pip install -r requirements-test.txt
pytest
```

Os testes são classificados por finalidade e podem ser executados separadamente:

```bash
pytest -m unit
pytest -m smoke
pytest -m regression
```

O comando padrão também gera o relatório de cobertura do backend no terminal. Para validar o frontend:

```bash
cd app/frontend
npm run build
```
