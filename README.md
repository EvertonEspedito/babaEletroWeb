# 👶 Babá Eletrônica IoT

Sistema de monitoramento de ambiente baseado em Internet das Coisas (IoT), desenvolvido para detectar níveis de som e enviar alertas para uma aplicação web. O projeto utiliza um Raspberry Pi Pico W, um sensor de som, uma API desenvolvida com Django e um painel de monitoramento acessível pelo navegador.

## 📌 Sobre o projeto

A **Babá Eletrônica IoT** tem como objetivo monitorar o ambiente em que o bebê se encontra, identificando níveis sonoros que possam exigir a atenção de um responsável.

O dispositivo realiza leituras do sensor de som, conecta-se à rede Wi-Fi e envia informações ao servidor. O backend recebe os dados, registra os eventos e disponibiliza as informações para o painel web.

O projeto também permite acompanhar o estado de conexão do dispositivo por meio de mensagens periódicas de *heartbeat*.

> **Aviso:** este projeto é experimental e não substitui a supervisão de um responsável nem equipamentos profissionais de monitoramento infantil.

## 🎯 Objetivos

- Desenvolver um sistema de monitoramento utilizando IoT.
- Detectar alterações no nível sonoro do ambiente.
- Enviar alertas do dispositivo para um servidor.
- Monitorar a conectividade do dispositivo em tempo real.
- Disponibilizar um painel web para acompanhamento dos eventos.
- Integrar hardware, comunicação de rede, API e interface web.

## 🏗️ Arquitetura do sistema

```text
┌─────────────────────────────┐
│ Sensor de som analógico     │
└──────────────┬──────────────┘
               │
               ▼
┌─────────────────────────────┐
│ Raspberry Pi Pico W         │
│ MicroPython + Wi-Fi         │
└──────────────┬──────────────┘
               │ HTTP
               ▼
┌─────────────────────────────┐
│ Backend Django              │
│ API + autenticação          │
└──────────────┬──────────────┘
               │ HTTP / JSON
               ▼
┌─────────────────────────────┐
│ Frontend Web                │
│ HTML + CSS + JavaScript     │
│ Hospedagem: Vercel           │
└─────────────────────────────┘
```

### Componentes

| Componente | Responsabilidade |
|---|---|
| Raspberry Pi Pico W | Leitura do sensor e conexão Wi-Fi |
| Sensor de som analógico | Captura de variações no nível sonoro |
| MicroPython | Execução do firmware do dispositivo |
| Django | Processamento das requisições e lógica do servidor |
| API REST | Comunicação entre o dispositivo, o backend e o painel |
| HTML, CSS e JavaScript | Construção da interface web |
| Vercel | Hospedagem do frontend |

## ⚙️ Tecnologias utilizadas

- **Hardware:** Raspberry Pi Pico W e sensor de som analógico.
- **Firmware:** MicroPython.
- **Backend:** Python e Django.
- **Frontend:** HTML5, CSS3 e JavaScript.
- **Comunicação:** Wi-Fi e HTTP.
- **Hospedagem do frontend:** Vercel.
- **Controle de acesso:** chaves e tokens de autenticação.

## ✨ Funcionalidades

- Monitoramento do estado de conexão do dispositivo.
- Envio periódico de *heartbeats*.
- Leitura de valores provenientes do sensor de som.
- Envio de alertas para o backend.
- Consulta do estado atual do sistema por meio da API.
- Painel web para visualizar informações do dispositivo.
- Exibição de alertas recentes e indicadores de monitoramento.
- Configuração do endereço da API e do acesso ao painel.

## 📁 Estrutura do projeto

A organização pode variar conforme a evolução do código. Uma estrutura de referência é:

```text
baba-eletronica-iot/
├── backend/
│   ├── manage.py
│   ├── config/
│   │   └── settings.py
│   └── iot/
│       ├── views.py
│       ├── urls.py
│       └── models.py
│
├── firmware/
│   └── main.py
│
├── frontend/
│   ├── index.html
│   ├── styles.css
│   └── app.js
│
├── requirements.txt
├── .env.example
└── README.md
```

Essa estrutura é ilustrativa. Os diretórios podem permanecer em repositórios separados, conforme a configuração utilizada no desenvolvimento.

## 🚀 Como executar o backend

### 1. Pré-requisitos

- Python instalado.
- pip.
- Git, caso utilize controle de versão.
- Ambiente virtual Python recomendado.

### 2. Acesse o diretório do Django

```bash
cd ~/Documentos/PROJETOS/baba_eletronica
```

### 3. Crie e ative o ambiente virtual

```bash
python3 -m venv venv
source venv/bin/activate
```

### 4. Instale as dependências

Se o projeto já possuir um arquivo `requirements.txt`:

```bash
pip install -r requirements.txt
```

Caso ele ainda não exista, instale as dependências definidas pelo projeto antes de executar os próximos comandos.

