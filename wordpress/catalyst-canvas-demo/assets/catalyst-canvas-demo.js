(function () {
  'use strict';

  const Engine = window.CatalystCanvasEngine;
  const Workspace = window.CatalystCanvasWorkspace;
  if (!Engine || !Workspace) {
    console.error('Catalyst Canvas shared engine or workspace manager was not loaded.');
    return;
  }

  const $ = (root, selector) => root.querySelector(selector);
  const $$ = (root, selector) => Array.from(root.querySelectorAll(selector));

  function field(root, name) {
    const element = root.querySelector('[data-field="' + name + '"]');
    return element ? element.value : '';
  }

  function projectTitle(root) {
    const element = root.querySelector('[data-workspace-field="title"]');
    return element ? String(element.value || '').trim() : '';
  }

  function inputPayload(root) {
    const existing = root._canvasContract || {};
    return {
      canvas_id: existing.canvas_id,
      revision_id: existing.revision_id,
      created_at: existing.created_at,
      title: projectTitle(root) || existing.title || 'Catalyst Canvas Brief',
      challenge: field(root, 'challenge'),
      audience: field(root, 'audience'),
      goal: field(root, 'goal'),
      constraint: field(root, 'constraint'),
      framework: field(root, 'framework'),
      provenance: {
        source_surface: 'wordpress',
        source_version: root.dataset.version || Engine.RELEASE_VERSION,
        warnings: []
      }
    };
  }

  function setText(root, name, value) {
    const element = root.querySelector('[data-output="' + name + '"]');
    if (element) element.textContent = value;
  }

  function setList(root, name, items) {
    const element = root.querySelector('[data-output="' + name + '"]');
    if (!element) return;
    element.innerHTML = '';
    items.forEach(item => {
      const li = document.createElement('li');
      li.textContent = item;
      element.appendChild(li);
    });
  }

  function setField(root, name, value) {
    const element = root.querySelector('[data-field="' + name + '"]');
    if (element) element.value = value || '';
  }

  function setWorkspaceStatus(root, text, state) {
    const element = root.querySelector('[data-workspace-status]');
    if (!element) return;
    element.textContent = text;
    element.dataset.state = state || 'idle';
  }

  function buildFromInputs(root) {
    const existing = root._canvasContract || null;
    const contract = Engine.buildContract(inputPayload(root), 'wordpress');
    if (existing && existing.framework && contract.framework && existing.framework.key === contract.framework.key) {
      const custom = (existing.framework.prompts || []).filter(item => item.label === 'Custom idea');
      contract.framework.prompts = contract.framework.prompts.concat(custom);
    }
    return Engine.validateContract(contract);
  }

  function summary(contract) {
    return `For ${contract.audience.primary}, the working challenge is: ${contract.challenge}. The goal is to ${contract.goal.toLowerCase()} while accounting for ${contract.constraints[0].statement.toLowerCase()}.`;
  }

  function render(root, contract) {
    Engine.validateContract(contract);
    root._canvasContract = contract;
    const persona = contract.personas[0];
    const prototype = contract.prototypes[0] || {};
    const test = contract.tests[0] || {};
    const risk = contract.review_notes.find(item => item.type === 'risk') || contract.review_notes[0] || {};

    setText(root, 'briefTitle', contract.title);
    setText(root, 'contractVersion', contract.schema_version);
    setText(root, 'summary', summary(contract));
    setText(root, 'personaName', persona.name);
    setText(root, 'personaBody', persona.description || `Needs a practical way to make progress on “${contract.challenge}” without losing sight of the constraint: ${contract.constraints[0].statement}.`);
    setText(root, 'pov', contract.point_of_view.statement);
    setList(root, 'hmw', contract.how_might_we.map(item => item.question));
    setText(root, 'prototypeTitle', prototype.title || 'Prototype concept');
    setText(root, 'prototypeBody', prototype.description || 'No prototype recorded.');
    setText(root, 'signal', test.signal || 'No signal recorded.');
    setText(root, 'test', test.method || 'No test method recorded.');
    setText(root, 'risk', risk.note || 'Review assumptions and evidence gaps before relying on this brief.');
    setList(root, 'ideas', contract.framework.prompts.map(item => `${item.label}: ${item.question} — apply this to: ${contract.challenge}`));
  }

  function populate(root, contract) {
    setField(root, 'challenge', contract.challenge);
    setField(root, 'audience', contract.audience.primary);
    setField(root, 'goal', contract.goal);
    setField(root, 'constraint', contract.constraints[0] ? contract.constraints[0].statement : '');
    setField(root, 'framework', contract.framework.key);
    const title = root.querySelector('[data-workspace-field="title"]');
    if (title) title.value = contract.title || 'Untitled Canvas Project';
    render(root, contract);
  }

  function downloadJSON(contract) {
    Engine.validateContract(contract);
    const blob = new Blob([JSON.stringify(contract, null, 2) + '\n'], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = contract.canvas_id + '.json';
    document.body.appendChild(link);
    link.click();
    link.remove();
    URL.revokeObjectURL(url);
  }

  function copyText(text) {
    if (navigator.clipboard && navigator.clipboard.writeText) return navigator.clipboard.writeText(text);
    const area = document.createElement('textarea');
    area.value = text;
    area.setAttribute('readonly', 'readonly');
    area.style.position = 'fixed';
    area.style.opacity = '0';
    document.body.appendChild(area);
    area.select();
    document.execCommand('copy');
    area.remove();
    return Promise.resolve();
  }

  function currentContract(root) {
    return root._canvasContract || buildFromInputs(root);
  }

  function refreshProjects(root, store) {
    const select = root.querySelector('[data-workspace-project]');
    if (!select) return;
    const active = store.active();
    select.innerHTML = '';
    const blank = document.createElement('option');
    blank.value = '';
    blank.textContent = 'New unsaved project';
    select.appendChild(blank);
    store.list('all').forEach(project => {
      const option = document.createElement('option');
      option.value = project.project_id;
      option.textContent = `${project.status === 'archived' ? '[Archived] ' : ''}${project.title} · ${project.revision_count} revisions`;
      select.appendChild(option);
    });
    select.value = active ? active.project_id : '';
  }

  function saveProject(root, store, autosave) {
    let contract = buildFromInputs(root);
    const active = store.active();
    let project;
    if (active) project = store.save(active.project_id, contract, { autosave: Boolean(autosave), title: projectTitle(root) });
    else project = store.create(contract, projectTitle(root) || contract.title);
    contract = store.currentCanvas(project.project_id);
    populate(root, contract);
    refreshProjects(root, store);
    setWorkspaceStatus(root, autosave ? 'Autosaved in this browser.' : 'Project and revision saved in this browser.', 'saved');
    return project;
  }

  function init(root) {
    const store = Workspace.createStore(window.localStorage);
    let autosaveTimer = null;

    function queueAutosave() {
      if (!store.active()) return;
      clearTimeout(autosaveTimer);
      setWorkspaceStatus(root, 'Unsaved browser changes.', 'idle');
      autosaveTimer = setTimeout(function () {
        try { saveProject(root, store, true); }
        catch (error) { setWorkspaceStatus(root, error.message || 'Autosave failed.', 'error'); }
      }, 900);
    }

    const active = store.active();
    if (active) {
      const canvas = store.currentCanvas(active.project_id);
      if (canvas) populate(root, canvas);
    } else {
      render(root, Engine.buildContract({}, 'wordpress'));
    }
    refreshProjects(root, store);

    const form = $(root, '[data-canvas-form]');
    if (form) {
      form.addEventListener('input', queueAutosave);
      form.addEventListener('change', queueAutosave);
    }
    const titleInput = root.querySelector('[data-workspace-field="title"]');
    if (titleInput) titleInput.addEventListener('input', queueAutosave);

    const projectSelect = root.querySelector('[data-workspace-project]');
    if (projectSelect) projectSelect.addEventListener('change', function () {
      const selected = store.get(projectSelect.value);
      if (!selected) {
        store.setActive('');
        root._selectedArchivedProject = '';
        root._canvasContract = null;
        if (form) form.reset();
        if (titleInput) titleInput.value = 'Untitled Canvas Project';
        render(root, Engine.buildContract({}, 'wordpress'));
        setWorkspaceStatus(root, 'New unsaved project.', 'idle');
        return;
      }
      if (selected.status === 'archived') {
        store.setActive('');
        root._selectedArchivedProject = selected.project_id;
        const archivedCanvas = store.currentCanvas(selected.project_id);
        if (archivedCanvas) populate(root, archivedCanvas);
        projectSelect.value = selected.project_id;
        setWorkspaceStatus(root, `Archived project selected. Restore ${selected.title} to edit it.`, 'idle');
        return;
      }
      root._selectedArchivedProject = '';
      const project = store.setActive(selected.project_id);
      const canvas = store.currentCanvas(project.project_id);
      if (canvas) populate(root, canvas);
      setWorkspaceStatus(root, `Opened ${project.title}.`, 'saved');
      refreshProjects(root, store);
    });

    $$(root, '[data-action]').forEach(button => {
      button.addEventListener('click', function () {
        const action = button.getAttribute('data-action');
        try {
          if (action === 'generate') {
            render(root, buildFromInputs(root));
            queueAutosave();
            return;
          }
          if (action === 'add-idea') {
            const idea = String(field(root, 'customIdea') || '').trim();
            const contract = JSON.parse(JSON.stringify(currentContract(root)));
            if (idea) {
              contract.framework.prompts.push({
                prompt_id: 'prompt-' + String(contract.framework.prompts.length + 1).padStart(3, '0'),
                label: 'Custom idea',
                question: idea
              });
            }
            render(root, Engine.validateContract(contract));
            queueAutosave();
            return;
          }
          if (action === 'reset' || action === 'new-project') {
            store.setActive('');
            root._canvasContract = null;
            if (form) form.reset();
            if (titleInput) titleInput.value = 'Untitled Canvas Project';
            render(root, Engine.buildContract({}, 'wordpress'));
            refreshProjects(root, store);
            setWorkspaceStatus(root, 'New unsaved project.', 'idle');
            return;
          }
          if (action === 'save-project') {
            saveProject(root, store, false);
            return;
          }
          if (action === 'duplicate-project') {
            const current = store.active();
            if (!current) { saveProject(root, store, false); return; }
            const duplicate = store.duplicate(current.project_id, projectTitle(root) + ' Copy');
            const canvas = store.currentCanvas(duplicate.project_id);
            if (canvas) populate(root, canvas);
            refreshProjects(root, store);
            setWorkspaceStatus(root, 'Project duplicated with independent revision history.', 'saved');
            return;
          }
          if (action === 'archive-project') {
            const current = store.active();
            if (!current) throw new Error('Save the project before archiving it.');
            store.archive(current.project_id);
            root._canvasContract = null;
            if (form) form.reset();
            if (titleInput) titleInput.value = 'Untitled Canvas Project';
            render(root, Engine.buildContract({}, 'wordpress'));
            refreshProjects(root, store);
            setWorkspaceStatus(root, 'Project archived in this browser.', 'saved');
            return;
          }
          if (action === 'restore-project') {
            const selectedId = root._selectedArchivedProject || (projectSelect ? projectSelect.value : '');
            const selected = store.get(selectedId);
            if (!selected || selected.status !== 'archived') throw new Error('Select an archived project to restore.');
            const restored = store.restore(selected.project_id);
            root._selectedArchivedProject = '';
            const canvas = store.currentCanvas(restored.project_id);
            if (canvas) populate(root, canvas);
            refreshProjects(root, store);
            setWorkspaceStatus(root, 'Project restored and ready to edit.', 'saved');
            return;
          }
          if (action === 'copy') {
            copyText(Engine.contractToMarkdown(currentContract(root))).then(() => {
              const original = button.textContent;
              button.textContent = 'Copied';
              setTimeout(() => { button.textContent = original; }, 1200);
            });
            return;
          }
          if (action === 'download') { downloadJSON(currentContract(root)); return; }
          if (action === 'print') window.print();
        } catch (error) {
          setWorkspaceStatus(root, error.message || 'Workspace action failed.', 'error');
        }
      });
    });
  }

  document.addEventListener('DOMContentLoaded', function () {
    $$(document, '[data-canvas-demo]').forEach(init);
  });
}());
