---
slug: /
sidebar_position: 1
sidebar_label: "Solução"
title: Solução
---

# Sistema Automatizado de Dragagem com Bomba Submersível

## Descrição

Em operações com bombas submersíveis de dragagem, é necessário reposicionar o equipamento conforme o acúmulo de sólidos ou a queda do nível do fluido bombeado — tarefa que, de forma manual, apresenta riscos operacionais e custos elevados, já que não é possível visualizar o que ocorre abaixo do flutuador.

Este projeto, desenvolvido em parceria com a **Itubombas**, propõe uma solução de **movimentação automatizada** para a bomba de dragagem, aumentando a eficiência e a segurança da operação e reduzindo a necessidade de mão de obra para o arrasto do equipamento. Com a solução validada, espera-se ampliar o alcance da Itubombas no mercado de dragagem e minimizar paradas operacionais decorrentes da realocação do equipamento.

---

## Estrutura do Repositório

```
.
├── src/                        # Código-fonte principal do projeto
│   ├── backend/                # API REST em Python (FastAPI) — sensores, movimentação e autenticação
│   │   ├── config.py           # Configurações da aplicação (banco de dados, MQTT, JWT)
│   │   ├── main.py             # Ponto de entrada do servidor
│   │   ├── db/                 # Conexão com banco de dados, schema SQL e seed
│   │   ├── models/             # Modelos de dados (bomba, leituras, movimentações, usuário)
│   │   ├── repositories/       # Camada de acesso ao banco de dados para cada entidade
│   │   ├── routes/             # Endpoints da API (autenticação, bombas, leituras, movimentação, logs)
│   │   └── services/           # Serviços auxiliares (autenticação JWT, comunicação MQTT)
│   ├── frontend/               # Interface web (React + Vite)
│   │   └── Autobombas/         # Aplicação frontend principal
│   ├── módulo1-A/              # Firmware e CLI do Módulo 1-A (ESP32/Arduino)
│   ├── módulo1-B/              # Firmware e CLI do Módulo 1-B
│   ├── módulo2-A/              # Firmware e CLI do Módulo 2-A
│   ├── módulo2-B/              # Firmware e CLI do Módulo 2-B
│   ├── módulo2-C/              # Firmware e CLI do Módulo 2-C
│   └── super-cli-unificado.py  # CLI unificada para interação com todos os módulos
├── docs/                       # Documentação do projeto (Docusaurus)
│   └── docs/
│       ├── solucao.md
│       └── sprints/            # Documentação por sprint (01 a 05)
├── requirements.txt            # Dependências Python do projeto
└── README.md
```

---

## Equipe de Desenvolvimento

