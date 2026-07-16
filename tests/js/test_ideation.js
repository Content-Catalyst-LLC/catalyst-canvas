'use strict';
const assert = require('assert');
const Engine = require('../../wordpress/catalyst-canvas-demo/assets/catalyst-canvas-engine.js');
const contract = Engine.buildContract({
  framework: 'ImpactEffort',
  ideation_sessions: [{session_id:'session-001',title:'Workshop',mode:'convergent',framework_key:'ImpactEffort',challenge_ids:['challenge-primary']}],
  idea_clusters: [{cluster_id:'cluster-001',name:'Quick tests',idea_ids:[],sequence:1}],
  ideas: [{idea_id:'idea-001',title:'Small pilot',session_id:'session-001',challenge_id:'challenge-primary',hmw_id:'hmw-001',prompt_id:'prompt-001',author:'Team',rationale:'Small and reversible',cluster_id:'cluster-001',status:'selected',vote_count:2,prototype_ids:['prototype-001']}]
}, 'wordpress');
assert.strictEqual(contract.schema_version, 'catalyst-canvas/2.0');
assert.strictEqual(contract.ideas[0].author, 'Team');
assert.strictEqual(contract.ideation_summary.vote_count, 2);
assert.ok(contract.idea_clusters[0].idea_ids.includes('idea-001'));
const packagePayload = Engine.exportFrameworkPackage([{key:'CustomOne',name:'Custom One',prompts:[{label:'Ask',question:'What matters?'}]}], 'Example');
assert.strictEqual(Engine.importFrameworkPackage(packagePayload)[0].key, 'CustomOne');
console.log('PASS: WordPress framework and ideation engine.');
