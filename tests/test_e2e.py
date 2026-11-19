"""Teste de interface headless isolado. Executa mesmo quando navegações localhost estão bloqueadas."""
import json
import os
import shutil
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT = Path(__file__).resolve().parents[1]

html=(ROOT/'index.html').read_text()
css=(ROOT/'styles.css').read_text()
js=(ROOT/'app.js').read_text()
html=html.replace('<link rel="stylesheet" href="./styles.css">',f'<style>{css}</style>')
html=html.replace('<script src="./app.js" defer></script>',f'<script>{js}</script>')

# As políticas do ambiente bloqueiam navegar inclusive para localhost. Por isso
# a página é montada em about:blank, com um mock persistente de localStorage.
FAKE_STORAGE="""() => {
 window.__store = new Map();
 Object.defineProperty(window, 'localStorage', {configurable:true,value:{
   getItem(k){return window.__store.has(k)?window.__store.get(k):null},
   setItem(k,v){window.__store.set(k,String(v))},
   removeItem(k){window.__store.delete(k)},
   clear(){window.__store.clear()}
 }});
 Object.defineProperty(window,'indexedDB',{configurable:true,value:{open(){throw new Error('simulated IDB failure')}}});
}"""
with sync_playwright() as p:
    chrome=os.environ.get('CHROMIUM_PATH') or shutil.which('chromium') or shutil.which('google-chrome')
    launch={'executable_path':chrome} if chrome else {}
    browser=p.chromium.launch(headless=True,args=['--no-sandbox'],**launch)
    context=browser.new_context(accept_downloads=True,viewport={'width':1440,'height':900})
    page=context.new_page()
    errors=[]
    page.on('pageerror',lambda e:errors.append(str(e)))
    page.evaluate(FAKE_STORAGE)
    page.set_content(html,wait_until='load')
    page.wait_for_timeout(200)
    assert 'Visão geral' in page.locator('#main').inner_text()
    page.get_by_role('button',name='Criar projeto').first.click()
    page.locator('#projectName').fill('Sistema de BI')
    page.locator('#projectKey').fill('BI')
    page.locator('#projectDescription').fill('Painel de indicadores')
    page.get_by_role('button',name='Salvar projeto').click()
    page.wait_for_timeout(120)
    assert page.locator('.project-link .name').inner_text()=='Sistema de BI'
    page.locator('[data-action="new-item"]').first.click()
    page.locator('#itemTitle').fill('Criar dashboard financeiro')
    page.locator('#itemDescription').fill('Cards de metas e análise de receitas.')
    page.locator('#itemPriority').select_option('urgent')
    page.locator('#itemStatus').select_option('todo')
    page.locator('#itemDue').fill('2027-01-20')
    page.locator('#itemLabels').fill('Power BI, Dados')
    page.locator('#itemForm button[type="submit"]').click()
    page.wait_for_timeout(150)
    assert 'Criar dashboard financeiro' in page.locator('.board-card').first.inner_text()
    assert page.evaluate('BacklogStudio.getStats().items')==1
    page.locator('.board-card').first.drag_to(page.locator('[data-drop-status="doing"]'))
    assert page.locator('[data-drop-status="doing"] .board-card').count()==1
    page.locator('[data-drop-status="doing"] .board-card').click()
    page.locator('#newChecklistText').fill('Modelar métricas em DAX')
    page.locator('#addChecklistBtn').click()
    assert page.locator('#itemChecklist input[type="checkbox"]').count()==1
    page.locator('#itemChecklist input[type="checkbox"]').check()
    page.locator('#newComment').fill('Modelo de dados criado e validado.')
    page.locator('#addCommentBtn').click()
    assert 'Modelo de dados criado' in page.locator('#itemComments').inner_text()
    page.locator('#itemDialog .close-dialog').first.click()
    page.wait_for_timeout(150)
    state=page.evaluate('BacklogStudio.getState()')
    assert len(state['projects'])==1 and len(state['items'])==1
    assert state['items'][0]['status']=='doing'
    assert state['items'][0]['checklist'][0]['done'] is True
    assert len(state['items'][0]['comments'])==1
    assert len(state['activities'])>=5
    print('PASS: cadastro, Kanban, checklist, comentários, histórico')
    page.locator('[data-view="list"]').first.click()
    assert 'Criar dashboard financeiro' in page.locator('table').inner_text()
    page.locator('#priorityFilter').select_option('low')
    assert page.locator('tbody tr').count()==0
    page.locator('#priorityFilter').select_option('all')
    page.locator('#searchInput').fill('financeiro')
    assert page.locator('tbody tr').count()==1
    page.locator('#searchInput').fill('nao-existe')
    assert page.locator('tbody tr').count()==0
    page.locator('#searchInput').fill('')
    page.locator('[data-view="calendar"]').first.click()
    assert page.locator('.calendar-day').count()>=28
    page.locator('[data-view="activity"]').first.click()
    assert 'Modelo de dados criado' in page.locator('#main').inner_text()
    print('PASS: filtros, busca, calendário e histórico')
    page.locator('[data-view="settings"]').first.click()
    with page.expect_download() as info:
        page.locator('[data-action="backup-json"]').first.click()
    path=ROOT/'tests'/'backup-test.json'; info.value.save_as(path)
    assert path.stat().st_size>200
    with page.expect_download() as info:
        page.locator('[data-action="backup-csv"]').first.click()
    assert info.value.suggested_filename.endswith('.csv')
    page.locator('[data-view="list"]').first.click()
    page.locator('tbody [data-action="edit-item"]').first.click()
    page.locator('#archiveItemBtn').click()
    page.locator('#confirmAccept').click()
    page.wait_for_timeout(100)
    assert page.locator('tbody tr').count()==0
    page.locator('#showArchived').check()
    assert page.locator('tbody tr').count()==1
    page.locator('tbody [data-action="edit-item"]').first.click()
    page.locator('#archiveItemBtn').click()
    page.locator('#confirmAccept').click()
    assert page.evaluate('BacklogStudio.getState().items[0].archived') is False
    print('PASS: backups JSON/CSV e arquivamento reversível')
    page.locator('[data-view="settings"]').first.click()
    page.locator('[data-action="import-json"]').first.click()
    page.locator('#importInput').set_input_files(str(path))
    page.locator('#confirmAccept').click()
    page.wait_for_timeout(140)
    assert page.evaluate('BacklogStudio.getStats().items')==1
    assert len(page.evaluate('BacklogStudio.getState().items[0].comments'))==1
    print('PASS: restauração de backup')
    # O modo de compatibilidade localStorage deve salvar o snapshot.
    persistent=page.evaluate('localStorage.getItem("backlog-studio-fallback-data")')
    assert len(json.loads(persistent)['activities'])>=5
    # Teste da restauração do estado ao inicializar uma nova sessão isolada.
    second=context.new_page()
    second.on('pageerror',lambda e:errors.append(str(e)))
    second.evaluate(FAKE_STORAGE)
    second.evaluate('(data)=>localStorage.setItem("backlog-studio-fallback-data",data)',persistent)
    second.set_content(html,wait_until='load')
    second.wait_for_timeout(150)
    assert second.evaluate('BacklogStudio.getStats().items')==1
    print('PASS: persistência do estado entre inicializações simuladas')
    assert not errors,errors
    # Verifica visualização em tela estreita.
    second.set_viewport_size({'width':390,'height':844})
    second.wait_for_timeout(400)
    second.evaluate("document.querySelector('#toastRegion').innerHTML=''")
    page.evaluate("document.querySelector('#toastRegion').innerHTML=''")
    second.screenshot(path=str(ROOT/'tests'/'mobile-preview.png'),full_page=True)
    page.screenshot(path=str(ROOT/'tests'/'desktop-preview.png'),full_page=True)
    browser.close()
    path.unlink(missing_ok=True)
    print('ALL BROWSER TESTS PASSED')
