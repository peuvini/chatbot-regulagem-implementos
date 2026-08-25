# Guia de Uso da Plataforma

## Objetivo

A plataforma foi criada para apoiar agricultores, operadores e pesquisadores na consulta técnica de implementos agrícolas e na geração de recomendações para regulagem de arados e grades. Ela combina banco de dados técnico, chatbot, recomendações assistidas e modelo de machine learning.

## Acesso Inicial

1. Abra o frontend no navegador:

```text
http://127.0.0.1:5173
```

2. Na primeira tela, escolha uma das opções:

- **Entrar no sistema**: para usuários já cadastrados.
- **Criar conta**: para novos usuários.

3. Para criar conta, informe:

- nome completo;
- e-mail;
- CPF;
- senha com no mínimo 8 caracteres.

Após o cadastro ou login, o sistema gera um token de acesso e libera a plataforma.

## Tipos de Usuário

A plataforma separa usuários em dois papéis:

- **Admin**: acessa Painel, Banco Técnico, Recomendação, Planejamento, Chatbot e recursos administrativos do modelo.
- **Usuário comum**: acessa apenas Recomendação, Planejamento e Chatbot.

Essa separação protege o banco técnico, impedindo que usuários comuns consultem diretamente as tabelas de implementos e tratores.

## Como Funciona o Token de Acesso

O token é uma credencial temporária criada pelo backend após o login. Ele mantém o usuário autenticado sem precisar reenviar senha a cada ação.

Fluxo prático:

1. Usuário informa e-mail e senha.
2. API valida as credenciais.
3. API retorna um `access_token`.
4. Frontend salva o token no navegador.
5. Ao abrir a plataforma novamente, o frontend consulta `GET /api/auth/me`.
6. Se o token ainda for válido, o usuário continua logado.

Quando o usuário clica em **Sair**, o token é removido do navegador.

## Menu Principal

A plataforma possui cinco áreas principais.

## Painel

O painel apresenta uma visão geral da base técnica e do modelo:

- total de implementos;
- total de tratores;
- faixa de potência dos tratores;
- erro médio do modelo de machine learning;
- famílias de implementos com mais configurações;
- fluxo resumido da arquitetura.

Essa tela é útil para demonstrar ao professor que a aplicação está conectada ao banco e que o modelo foi treinado com os dados carregados.

Além do resumo geral, o painel científico também apresenta:

- **Qualidade dos dados**: percentual de preenchimento de modelo, largura, peso, potência e profundidade.
- **Prontidão do modelo**: cobertura do treinamento, MAE relativo, variável alvo e quantidade de variáveis usadas.
- **Distribuição por potência**: comparação das faixas de potência dos implementos.
- **Disponibilidade de tratores**: distribuição dos tratores por faixa de potência.
- **Uso nas recomendações**: total de recomendações salvas, score médio e itens mais consultados.
- **Checklist de validação**: critérios de base carregada, modelo treinado, erro mensurado e uso registrado.

## Recomendação

A tela de recomendação permite informar parâmetros operacionais:

- tipo de implemento;
- família ou modelo;
- potência do trator;
- tipo de solo;
- umidade;
- cultura.

Depois de clicar em **Gerar recomendação**, o sistema retorna uma lista ranqueada com:

- modelo do implemento;
- faixa de potência recomendada;
- estimativa do modelo de machine learning;
- largura de trabalho;
- peso médio;
- nota técnica.

## Planejamento

A tela de planejamento operacional calcula quantos conjuntos mecanizados sao necessarios para preparar uma area dentro de um periodo de trabalho.

Entradas:

- area a ser preparada, em hectares;
- data inicial;
- data final;
- horas por dia de trabalho.

O sistema calcula:

- tempo disponivel total;
- tempo destinado ao arado;
- tempo destinado as grades;
- tempo da grade destorroadora;
- tempo da grade niveladora;
- ritmo operacional de cada operacao;
- largura minima de trabalho;
- implemento compativel no banco de dados;
- trator compativel;
- numero de conjuntos para cada operacao.

