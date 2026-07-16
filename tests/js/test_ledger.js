'use strict';
const assert = require('assert');
const path = require('path');
const Engine = require(path.resolve('wordpress/catalyst-canvas-demo/assets/catalyst-canvas-engine.js'));

const contract = Engine.buildContract({
  canvas_id:'canvas-ledger-js', revision_id:'revision-ledger-js',
  created_at:'2026-07-16T12:00:00.000Z', updated_at:'2026-07-16T12:00:00.000Z',
  sources:[{source_id:'source-001',source_type:'interview',title:'Partner interview',limitations:['Single participant']}],
  evidence:[{evidence_id:'evidence-001',source_id:'source-001',evidence_type:'quote',title:'Shared evidence quote',quote:'Keep the evidence gap visible.',confidence:'medium'}],
  claims:[
    {claim_id:'claim-001',statement:'Partners need visible evidence gaps.',state:'supported',evidence_ids:['evidence-001'],source_ids:['source-001']},
    {claim_id:'claim-002',statement:'The pilot will guarantee alignment.',state:'unsupported'}
  ],
  assumptions:[{assumption_id:'assumption-001',statement:'A one-page brief will improve clarity.',criticality:'high',status:'planned',owner:'Research lead',test_method:'Prototype review',experiment_ids:['test-001'],evidence_ids:['evidence-001']}],
  research_questions:[{research_question_id:'research-question-001',question:'Where does clarity break down?',priority:'high'}],
  handoffs:[{handoff_id:'handoff-001',target:'knowledge_library',status:'ready',source_ids:['source-001'],evidence_ids:['evidence-001'],claim_ids:['claim-001'],assumption_ids:['assumption-001']}]
}, 'wordpress');

assert.strictEqual(contract.schema_version, 'catalyst-canvas/2.0');
assert.strictEqual(contract.ledger_summary.source_count, 1);
assert.strictEqual(contract.ledger_summary.evidence_count, 1);
assert.strictEqual(contract.ledger_summary.claim_states.supported, 1);
assert.strictEqual(contract.ledger_summary.claim_states.unsupported, 1);
assert.strictEqual(contract.ledger_summary.unsupported_or_disputed_count, 1);
assert.strictEqual(contract.ledger_summary.open_high_criticality_assumption_count, 1);
assert.strictEqual(contract.ledger_summary.evidence_coverage, 'some_material_claims_linked');
assert.deepStrictEqual(contract.assumptions[0].experiment_ids, ['test-001']);
assert.strictEqual(contract.handoffs[0].target, 'knowledge_library');
const markdown = Engine.contractToMarkdown(contract);
assert.ok(markdown.includes('## Publication and Review Warning'));
assert.ok(markdown.includes('claim-002: The pilot will guarantee alignment. [unsupported]'));
assert.ok(markdown.indexOf('## Publication and Review Warning') < markdown.indexOf('## Sources'));
assert.ok(contract.ledger_summary.indicator_note.includes('do not measure truth'));
console.log('PASS: WordPress evidence ledger contract behavior.');
