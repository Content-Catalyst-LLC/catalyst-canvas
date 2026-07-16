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

  function lines(value) { return String(value || '').split(/\r?\n/).map(item => item.trim()).filter(Boolean); }

  function parseStakeholders(value) {
    return lines(value).map((line, index) => {
      const parts = line.split('|').map(item => item.trim());
      const list = text => String(text || '').split(';').map(item => item.trim()).filter(Boolean);
      return {
        stakeholder_id: 'stakeholder-' + String(index + 1).padStart(3, '0'),
        name: parts[0] || 'Stakeholder ' + (index + 1),
        stakeholder_type: parts[1] || 'other', influence: parts[2] || 3, interest: parts[3] || 3, impact: parts[4] || 3,
        stance: parts[5] || 'unknown', decision_role: parts[6] || 'affected', engagement_strategy: parts[7] || '',
        responsibilities: list(parts[8]), tensions: list(parts[9]), notes: parts[10] || ''
      };
    });
  }

  function parseJourneyStages(value) {
    return lines(value).map((line, index) => {
      const parts = line.split('|').map(item => item.trim());
      const list = text => String(text || '').split(';').map(item => item.trim()).filter(Boolean);
      const ids = text => String(text || '').split(',').map(item => item.trim()).filter(Boolean);
      return { stage_id:'stage-' + String(index + 1).padStart(3,'0'), name:parts[0] || 'Stage ' + (index + 1), actions:list(parts[1]), questions:list(parts[2]), emotion:parts[3] || 0, frictions:list(parts[4]), opportunities:list(parts[5]), touchpoints:list(parts[6]), channels:list(parts[7]), metrics:list(parts[8]), owner:parts[9] || '', evidence_ids:ids(parts[10]), experiment_ids:ids(parts[11]) };
    });
  }

  function parseAttributes(value) {
    return lines(value).map((line,index)=>{const parts=line.split('|').map(item=>item.trim());return {attribute_id:'attribute-'+String(index+1).padStart(3,'0'),category:parts[0]||'other',statement:parts[1]||'',basis:parts[2]||'assumed',confidence:parts[3]||'low',evidence_ids:String(parts[4]||'').split(',').map(item=>item.trim()).filter(Boolean),notes:parts[5]||''};}).filter(item=>item.statement);
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
      audience: {primary:field(root,'audience'),secondary:lines(field(root,'audienceSecondary')),affected:lines(field(root,'audienceAffected')),excluded:lines(field(root,'audienceExcluded'))},
      goal: field(root, 'goal'),
      constraint: field(root, 'constraint'),
      persona: {
        persona_id: existing.personas && existing.personas[0] ? existing.personas[0].persona_id : undefined,
        name: field(root, 'personaName') || field(root, 'audience'),
        role: field(root, 'personaRole'), description: field(root, 'personaContext'), context: field(root, 'personaContext'),
        jobs:lines(field(root,'personaJobs')), goals: lines(field(root, 'personaGoals')), needs: lines(field(root, 'personaNeeds')), pains: lines(field(root, 'personaPains')), gains:lines(field(root,'personaGains')), behaviors: lines(field(root, 'personaBehaviors')), barriers:lines(field(root,'personaBarriers')), motivations:lines(field(root,'personaMotivations')), accessibility_needs: lines(field(root, 'personaAccessibility')), preferred_channels:lines(field(root,'personaChannels')), quotes:lines(field(root,'personaQuotes')),
        empathy_map:{says:lines(field(root,'empathySays')),thinks:lines(field(root,'empathyThinks')),does:lines(field(root,'empathyDoes')),feels:lines(field(root,'empathyFeels')),sees:lines(field(root,'empathySees')),hears:lines(field(root,'empathyHears'))},
        attributes:parseAttributes(field(root,'personaAttributes')), evidence_ids:lines(field(root,'personaEvidenceIds')), assumption_ids:lines(field(root,'personaAssumptionIds')), tags:lines(field(root,'personaTags')),
        source_type: field(root, 'personaSource') || 'assumption', source_notes:field(root,'personaSourceNotes'), confidence: field(root, 'personaConfidence') || 'low', confidence_notes:field(root,'personaConfidenceNotes'), validation_status: field(root, 'personaValidation') || 'hypothesis'
      },
      stakeholders: parseStakeholders(field(root, 'stakeholders')),
      journeys: field(root, 'journeyTitle') || field(root, 'journeyStages') ? [{
        journey_id: existing.journeys && existing.journeys[0] ? existing.journeys[0].journey_id : undefined,
        title: field(root, 'journeyTitle') || 'Primary experience journey',
        persona_id: existing.personas && existing.personas[0] ? existing.personas[0].persona_id : 'persona-001',
        scenario: field(root, 'journeyScenario'), desired_outcome: field(root, 'journeyOutcome') || field(root, 'goal'),
        status: field(root,'journeyStatus') || 'draft', stages: parseJourneyStages(field(root, 'journeyStages'))
      }] : [],
      behavioral_signals:Engine.parseBehavioralSignalCsv(field(root,'behavioralSignalCsv'),field(root,'behavioralSignalSource')||'analytics_csv'),
      framework: field(root, 'framework'),
      provenance: { source_surface: 'wordpress', source_version: root.dataset.version || Engine.RELEASE_VERSION, warnings: [] }
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
    setText(root, 'personaBody', persona.description || persona.context || `Needs a practical way to make progress on “${contract.challenge}” without losing sight of the constraint: ${contract.constraints[0].statement}.`);
    setText(root, 'researchReadiness', contract.research_summary.readiness.replace(/_/g, ' '));
    setText(root, 'stakeholderCount', contract.research_summary.stakeholder_count + ' mapped');
    setText(root, 'journeyCount', contract.research_summary.journey_count + ' mapped');
    setText(root, 'signalCount', contract.research_summary.behavioral_signal_count + ' hints');
    setList(root, 'stakeholderSummary', contract.stakeholders.map(item => `${item.name}: influence ${item.influence}/5, interest ${item.interest}/5 — ${item.engagement_strategy || item.stance}`));
    const journey = contract.journeys[0];
    setList(root, 'journeySummary', journey ? journey.stages.map(stage => `${stage.sequence}. ${stage.name}: ${stage.actions.join('; ') || 'No action recorded'} (emotion ${stage.emotion})`) : []);
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
    const persona = contract.personas[0] || {};
    setField(root,'audienceSecondary',(contract.audience.secondary||[]).join('\n')); setField(root,'audienceAffected',(contract.audience.affected||[]).join('\n')); setField(root,'audienceExcluded',(contract.audience.excluded||[]).join('\n'));
    setField(root, 'personaName', persona.name); setField(root,'personaRole',persona.role); setField(root, 'personaContext', persona.context || persona.role);
    setField(root,'personaJobs',(persona.jobs||[]).join('\n')); setField(root, 'personaGoals', (persona.goals || []).join('\n')); setField(root,'personaNeeds',(persona.needs||[]).join('\n')); setField(root, 'personaBehaviors', (persona.behaviors || []).join('\n')); setField(root, 'personaPains', (persona.pains || []).join('\n')); setField(root,'personaGains',(persona.gains||[]).join('\n')); setField(root,'personaBarriers',(persona.barriers||[]).join('\n')); setField(root,'personaMotivations',(persona.motivations||[]).join('\n')); setField(root, 'personaAccessibility', (persona.accessibility_needs || []).join('\n')); setField(root,'personaChannels',(persona.preferred_channels||[]).join('\n')); setField(root,'personaQuotes',(persona.quotes||[]).join('\n')); setField(root,'personaEvidenceIds',(persona.evidence_ids||[]).join('\n')); setField(root,'personaAssumptionIds',(persona.assumption_ids||[]).join('\n')); setField(root,'personaTags',(persona.tags||[]).join('\n'));
    setField(root,'empathySays',(persona.empathy_map&&persona.empathy_map.says||[]).join('\n')); setField(root,'empathyThinks',(persona.empathy_map&&persona.empathy_map.thinks||[]).join('\n')); setField(root,'empathyDoes',(persona.empathy_map&&persona.empathy_map.does||[]).join('\n')); setField(root,'empathyFeels',(persona.empathy_map&&persona.empathy_map.feels||[]).join('\n')); setField(root,'empathySees',(persona.empathy_map&&persona.empathy_map.sees||[]).join('\n')); setField(root,'empathyHears',(persona.empathy_map&&persona.empathy_map.hears||[]).join('\n'));
    setField(root,'personaAttributes',(persona.attributes||[]).map(item=>[item.category,item.statement,item.basis,item.confidence,(item.evidence_ids||[]).join(', '),item.notes].join(' | ')).join('\n'));
    setField(root, 'personaSource', persona.source_type); setField(root,'personaSourceNotes',persona.source_notes); setField(root, 'personaConfidence', persona.confidence); setField(root,'personaConfidenceNotes',persona.confidence_notes); setField(root, 'personaValidation', persona.validation_status);
    setField(root, 'stakeholders', contract.stakeholders.map(item => [item.name,item.stakeholder_type,item.influence,item.interest,item.impact,item.stance,item.decision_role,item.engagement_strategy,(item.responsibilities||[]).join('; '),(item.tensions||[]).join('; '),item.notes].join(' | ')).join('\n'));
    const journey = contract.journeys[0] || {};
    setField(root, 'journeyTitle', journey.title); setField(root, 'journeyScenario', journey.scenario); setField(root, 'journeyOutcome', journey.desired_outcome); setField(root,'journeyStatus',journey.status);
    setField(root, 'journeyStages', (journey.stages || []).map(stage => [stage.name,(stage.actions||[]).join('; '),(stage.questions||[]).join('; '),stage.emotion,(stage.frictions||[]).join('; '),(stage.opportunities||[]).join('; '),(stage.touchpoints||[]).join('; '),(stage.channels||[]).join('; '),(stage.metrics||[]).join('; '),stage.owner,(stage.evidence_ids||[]).join(', '),(stage.experiment_ids||[]).join(', ')].join(' | ')).join('\n'));
    setField(root,'behavioralSignalSource',contract.behavioral_signals[0]?contract.behavioral_signals[0].source_type:'analytics_csv');
    setField(root,'behavioralSignalCsv',contract.behavioral_signals.length?'metric,segment,value,period,interpretation,limitation,evidence_ids,tags\n'+contract.behavioral_signals.map(item=>[item.metric,item.segment,item.value,item.period,item.interpretation,item.limitation,(item.evidence_ids||[]).join(';'),(item.tags||[]).join(';')].join(',')).join('\n'):'');
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
    const comparison = root.querySelector('[data-output="researchComparison"]');
    if (comparison) {
      comparison.innerHTML = '';
      store.list('active').forEach(project => {
        const canvas=store.currentCanvas(project.project_id); if(!canvas)return;
        const card=document.createElement('article'); card.className='ccanvasdemo-mini';
        const persona=canvas.personas&&canvas.personas[0]||{}; const journey=canvas.journeys&&canvas.journeys[0]||{};
        const title=document.createElement('strong'); title.textContent=project.title; card.appendChild(title);
        const text=document.createElement('p'); text.textContent=(persona.name||'No persona')+' · '+(persona.source_type||'assumption')+' · '+((journey.stages||[]).length)+' journey stages'; card.appendChild(text); comparison.appendChild(card);
      });
    }
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

    const signalFile = root.querySelector('[data-field="behavioralSignalFile"]');
    if (signalFile) signalFile.addEventListener('change', function () {
      const file = signalFile.files && signalFile.files[0];
      if (!file) return;
      if (!/\.csv$/i.test(file.name) || file.size > 2000000) {
        setWorkspaceStatus(root, 'Choose a UTF-8 CSV file no larger than 2 MB.', 'error');
        signalFile.value = '';
        return;
      }
      const reader = new FileReader();
      reader.onload = function () { setField(root, 'behavioralSignalCsv', String(reader.result || '')); render(root, buildFromInputs(root)); queueAutosave(); };
      reader.onerror = function () { setWorkspaceStatus(root, 'The CSV file could not be read.', 'error'); };
      reader.readAsText(file, 'UTF-8');
    });

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
          if (action === 'apply-persona-template') {
            const key=field(root,'personaTemplate'), template=Engine.PERSONA_TEMPLATES[key];
            if(!template) throw new Error('Choose a persona template first.');
            setField(root,'personaName',template.name); setField(root,'personaRole',template.role); setField(root,'personaContext',template.context); setField(root,'personaJobs',(template.jobs||[]).join('\n')); setField(root,'personaNeeds',(template.needs||[]).join('\n')); setField(root,'personaBarriers',(template.barriers||[]).join('\n')); setField(root,'personaMotivations',(template.motivations||[]).join('\n')); setField(root,'personaTags',(template.tags||[]).join('\n')); setField(root,'personaSource','assumption'); setField(root,'personaConfidence','low'); setField(root,'personaValidation','hypothesis');
            queueAutosave(); return;
          }
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