| Integrante | LinkedIn |
|---|---|
| Guilherme Holanda Marques | [LinkedIn](https://www.linkedin.com/in/guilhermeholandamarques/) |
| Carlos Icaro | [LinkedIn](https://www.linkedin.com/in/carlosicaro/?locale=pt) |
| Guilherme Schmidt | [LinkedIn](https://www.linkedin.com/in/guilherme-schmidt14/) |
| Isabel Montenegro | [LinkedIn](https://www.linkedin.com/in/isabel-montenegro01/) |
| Christian de Carvalho Lawrence | [LinkedIn](https://www.linkedin.com/in/christian-de-carvalho-lawrence/) |
| Bruno Frossard | [LinkedIn](https://www.linkedin.com/in/bruno-frossardd/) |
| João Cardoso Dias | [LinkedIn](https://www.linkedin.com/in/jo%C3%A3ocardosodias/) |
| Sara Sbardelotto | [LinkedIn](https://www.linkedin.com/in/sara-sbardelotto/) |

---

## Professores do Módulo

| Professor | Papel | LinkedIn |
|---|---|---|
| Murilo Zanini de Carvalho | Orientador de Projeto | [LinkedIn](https://www.linkedin.com/in/murilo-zanini-de-carvalho-0980415b/) |
| Filipe Gonçalves | Liderança | [LinkedIn](https://www.linkedin.com/in/filipe-gon%C3%A7alves-08a55015b/) |
| Geraldo Magela Severino Vasconcelos | Matemática e Física | [LinkedIn](https://www.linkedin.com/in/geraldo-magela-severino-vasconcelos-22b1b220/) |
| Guilherme Cestari | UX e Design | [LinkedIn](https://www.linkedin.com/in/gui-cestari/) |
| Michele Bazana de Souza | Coordenadora — Eng. de Computação | [LinkedIn](https://www.linkedin.com/in/michelebazana/) |
| Rodrigo Mangoni Nicola | Computação | [LinkedIn](https://www.linkedin.com/in/rodrigo-mangoni-nicola-537027158/) |

---

## Como Rodar o Projeto

### Pré-requisitos

- Python 3.9+
- Broker MQTT configurado (ex: [Mosquitto](https://mosquitto.org/))
- Banco de dados compatível com o schema em `backend/db/schema.sql`
- Hardware: módulos ESP32/Arduino com os firmwares da pasta `src/`

### Passo a Passo

**1. Clone o repositório**

```bash
git clone https://git.inteli.edu.br/graduacao/2026-1a/t16/g06.git
cd g06
```

**2. Crie e ative o ambiente virtual**

```bash
python3 -m venv venv
source venv/bin/activate   # Linux/macOS
venv\Scripts\activate      # Windows
```

**3. Instale as dependências**

```bash
pip install -r requirements.txt
```

**4. Configure as variáveis de ambiente**

Copie o arquivo de configuração de exemplo e preencha com os dados do seu ambiente (banco de dados, broker MQTT, etc.):

```bash
cp backend/config.py.example backend/config.py
# edite backend/config.py com suas configurações
```

**5. Inicialize o banco de dados**

```bash
python backend/db/seed.py
```

**6. Inicie o backend**

```bash
python backend/main.py
```

**7. (Opcional) Use a CLI principal**

```bash
python cli.py
```

**8. Grave o firmware no hardware**

Abra o arquivo `.ino` do módulo correspondente (em `src/módulo<X>/firmware.ino`) na Arduino IDE e faça o upload para o dispositivo.

---

## Como Executar a Documentação

A documentação completa do projeto está disponível online:

🔗 **[https://graduacao.pages.git.inteli.edu.br/2026-1a/t16/g06/](https://graduacao.pages.git.inteli.edu.br/2026-1a/t16/g06/)**

Para rodar a documentação localmente:

### Pré-requisitos

- Node.js 18+
- npm ou yarn

### Passo a Passo

```bash
cd docs
npm install
npm start
```

A documentação estará disponível em `http://localhost:3000`.

---

## Licença

<img style={{height: "22px", marginLeft: "3px", verticalAlign: "text-bottom"}} src="https://mirrors.creativecommons.org/presskit/icons/cc.svg?ref=chooser-v1" /><img style={{height: "22px", marginLeft: "3px", verticalAlign: "text-bottom"}} src="https://mirrors.creativecommons.org/presskit/icons/by.svg?ref=chooser-v1" /><p xmlnsCc="http://creativecommons.org/ns#" xmlnsDct="http://purl.org/dc/terms/"><a property="dct:title" rel="cc:attributionURL" href="https://git.inteli.edu.br/graduacao/2026-1a/t16/g06">Autobombas</a> by <a rel="cc:attributionURL dct:creator" property="cc:attributionName" href="https://github.com/InteliProjects">Inteli</a>, <a property="dct:title" rel="cc:attributionURL" href="https://www.linkedin.com/in/guilhermeholandamarques/">Guilherme Holanda Marques</a>, <a property="dct:title" rel="cc:attributionURL" href="https://www.linkedin.com/in/carlosicaro/?locale=pt">Carlos Icaro</a>, <a property="dct:title" rel="cc:attributionURL" href="https://www.linkedin.com/in/guilherme-schmidt14/">Guilherme Schmidt</a>, <a property="dct:title" rel="cc:attributionURL" href="https://www.linkedin.com/in/isabel-montenegro01/">Isabel Montenegro</a>, <a property="dct:title" rel="cc:attributionURL" href="https://www.linkedin.com/in/christian-de-carvalho-lawrence/">Christian de Carvalho Lawrence</a>, <a property="dct:title" rel="cc:attributionURL" href="https://www.linkedin.com/in/bruno-frossardd/">Bruno Frossard</a>, <a property="dct:title" rel="cc:attributionURL" href="https://www.linkedin.com/in/jo%C3%A3ocardosodias/">João Cardoso Dias</a>, <a property="dct:title" rel="cc:attributionURL" href="https://www.linkedin.com/in/sara-sbardelotto/">Sara Sbardelotto</a> is licensed under <a href="http://creativecommons.org/licenses/by/4.0/?ref=chooser-v1" target="_blank" rel="license noopener noreferrer" style={{display: "inline-block"}}>Attribution 4.0 International</a>.</p>
