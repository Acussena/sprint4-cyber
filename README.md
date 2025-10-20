# Projeto de Pipeline DevSecOps - Sprint Cybersecurity

Este repositório é uma demonstração prática da implementação de um pipeline de CI/CD com segurança integrada (DevSecOps), utilizando GitHub Actions, para uma aplicação Python com Flask.

O objetivo do projeto é automatizar a identificação de vulnerabilidades em todas as fases do ciclo de desenvolvimento, consolidando as práticas de SAST, DAST e SCA numa esteira de integração contínua que bloqueia código inseguro e notifica a equipa em tempo real.

---

## 👥 Equipe

- Açussena Mautone - 552568
- Fabrício Saavedra - 97631
- Guilherme Akio – 98582
- Guilherme Morais – 551981

## ESPY

## 📂 Estrutura do Projeto

O projeto está organizado da seguinte forma para garantir clareza e separação de responsabilidades:

```
ESPY-Sprint3-Cybersecurity/
├── .github/
│   └── workflows/
│       └── security-pipeline.yml
├── .gitignore
├── app.py
├── README.md
├── relatorio-dast.html
└── requirements.txt
```

- **`.github/workflows/security-pipeline.yml`**: Ficheiro principal que define todo o workflow do GitHub Actions. Contém os jobs, passos, gatilhos e a configuração de todas as ferramentas de segurança (Snyk, CodeQL, ZAP).
- **`app.py`**: A aplicação web de exemplo, construída com o micro-framework Flask.
- **`requirements.txt`**: Ficheiro de manifesto que lista todas as dependências Python do projeto e as suas versões. É o alvo principal da análise de SCA do Snyk.
- **`relatorio-dast.html`**: Um exemplo de relatório gerado pela ferramenta de DAST (OWASP ZAP), que é disponibilizado como um artefacto ao final da execução do pipeline.
- **`README.md`**: Este ficheiro de documentação.

---

## 🐍 Bibliotecas e Dependências

A aplicação utiliza as seguintes bibliotecas principais, listadas no `requirements.txt`:

- **`Flask`**: O micro-framework web utilizado para construir a aplicação `app.py`.
- **`Werkzeug`**: Uma biblioteca de utilitários WSGI para Python. É uma dependência central do Flask, responsável por tarefas como routing e debugging.
- **`Jinja2`**: O motor de templates para Python, utilizado pelo Flask para renderizar as páginas HTML.
- **`itsdangerous`**: Utilizado para assinar dados com segurança, essencial para o funcionamento dos cookies de sessão do Flask.
- **`Click`**: Uma biblioteca para criar interfaces de linha de comando, utilizada pelo Flask para os seus comandos de gestão.
- **`MarkupSafe`**: Uma dependência do Jinja2 que escapa caracteres para prevenir ataques de injeção, como XSS.

_**Nota:** Foram utilizadas versões deliberadamente desatualizadas destas bibliotecas para demonstrar a capacidade do pipeline em detetar e bloquear vulnerabilidades conhecidas._

---

## 🚀 Metodologia e Resultados das Tarefas

### Tarefa 1: SAST – Análise Estática

A Análise Estática (SAST) foi implementada com o **GitHub CodeQL**, que analisa o código-fonte (`app.py`) em busca de padrões de vulnerabilidades. As falhas encontradas são geridas no separador **Security > Code scanning alerts** do repositório.

### Tarefa 2: DAST – Análise Dinâmica

A Análise Dinâmica (DAST) foi configurada com o **OWASP ZAP**, que simula ataques básicos à aplicação. O resultado é um relatório HTML (`relatorio-dast.html`) disponibilizado como artefacto do pipeline.

### Tarefa 3: SCA – Análise de Componentes

A Análise de Componentes (SCA) foi realizada com o **Snyk**, que verifica o ficheiro `requirements.txt` em busca de vulnerabilidades nas dependências. O resultado detalhado é visível no **dashboard do Snyk**, que se mantém sincronizado com o repositório.

### Tarefa 4: Integração e Monitoramento no CI/CD

A consolidação de todas as ferramentas foi feita no ficheiro `security-pipeline.yml`, que inclui:

- **Gatilhos Automáticos:** O pipeline é acionado a cada `push` ou `pull_request` para o branch `main`.
- **Quality Gates:** O pipeline é configurado para **falhar e bloquear o processo** caso o Snyk detete qualquer vulnerabilidade de severidade **alta** ou **crítica**.
- **Notificações em Tempo Real:** Uma integração com o **Slack** envia um alerta instantâneo para um canal da equipa caso o pipeline falhe, garantindo uma resposta rápida.
- **Validação:** A eficácia do sistema foi comprovada ao submeter código com dependências vulneráveis. O pipeline **identificou** as falhas, **bloqueou** a execução e **notificou** a equipa via Slack, demonstrando o ciclo completo de proteção DevSecOps.
