# Backlog Studio

**Gestor pessoal de projetos e backlog, 100% no navegador, sem backend, sem banco de dados remoto e sem dependências externas.**

## O que está pronto

- Portfólio de múltiplos projetos com cor, código, descrição e link ao repositório.
- Itens de backlog com número sequencial por projeto, título, descrição e critérios de aceite, tipo, prioridade, status, responsável, sprint, estimativa, horas utilizadas, início, prazo, etiquetas e URL.
- Etapas: **Backlog → A fazer → Em andamento → Em revisão → Concluído**.
- **Kanban arrastar-e-soltar**, com edição em formulário (inclusive no celular).
- **Lista de backlog** com pesquisa, filtros e classificação.
- **Calendário** com prazos e indicação visual de itens concluídos.
- **Dashboard** com KPIs, distribuição do trabalho, progressos e prioridades.
- **Checklist**, registro de atualizações/comentários e **histórico automático de alterações por item e por projeto**.
- **Arquivamento reversível** de itens e projetos, preservando o histórico.
- **Exportação de backup JSON completo**, restauração com validação e exportação de relatório CSV.
- Salvamento automático com **IndexedDB** (e fallback em localStorage quando o IndexedDB estiver indisponível).
- Atualização entre abas do mesmo site e perfil de navegador (BroadcastChannel).
- Tema claro/escuro, interface responsiva e atalho instalável como PWA, com cache de arquivos para uso offline.
- Publicação automática no **GitHub Pages via GitHub Actions**.

## Publicar no GitHub Pages (passo a passo)

1. Acesse **https://github.com/new** e crie um repositório de nome `backlog-studio` (preferencialmente público para GitHub Pages na conta gratuita). **Não** marque a criação automática de README ou .gitignore.
2. Extraia o arquivo ZIP do projeto no computador. Entre na pasta extraída `backlog-studio`, que contém `index.html`, `app.js`, `styles.css` e a pasta oculta `.github`.
3. No terminal com Git instalado, execute os comandos abaixo **dentro da pasta do projeto**:

   ```bash
   git init
   git add .
   git commit -m "feat: adicionar Backlog Studio"
   git branch -M main
   git remote add origin https://github.com/BrendoGarcia/backlog-studio.git
   git push -u origin main
   ```

   Se o Git não estiver instalado, use o upload de arquivos da interface do GitHub, preservando a pasta `.github/workflows` e o restante da estrutura. **Não envie o ZIP fechado como único arquivo**: envie o conteúdo extraído.

4. Abra **Settings → Pages → Build and deployment → Source** e selecione **GitHub Actions**.
5. Abra a aba **Actions**, encontre **Publicar Backlog Studio no GitHub Pages** e confirme que a execução terminou com sucesso. Se ainda não houver uma execução, vá em **Actions → workflow → Run workflow**.
6. Com a publicação concluída, o endereço esperado será `https://brendogarcia.github.io/backlog-studio/` (pode variar se o nome do repositório for diferente). O GitHub Pages mostra a URL definitiva nas configurações ou no workflow.

**Atualizações futuras:** basta fazer um novo `git push` na branch `main`; a publicação é atualizada automaticamente.

### Alternativa local

Abra `index.html` em um navegador moderno. Para instalar como PWA e obter armazenamento mais previsível, prefira abrir a página publicada via HTTPS no GitHub Pages. A abertura por `file://` pode limitar as APIs de persistência em alguns navegadores.

## Onde as informações ficam salvas?

No próprio **site de origem** e no **perfil do navegador** usando IndexedDB. O GitHub contém **só os arquivos do aplicativo**, não seus itens de backlog. Alterar um projeto não cria commits e não atualiza Issues/Projects do GitHub.

**Atenção:** os dados não são sincronizados entre dispositivos, navegadores/perfis diferentes ou modo anônimo. Limpar os dados do site, redefinir o navegador ou perder o dispositivo pode excluir essas informações. Para evitar perdas:

1. Abra **Configurações → Exportar backup JSON** pelo menos semanalmente.
2. Guarde o arquivo JSON em um local independente (por exemplo, drive pessoal ou disco externo).
3. Ao trocar de aparelho, abra a mesma aplicação e use **Configurações → Restaurar backup**.
4. Use **Solicitar armazenamento protegido**, se o navegador oferecer suporte; isso reduz risco de remoção automática, mas não substitui o backup.

A aplicação não exige nem armazena tokens do GitHub. Se um backup JSON for compartilhado, **todas as informações do backlog e comentários no arquivo poderão ser lidas por quem o receber**. Não coloque backups pessoais dentro de repositórios públicos.

## Atalhos

- `N`: criar um novo item quando nenhum campo de texto estiver em foco.
- `Ctrl+K` ou `Cmd+K`: abrir a lista e focar a pesquisa.
- Arrastar cartões no Kanban: mudar o status com histórico automático.

## Arquitetura

```text
backlog-studio/
├── .github/workflows/deploy.yml    # Publicação via GitHub Actions
├── .nojekyll
├── assets/icon.svg
├── index.html                      # Interface HTML
├── styles.css                      # Layout responsivo e temas
├── app.js                          # Estado, IndexedDB, histórico e UI
├── sw.js                           # Cache offline de arquivos estáticos
├── manifest.webmanifest            # Instalação PWA
├── tests/test_e2e.py               # Testes de interface
└── README.md
```

A aplicação utiliza JavaScript puro. Não é necessário executar `npm install`, Node, Vite ou nenhum comando de build. O workflow copia os arquivos públicos para `_site` no runner do GitHub Actions e os publica no Pages.

### Testes

`node --check app.js` verifica a sintaxe. Os testes de interface usam Python + Playwright + Chromium: `python tests/test_e2e.py`. No ambiente automatizado em que o projeto foi criado, as navegações locais são bloqueadas. Por isso, a suíte monta a interface dentro do browser usando um armazenamento local simulado, e **não é um teste end-to-end de IndexedDB real ou de publicação em GitHub Pages**.

## Notas sobre histórico e exclusão

Todo evento de criação, atualização, mudança de etapa, checklist e comentário gera um registro com data e hora. Arquivar apenas oculta o item dos filtros normais: ele pode ser restaurado a qualquer momento. Ao restaurar um backup, um evento de importação é registrado no histórico recuperado. O histórico não é uma auditoria imutável, já que o proprietário do navegador controla e pode substituir os arquivos JSON e o armazenamento local.

## Licença

MIT. Código destinado a uso pessoal ou adaptação.
