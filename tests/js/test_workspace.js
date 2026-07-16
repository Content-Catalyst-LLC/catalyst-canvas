'use strict';
const fs = require('fs');
const vm = require('vm');
const assert = require('assert');

const context = { console, Date, Math, JSON, setTimeout, clearTimeout };
context.globalThis = context;
vm.createContext(context);
vm.runInContext(fs.readFileSync('wordpress/catalyst-canvas-demo/assets/catalyst-canvas-workspace.js', 'utf8'), context);
const Workspace = context.CatalystCanvasWorkspace;
const store = Workspace.createStore(Workspace.memoryStorage());
const canvas = {
  schema_version: 'catalyst-canvas/1.1', canvas_id: 'canvas-test', revision_id: 'revision-test',
  title: 'Workspace Test', created_at: '2026-07-16T00:00:00.000Z', updated_at: '2026-07-16T00:00:00.000Z'
};
const project = store.create(canvas, 'Workspace Test');
assert.strictEqual(store.list('active').length, 1);
assert.strictEqual(store.active().project_id, project.project_id);
store.save(project.project_id, canvas, { autosave: true });
assert.strictEqual(store.get(project.project_id).revisions.length, 2);
const duplicate = store.duplicate(project.project_id);
assert.notStrictEqual(duplicate.project_id, project.project_id);
assert.notStrictEqual(store.currentCanvas(duplicate.project_id).canvas_id, canvas.canvas_id);
store.archive(project.project_id);
assert.strictEqual(store.list('archived').length, 1);
store.restore(project.project_id);
assert.strictEqual(store.get(project.project_id).status, 'active');
console.log('WordPress browser workspace persistence passed.');