Formulas principais:

```text
TD = (data final - data inicial) x horas por dia
TD arado = TD x 2/3
TD grades = TD x 1/3
TD grade destorroadora = TD grades / 2
TD grade niveladora = TD grades / 2
RO arado = area / TD arado
RO grades = area x 2 / TD da operacao
L = RO x 10 / (velocidade x eficiencia de campo)
```

Velocidades usadas:

- arado: 5,5 km/h;
- grade destorroadora: 7,0 km/h;
- grade niveladora: 10,0 km/h.

Eficiencias usadas:

- arado: 0,85;
- grades: 0,90.

O relatorio final informa, por exemplo, quantos conjuntos de `trator + arado`, `trator + grade destorroadora` e `trator + grade niveladora` serao necessarios.

## Chatbot

O chatbot permite perguntar em linguagem natural. Exemplos:

```text
Tenho trator de 120 hp e solo argiloso. Qual grade usar?
```

```text
Como escolher um arado para solo seco?
```

```text
Quais implementos combinam com 90 hp?
```

O backend interpreta a pergunta, extrai parâmetros prováveis e chama o serviço de recomendação.

O chatbot também possui histórico por usuário. A lateral da tela mostra conversas anteriores, permitindo abrir uma conversa antiga e continuar perguntando no mesmo contexto. Cada usuário enxerga somente o próprio histórico.

## Banco Técnico

A área de banco técnico permite consultar os implementos carregados das planilhas.

Filtros disponíveis:

- todos;
- arados;
- grades;
- busca por família, modelo ou descrição.

A tabela mostra:

- grupo;
- modelo;
- descrição;
- largura;
- peso;
- potência.

Essa tela ajuda na conferência manual dos dados extraídos.

Essa área é exclusiva para usuários administradores.

## Uso da API

Documentação interativa da API:

```text
http://127.0.0.1:8000/docs
```

Endpoints principais:

- `POST /api/auth/register`: cria usuário.
- `POST /api/auth/login`: autentica usuário.
- `GET /api/auth/me`: valida token e retorna usuário logado.
- `GET /api/recommendations/dashboard`: dados do painel, apenas admin.
- `GET /api/implements`: consulta implementos, apenas admin.
- `GET /api/tractors`: consulta tratores, apenas admin.
- `POST /api/recommendations`: gera recomendação estruturada para usuário autenticado.
- `POST /api/operation-planning/calculate`: calcula dimensionamento operacional para usuário autenticado.
- `POST /api/chat`: envia pergunta ao chatbot para usuário autenticado.
- `GET /api/chat/conversations`: lista históricos do usuário autenticado.
- `GET /api/chat/conversations/{id}`: abre uma conversa anterior do usuário autenticado.

## Exemplo de Demonstração para o Professor

1. Acessar `http://127.0.0.1:5173`.
2. Criar um usuário com nome, e-mail, CPF e senha.
3. Mostrar que a plataforma entra com sessão autenticada.
4. Abrir o **Painel** e apresentar os dados carregados.
5. Abrir **Recomendação** e simular um trator de 120 hp em solo argiloso.
6. Abrir **Planejamento** e dimensionar uma area de exemplo com datas de inicio e fim.
7. Abrir **Chatbot** e fazer a mesma pergunta em linguagem natural.
8. Abrir **Banco técnico** e mostrar que os dados vêm das planilhas extraídas.
9. Abrir `http://127.0.0.1:8000/docs` para mostrar a API FastAPI.

## Observações Técnicas

- O sistema usa PostgreSQL para persistência.
- As migrations são aplicadas com Alembic.
- O frontend usa React, TypeScript e Tailwind.
- O backend usa FastAPI, SQLAlchemy e Pydantic.
- A autenticação usa token assinado e senha com hash PBKDF2.
- O modelo de machine learning é salvo em `app/artifacts/power_model.json`.
