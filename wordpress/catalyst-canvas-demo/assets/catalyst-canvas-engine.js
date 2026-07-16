(function (root, factory) {
  'use strict';
  const data = typeof module === 'object' && module.exports
    ? require('./catalyst-canvas-contract-data.js')
    : root.CatalystCanvasContractData;
  const api = factory(data);
  if (typeof module === 'object' && module.exports) module.exports = api;
  if (root) root.CatalystCanvasEngine = api;
}(typeof globalThis !== 'undefined' ? globalThis : this, function (data) {
  'use strict';

  if (!data || !data.frameworks || !data.contractVersion) {
    throw new Error('Catalyst Canvas contract data is unavailable.');
  }

  const ALIASES = {
    aida: 'AIDA',
    jtbd: 'JTBD',
    'jobs to be done': 'JTBD',
    hero: 'Hero',
    "hero's journey": 'Hero',
    'heros journey': 'Hero',
    matrix: 'Matrix',
    'content matrix': 'Matrix',
    'assumption matrix': 'Matrix'
  };

  function clean(value, fallback) {
    const text = String(value == null ? '' : value).trim();
    return text || (fallback || '');
  }

  function cleanList(value) {
    if (value == null) return [];
    if (Array.isArray(value)) return value.map(item => clean(item)).filter(Boolean);
    if (typeof value === 'string') return value.split(/\r?\n/).map(item => item.trim()).filter(Boolean);
    return clean(value) ? [clean(value)] : [];
  }

  function clone(value) {
    return JSON.parse(JSON.stringify(value));
  }

  function now() {
    return new Date().toISOString();
  }

  function randomId(prefix) {
    if (typeof crypto !== 'undefined' && typeof crypto.randomUUID === 'function') {
      return prefix + '-' + crypto.randomUUID();
    }
    return prefix + '-' + Date.now().toString(36) + '-' + Math.random().toString(36).slice(2);
  }

  function normalizeFrameworkKey(value) {
    const text = clean(value, 'AIDA');
    if (data.frameworks[text]) return text;
    return ALIASES[text.toLowerCase()] || 'AIDA';
  }

  function frameworkRecord(value) {
    const key = normalizeFrameworkKey(value);
    const record = clone(data.frameworks[key]);
    record.key = key;
    record.prompts = record.prompts.map((prompt, index) => ({
      prompt_id: 'prompt-' + String(index + 1).padStart(3, '0'),
      label: prompt.label,
      question: prompt.question
    }));
    return record;
  }

  function normalizeOwnerContext(value) {
    const source = value && typeof value === 'object' && !Array.isArray(value) ? value : {};
    return {
      owner_id: clean(source.owner_id),
      name: clean(source.name),
      organization: clean(source.organization),
      role: clean(source.role)
    };
  }

  function normalizeAudience(value) {
    if (value && typeof value === 'object' && !Array.isArray(value)) {
      return {
        primary: clean(value.primary, 'A stakeholder who needs a clearer path forward.'),
        secondary: cleanList(value.secondary),
        affected: cleanList(value.affected),
        excluded: cleanList(value.excluded)
      };
    }
    return {
      primary: clean(value, 'A stakeholder who needs a clearer path forward.'),
      secondary: [],
      affected: [],
      excluded: []
    };
  }

  function normalizeConstraints(value) {
    let raw = Array.isArray(value) ? value : (value == null ? [] : [value]);
    if (!raw.length) raw = ['Limited time, limited evidence, and competing priorities.'];
    return raw.map((item, index) => {
      const source = item && typeof item === 'object' && !Array.isArray(item) ? item : { statement: item };
      return {
        constraint_id: clean(source.constraint_id, 'constraint-' + String(index + 1).padStart(3, '0')),
        statement: clean(source.statement, 'Limited time, limited evidence, and competing priorities.'),
        source: clean(source.source, 'input')
      };
    });
  }

  function normalizePersonas(value, audience, challenge, goal, constraint) {
    let raw = Array.isArray(value) ? value : (value && typeof value === 'object' ? [value] : []);
    if (!raw.length) {
      const name = clean(audience.primary.split(',')[0], 'Primary user');
      raw = [{
        name,
        description: `Needs help addressing: ${challenge}. The user wants ${goal.toLowerCase()} while navigating ${constraint.toLowerCase()}.`,
        needs: [goal],
        pains: [constraint],
        source_type: 'assumption',
        confidence: 'low'
      }];
    }
    return raw.map((item, index) => {
      const source = item && typeof item === 'object' ? item : { name: item };
      return {
        persona_id: clean(source.persona_id, 'persona-' + String(index + 1).padStart(3, '0')),
        name: clean(source.name, 'Primary user'),
        role: clean(source.role),
        description: clean(source.description),
        needs: cleanList(source.needs),
        pains: cleanList(source.pains),
        source_type: clean(source.source_type, 'assumption'),
        confidence: clean(source.confidence, 'low')
      };
    });
  }

  function normalizeStakeholders(value) {
    const raw = Array.isArray(value) ? value : [];
    return raw.map((item, index) => {
      const source = item && typeof item === 'object' ? item : { name: item };
      return {
        stakeholder_id: clean(source.stakeholder_id, 'stakeholder-' + String(index + 1).padStart(3, '0')),
        name: clean(source.name, 'Unnamed stakeholder'),
        relationship: clean(source.relationship, 'affected'),
        influence: clean(source.influence, 'unknown'),
        interest: clean(source.interest, 'unknown'),
        notes: clean(source.notes)
      };
    });
  }

  function normalizeEvidence(value) {
    const raw = Array.isArray(value) ? value : (clean(value) ? [value] : []);
    return raw.map((item, index) => {
      const source = item && typeof item === 'object' ? item : { summary: item };
      return {
        evidence_id: clean(source.evidence_id, 'evidence-' + String(index + 1).padStart(3, '0')),
        type: clean(source.type, 'note'),
        title: clean(source.title, 'Available evidence'),
        summary: clean(source.summary),
        citation: clean(source.citation),
        confidence: clean(source.confidence, 'medium')
      };
    });
  }

  function normalizeAssumptions(value) {
    const defaults = [
      'The stated audience is the right primary user for the first iteration.',
      'The goal is specific enough to test with a small prototype.',
      'The constraint is material and should remain visible in the design process.',
      'A lightweight brief can reduce ambiguity before heavier implementation work begins.'
    ];
    const raw = Array.isArray(value) ? value : (clean(value) ? [value] : defaults);
    return raw.map((item, index) => {
      const source = item && typeof item === 'object' ? item : { statement: item };
      return {
        assumption_id: clean(source.assumption_id, 'assumption-' + String(index + 1).padStart(3, '0')),
        statement: clean(source.statement),
        status: clean(source.status, 'untested'),
        criticality: clean(source.criticality, 'medium')
      };
    });
  }

  function normalizePrototypes(value) {
    let raw = Array.isArray(value) ? value : (value ? [value] : []);
    if (!raw.length) {
      raw = [{
        title: 'Reviewable Canvas Brief',
        description: 'A one-page working artifact that captures the challenge, audience, goal, constraints, point of view, HMW prompts, prototype concept, assumptions, and test plan.'
      }];
    }
    return raw.map((item, index) => {
      const source = item && typeof item === 'object' ? item : { description: item };
      return {
        prototype_id: clean(source.prototype_id, 'prototype-' + String(index + 1).padStart(3, '0')),
        title: clean(source.title, 'Prototype concept'),
        description: clean(source.description),
        status: clean(source.status, 'concept')
      };
    });
  }

  function normalizeTests(value) {
    let raw = Array.isArray(value) ? value : (value ? [value] : []);
    if (!raw.length) {
      raw = [{
        title: 'Stakeholder clarity review',
        signal: 'A stakeholder can explain the problem, proposed next step, and key assumption in their own words.',
        method: 'Share the brief with 3–5 users or reviewers and capture confusion, objections, missing evidence, and next-step clarity.',
        learning_goal: 'Determine whether the framing is clear enough to guide a real prototype or decision.'
      }];
    }
    return raw.map((item, index) => {
      const source = item && typeof item === 'object' ? item : { method: item };
      return {
        test_id: clean(source.test_id, 'test-' + String(index + 1).padStart(3, '0')),
        title: clean(source.title, 'Learning test'),
        signal: clean(source.signal),
        method: clean(source.method),
        learning_goal: clean(source.learning_goal),
        status: clean(source.status, 'planned')
      };
    });
  }

  function normalizeReviewNotes(value) {
    const defaults = [
      { type: 'review_question', note: 'What claim in this brief needs stronger evidence?' },
      { type: 'review_question', note: 'What assumption would most change the next step if it proved false?' },
      { type: 'review_question', note: 'What user signal would show that the prototype is worth continuing?' },
      { type: 'review_question', note: 'What should be rewritten to avoid overpromising?' }
    ];
    const raw = Array.isArray(value) ? value : (clean(value) ? [value] : defaults);
    return raw.map((item, index) => {
      const source = item && typeof item === 'object' ? item : { note: item };
      return {
        review_note_id: clean(source.review_note_id, 'review-' + String(index + 1).padStart(3, '0')),
        type: clean(source.type, 'note'),
        note: clean(source.note),
        status: clean(source.status, 'open')
      };
    });
  }

  function normalizeProvenance(value, sourceSurface, migratedFrom) {
    const source = value && typeof value === 'object' && !Array.isArray(value) ? value : {};
    return {
      generator: 'catalyst-canvas',
      generator_version: data.releaseVersion,
      source_surface: clean(source.source_surface, sourceSurface),
      source_version: clean(source.source_version, data.releaseVersion),
      migrated_from: clean(source.migrated_from, migratedFrom || ''),
      warnings: cleanList(source.warnings)
    };
  }

  function validateContract(contract) {
    const required = [
      'schema_version', 'canvas_id', 'revision_id', 'title', 'status', 'owner_context',
      'created_at', 'updated_at', 'challenge', 'audience', 'goal', 'constraints', 'personas',
      'stakeholders', 'point_of_view', 'how_might_we', 'framework', 'evidence', 'assumptions',
      'prototypes', 'tests', 'review_notes', 'provenance'
    ];
    const errors = [];
    if (!contract || typeof contract !== 'object' || Array.isArray(contract)) {
      throw new Error('Canvas Contract 1.0 must be an object.');
    }
    required.forEach(key => { if (!(key in contract)) errors.push('missing ' + key); });
    if (contract.schema_version !== data.contractVersion) errors.push('unsupported schema_version');
    if (!contract.canvas_id) errors.push('canvas_id is empty');
    if (!contract.revision_id) errors.push('revision_id is empty');
    if (!contract.challenge) errors.push('challenge is empty');
    if (!contract.audience || !contract.audience.primary) errors.push('audience.primary is empty');
    if (!Array.isArray(contract.constraints) || !contract.constraints.length) errors.push('constraints is empty');
    if (!Array.isArray(contract.personas) || !contract.personas.length) errors.push('personas is empty');
    if (!Array.isArray(contract.how_might_we) || !contract.how_might_we.length) errors.push('how_might_we is empty');
    if (!contract.framework || !data.frameworks[contract.framework.key]) errors.push('framework.key is invalid');
    if (errors.length) throw new Error('Canvas Contract 1.0 validation failed: ' + errors.join('; '));
    return contract;
  }

  function buildContract(payload, sourceSurface) {
    const source = payload && typeof payload === 'object' ? payload : {};
    const challenge = clean(source.challenge, 'A team is working through an unclear sustainability or systems problem.');
    const audience = normalizeAudience(source.audience);
    const goal = clean(source.goal, 'Create a more useful, testable, and reviewable next step.');
    const constraints = normalizeConstraints(source.constraints !== undefined ? source.constraints : source.constraint);
    const constraintText = constraints[0].statement;
    const personas = normalizePersonas(source.personas !== undefined ? source.personas : source.persona, audience, challenge, goal, constraintText);
    const primaryPersona = personas[0];
    let pointOfView;
    if (source.point_of_view && typeof source.point_of_view === 'object' && !Array.isArray(source.point_of_view)) {
      pointOfView = {
        statement: clean(source.point_of_view.statement),
        persona_id: clean(source.point_of_view.persona_id, primaryPersona.persona_id)
      };
    } else {
      pointOfView = {
        statement: clean(source.point_of_view, `${primaryPersona.name} needs a practical way to address '${challenge}' so they can ${goal.toLowerCase().replace(/\.$/, '')} without ignoring the constraint: ${constraintText.replace(/\.$/, '')}.`),
        persona_id: primaryPersona.persona_id
      };
    }

    let rawHmw;
    if (Array.isArray(source.how_might_we) && source.how_might_we.length) rawHmw = source.how_might_we;
    else if (clean(source.how_might_we)) rawHmw = [source.how_might_we];
    else rawHmw = [
      `How might we help ${primaryPersona.name} make the challenge concrete enough to act on?`,
      `How might we turn the goal — ${goal.replace(/\.$/, '')} — into a small testable experiment?`,
      'How might we make the constraint visible without letting it stop progress?',
      'How might we document assumptions so the next decision can be reviewed?'
    ];
    const howMightWe = rawHmw.map((item, index) => {
      const itemSource = item && typeof item === 'object' ? item : { question: item };
      return {
        hmw_id: clean(itemSource.hmw_id, 'hmw-' + String(index + 1).padStart(3, '0')),
        question: clean(itemSource.question),
        status: clean(itemSource.status, 'candidate')
      };
    });

    const frameworkValue = source.framework && typeof source.framework === 'object'
      ? source.framework.key
      : source.framework;
    const createdAt = clean(source.created_at, now());
    const updatedAt = clean(source.updated_at, createdAt);
    const contract = {
      schema_version: data.contractVersion,
      canvas_id: clean(source.canvas_id, randomId('canvas')),
      revision_id: clean(source.revision_id, randomId('revision')),
      title: clean(source.title, 'Catalyst Canvas Brief'),
      status: clean(source.status, 'draft'),
      owner_context: normalizeOwnerContext(source.owner_context),
      created_at: createdAt,
      updated_at: updatedAt,
      challenge,
      audience,
      goal,
      constraints,
      personas,
      stakeholders: normalizeStakeholders(source.stakeholders),
      point_of_view: pointOfView,
      how_might_we: howMightWe,
      framework: frameworkRecord(frameworkValue),
      evidence: normalizeEvidence(source.evidence),
      assumptions: normalizeAssumptions(source.assumptions !== undefined ? source.assumptions : source.assumption),
      prototypes: normalizePrototypes(source.prototypes !== undefined ? source.prototypes : source.prototype),
      tests: normalizeTests(source.tests !== undefined ? source.tests : source.test_plan),
      review_notes: normalizeReviewNotes(source.review_notes !== undefined ? source.review_notes : source.review_note),
      provenance: normalizeProvenance(source.provenance, sourceSurface || 'wordpress', '')
    };
    return validateContract(contract);
  }

  function detectPayloadVersion(payload) {
    if (payload && payload.schema_version) return clean(payload.schema_version);
    if (payload && payload.inputs && payload.canvas) return 'legacy-wrapper/' + clean(payload.version, 'unknown');
    if (payload && payload.version && payload.generated_at && payload.persona) return 'legacy-core/' + clean(payload.version, 'unknown');
    if (payload && payload.challenge && payload.audience && payload.goal && payload.constraint) return 'legacy-flask/1.x';
    return 'unknown';
  }

  function migratePayload(payload) {
    const detected = detectPayloadVersion(payload);
    if (detected === data.contractVersion) return { contract: validateContract(payload), migrated_from: '', warnings: [] };
    if (detected.startsWith('catalyst-canvas/')) {
      throw new Error(`Unsupported Canvas contract '${detected}'. This release accepts '${data.contractVersion}'.`);
    }
    let compact;
    if (detected.startsWith('legacy-wrapper/')) compact = Object.assign({}, payload.inputs || {}, { title: payload.canvas && payload.canvas.title });
    else if (detected.startsWith('legacy-core/')) compact = payload;
    else if (detected === 'legacy-flask/1.x') compact = payload;
    else throw new Error('Unable to identify this Canvas payload.');
    const warning = `Migrated ${detected} to ${data.contractVersion}; review assumptions, evidence, and generated identifiers.`;
    compact = Object.assign({}, compact, {
      provenance: { source_surface: 'migration', source_version: detected, migrated_from: detected, warnings: [warning] }
    });
    return { contract: buildContract(compact, 'migration'), migrated_from: detected, warnings: [warning] };
  }

  function contractToMarkdown(contract) {
    const value = validateContract(contract);
    const persona = value.personas[0];
    const prototype = value.prototypes[0] || {};
    const test = value.tests[0] || {};
    const bullets = items => items.length ? items.map(item => '- ' + item).join('\n') : '- None recorded';
    return [
      '# ' + value.title,
      '',
      'Contract: ' + value.schema_version,
      'Canvas ID: ' + value.canvas_id,
      'Revision ID: ' + value.revision_id,
      'Status: ' + value.status,
      'Updated: ' + value.updated_at,
      '',
      '## Challenge', '', value.challenge,
      '', '## Audience', '', value.audience.primary,
      '', '## Goal', '', value.goal,
      '', '## Constraints', '', bullets(value.constraints.map(item => item.statement)),
      '', '## Primary Persona', '', `**${persona.name}** — ${persona.description}`,
      '', '## Point of View', '', value.point_of_view.statement,
      '', '## How Might We', '', bullets(value.how_might_we.map(item => item.question)),
      '', '## Ideation Framework: ' + value.framework.name, '', bullets(value.framework.prompts.map(item => `${item.label}: ${item.question}`)),
      '', '## Evidence', '', bullets(value.evidence.map(item => `${item.title}: ${item.summary}`)),
      '', '## Assumptions', '', bullets(value.assumptions.map(item => item.statement)),
      '', '## Prototype', '', `**${prototype.title || 'No prototype'}** — ${prototype.description || ''}`,
      '', '## Test Plan', '',
      '- **Title:** ' + (test.title || ''),
      '- **Signal:** ' + (test.signal || ''),
      '- **Method:** ' + (test.method || ''),
      '- **Learning goal:** ' + (test.learning_goal || ''),
      '', '## Review Notes', '', bullets(value.review_notes.map(item => item.note)),
      '', '## Provenance', '', `Generated by Catalyst Canvas ${value.provenance.generator_version} from the ${value.provenance.source_surface} surface.`,
      ''
    ].join('\n');
  }

  return {
    CONTRACT_VERSION: data.contractVersion,
    RELEASE_VERSION: data.releaseVersion,
    buildContract,
    contractToMarkdown,
    detectPayloadVersion,
    frameworkRecord,
    migratePayload,
    validateContract
  };
}));