### 5. Execute as migrações

```bash
python manage.py migrate
```

### 6. Inicie o servidor

```bash
python manage.py runserver 0.0.0.0:8000
```

O backend ficará disponível na porta `8000`. O endereço `127.0.0.1:8000` pode ser usado na própria máquina; para outros dispositivos da rede, utilize o IP local do computador.

> O servidor de desenvolvimento do Django é indicado para testes. Para publicação na internet, utilize uma configuração de produção com HTTPS.

## 📡 Comunicação com o dispositivo

O Raspberry Pi Pico W utiliza MicroPython para se conectar ao Wi-Fi, realizar leituras do sensor e enviar informações ao backend.

Os endpoints implementados no projeto são:

| Endpoint | Finalidade |
|---|---|
| `/iot/heartbeat/` | Informar que o dispositivo está ativo |
| `/iot/alert/` | Enviar alertas detectados pelo dispositivo |
| `/iot/state/` | Consultar o estado do sistema para o painel |

As rotas devem ser acessadas utilizando o endereço configurado para a API.

Exemplo de endereço local:

```text
http://192.168.0.106:8000/iot/state/
```

O IP acima é um exemplo de configuração local e deve ser atualizado conforme a rede utilizada. Em produção, substitua-o pelo domínio HTTPS do backend.

O dispositivo utiliza o cabeçalho `X-Device-Key` para autenticação. O painel utiliza o cabeçalho `X-Dashboard-Token`, conforme a implementação atual.

Os métodos HTTP, os campos JSON e as respostas de cada endpoint devem seguir as definições presentes no código do backend.

## 🌐 Como executar o frontend

O frontend utiliza HTML, CSS e JavaScript e pode ser hospedado na Vercel.

Para testar os arquivos localmente, acesse o diretório do frontend e execute:

```bash
python3 -m http.server 5500
```

Depois, abra:

```text
http://localhost:5500
```

Configure no painel o endereço da API Django e o token de acesso exigido pelo backend.

### Configuração de CORS

O backend deve autorizar a origem do frontend. Para a aplicação publicada na Vercel, a origem pode ser configurada assim:

```python
import os

IOT_ALLOWED_ORIGIN = os.environ.get(
    "IOT_ALLOWED_ORIGIN",
    "https://babaeletronica.vercel.app"
)
```

Essa variável, por si só, não habilita CORS: o middleware ou mecanismo de CORS do projeto precisa utilizá-la para autorizar a origem.

Se o frontend estiver em outro domínio, atualize a configuração para corresponder ao domínio efetivamente utilizado.

## 🔐 Segurança

Para proteger o sistema:

- Não publique chaves de autenticação ou senhas no repositório.
- Utilize variáveis de ambiente para configurar segredos.
- Não disponibilize o Django diretamente na internet utilizando o servidor de desenvolvimento.
- Utilize HTTPS na comunicação com o backend publicado.
- Restrinja as origens autorizadas por CORS.
- Não exponha tokens administrativos ou credenciais de dispositivos no JavaScript público.
- Implemente validação das requisições recebidas.
- Considere limites de requisições e registros de eventos de segurança.

**Atenção:** qualquer token incluído no JavaScript enviado ao navegador pode ser visualizado pelos usuários. Para produção, prefira um mecanismo de autenticação apropriado, com credenciais individuais e permissões limitadas.

## 🧪 Testes e validação

Durante os testes, verifique:

- [ ] O Raspberry Pi Pico W conecta-se ao Wi-Fi.
- [ ] O sensor apresenta leituras.
- [ ] O dispositivo envia *heartbeats* ao backend.
- [ ] Os alertas chegam corretamente à API.
- [ ] O estado do dispositivo é retornado pelo endpoint correspondente.
- [ ] O painel exibe os dados recebidos.
- [ ] A autenticação funciona conforme esperado.
- [ ] O frontend hospedado na Vercel consegue acessar o backend.
- [ ] O sistema identifica perda de comunicação com o dispositivo.

## 🔮 Melhorias futuras

- Configuração personalizada dos limites de detecção sonora.
- Histórico de alertas com filtros por data.
- Notificações em tempo real.
- Aplicação responsiva para dispositivos móveis.
- Gráficos com histórico dos níveis sonoros.
- Armazenamento e análise de dados históricos.
- Monitoramento de múltiplos dispositivos.
- Melhorias de segurança e autenticação para produção.

## 👨‍💻 Desenvolvimento

Projeto desenvolvido com foco em Internet das Coisas, sistemas embarcados, desenvolvimento web e integração entre hardware e software.

## 📄 Licença

A licença ainda precisa ser definida. Antes de distribuir ou permitir a reutilização do projeto, escolha uma licença compatível com os objetivos de publicação.

---

**Babá Eletrônica IoT — conectando sensores, dados e monitoramento.**
