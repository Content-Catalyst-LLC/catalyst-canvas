'use strict';

const assert = require('assert');
const fs = require('fs');
const path = require('path');

const root = path.resolve(__dirname, '..', '..');
const Engine = require(path.join(root, 'wordpress', 'catalyst-canvas-demo', 'assets', 'catalyst-canvas-engine.js'));
const input = JSON.parse(fs.readFileSync(path.join(root, 'fixtures', 'canvas_contract_1_4.input.json'), 'utf8'));
const expected = JSON.parse(fs.readFileSync(path.join(root, 'fixtures', 'canvas_contract_1_4.expected.json'), 'utf8'));

const actual = Engine.buildContract(input, 'wordpress');
assert.deepStrictEqual(actual, expected, 'WordPress engine output diverges from the canonical fixture');
assert.strictEqual(Engine.validateContract(actual), actual);
assert.ok(Engine.contractToMarkdown(actual).includes('Contract: catalyst-canvas/1.4'));
console.log('PASS: WordPress engine matches Canvas Contract 1.4 fixture.');
