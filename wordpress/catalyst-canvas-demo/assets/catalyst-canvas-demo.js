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

  function pipeRows(value, count) { return lines(value).map(line => { const parts=line.split('|').map(item=>item.trim()); while(parts.length<count)parts.push(''); return parts; }); }
  function ids(value){return String(value||'').replace(/;/g,',').split(',').map(item=>item.trim()).filter(Boolean);}
  function parseSources(value){return pipeRows(value,10).filter(p=>p[1]).map((p,i)=>({source_id:'source-'+String(i+1).padStart(3,'0'),source_type:p[0]||'other',title:p[1],creator:p[2],publisher:'',source_date:p[3],accessed_at:'',url:p[4],owner:p[5],description:p[9],rights:'',limitations:ids(p[6]),tags:ids(p[7]),knowledge_library_record_id:p[8],provenance_note:''}));}
  function parseEvidence(value){return pipeRows(value,10).filter(p=>p[0]||p[3]||p[4]).map((p,i)=>({evidence_id:'evidence-'+String(i+1).padStart(3,'0'),source_id:p[2],evidence_type:p[1]||'note',title:p[0]||'Evidence record',summary:p[3],quote:p[4],locator:p[5],citation:p[6],url:'',captured_at:'',captured_by:'',confidence:p[7]||'unknown',limitations:ids(p[8]),contradiction_ids:[],tags:ids(p[9])}));}
  function parseClaims(value){return pipeRows(value,12).filter(p=>p[1]).map((p,i)=>({claim_id:'claim-'+String(i+1).padStart(3,'0'),state:p[0]||'unsupported',statement:p[1],owner:p[2],confidence:p[3]||'unknown',evidence_ids:ids(p[4]),assumption_ids:ids(p[5]),source_ids:[],uncertainty:p[6],limitations:ids(p[7]),contradictions:ids(p[8]),missing_data:ids(p[9]),review_status:p[10]||'draft',reviewed_by:'',reviewed_at:'',updated_at:'',tags:ids(p[11])}));}
  function parseAssumptions(value){return pipeRows(value,12).filter(p=>p[1]).map((p,i)=>({assumption_id:'assumption-'+String(i+1).padStart(3,'0'),criticality:p[0]||'medium',statement:p[1],owner:p[2],confidence:p[3]||'unknown',consequence:p[4],test_method:p[5],status:p[6]||'untested',experiment_ids:ids(p[7]),evidence_ids:ids(p[8]),due_date:p[9],limitations:ids(p[10]),tags:ids(p[11])}));}
  function parseResearchQuestions(value){return pipeRows(value,8).filter(p=>p[1]).map((p,i)=>({research_question_id:'research-question-'+String(i+1).padStart(3,'0'),priority:p[0]||'medium',question:p[1],owner:p[2],status:p[3]||'open',source_ids:ids(p[4]),evidence_ids:ids(p[5]),notes:p[6],tags:ids(p[7])}));}
  function parseHandoffs(value){return pipeRows(value,9).filter(p=>p[2]||p[3]).map((p,i)=>({handoff_id:'handoff-'+String(i+1).padStart(3,'0'),target:p[0]||'knowledge_library',status:p[1]||'draft',purpose:p[2],context_note:p[3],source_ids:ids(p[4]),evidence_ids:ids(p[5]),claim_ids:ids(p[6]),assumption_ids:ids(p[7]),created_at:'',created_by:p[8]}));}
  function parseIdeas(value,existing){const session=(existing.ideation_sessions||[])[0]||{};return pipeRows(value,15).filter(p=>p[0]).map((p,i)=>({idea_id:'idea-'+String(i+1).padStart(3,'0'),title:p[0],description:p[1],author:p[2]||'Unassigned author',rationale:p[3]||'Captured for review; rationale not yet expanded.',hmw_id:p[4]||'hmw-001',prompt_id:p[5]||'prompt-001',tags:ids(p[6]),cluster_id:p[7],status:p[8]||'captured',vote_count:p[9]||0,voter_ids:[],prototype_ids:ids(p[10]),assumption_ids:ids(p[11]),evidence_ids:ids(p[12]),parent_idea_ids:ids(p[13]),merged_into_id:p[14],session_id:session.session_id||'ideation-session-001',challenge_id:existing.challenge_id||'challenge-primary'}));}
  function parseClusters(value){return pipeRows(value,6).filter(p=>p[0]).map((p,i)=>({cluster_id:'idea-cluster-'+String(i+1).padStart(3,'0'),name:p[0],description:p[1],idea_ids:ids(p[2]),tags:ids(p[3]),rationale:p[4],sequence:p[5]||i+1}));}
  function parseJsonList(value){const text=String(value||'').trim();if(!text)return[];const parsed=JSON.parse(text);return Array.isArray(parsed)?parsed:[parsed];}

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
      sources:parseSources(field(root,'sourceLines')), evidence:parseEvidence(field(root,'evidenceLines')), claims:parseClaims(field(root,'claimLines')), assumptions:parseAssumptions(field(root,'assumptionLines')), research_questions:parseResearchQuestions(field(root,'researchQuestionLines')), interview_guides:existing.interview_guides||[], observation_notes:existing.observation_notes||[], synthesis_tags:lines(field(root,'synthesisTags')), handoffs:parseHandoffs(field(root,'handoffLines')),
      custom_frameworks:parseJsonList(field(root,'customFrameworksJson')), prompt_packs:parseJsonList(field(root,'promptPacksJson')),
      ideation_sessions:[Object.assign({},(existing.ideation_sessions||[])[0]||{},{title:field(root,'ideationSessionTitle')||'Primary ideation session',mode:field(root,'ideationMode')||'divergent',framework_key:field(root,'framework')||'AIDA',challenge_ids:[existing.challenge_id||'challenge-primary'],hmw_ids:(existing.how_might_we||[]).map(item=>item.hmw_id),facilitator:field(root,'ideationFacilitator'),participants:lines(field(root,'ideationParticipants')),status:field(root,'ideationStatus')||'planned',notes:field(root,'ideationNotes')})],
      ideas:parseIdeas(field(root,'ideaLines'),existing), idea_clusters:parseClusters(field(root,'clusterLines')),
      decision_criteria:parseJsonList(field(root,'decisionCriteriaJson')),
      decision_options:parseJsonList(field(root,'decisionOptionsJson')),
      sensitivity_views:parseJsonList(field(root,'sensitivityViewsJson')),
      decision_notes:parseJsonList(field(root,'decisionNotesJson')),
      decision_handoffs:parseJsonList(field(root,'decisionHandoffsJson')),
      prototypes:parseJsonList(field(root,'prototypesJson')),
      hypotheses:parseJsonList(field(root,'hypothesesJson')),
      experiment_plans:parseJsonList(field(root,'experimentPlansJson')),
      experiment_runs:parseJsonList(field(root,'experimentRunsJson')),
      learning_decisions:parseJsonList(field(root,'learningDecisionsJson')),
      iteration_history:parseJsonList(field(root,'iterationHistoryJson')),
      experiment_handoffs:parseJsonList(field(root,'experimentHandoffsJson')),
      tests:existing.tests||[], review_notes:existing.review_notes||[],
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
    const experimentPlan = contract.experiment_plans[0] || {};
    const latestRun = contract.experiment_runs[contract.experiment_runs.length - 1] || {};
    const latestDecision = contract.learning_decisions[contract.learning_decisions.length - 1] || {};
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
    setText(root, 'sourceCount', contract.ledger_summary.source_count + ' recorded');
    setText(root, 'claimRiskCount', contract.ledger_summary.unsupported_or_disputed_count + ' visible');
    setText(root, 'evidenceCoverage', contract.ledger_summary.evidence_coverage.replace(/_/g, ' '));
    setText(root, 'assumptionExposure', contract.ledger_summary.assumption_exposure.replace(/_/g, ' '));
    setText(root, 'decisionReadiness', contract.prioritization_summary.readiness.replace(/_/g, ' '));
    setText(root, 'decisionOptionCount', contract.prioritization_summary.option_count + ' options');
    setText(root, 'decisionGapCount', contract.prioritization_summary.incomplete_score_count + ' input gaps');
    const baseline = contract.sensitivity_views[0] || {rankings:[]};
    const topRank = baseline.rankings[0];
    const topOption = topRank ? contract.decision_options.find(item => item.option_id === topRank.option_id) : null;
    setText(root, 'topDecisionOption', topOption ? `${topOption.title} · ${topRank.score.toFixed(2)}` : 'No ranked option');
    setText(root, 'experimentReadiness', contract.experiment_summary.readiness.replace(/_/g, ' '));
    setText(root, 'prototypeCount', contract.experiment_summary.prototype_count + ' prototypes');
    setText(root, 'experimentCount', contract.experiment_summary.experiment_count + ' plans');
    setText(root, 'completedRunCount', contract.experiment_summary.completed_run_count + ' completed');
    setText(root, 'learningDecisionCount', contract.experiment_summary.learning_decision_count + ' decisions');
    setText(root, 'iterationCount', contract.experiment_summary.iteration_count + ' iterations');
    setList(root, 'decisionRanking', baseline.rankings.map(rank => { const option=contract.decision_options.find(item=>item.option_id===rank.option_id); return `#${rank.rank} ${option?option.title:rank.option_id} — ${rank.score.toFixed(2)}`; }));
    setList(root, 'stakeholderSummary', contract.stakeholders.map(item => `${item.name}: influence ${item.influence}/5, interest ${item.interest}/5 — ${item.engagement_strategy || item.stance}`));
    const journey = contract.journeys[0];
    setList(root, 'journeySummary', journey ? journey.stages.map(stage => `${stage.sequence}. ${stage.name}: ${stage.actions.join('; ') || 'No action recorded'} (emotion ${stage.emotion})`) : []);
    setText(root, 'pov', contract.point_of_view.statement);
    setList(root, 'hmw', contract.how_might_we.map(item => item.question));
    setText(root, 'prototypeTitle', prototype.title || 'Prototype concept');
    setText(root, 'prototypeBody', prototype.description || 'No prototype recorded.');
    setText(root, 'signal', (experimentPlan.metrics && experimentPlan.metrics[0] && experimentPlan.metrics[0].success_threshold) || test.signal || 'No success threshold recorded.');
    setText(root, 'test', experimentPlan.method || test.method || 'No experiment method recorded.');
    setText(root, 'risk', (experimentPlan.safeguards && experimentPlan.safeguards.risks && experimentPlan.safeguards.risks[0]) || risk.note || 'Review assumptions, safeguards, and evidence gaps before relying on this test.');
    setList(root, 'experimentPlanSummary', contract.experiment_plans.map(item => `${item.title} [${item.status}] — ${item.method}`));
    setList(root, 'experimentRunSummary', contract.experiment_runs.map(item => `${item.run_id}: ${item.result_state} with ${item.participant_count} participants — ${item.summary || 'No summary recorded'}`));
    setList(root, 'learningSummary', contract.learning_decisions.map(item => `${item.outcome}: ${item.rationale || 'No rationale recorded'}`));
    setText(root, 'latestExperimentResult', latestRun.summary || 'No run recorded.');
    setText(root, 'latestLearningDecision', latestDecision.rationale || 'No learning decision recorded.');
    setList(root, 'ideas', contract.ideas.length ? contract.ideas.map(item => `${item.title} [${item.status}; ${item.vote_count} votes] — ${item.rationale}`) : contract.framework.prompts.map(item => `${item.label}: ${item.question} — apply this to: ${contract.challenge}`));
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
    setField(root,'sourceLines',(contract.sources||[]).map(i=>[i.source_type,i.title,i.creator,i.source_date,i.url,i.owner,(i.limitations||[]).join('; '),(i.tags||[]).join(', '),i.knowledge_library_record_id,i.description].join(' | ')).join('\n'));
    setField(root,'evidenceLines',(contract.evidence||[]).map(i=>[i.title,i.evidence_type,i.source_id,i.summary,i.quote,i.locator,i.citation,i.confidence,(i.limitations||[]).join('; '),(i.tags||[]).join(', ')].join(' | ')).join('\n'));
    setField(root,'claimLines',(contract.claims||[]).map(i=>[i.state,i.statement,i.owner,i.confidence,(i.evidence_ids||[]).join(', '),(i.assumption_ids||[]).join(', '),i.uncertainty,(i.limitations||[]).join('; '),(i.contradictions||[]).join('; '),(i.missing_data||[]).join('; '),i.review_status,(i.tags||[]).join(', ')].join(' | ')).join('\n'));
    setField(root,'assumptionLines',(contract.assumptions||[]).map(i=>[i.criticality,i.statement,i.owner,i.confidence,i.consequence,i.test_method,i.status,(i.experiment_ids||[]).join(', '),(i.evidence_ids||[]).join(', '),i.due_date,(i.limitations||[]).join('; '),(i.tags||[]).join(', ')].join(' | ')).join('\n'));
    setField(root,'researchQuestionLines',(contract.research_questions||[]).map(i=>[i.priority,i.question,i.owner,i.status,(i.source_ids||[]).join(', '),(i.evidence_ids||[]).join(', '),i.notes,(i.tags||[]).join(', ')].join(' | ')).join('\n'));
    setField(root,'synthesisTags',(contract.synthesis_tags||[]).join('\n'));
    setField(root,'handoffLines',(contract.handoffs||[]).map(i=>[i.target,i.status,i.purpose,i.context_note,(i.source_ids||[]).join(', '),(i.evidence_ids||[]).join(', '),(i.claim_ids||[]).join(', '),(i.assumption_ids||[]).join(', '),i.created_by].join(' | ')).join('\n'));
    setField(root, 'framework', contract.framework.key);
    const session=(contract.ideation_sessions||[])[0]||{}; setField(root,'ideationSessionTitle',session.title); setField(root,'ideationMode',session.mode); setField(root,'ideationFacilitator',session.facilitator); setField(root,'ideationParticipants',(session.participants||[]).join('\n')); setField(root,'ideationStatus',session.status); setField(root,'ideationNotes',session.notes);
    setField(root,'ideaLines',(contract.ideas||[]).map(i=>[i.title,i.description,i.author,i.rationale,i.hmw_id,i.prompt_id,(i.tags||[]).join(', '),i.cluster_id,i.status,i.vote_count,(i.prototype_ids||[]).join(', '),(i.assumption_ids||[]).join(', '),(i.evidence_ids||[]).join(', '),(i.parent_idea_ids||[]).join(', '),i.merged_into_id].join(' | ')).join('\n'));
    setField(root,'clusterLines',(contract.idea_clusters||[]).map(i=>[i.name,i.description,(i.idea_ids||[]).join(', '),(i.tags||[]).join(', '),i.rationale,i.sequence].join(' | ')).join('\n'));
    setField(root,'customFrameworksJson',JSON.stringify(contract.custom_frameworks||[],null,2)); setField(root,'promptPacksJson',JSON.stringify(contract.prompt_packs||[],null,2));
    setField(root,'decisionCriteriaJson',JSON.stringify(contract.decision_criteria||[],null,2));
    setField(root,'decisionOptionsJson',JSON.stringify(contract.decision_options||[],null,2));
    setField(root,'sensitivityViewsJson',JSON.stringify((contract.sensitivity_views||[]).slice(1),null,2));
    setField(root,'decisionNotesJson',JSON.stringify(contract.decision_notes||[],null,2));
    setField(root,'decisionHandoffsJson',JSON.stringify(contract.decision_handoffs||[],null,2));
    setField(root,'prototypesJson',JSON.stringify(contract.prototypes||[],null,2));
    setField(root,'hypothesesJson',JSON.stringify(contract.hypotheses||[],null,2));
    setField(root,'experimentPlansJson',JSON.stringify(contract.experiment_plans||[],null,2));
    setField(root,'experimentRunsJson',JSON.stringify(contract.experiment_runs||[],null,2));
    setField(root,'learningDecisionsJson',JSON.stringify(contract.learning_decisions||[],null,2));
    setField(root,'iterationHistoryJson',JSON.stringify(contract.iteration_history||[],null,2));
    setField(root,'experimentHandoffsJson',JSON.stringify(contract.experiment_handoffs||[],null,2));
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
              const index=contract.ideas.length+1, session=(contract.ideation_sessions||[])[0]||{}, hmw=(contract.how_might_we||[])[0]||{}, prompt=(contract.framework.prompts||[])[0]||{};
              contract.ideas.push({idea_id:'idea-'+String(index).padStart(3,'0'),title:idea,description:'',session_id:session.session_id||'ideation-session-001',challenge_id:contract.challenge_id||'challenge-primary',hmw_id:hmw.hmw_id||'hmw-001',prompt_id:prompt.prompt_id||'prompt-001',author:'Browser participant',rationale:'Added directly in the browser workspace for later review.',tags:[],cluster_id:'',status:'captured',vote_count:0,voter_ids:[],parent_idea_ids:[],merged_into_id:'',prototype_ids:[],assumption_ids:[],evidence_ids:[],created_at:new Date().toISOString(),updated_at:new Date().toISOString()});
            }
            const rebuilt=Engine.buildContract(contract,'wordpress'); populate(root,rebuilt); queueAutosave();
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
