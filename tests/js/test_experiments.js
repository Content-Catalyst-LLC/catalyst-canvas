'use strict';
const assert = require('assert');
const Engine = require('../../wordpress/catalyst-canvas-demo/assets/catalyst-canvas-engine.js');
const source = require('../../fixtures/canvas_contract_1_5.input.json');

const contract = Engine.buildContract(source, 'wordpress');
assert.strictEqual(contract.schema_version, 'catalyst-canvas/1.5');
assert.strictEqual(contract.prototypes[0].prototype_type, 'paper');
assert.strictEqual(contract.hypotheses[0].status, 'partially_supported');
assert.strictEqual(contract.experiment_plans[0].participant_plan.target_count, 5);
assert.strictEqual(contract.experiment_plans[0].metrics.length, 2);
assert.ok(contract.experiment_plans[0].safeguards.stop_conditions.length);
assert.strictEqual(contract.experiment_runs[0].metric_results[0].met_threshold, true);
assert.strictEqual(contract.experiment_runs[0].metric_results[1].met_threshold, false);
assert.strictEqual(contract.experiment_summary.readiness, 'learning_recorded');

const lab = Engine.buildExperimentHandoffPackage(contract, 'research_lab');
assert.strictEqual(lab.handoff_contract, 'catalyst-canvas-experiment-handoff/1.0');
assert.strictEqual(lab.target, 'research_lab');
assert.strictEqual(lab.research_execution.participant_plans[0].target_count, 5);
assert.ok(lab.research_execution.dataset_refs.includes('dataset://heat-brief-clarity-pilot'));

const workbench = Engine.buildExperimentHandoffPackage(contract, 'workbench');
assert.strictEqual(workbench.target, 'workbench');
assert.strictEqual(workbench.technical_validation.metric_definitions.length, 2);
assert.ok(workbench.technical_validation.modeling_questions.length);
assert.ok(workbench.technical_validation.prototype_artifacts.includes('artifact://heat-action-brief/v0.2'));

const migrated = Engine.migratePayload(require('../../fixtures/canvas_contract_1_4.expected.json'));
assert.strictEqual(migrated.migrated_from, 'catalyst-canvas/1.4');
assert.strictEqual(migrated.contract.schema_version, 'catalyst-canvas/1.5');
assert.ok(migrated.contract.experiment_plans.length);
assert.ok(migrated.warnings[0].includes('experiment fields'));

console.log('PASS: WordPress prototype and experiment engine.');
