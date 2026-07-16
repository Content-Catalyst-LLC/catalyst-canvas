(function () {
  'use strict';

  const Engine = window.CatalystCanvasEngine;
  if (!Engine) {
    console.error('Catalyst Canvas shared engine was not loaded.');
    return;
  }

  const $ = (root, selector) => root.querySelector(selector);
  const $$ = (root, selector) => Array.from(root.querySelectorAll(selector));

  function field(root, name) {
    const element = root.querySelector('[data-field="' + name + '"]');
    return element ? element.value : '';
  }

  function inputPayload(root) {
    return {
      title: 'Catalyst Canvas Brief',
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
    if (navigator.clipboard && navigator.clipboard.writeText) {
      return navigator.clipboard.writeText(text);
    }
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
    return root._canvasContract || Engine.buildContract(inputPayload(root), 'wordpress');
  }

  function init(root) {
    $$(root, '[data-action]').forEach(button => {
      button.addEventListener('click', function () {
        const action = button.getAttribute('data-action');
        if (action === 'generate') {
          render(root, Engine.buildContract(inputPayload(root), 'wordpress'));
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
          return;
        }
        if (action === 'reset') {
          const form = $(root, '[data-canvas-form]');
          if (form) form.reset();
          render(root, Engine.buildContract({}, 'wordpress'));
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
        if (action === 'download') {
          downloadJSON(currentContract(root));
          return;
        }
        if (action === 'print') window.print();
      });
    });
  }

  document.addEventListener('DOMContentLoaded', function () {
    $$(document, '[data-canvas-demo]').forEach(init);
  });
}());
