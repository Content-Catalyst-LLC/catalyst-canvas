'use strict';
const assert = require('assert');
const path = require('path');
const Engine = require(path.resolve('wordpress/catalyst-canvas-demo/assets/catalyst-canvas-engine.js'));
const contract = Engine.buildContract({
  canvas_id:'canvas-research-js', revision_id:'revision-research-js',
  created_at:'2026-07-16T12:00:00.000Z', updated_at:'2026-07-16T12:00:00.000Z',
  audience:{primary:'Program lead',affected:['Residents'],excluded:['Individual targeting']},
  persona:{
    name:'Program Lead', jobs:['Coordinate pilot'], gains:['Shared accountability'], barriers:['Uneven evidence'], motivations:['Defensible decisions'],
    empathy_map:{says:['Show the evidence gap.'],does:['Reviews source notes']},
    attributes:[{category:'behavior',statement:'Reviews source notes',basis:'observed',confidence:'high',evidence_ids:['evidence-001']}],
    confidence:'medium',validation_status:'researching',evidence_ids:['evidence-001']
  },
  stakeholders:[{name:'Sponsor',influence:'high',interest:'medium',impact:5,stance:'supportive',responsibilities:['Approve pilot'],tensions:['Speed versus evidence']}],
  journeys:[{title:'Pilot journey',stages:[{name:'Discover',emotion:-9,questions:['What is supported?'],frictions:['Missing evidence'],opportunities:['Show confidence'],evidence_ids:['evidence-001'],experiment_ids:['test-001']},{name:'Act',emotion:9}]}],
  behavioral_signals:[{source_type:'ga4_export',metric:'brief_downloads',value:'42',interpretation:'Investigate format use'}]
}, 'wordpress');
assert.strictEqual(contract.schema_version, 'catalyst-canvas/1.2');
assert.strictEqual(contract.stakeholders[0].influence, 5);
assert.strictEqual(contract.stakeholders[0].interest, 3);
assert.strictEqual(contract.stakeholders[0].impact, 5);
assert.strictEqual(contract.journeys[0].stages[0].emotion, -2);
assert.strictEqual(contract.journeys[0].stages[1].emotion, 2);
assert.deepStrictEqual(contract.journeys[0].stages[0].experiment_ids, ['test-001']);
assert.strictEqual(contract.personas[0].attributes[0].basis, 'observed');
assert.strictEqual(contract.behavioral_signals[0].evidence_status, 'hint');
assert.ok(contract.behavioral_signals[0].limitation.includes('do not prove intent'));
assert.strictEqual(contract.research_summary.behavioral_signal_count, 1);
assert.strictEqual(contract.research_summary.readiness, 'review_ready');
assert.strictEqual(Object.keys(Engine.PERSONA_TEMPLATES).length, 6);
const csvSignals = Engine.parseBehavioralSignalCsv('metric,segment,value,period,interpretation,limitation,evidence_ids,tags,age,gender\nviews,all,10,2026-06,Investigate,,,engagement,35-44,x','ga4_export');
assert.strictEqual(csvSignals[0].evidence_status, 'hint');
assert.strictEqual(csvSignals[0].age, undefined);
assert.ok(Engine.contractToMarkdown(contract).includes('## Journey Maps'));
assert.ok(Engine.contractToMarkdown(contract).toLowerCase().includes('evidence hint'));
console.log('PASS: WordPress research studio contract behavior.');
