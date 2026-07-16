<?php
/**
 * Plugin Name: Catalyst Canvas Demo
 * Plugin URI: https://sustainablecatalyst.com/catalyst-canvas/
 * Description: Adds a persistent, client-side Catalyst Canvas project workspace via the [catalyst_canvas_demo] shortcode.
 * Version: 1.7.0
 * Author: Content Catalyst LLC
 * License: MIT
 * Text Domain: catalyst-canvas-demo
 */

if (!defined('ABSPATH')) {
    exit;
}

final class Catalyst_Canvas_Demo_Plugin {
    private const VERSION = '1.7.0';
    private const CONTRACT_VERSION = 'catalyst-canvas/1.4';
    private const SHORTCODE = 'catalyst_canvas_demo';

    public function __construct() {
        add_shortcode(self::SHORTCODE, array($this, 'render_shortcode'));
        add_action('wp_enqueue_scripts', array($this, 'register_assets'));
        add_action('admin_menu', array($this, 'register_admin_page'));
    }

    public function register_assets(): void {
        $base = plugin_dir_url(__FILE__);

        wp_register_style(
            'catalyst-canvas-demo',
            $base . 'assets/catalyst-canvas-demo.css',
            array(),
            self::VERSION
        );

        wp_register_script(
            'catalyst-canvas-contract-data',
            $base . 'assets/catalyst-canvas-contract-data.js',
            array(),
            self::VERSION,
            true
        );

        wp_register_script(
            'catalyst-canvas-engine',
            $base . 'assets/catalyst-canvas-engine.js',
            array('catalyst-canvas-contract-data'),
            self::VERSION,
            true
        );

        wp_register_script(
            'catalyst-canvas-workspace',
            $base . 'assets/catalyst-canvas-workspace.js',
            array(),
            self::VERSION,
            true
        );

        wp_register_script(
            'catalyst-canvas-demo',
            $base . 'assets/catalyst-canvas-demo.js',
            array('catalyst-canvas-engine', 'catalyst-canvas-workspace'),
            self::VERSION,
            true
        );
    }

