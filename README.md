# Sistema Automatizado de Dragagem com Bomba Submersível

## Descrição

Em operações com bombas submersíveis de dragagem, é necessário reposicionar o equipamento conforme o acúmulo de sólidos ou a queda do nível do fluido bombeado — tarefa que, de forma manual, apresenta riscos operacionais e custos elevados, já que não é possível visualizar o que ocorre abaixo do flutuador.

Este projeto, desenvolvido em parceria com a **Itubombas**, propõe uma solução de **movimentação automatizada** para a bomba de dragagem, aumentando a eficiência e a segurança da operação e reduzindo a necessidade de mão de obra para o arrasto do equipamento. Com a solução validada, espera-se ampliar o alcance da Itubombas no mercado de dragagem e minimizar paradas operacionais decorrentes da realocação do equipamento.

---

## Estrutura do Repositório

O código-fonte, a documentação e os firmwares estão organizados em diretórios separados para facilitar a navegação e manutenção independente de cada camada.

```
.
├── src/                        # Código-fonte principal do projeto
│   ├── backend/                # API REST em Python (Flask) — sensores, movimentação e autenticação
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

Alunos de Engenharia de Computação do Inteli responsáveis pelo projeto do grupo 6 do módulo 5 (2026.1).

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

Docentes que orientaram e avaliaram o desenvolvimento ao longo das cinco sprints.

| Professor | Papel | LinkedIn |
|---|---|---|
| Murilo Zanini de Carvalho | Orientador de Projeto | [LinkedIn](https://www.linkedin.com/in/murilo-zanini-de-carvalho-0980415b/) |
| Filipe Gonçalves | Liderança | [LinkedIn](https://www.linkedin.com/in/filipe-gon%C3%A7alves-08a55015b/) |
| Geraldo Magela Severino Vasconcelos | Matemática e Física | [LinkedIn](https://www.linkedin.com/in/geraldo-magela-severino-vasconcelos-22b1b220/) |
| Guilherme Cestari | UX e Design | [LinkedIn](https://www.linkedin.com/in/gui-cestari/) |
| Michele Bazana de Souza | Coordenadora — Eng. de Computação | [LinkedIn](https://www.linkedin.com/in/michelebazana/) |
| Rodrigo Mangoni Nicola | Computação | [LinkedIn](https://www.linkedin.com/in/rodrigo-mangoni-nicola-537027158/) |

---

## Como executar o projeto

Instruções para reproduzir o sistema completo localmente — backend, frontend, banco de dados e hardware.

### Pré-requisitos

- Python 3.9+
- Broker MQTT configurado (ex: [Mosquitto](https://mosquitto.org/))
- Banco de dados compatível com o schema em `backend/db/schema.sql`
- Hardware: módulos ESP32/Arduino com os firmwares da pasta `src/`

### Passo a Passo

**1. Clone o repositório**

Obtém a cópia completa do projeto (código, docs e firmwares) na máquina local.

```bash
git clone https://git.inteli.edu.br/graduacao/2026-1a/t16/g06.git
cd g06
```

**2. Crie e ative o ambiente virtual**

Isola as dependências Python do projeto para não conflitar com pacotes do sistema.

```bash
python3 -m venv venv
source venv/bin/activate   # Linux/macOS
venv\Scripts\activate      # Windows
```

**3. Instale as dependências**

Instala as bibliotecas necessárias para o backend (Flask, MQTT, JWT, etc.).

```bash
pip install -r requirements.txt
```

**4. Configure as variáveis de ambiente**

Define credenciais e endereços (banco de dados, broker MQTT, chave JWT) sem expor dados sensíveis no repositório.

```bash
cp .env.example .env
# edite .env com suas configurações
```

**5. Inicialize o banco de dados**

Cria as tabelas e insere dados iniciais necessários para o funcionamento do sistema.

```bash
python backend/db/seed.py
```

**6. Inicie o backend**

Sobe a API REST que recebe comandos do frontend e se comunica com os módulos via MQTT.

```bash
python backend/main.py
```

**7. Inicie o frontend**

Sobe a interface web que permite ao operador e ao gestor interagirem com o sistema.

```bash
cd src/frontend/Autobombas
npm install
npm run dev
```

A interface estará disponível em `http://localhost:5173`.

**8. (Opcional) Use a CLI unificada**

Alternativa ao frontend para interagir diretamente com os módulos via terminal, útil para depuração e testes rápidos.

```bash
python src/super-cli-unificado.py
```

**9. Grave o firmware no hardware**

Carrega o código embarcado nos microcontroladores para que os módulos físicos respondam aos comandos do sistema.

Abra o arquivo `.ino` do módulo correspondente (em `src/módulo<X>/firmware.ino`) na Arduino IDE e faça o upload para o dispositivo.

---

## Como Executar a Documentação

A documentação técnica é construída com Docusaurus e publicada automaticamente via CI/CD (GitLab Pages). Também pode ser executada localmente para desenvolvimento ou revisão offline.

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

Este projeto é disponibilizado sob licença aberta para fins acadêmicos e de referência, conforme os termos abaixo.

<img style="height:22px!important;margin-left:3px;vertical-align:text-bottom;" src="https://mirrors.creativecommons.org/presskit/icons/cc.svg?ref=chooser-v1"><img style="height:22px!important;margin-left:3px;vertical-align:text-bottom;" src="https://mirrors.creativecommons.org/presskit/icons/by.svg?ref=chooser-v1"><p xmlns:cc="http://creativecommons.org/ns#" xmlns:dct="http://purl.org/dc/terms/"><a property="dct:title" rel="cc:attributionURL" href="https://git.inteli.edu.br/graduacao/2026-1a/t16/g06">Autobombas</a> by <a rel="cc:attributionURL dct:creator" property="cc:attributionName" href="https://github.com/InteliProjects">Inteli</a>, <a property="dct:title" rel="cc:attributionURL" href="https://www.linkedin.com/in/guilhermeholandamarques/">Guilherme Holanda Marques</a>, <a property="dct:title" rel="cc:attributionURL" href="https://www.linkedin.com/in/carlosicaro/?locale=pt">Carlos Icaro</a>, <a property="dct:title" rel="cc:attributionURL" href="https://www.linkedin.com/in/guilherme-schmidt14/">Guilherme Schmidt</a>, <a property="dct:title" rel="cc:attributionURL" href="https://www.linkedin.com/in/isabel-montenegro01/">Isabel Montenegro</a>, <a property="dct:title" rel="cc:attributionURL" href="https://www.linkedin.com/in/christian-de-carvalho-lawrence/">Christian de Carvalho Lawrence</a>, <a property="dct:title" rel="cc:attributionURL" href="https://www.linkedin.com/in/bruno-frossardd/">Bruno Frossard</a>, <a property="dct:title" rel="cc:attributionURL" href="https://www.linkedin.com/in/jo%C3%A3ocardosodias/">João Cardoso Dias</a>, <a property="dct:title" rel="cc:attributionURL" href="https://www.linkedin.com/in/sara-sbardelotto/">Sara Sbardelotto</a> is licensed under <a href="http://creativecommons.org/licenses/by/4.0/?ref=chooser-v1" target="_blank" rel="license noopener noreferrer" style="display:inline-block;">Attribution 4.0 International</a>.</p>
