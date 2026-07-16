(function (root, factory) {
  'use strict';
  const data = factory();
  if (typeof module === 'object' && module.exports) module.exports = data;
  if (root) root.CatalystCanvasContractData = data;
}(typeof globalThis !== 'undefined' ? globalThis : this, function () {
  'use strict';
  return {"releaseVersion":"1.3.0","contractVersion":"catalyst-canvas/1.0","frameworks":{"AIDA":{"name":"AIDA","prompts":[{"label":"Attention","question":"What concrete tension should the audience notice first?"},{"label":"Interest","question":"What evidence or story makes the problem worth caring about?"},{"label":"Desire","question":"What better state becomes imaginable and credible?"},{"label":"Action","question":"What small next step can be tested?"}]},"JTBD":{"name":"Jobs To Be Done","prompts":[{"label":"When","question":"What situation creates the need?"},{"label":"I want to","question":"What progress is the user trying to make?"},{"label":"So I can","question":"What outcome matters?"},{"label":"Constraint","question":"What prevents the user from making progress today?"}]},"Hero":{"name":"Hero's Journey","prompts":[{"label":"Ordinary world","question":"What is the current operating reality?"},{"label":"Call","question":"What pressure or opportunity forces change?"},{"label":"Guide","question":"What support helps the user move forward?"},{"label":"Return","question":"What measurable improvement should be visible?"}]},"Matrix":{"name":"Content Matrix","prompts":[{"label":"Audience need","question":"What question does this audience need answered?"},{"label":"Evidence type","question":"What proof would make the answer credible?"},{"label":"Format","question":"What artifact should carry the answer?"},{"label":"Review signal","question":"What would show that the artifact worked?"}]}}};
}));
