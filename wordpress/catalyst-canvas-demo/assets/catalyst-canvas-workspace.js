(function (global) {
  'use strict';

  const STORAGE_KEY = 'catalyst_canvas_workspace_v1';
  const MAX_REVISIONS = 50;
  const MAX_AUTOSAVES = 20;

  function now() { return new Date().toISOString(); }
  function clone(value) { return JSON.parse(JSON.stringify(value)); }
  function randomId(prefix) {
    if (global.crypto && typeof global.crypto.randomUUID === 'function') return prefix + '-' + global.crypto.randomUUID();
    return prefix + '-' + Date.now().toString(36) + '-' + Math.random().toString(36).slice(2, 12);
  }
  function clean(value, fallback) {
    const text = String(value === undefined || value === null ? '' : value).trim();
    return text || String(fallback || '');
  }

  function memoryStorage() {
    const values = {};
    return {
      getItem: key => Object.prototype.hasOwnProperty.call(values, key) ? values[key] : null,
      setItem: (key, value) => { values[key] = String(value); },
      removeItem: key => { delete values[key]; }
    };
  }

  function blankState() {
    return {
      schema_version: 'catalyst-canvas-browser-workspace/1.0',
      workspace_id: randomId('workspace'),
      active_project_id: '',
      created_at: now(),
      updated_at: now(),
      projects: []
    };
  }

  function normalizeState(value) {
    const state = value && typeof value === 'object' && !Array.isArray(value) ? value : blankState();
    state.schema_version = 'catalyst-canvas-browser-workspace/1.0';
    state.workspace_id = clean(state.workspace_id, randomId('workspace'));
    state.active_project_id = clean(state.active_project_id);
    state.created_at = clean(state.created_at, now());
    state.updated_at = clean(state.updated_at, state.created_at);
    state.projects = Array.isArray(state.projects) ? state.projects.filter(Boolean) : [];
    state.projects.forEach(project => {
      project.project_id = clean(project.project_id, randomId('project'));
      project.title = clean(project.title, 'Untitled Canvas Project');
      project.status = project.status === 'archived' ? 'archived' : 'active';
      project.created_at = clean(project.created_at, now());
      project.updated_at = clean(project.updated_at, project.created_at);
      project.archived_at = clean(project.archived_at);
      project.revisions = Array.isArray(project.revisions) ? project.revisions.filter(Boolean) : [];
    });
    if (state.active_project_id && !state.projects.some(project => project.project_id === state.active_project_id && project.status === 'active')) {
      state.active_project_id = '';
    }
    return state;
  }

  function createStore(storage) {
    const target = storage || (global.localStorage || memoryStorage());

    function load() {
      try {
        const raw = target.getItem(STORAGE_KEY);
        return normalizeState(raw ? JSON.parse(raw) : blankState());
      } catch (error) {
        return blankState();
      }
    }

    function persist(state) {
      state.updated_at = now();
      target.setItem(STORAGE_KEY, JSON.stringify(state));
      return clone(state);
    }

    function list(status) {
      const state = load();
      const wanted = status || 'active';
      return state.projects
        .filter(project => wanted === 'all' || project.status === wanted)
        .sort((left, right) => String(right.updated_at).localeCompare(String(left.updated_at)))
        .map(project => ({
          project_id: project.project_id,
          title: project.title,
          status: project.status,
          created_at: project.created_at,
          updated_at: project.updated_at,
          archived_at: project.archived_at,
          revision_count: project.revisions.length,
          current_revision_id: project.revisions.length ? project.revisions[project.revisions.length - 1].revision_id : ''
        }));
    }

    function get(projectId) {
      const state = load();
      const project = state.projects.find(item => item.project_id === projectId);
      return project ? clone(project) : null;
    }

    function active() {
      const state = load();
      return state.active_project_id ? get(state.active_project_id) : null;
    }

    function setActive(projectId) {
      const state = load();
      const project = state.projects.find(item => item.project_id === projectId && item.status === 'active');
      state.active_project_id = project ? project.project_id : '';
      persist(state);
      return project ? clone(project) : null;
    }

    function revisionRecord(canvas, autosave, note) {
      const payload = clone(canvas);
      payload.revision_id = randomId('revision');
      payload.updated_at = now();
      return {
        revision_id: payload.revision_id,
        created_at: payload.updated_at,
        autosave: Boolean(autosave),
        note: clean(note, autosave ? 'Autosave' : 'Canvas saved'),
        canvas: payload
      };
    }

    function prune(revisions) {
      let result = revisions.slice(-MAX_REVISIONS);
      const autosaves = result.filter(item => item.autosave);
      if (autosaves.length > MAX_AUTOSAVES) {
        const remove = new Set(autosaves.slice(0, autosaves.length - MAX_AUTOSAVES).map(item => item.revision_id));
        result = result.filter(item => !remove.has(item.revision_id));
      }
      return result;
    }

    function create(canvas, title) {
      const state = load();
      const created = now();
      const revision = revisionRecord(canvas, false, 'Project created');
      const project = {
        project_id: randomId('project'),
        title: clean(title || revision.canvas.title, 'Untitled Canvas Project'),
        status: 'active',
        created_at: created,
        updated_at: revision.created_at,
        archived_at: '',
        revisions: [revision]
      };
      revision.canvas.title = project.title;
      state.projects.push(project);
      state.active_project_id = project.project_id;
      persist(state);
      return clone(project);
    }

    function save(projectId, canvas, options) {
      const settings = options || {};
      const state = load();
      const project = state.projects.find(item => item.project_id === projectId);
      if (!project) throw new Error('Project not found.');
      if (project.status === 'archived') throw new Error('Archived projects are read-only.');
      const revision = revisionRecord(canvas, Boolean(settings.autosave), settings.note);
      project.title = clean(settings.title || revision.canvas.title || project.title, project.title);
      revision.canvas.title = project.title;
      project.revisions.push(revision);
      project.revisions = prune(project.revisions);
      project.updated_at = revision.created_at;
      state.active_project_id = project.project_id;
      persist(state);
      return clone(project);
    }

    function currentCanvas(projectId) {
      const project = get(projectId);
      if (!project || !project.revisions.length) return null;
      return clone(project.revisions[project.revisions.length - 1].canvas);
    }

    function duplicate(projectId, title) {
      const source = get(projectId);
      if (!source || !source.revisions.length) throw new Error('Project not found.');
      const canvas = clone(source.revisions[source.revisions.length - 1].canvas);
      canvas.canvas_id = randomId('canvas');
      canvas.revision_id = randomId('revision');
      canvas.created_at = now();
      canvas.updated_at = canvas.created_at;
      canvas.title = clean(title, source.title + ' Copy');
      return create(canvas, canvas.title);
    }

    function archive(projectId) {
      const state = load();
      const project = state.projects.find(item => item.project_id === projectId);
      if (!project) return null;
      project.status = 'archived';
      project.archived_at = now();
      project.updated_at = project.archived_at;
      if (state.active_project_id === projectId) state.active_project_id = '';
      persist(state);
      return clone(project);
    }

    function restore(projectId) {
      const state = load();
      const project = state.projects.find(item => item.project_id === projectId);
      if (!project) return null;
      project.status = 'active';
      project.archived_at = '';
      project.updated_at = now();
      state.active_project_id = projectId;
      persist(state);
      return clone(project);
    }

    function clear() {
      target.removeItem(STORAGE_KEY);
      return blankState();
    }

    return { load, list, get, active, setActive, create, save, currentCanvas, duplicate, archive, restore, clear };
  }

  global.CatalystCanvasWorkspace = {
    STORAGE_KEY,
    createStore,
    memoryStorage
  };
}(typeof window !== 'undefined' ? window : globalThis));