    public function render_shortcode($atts = array(), $content = null): string {
        $atts = shortcode_atts(
            array(
                'title' => 'Catalyst Canvas Demo',
                'subtitle' => 'Turn a messy problem into a structured design-thinking brief.',
            ),
            $atts,
            self::SHORTCODE
        );

        wp_enqueue_style('catalyst-canvas-demo');
        wp_enqueue_script('catalyst-canvas-contract-data');
        wp_enqueue_script('catalyst-canvas-engine');
        wp_enqueue_script('catalyst-canvas-workspace');
        wp_enqueue_script('catalyst-canvas-demo');

        $instance_id = function_exists('wp_unique_id') ? wp_unique_id('ccanvasdemo-') : 'ccanvasdemo-' . wp_rand(1000, 999999);

        ob_start();
        ?>
        <section id="<?php echo esc_attr($instance_id); ?>" class="ccanvasdemo" data-canvas-demo data-version="<?php echo esc_attr(self::VERSION); ?>">
            <header class="ccanvasdemo-hero">
                <p class="ccanvasdemo-eyebrow">Interactive demo</p>
                <h2><?php echo esc_html($atts['title']); ?></h2>
                <p class="ccanvasdemo-lede"><?php echo esc_html($atts['subtitle']); ?></p>
                <p class="ccanvasdemo-note">This demo runs in the browser. It does not submit form inputs to Sustainable Catalyst. Export contract: <strong data-output="contractVersion"><?php echo esc_html(self::CONTRACT_VERSION); ?></strong>.</p>
            </header>

            <div class="ccanvasdemo-workspace" data-workspace-toolbar>
                <div>
                    <p class="ccanvasdemo-section-label">Private browser workspace</p>
                    <label><span>Project title</span><input data-workspace-field="title" type="text" value="Untitled Canvas Project"></label>
                    <label><span>Saved projects</span><select data-workspace-project><option value="">New unsaved project</option></select></label>
                </div>
                <div class="ccanvasdemo-actions">
                    <button type="button" class="ccanvasdemo-btn ccanvasdemo-btn-primary" data-action="save-project">Save project</button>
                    <button type="button" class="ccanvasdemo-btn" data-action="new-project">New</button>
                    <button type="button" class="ccanvasdemo-btn" data-action="duplicate-project">Duplicate</button>
                    <button type="button" class="ccanvasdemo-btn" data-action="archive-project">Archive</button>
                    <button type="button" class="ccanvasdemo-btn" data-action="restore-project">Restore</button>
                </div>
                <p class="ccanvasdemo-workspace-status" data-workspace-status>Projects and revisions stay in this browser.</p>
            </div>

            <div class="ccanvasdemo-layout">
                <form class="ccanvasdemo-inputs" data-canvas-form>
                    <div class="ccanvasdemo-panel">
                        <p class="ccanvasdemo-section-label">Problem framing and audiences</p>
                        <label><span>Challenge</span><textarea data-field="challenge" rows="3" placeholder="Example: A nonprofit needs a clearer way to explain program impact to funders."></textarea></label>
                        <label><span>Primary audience / user</span><input data-field="audience" type="text" placeholder="Example: Program director at a community nonprofit"></label>
                        <div class="ccanvasdemo-inline-fields">
                            <label><span>Secondary audiences</span><textarea data-field="audienceSecondary" rows="2" placeholder="One per line"></textarea></label>
                            <label><span>Affected groups</span><textarea data-field="audienceAffected" rows="2" placeholder="One per line"></textarea></label>
                            <label><span>Excluded from scope</span><textarea data-field="audienceExcluded" rows="2" placeholder="One per line"></textarea></label>
                        </div>
                        <label><span>Goal</span><input data-field="goal" type="text" placeholder="Example: Build a defensible impact story with traceable indicators"></label>
                        <label><span>Constraint</span><input data-field="constraint" type="text" placeholder="Example: Limited data, small team, stakeholder pressure"></label>
                    </div>

                    <div class="ccanvasdemo-panel">
                        <p class="ccanvasdemo-section-label">Persona research</p>
                        <div class="ccanvasdemo-inline-fields"><label><span>Template</span><select data-field="personaTemplate"><option value="">Choose a reusable template</option><option value="civic">Civic service</option><option value="sustainability">Sustainability</option><option value="research">Research</option><option value="technical_content">Technical content</option><option value="institutional">Institutional</option><option value="public_interest">Public interest</option></select></label><div class="ccanvasdemo-template-action"><button type="button" class="ccanvasdemo-btn" data-action="apply-persona-template">Apply template</button></div></div>
                        <div class="ccanvasdemo-inline-fields"><label><span>Persona name</span><input data-field="personaName" type="text"></label><label><span>Role</span><input data-field="personaRole" type="text"></label></div>
                        <label><span>Context</span><textarea data-field="personaContext" rows="3"></textarea></label>
                        <div class="ccanvasdemo-inline-fields"><label><span>Jobs</span><textarea data-field="personaJobs" rows="2"></textarea></label><label><span>Goals</span><textarea data-field="personaGoals" rows="2"></textarea></label><label><span>Needs</span><textarea data-field="personaNeeds" rows="2"></textarea></label></div>
                        <div class="ccanvasdemo-inline-fields"><label><span>Pains</span><textarea data-field="personaPains" rows="2"></textarea></label><label><span>Gains</span><textarea data-field="personaGains" rows="2"></textarea></label><label><span>Behaviors</span><textarea data-field="personaBehaviors" rows="2"></textarea></label></div>
                        <div class="ccanvasdemo-inline-fields"><label><span>Barriers</span><textarea data-field="personaBarriers" rows="2"></textarea></label><label><span>Motivations</span><textarea data-field="personaMotivations" rows="2"></textarea></label><label><span>Accessibility needs</span><textarea data-field="personaAccessibility" rows="2"></textarea></label></div>
                        <div class="ccanvasdemo-inline-fields"><label><span>Preferred channels</span><textarea data-field="personaChannels" rows="2"></textarea></label><label><span>Quotes</span><textarea data-field="personaQuotes" rows="2"></textarea></label><label><span>Tags</span><textarea data-field="personaTags" rows="2"></textarea></label></div>
                        <div class="ccanvasdemo-inline-fields">
                            <label><span>Source</span><select data-field="personaSource"><option value="assumption">Assumption</option><option value="research">Research</option><option value="observed">Observed</option><option value="mixed">Mixed</option></select></label>
                            <label><span>Confidence</span><select data-field="personaConfidence"><option value="low">Low</option><option value="medium">Medium</option><option value="high">High</option></select></label>
                            <label><span>Validation</span><select data-field="personaValidation"><option value="hypothesis">Hypothesis</option><option value="researching">Researching</option><option value="validated">Validated</option><option value="retired">Retired</option></select></label>
                        </div>
                        <div class="ccanvasdemo-inline-fields"><label><span>Source notes</span><textarea data-field="personaSourceNotes" rows="2"></textarea></label><label><span>Confidence notes</span><textarea data-field="personaConfidenceNotes" rows="2"></textarea></label><label><span>Evidence IDs</span><textarea data-field="personaEvidenceIds" rows="2"></textarea></label></div>
                        <label><span>Assumption IDs</span><textarea data-field="personaAssumptionIds" rows="2"></textarea></label>
                        <label><span>Observed versus assumed attributes</span><textarea data-field="personaAttributes" rows="5" placeholder="Category | Statement | observed/research/assumed | Confidence | Evidence IDs | Notes"></textarea></label>
                    </div>

                    <div class="ccanvasdemo-panel">
                        <p class="ccanvasdemo-section-label">Empathy map</p>
                        <div class="ccanvasdemo-inline-fields"><label><span>Says</span><textarea data-field="empathySays" rows="2"></textarea></label><label><span>Thinks</span><textarea data-field="empathyThinks" rows="2"></textarea></label><label><span>Does</span><textarea data-field="empathyDoes" rows="2"></textarea></label></div>
                        <div class="ccanvasdemo-inline-fields"><label><span>Feels</span><textarea data-field="empathyFeels" rows="2"></textarea></label><label><span>Sees</span><textarea data-field="empathySees" rows="2"></textarea></label><label><span>Hears</span><textarea data-field="empathyHears" rows="2"></textarea></label></div>
                    </div>

                    <div class="ccanvasdemo-panel">
                        <p class="ccanvasdemo-section-label">Stakeholder map</p>
                        <label><span>Stakeholders</span><textarea data-field="stakeholders" rows="7" placeholder="Name | Type | Influence | Interest | Impact | Stance | Decision role | Strategy | Responsibilities ; | Tensions ; | Notes"></textarea></label>
                    </div>

                    <div class="ccanvasdemo-panel">
                        <p class="ccanvasdemo-section-label">Journey map</p>
                        <div class="ccanvasdemo-inline-fields"><label><span>Journey title</span><input data-field="journeyTitle" type="text"></label><label><span>Status</span><select data-field="journeyStatus"><option value="draft">Draft</option><option value="research">Research</option><option value="review">Review</option><option value="validated">Validated</option><option value="archived">Archived</option></select></label></div>
                        <label><span>Scenario</span><textarea data-field="journeyScenario" rows="2"></textarea></label>
                        <label><span>Desired outcome</span><textarea data-field="journeyOutcome" rows="2"></textarea></label>
                        <label><span>Stages</span><textarea data-field="journeyStages" rows="9" placeholder="Stage | Actions ; | Questions ; | Emotion | Frictions ; | Opportunities ; | Touchpoints ; | Channels ; | Metrics ; | Owner | Evidence IDs | Experiment IDs"></textarea></label>
                    </div>

                    <div class="ccanvasdemo-panel">
                        <p class="ccanvasdemo-section-label">Behavioral signal import</p>
                        <label><span>Source</span><select data-field="behavioralSignalSource"><option value="analytics_csv">Analytics CSV</option><option value="ga4_export">GA4 export</option></select></label>
                        <label><span>CSV file</span><input data-field="behavioralSignalFile" type="file" accept=".csv,text/csv"></label><label><span>CSV</span><textarea data-field="behavioralSignalCsv" rows="7" placeholder="metric,segment,value,period,interpretation,limitation,evidence_ids,tags"></textarea></label>
                        <p class="ccanvasdemo-help">Analytics are stored only as evidence hints. Extra demographic or identity columns are ignored and never create persona claims.</p>
                    </div>

                    <div class="ccanvasdemo-panel">
                        <p class="ccanvasdemo-section-label">Research evidence ledger</p>
                        <p class="ccanvasdemo-help">Coverage indicators describe recorded links and gaps. They do not score truth or research quality.</p>
                        <label><span>Sources</span><textarea data-field="sourceLines" rows="6" placeholder="Type | Title | Creator | Date | URL | Owner | Limitations | Tags | Knowledge Library ID | Description"></textarea></label>
                        <label><span>Evidence</span><textarea data-field="evidenceLines" rows="7" placeholder="Title | Type | Source ID | Summary | Quote | Locator | Citation | Confidence | Limitations | Tags"></textarea></label>
                        <label><span>Claims</span><textarea data-field="claimLines" rows="8" placeholder="State | Statement | Owner | Confidence | Evidence IDs | Assumption IDs | Uncertainty | Limitations | Contradictions | Missing data | Review status | Tags"></textarea></label>
                        <label><span>Assumptions</span><textarea data-field="assumptionLines" rows="8" placeholder="Criticality | Statement | Owner | Confidence | Consequence | Test method | Status | Experiment IDs | Evidence IDs | Due date | Limitations | Tags"></textarea></label>
                        <label><span>Research questions</span><textarea data-field="researchQuestionLines" rows="5" placeholder="Priority | Question | Owner | Status | Source IDs | Evidence IDs | Notes | Tags"></textarea></label>
                        <label><span>Synthesis tags</span><textarea data-field="synthesisTags" rows="3" placeholder="One per line"></textarea></label>
                        <label><span>Handoffs</span><textarea data-field="handoffLines" rows="4" placeholder="Target | Status | Purpose | Context note | Source IDs | Evidence IDs | Claim IDs | Assumption IDs | Created by"></textarea></label>
                    </div>

                    <div class="ccanvasdemo-panel">
                        <p class="ccanvasdemo-section-label">Ideation framework</p>
                        <label>
                            <span>Framework</span>
                            <select data-field="framework">
                                <option value="AIDA">AIDA</option>
                                <option value="JTBD">Jobs To Be Done</option>
                                <option value="ValueProposition">Value Proposition Canvas</option>
                                <option value="MessageHouse">Message House</option>
                                <option value="SWOT">SWOT</option>
                                <option value="PESTLE">PESTLE</option>
                                <option value="FiveWOneH">5W1H</option>
                                <option value="HeroGuide">Hero / Guide</option>
                                <option value="AssumptionMatrix">Assumption Matrix</option>
                                <option value="ImpactEffort">Impact–Effort Matrix</option>
                            </select>
                        </label>
                        <div class="ccanvasdemo-inline-fields"><label><span>Session title</span><input data-field="ideationSessionTitle" type="text" value="Primary ideation session"></label><label><span>Mode</span><select data-field="ideationMode"><option value="divergent">Divergent</option><option value="convergent">Convergent</option></select></label></div>
                        <div class="ccanvasdemo-inline-fields"><label><span>Facilitator</span><input data-field="ideationFacilitator" type="text"></label><label><span>Status</span><select data-field="ideationStatus"><option value="planned">Planned</option><option value="active">Active</option><option value="complete">Complete</option><option value="archived">Archived</option></select></label></div>
                        <label><span>Participants</span><textarea data-field="ideationParticipants" rows="3" placeholder="One participant per line"></textarea></label>
                        <label><span>Session notes</span><textarea data-field="ideationNotes" rows="3"></textarea></label>
                        <label><span>Idea cards</span><textarea data-field="ideaLines" rows="8" placeholder="Title | Description | Author | Rationale | HMW ID | Prompt ID | Tags | Cluster ID | Status | Votes | Prototype IDs | Assumption IDs | Evidence IDs | Parent IDs | Merged Into"></textarea></label>
                        <label><span>Idea clusters</span><textarea data-field="clusterLines" rows="5" placeholder="Name | Description | Idea IDs | Tags | Rationale | Sequence"></textarea></label>
                        <details><summary>Custom framework JSON</summary><textarea data-field="customFrameworksJson" rows="10">[]</textarea></details>
                        <details><summary>Reusable prompt-pack JSON</summary><textarea data-field="promptPacksJson" rows="8">[]</textarea></details>
                        <label><span>Custom idea</span><input data-field="customIdea" type="text" placeholder="Add your own idea after generating the draft"></label>
                        <div class="ccanvasdemo-actions">
                            <button type="button" class="ccanvasdemo-btn ccanvasdemo-btn-primary" data-action="generate">Generate draft canvas</button>
                            <button type="button" class="ccanvasdemo-btn" data-action="add-idea">Add custom idea</button>
                            <button type="button" class="ccanvasdemo-btn" data-action="reset">Reset</button>
                        </div>
                    </div>

                    <div class="ccanvasdemo-panel">
                        <p class="ccanvasdemo-section-label">Prioritization and decision readiness</p>
                        <p class="ccanvasdemo-help">Scores preserve inputs, basis, confidence, rationale, and evidence. Sensitivity scenarios change weights without overwriting raw values.</p>
                        <details open><summary>Decision criteria JSON</summary><textarea data-field="decisionCriteriaJson" rows="12">[]</textarea></details>
                        <details open><summary>Decision options JSON</summary><textarea data-field="decisionOptionsJson" rows="18">[]</textarea></details>
                        <details><summary>Sensitivity scenarios JSON</summary><textarea data-field="sensitivityViewsJson" rows="10">[]</textarea></details>
                        <details><summary>Decision notes JSON</summary><textarea data-field="decisionNotesJson" rows="8">[]</textarea></details>
                        <details><summary>Decision Studio and Workbench handoffs JSON</summary><textarea data-field="decisionHandoffsJson" rows="10">[]</textarea></details>
                    </div>
                </form>

                <div class="ccanvasdemo-output" aria-live="polite">
                    <div class="ccanvasdemo-panel ccanvasdemo-brief">
                        <p class="ccanvasdemo-section-label">Generated brief</p>
                        <h3 data-output="briefTitle">Canvas draft</h3>
                        <p data-output="summary">Enter a challenge, audience, goal, and constraint. Then generate a draft canvas.</p>
                    </div>

                    <div class="ccanvasdemo-grid">
                        <article class="ccanvasdemo-card"><span>Persona</span><h4 data-output="personaName">Primary user</h4><p data-output="personaBody">A draft persona will appear here.</p></article>
                        <article class="ccanvasdemo-card"><span>POV</span><h4>Point of view</h4><p data-output="pov">A point-of-view statement will appear here.</p></article>
                        <article class="ccanvasdemo-card"><span>HMW</span><h4>How might we?</h4><ul data-output="hmw"></ul></article>
                        <article class="ccanvasdemo-card"><span>Prototype</span><h4 data-output="prototypeTitle">Concept card</h4><p data-output="prototypeBody">A prototype concept will appear here.</p></article>
                    </div>

                    <div class="ccanvasdemo-panel">
                        <p class="ccanvasdemo-section-label">Research readiness</p>
                        <div class="ccanvasdemo-grid ccanvasdemo-grid-three">
                            <article class="ccanvasdemo-mini"><strong>Readiness</strong><p data-output="researchReadiness">Hypothesis</p></article>
                            <article class="ccanvasdemo-mini"><strong>Stakeholders</strong><p data-output="stakeholderCount">0 mapped</p></article>
                            <article class="ccanvasdemo-mini"><strong>Journeys</strong><p data-output="journeyCount">0 mapped</p></article>
                            <article class="ccanvasdemo-mini"><strong>Analytics</strong><p data-output="signalCount">0 hints</p></article>
                            <article class="ccanvasdemo-mini"><strong>Sources</strong><p data-output="sourceCount">0 recorded</p></article>
                            <article class="ccanvasdemo-mini"><strong>Unsupported / disputed</strong><p data-output="claimRiskCount">0 visible</p></article>
                            <article class="ccanvasdemo-mini"><strong>Evidence coverage</strong><p data-output="evidenceCoverage">not assessed</p></article>
                            <article class="ccanvasdemo-mini"><strong>Assumption exposure</strong><p data-output="assumptionExposure">none recorded</p></article>
                        </div>
                        <div class="ccanvasdemo-research-preview">
                            <h4>Stakeholder engagement</h4><ul data-output="stakeholderSummary"></ul>
                            <h4>Journey stages</h4><ul data-output="journeySummary"></ul>
                        </div>
                    </div>

                    <div class="ccanvasdemo-panel">
                        <p class="ccanvasdemo-section-label">Decision readiness</p>
                        <div class="ccanvasdemo-grid ccanvasdemo-grid-three">
                            <article class="ccanvasdemo-mini"><strong>Readiness</strong><p data-output="decisionReadiness">Needs review</p></article>
                            <article class="ccanvasdemo-mini"><strong>Alternatives</strong><p data-output="decisionOptionCount">0 options</p></article>
                            <article class="ccanvasdemo-mini"><strong>Input gaps</strong><p data-output="decisionGapCount">0 input gaps</p></article>
                            <article class="ccanvasdemo-mini"><strong>Top baseline option</strong><p data-output="topDecisionOption">No ranked option</p></article>
                        </div>
                        <h4>Baseline ranking</h4><ol data-output="decisionRanking"></ol>
                        <p class="ccanvasdemo-help">Rankings reflect recorded values and weights. They do not establish certainty, approval, or objective quality.</p>
                    </div>

                    <div class="ccanvasdemo-panel">
                        <p class="ccanvasdemo-section-label">Saved research comparison</p>
                        <p class="ccanvasdemo-help">Compare the primary persona and journey coverage across active browser projects.</p>
                        <div class="ccanvasdemo-grid ccanvasdemo-grid-three" data-output="researchComparison"></div>
                    </div>

                    <div class="ccanvasdemo-panel">
                        <p class="ccanvasdemo-section-label">Experiment plan</p>
                        <div class="ccanvasdemo-grid ccanvasdemo-grid-three">
                            <article class="ccanvasdemo-mini"><strong>Signal</strong><p data-output="signal">What evidence would show whether this idea is working?</p></article>
                            <article class="ccanvasdemo-mini"><strong>Test</strong><p data-output="test">What small test could be run next?</p></article>
                            <article class="ccanvasdemo-mini"><strong>Risk</strong><p data-output="risk">What could be overclaimed or misunderstood?</p></article>
                        </div>
                    </div>

                    <div class="ccanvasdemo-panel">
                        <p class="ccanvasdemo-section-label">Ideas</p>
                        <ul class="ccanvasdemo-ideas" data-output="ideas"></ul>
                    </div>

                    <div class="ccanvasdemo-actions ccanvasdemo-export-actions">
                        <button type="button" class="ccanvasdemo-btn" data-action="copy">Copy brief</button>
                        <button type="button" class="ccanvasdemo-btn" data-action="download">Download JSON</button>
                        <button type="button" class="ccanvasdemo-btn" data-action="print">Print / Save PDF</button>
                    </div>
                </div>
            </div>
        </section>
        <?php
        return ob_get_clean();
    }

    public function register_admin_page(): void {
        add_options_page(
            'Catalyst Canvas Demo',
            'Catalyst Canvas Demo',
            'manage_options',
            'catalyst-canvas-demo',
            array($this, 'render_admin_page')
        );
    }

    public function render_admin_page(): void {
        if (!current_user_can('manage_options')) {
            return;
        }
        ?>
        <div class="wrap">
            <h1>Catalyst Canvas Demo</h1>
            <p>Add the interactive Catalyst Canvas demo to a page with:</p>
            <pre><code>[catalyst_canvas_demo]</code></pre>
            <p>The project workspace runs client-side, stores projects and revisions in this browser, and does not submit visitor inputs to Sustainable Catalyst.</p>
            <p>All generated downloads use <code><?php echo esc_html(self::CONTRACT_VERSION); ?></code> and the shared browser engine.</p>
        </div>
        <?php
    }
}

new Catalyst_Canvas_Demo_Plugin();
