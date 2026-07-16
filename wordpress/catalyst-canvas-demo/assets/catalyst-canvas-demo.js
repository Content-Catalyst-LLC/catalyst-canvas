(function () {
  'use strict';

  const FRAMEWORKS = {
    AIDA: ['Attention: name the tension clearly', 'Interest: connect the problem to evidence', 'Desire: show a credible better state', 'Action: define one small test'],
    JTBD: ['When: identify the situation', 'I want to: name the progress sought', 'So I can: clarify the outcome', 'Constraint: expose the friction'],
    Hero: ['Ordinary world: describe current reality', 'Call: define the pressure for change', 'Guide: identify useful support', 'Return: define the improved state'],
    Matrix: ['Audience need', 'Evidence type', 'Format', 'Review signal']
  };

  const $ = (root, selector) => root.querySelector(selector);
  const $$ = (root, selector) => Array.from(root.querySelectorAll(selector));

  function clean(value, fallback) {
    const text = String(value || '').trim();
    return text || fallback;
  }

  function getState(root) {
    const field = name => {
      const el = root.querySelector('[data-field="' + name + '"]');
      return el ? el.value : '';
    };
    return {
      challenge: clean(field('challenge'), 'A team is trying to clarify a complex sustainability or systems challenge.'),
      audience: clean(field('audience'), 'A stakeholder who needs a clearer path forward'),
      goal: clean(field('goal'), 'Create a testable, evidence-aware next step'),
      constraint: clean(field('constraint'), 'Limited time, limited evidence, and competing priorities'),
      framework: clean(field('framework'), 'AIDA'),
      customIdea: clean(field('customIdea'), '')
    };
  }

  function generate(state, version) {
    const personaName = state.audience.split(',')[0].trim() || 'Primary user';
    const hmw = [
      `How might we help ${personaName} make the challenge concrete enough to act on?`,
      `How might we turn “${state.goal}” into a small testable experiment?`,
      `How might we make “${state.constraint}” visible without letting it stop progress?`,
      'How might we document assumptions so the next decision can be reviewed?'
    ];
    const ideas = (FRAMEWORKS[state.framework] || FRAMEWORKS.AIDA).map(item => `${item} — apply this to: ${state.challenge}`);
    return {
      tool: 'Catalyst Canvas Demo',
      version: version || 'unknown',
      title: 'Catalyst Canvas Brief',
      summary: `For ${state.audience}, the working challenge is: ${state.challenge}. The goal is to ${state.goal.toLowerCase()} while accounting for ${state.constraint.toLowerCase()}.`,
      personaName,
      personaBody: `Needs a practical way to make progress on “${state.challenge}” without losing sight of the constraint: ${state.constraint}.`,
      pov: `${personaName} needs a practical way to address “${state.challenge}” so they can ${state.goal.toLowerCase()} while accounting for ${state.constraint.toLowerCase()}.`,
      hmw,
      prototypeTitle: 'Reviewable Canvas Brief',
      prototypeBody: 'Create a one-page working artifact with the problem, persona, POV, HMW questions, prototype concept, assumptions, test plan, and review notes.',
      signal: 'A stakeholder can explain the problem, proposed next step, and key assumption in their own words.',
      test: 'Share the brief with 3–5 users or reviewers and capture confusion, objections, missing evidence, and next-step clarity.',
      risk: 'The brief may overstate confidence if assumptions, evidence gaps, or implementation limits are not documented.',
      ideas
    };
  }

  function setText(root, name, value) {
    const el = root.querySelector('[data-output="' + name + '"]');
    if (el) el.textContent = value;
  }

  function setList(root, name, items) {
    const el = root.querySelector('[data-output="' + name + '"]');
    if (!el) return;
    el.innerHTML = '';
    items.forEach(item => {
      const li = document.createElement('li');
      li.textContent = item;
      el.appendChild(li);
    });
  }

  function render(root, brief) {
    root._canvasBrief = brief;
    setText(root, 'briefTitle', brief.title);
    setText(root, 'summary', brief.summary);
    setText(root, 'personaName', brief.personaName);
    setText(root, 'personaBody', brief.personaBody);
    setText(root, 'pov', brief.pov);
    setList(root, 'hmw', brief.hmw);
    setText(root, 'prototypeTitle', brief.prototypeTitle);
    setText(root, 'prototypeBody', brief.prototypeBody);
    setText(root, 'signal', brief.signal);
    setText(root, 'test', brief.test);
    setText(root, 'risk', brief.risk);
    setList(root, 'ideas', brief.ideas);
  }

  function briefToText(brief) {
    return [
      '# Catalyst Canvas Brief',
      '',
      '## Summary',
      brief.summary,
      '',
      '## Persona',
      brief.personaName + ' — ' + brief.personaBody,
      '',
      '## Point of View',
      brief.pov,
      '',
      '## How Might We',
      ...brief.hmw.map(item => '- ' + item),
      '',
      '## Prototype',
      brief.prototypeTitle + ' — ' + brief.prototypeBody,
      '',
      '## Experiment Plan',
      '- Signal: ' + brief.signal,
      '- Test: ' + brief.test,
      '- Risk: ' + brief.risk,
      '',
      '## Ideas',
      ...brief.ideas.map(item => '- ' + item)
    ].join('\n');
  }

  function downloadJSON(brief) {
    const blob = new Blob([JSON.stringify(brief, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'catalyst-canvas-brief.json';
    document.body.appendChild(a);
    a.click();
    a.remove();
    URL.revokeObjectURL(url);
  }

  function init(root) {
    const actions = $$ (root, '[data-action]');
    actions.forEach(btn => {
      btn.addEventListener('click', function () {
        const action = btn.getAttribute('data-action');
        if (action === 'generate') {
          render(root, generate(getState(root), root.dataset.version));
        }
        if (action === 'add-idea') {
          const state = getState(root);
          const brief = root._canvasBrief || generate(state, root.dataset.version);
          if (state.customIdea) brief.ideas.push(state.customIdea);
          render(root, brief);
        }
        if (action === 'reset') {
          const form = $('[data-canvas-form]', root);
          if (form) form.reset();
          render(root, generate({ challenge: '', audience: '', goal: '', constraint: '', framework: 'AIDA' }, root.dataset.version));
        }
        if (action === 'copy') {
          const brief = root._canvasBrief || generate(getState(root), root.dataset.version);
          navigator.clipboard.writeText(briefToText(brief)).then(() => { btn.textContent = 'Copied'; setTimeout(() => { btn.textContent = 'Copy brief'; }, 1200); });
        }
        if (action === 'download') {
          downloadJSON(root._canvasBrief || generate(getState(root), root.dataset.version));
        }
        if (action === 'print') {
          window.print();
        }
      });
    });
  }

  document.addEventListener('DOMContentLoaded', function () {
    $$ (document, '[data-canvas-demo]').forEach(init);
  });
}());
