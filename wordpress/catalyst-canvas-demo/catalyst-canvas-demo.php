<?php
/**
 * Plugin Name: Catalyst Canvas Demo
 * Plugin URI: https://sustainablecatalyst.com/catalyst-canvas/
 * Description: Adds a guided, client-side Catalyst Canvas demo via the [catalyst_canvas_demo] shortcode.
 * Version: 1.1.1
 * Author: Content Catalyst LLC
 * License: MIT
 * Text Domain: catalyst-canvas-demo
 */

if (!defined('ABSPATH')) {
    exit;
}

final class Catalyst_Canvas_Demo_Plugin {
    private const VERSION = '1.1.1';
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
            'catalyst-canvas-demo',
            $base . 'assets/catalyst-canvas-demo.js',
            array(),
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
        wp_enqueue_script('catalyst-canvas-demo');

        $instance_id = function_exists('wp_unique_id') ? wp_unique_id('ccanvasdemo-') : 'ccanvasdemo-' . wp_rand(1000, 999999);

        ob_start();
        ?>
        <section id="<?php echo esc_attr($instance_id); ?>" class="ccanvasdemo" data-canvas-demo data-version="<?php echo esc_attr(self::VERSION); ?>">
            <header class="ccanvasdemo-hero">
                <p class="ccanvasdemo-eyebrow">Interactive demo</p>
                <h2><?php echo esc_html($atts['title']); ?></h2>
                <p class="ccanvasdemo-lede"><?php echo esc_html($atts['subtitle']); ?></p>
                <p class="ccanvasdemo-note">This demo runs in the browser. It does not submit form inputs to Sustainable Catalyst.</p>
            </header>

            <div class="ccanvasdemo-layout">
                <form class="ccanvasdemo-inputs" data-canvas-form>
                    <div class="ccanvasdemo-panel">
                        <p class="ccanvasdemo-section-label">Problem framing</p>
                        <label><span>Challenge</span><textarea data-field="challenge" rows="3" placeholder="Example: A nonprofit needs a clearer way to explain program impact to funders."></textarea></label>
                        <label><span>Audience / user</span><input data-field="audience" type="text" placeholder="Example: Program director at a community nonprofit"></label>
                        <label><span>Goal</span><input data-field="goal" type="text" placeholder="Example: Build a defensible impact story with traceable indicators"></label>
                        <label><span>Constraint</span><input data-field="constraint" type="text" placeholder="Example: Limited data, small team, stakeholder pressure"></label>
                    </div>

                    <div class="ccanvasdemo-panel">
                        <p class="ccanvasdemo-section-label">Ideation framework</p>
                        <label>
                            <span>Framework</span>
                            <select data-field="framework">
                                <option value="AIDA">AIDA</option>
                                <option value="JTBD">Jobs To Be Done</option>
                                <option value="Hero">Hero’s Journey</option>
                                <option value="Matrix">Content Matrix</option>
                            </select>
                        </label>
                        <label><span>Custom idea</span><input data-field="customIdea" type="text" placeholder="Add your own idea after generating the draft"></label>
                        <div class="ccanvasdemo-actions">
                            <button type="button" class="ccanvasdemo-btn ccanvasdemo-btn-primary" data-action="generate">Generate draft canvas</button>
                            <button type="button" class="ccanvasdemo-btn" data-action="add-idea">Add custom idea</button>
                            <button type="button" class="ccanvasdemo-btn" data-action="reset">Reset</button>
                        </div>
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
            <p>The demo runs client-side in the browser and does not submit visitor inputs to Sustainable Catalyst.</p>
        </div>
        <?php
    }
}

new Catalyst_Canvas_Demo_Plugin();
