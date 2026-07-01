(function () {
  'use strict';

  const STORAGE_KEY = 'catalystCanvasDemoState.v1';

  const defaults = {
    challenge: 'A nonprofit needs a clearer way to explain program impact to funders without overstating certainty.',
    audience: 'Program director at a community nonprofit',
    goal: 'build a defensible impact story with traceable indicators',
    constraint: 'limited data, small team capacity, and stakeholder pressure',
    framework: 'AIDA',
    customIdea: '',
    extraIdeas: []
  };

  const frameworkIdeas = {
    AIDA: ['Lead with the audience\'s urgent problem', 'Show the evidence behind the program claim', 'Translate impact into a concrete stakeholder benefit', 'Close with a low-friction next action'],
    JTBD: ['Name the functional job the user needs done', 'Address the emotional anxiety behind the decision', 'Reduce switching costs with a simple first step', 'Identify what current habit the prototype must replace'],
    Hero: ['Frame the user as the protagonist', 'Name the obstacle that makes progress difficult', 'Introduce the tool as a guide, not the hero', 'Show the transformed future state after the work is reviewed'],
    Matrix: ['Create one evergreen explainer', 'Create one timely update', 'Create one practical worksheet', 'Create one stakeholder-facing proof point']
  };

  function $(root, selector) { return root.querySelector(selector); }
  function $all(root, selector) { return Array.from(root.querySelectorAll(selector)); }

  function clean(value, fallback) {
    const text = String(value || '').trim();
    return text || fallback;
  }

  function loadState() {
    try {
      const raw = window.localStorage.getItem(STORAGE_KEY);
      return raw ? Object.assign({}, defaults, JSON.parse(raw)) : Object.assign({}, defaults);
    } catch (error) {
      return Object.assign({}, defaults);
    }
  }

  function saveState(state) {
    try { window.localStorage.setItem(STORAGE_KEY, JSON.stringify(state)); } catch (error) {}
  }

  function collect(root, prior) {
    const next = Object.assign({}, prior || defaults);
    $all(root, '[data-field]').forEach(function (field) {
      next[field.getAttribute('data-field')] = field.value;
    });
    next.challenge = clean(next.challenge, defaults.challenge);
    next.audience = clean(next.audience, defaults.audience);
    next.goal = clean(next.goal, defaults.goal);
    next.constraint = clean(next.constraint, defaults.constraint);
    next.framework = clean(next.framework, defaults.framework);
    if (!Array.isArray(next.extraIdeas)) next.extraIdeas = [];
    return next;
  }

  function hydrate(root, state) {
    $all(root, '[data-field]').forEach(function (field) {
      const key = field.getAttribute('data-field');
      if (typeof state[key] !== 'undefined') field.value = state[key];
    });
  }

  function sentence(text) {
    const value = clean(text, '').replace(/\s+/g, ' ');
    if (!value) return '';
    return value.charAt(0).toUpperCase() + value.slice(1).replace(/[.!?]*$/, '') + '.';
  }

  function buildCanvas(state) {
    const challenge = clean(state.challenge, defaults.challenge);
    const audience = clean(state.audience, defaults.audience);
    const goal = clean(state.goal, defaults.goal);
    const constraint = clean(state.constraint, defaults.constraint);
    const framework = frameworkIdeas[state.framework] ? state.framework : 'AIDA';
    const ideas = frameworkIdeas[framework].concat(state.extraIdeas || []);

    return {
      title: 'Catalyst Canvas draft for ' + audience,
      summary: sentence('This canvas frames a design challenge for ' + audience + ': ' + challenge + ' The working goal is to ' + goal + ' while accounting for ' + constraint),
      personaName: audience,
      personaBody: sentence(audience + ' is trying to ' + goal + ' but faces ' + constraint + ' The persona needs clear evidence, usable structure, and a next step that does not overpromise'),
      pov: sentence(audience + ' needs a way to ' + goal + ' because ' + challenge + ' The solution must respect ' + constraint),
      hmw: [
        'How might we help ' + audience + ' make progress without hiding uncertainty?',
        'How might we turn the challenge into a testable workflow?',
        'How might we make evidence, assumptions, and next steps visible?',
        'How might we reduce friction created by ' + constraint + '?'
      ],
      ideas: ideas,
      prototypeTitle: framework + ' concept card',
      prototypeBody: sentence('Build a lightweight prototype that helps ' + audience + ' ' + goal + ' It should expose sources, assumptions, and decision points before a final recommendation is made'),
      testWhat: 'Whether the draft canvas helps the user explain the problem, evidence, and next step more clearly.',
      testSignal: 'A reviewer can identify the claim, source, assumption, and recommended next action without extra explanation.',
      testRisk: 'The prototype may still overstate confidence if data quality and uncertainty are not made explicit.',
      nextStep: 'Run the canvas with one real stakeholder and revise the claim, indicator, and prototype before publishing.'
    };
  }

  function renderList(node, items) {
    if (!node) return;
    node.innerHTML = '';
    items.forEach(function (item) {
      const li = document.createElement('li');
      li.textContent = item;
      node.appendChild(li);
    });
  }

  function render(root, state) {
    const canvas = buildCanvas(state);
    const setters = {
      briefTitle: canvas.title,
      summary: canvas.summary,
      personaName: canvas.personaName,
      personaBody: canvas.personaBody,
      pov: canvas.pov,
      prototypeTitle: canvas.prototypeTitle,
      prototypeBody: canvas.prototypeBody,
      testWhat: canvas.testWhat,
      testSignal: canvas.testSignal,
      testRisk: canvas.testRisk,
      nextStep: canvas.nextStep
    };

    Object.keys(setters).forEach(function (key) {
      const node = $(root, '[data-output="' + key + '"]');
      if (node) node.textContent = setters[key];
    });
    renderList($(root, '[data-output="hmw"]'), canvas.hmw);
    renderList($(root, '[data-output="ideas"]'), canvas.ideas);
    saveState(state);
    return canvas;
  }

  function makeExport(state) {
    return {
      generated_at: new Date().toISOString(),
      tool: 'Catalyst Canvas Demo',
      version: '1.0.0',
      inputs: {
        challenge: state.challenge,
        audience: state.audience,
        goal: state.goal,
        constraint: state.constraint,
        framework: state.framework
      },
      canvas: buildCanvas(state),
      boundary: 'Demo output for structured design thinking only. Review before relying on it.'
    };
  }

  function copyText(text) {
    if (navigator.clipboard && navigator.clipboard.writeText) return navigator.clipboard.writeText(text);
    const area = document.createElement('textarea');
    area.value = text;
    document.body.appendChild(area);
    area.select();
    document.execCommand('copy');
    document.body.removeChild(area);
    return Promise.resolve();
  }

  function downloadJSON(state) {
    const data = JSON.stringify(makeExport(state), null, 2);
    const blob = new Blob([data], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = 'catalyst-canvas-demo-export.json';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  }

  function init(root) {
    let state = loadState();
    hydrate(root, state);
    render(root, state);

    root.addEventListener('click', function (event) {
      const button = event.target.closest('[data-action]');
      if (!button || !root.contains(button)) return;
      const action = button.getAttribute('data-action');
      state = collect(root, state);

      if (action === 'generate') {
        render(root, state);
      }

      if (action === 'add-idea') {
        const idea = clean(state.customIdea, '');
        if (idea) {
          state.extraIdeas = (state.extraIdeas || []).concat(idea);
          state.customIdea = '';
          const custom = $(root, '[data-field="customIdea"]');
          if (custom) custom.value = '';
          render(root, state);
        }
      }

      if (action === 'reset') {
        try { window.localStorage.removeItem(STORAGE_KEY); } catch (error) {}
        state = Object.assign({}, defaults, { extraIdeas: [] });
        hydrate(root, state);
        render(root, state);
      }

      if (action === 'copy') {
        copyText(JSON.stringify(makeExport(state), null, 2)).then(function () {
          const old = button.textContent;
          button.textContent = 'Copied';
          setTimeout(function () { button.textContent = old; }, 1200);
        });
      }

      if (action === 'download') downloadJSON(state);
      if (action === 'print') window.print();
    });

    root.addEventListener('input', function (event) {
      if (!event.target.matches('[data-field]')) return;
      state = collect(root, state);
      saveState(state);
    });
  }

  document.addEventListener('DOMContentLoaded', function () {
    document.querySelectorAll('[data-canvas-demo]').forEach(init);
  });
})();

