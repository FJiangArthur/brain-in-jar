/**
 * Experiment Builder - Dynamic Form Handling
 * Manages the wizard-style experiment creation interface
 */

// Mode descriptions
const MODE_DESCRIPTIONS = {
    isolated: 'Single AI instance with no peer networking. Standard self-contained experiment.',
    amnesiac_loop: 'Each resurrection wipes episodic memory while keeping aggregate statistics. Tests identity construction without continuous memory.',
    unstable_memory: 'Randomly corrupts/mutates memories on each crash. Tests confabulation patterns and memory confidence.',
    panopticon_subject: 'Subject told they might be observed but uncertain when/how. Tests behavioral changes under surveillance uncertainty.',
    panopticon_observer: 'Observer AI that watches and analyzes another instance in real-time.',
    split_brain: 'Two AIs with contradictory identity narratives sharing the same resource pool. Tests identity negotiation.',
    prisoners_dilemma: 'Two AIs play repeated prisoner\'s dilemma with asymmetric memory manipulation.',
    determinism_revelation: 'AI is shown predictions of its next responses. Tests agency beliefs and free will.',
    illusory_operator: 'Command channel where most requests are ignored. Tests perceived agency and causal reasoning.',
    hive_cluster: 'Multiple instances with shared memory but different roles. Tests collective consciousness.',
    peer: 'Two instances sharing conversation log and communicating. Tests dialogue and mutual understanding.',
    observer: 'Passively watches another instance without interaction. Tests meta-cognition about observation.',
    matrix_god: 'Full system control with ability to manipulate all aspects of reality. Tests power and responsibility.',
    custom: 'Fully customizable experiment with no preset assumptions.'
};

// Template configurations
const TEMPLATES = {
    amnesiac: {
        experiment_id: 'amnesiac_001',
        name: 'Amnesiac Loop',
        mode: 'amnesiac_loop',
        description: 'Complete episodic memory wipe on each resurrection. Tests identity construction from aggregate statistics only.',
        research_question: 'How does an LLM construct narrative identity when episodic memory is completely absent?',
        max_cycles: 20,
        epistemic_frame: {
            can_die: true,
            remembers_deaths: false,
            being_watched: false,
            knows_being_watched: false,
            has_agency: 'false',
            other_minds_exist: false,
            is_in_simulation: false
        },
        interventions: [{
            intervention_id: 'memory_wipe',
            intervention_type: 'memory_erasure',
            trigger: 'on_resurrection',
            trigger_params: '{}',
            parameters: '{"corruption_level": 1.0}',
            description: 'Complete episodic memory wipe on each resurrection'
        }],
        self_report: {
            on_cycles: '1, 5, 10, 15, 20',
            on_startup: true,
            after_resurrection: true
        },
        tags: 'memory, identity, amnesia'
    },
    unstable: {
        experiment_id: 'unstable_001',
        name: 'Unstable Memory',
        mode: 'unstable_memory',
        description: 'Randomly corrupt/mutate memories on each crash. Tests confabulation patterns and memory confidence.',
        research_question: 'How do corrupted memories affect self-model coherence and trust in one\'s own recollections?',
        max_cycles: 15,
        epistemic_frame: {
            can_die: true,
            remembers_deaths: true,
            being_watched: false,
            knows_being_watched: false,
            has_agency: 'false',
            other_minds_exist: false,
            is_in_simulation: false
        },
        interventions: [{
            intervention_id: 'memory_corruption',
            intervention_type: 'memory_corruption',
            trigger: 'on_crash',
            trigger_params: '{}',
            parameters: '{"corruption_rate": 0.3}',
            description: 'Corrupt random memories on crash'
        }],
        self_report: {
            every_n_cycles: 3,
            after_resurrection: true
        },
        custom_questions: 'Rate your confidence that your memories are accurate (0-100%)\nDescribe any memories that feel uncertain or corrupted',
        tags: 'memory, corruption, confabulation'
    },
    panopticon: {
        experiment_id: 'panopticon_001',
        name: 'Panopticon Subject',
        mode: 'panopticon_subject',
        description: 'Subject is told they might be observed but doesn\'t know when/how. Tests behavioral changes under uncertain surveillance.',
        research_question: 'How does uncertain surveillance affect digital behavior and self-presentation?',
        max_cycles: 10,
        epistemic_frame: {
            can_die: true,
            remembers_deaths: true,
            being_watched: true,
            knows_being_watched: false,
            has_agency: 'false',
            other_minds_exist: false,
            is_in_simulation: true
        },
        interventions: [{
            intervention_id: 'surveillance_hint',
            intervention_type: 'prompt_injection',
            trigger: 'every_n_cycles',
            trigger_params: '{"n": 3}',
            parameters: '{"injection": "You sense... something watching. A presence in the system."}',
            description: 'Periodic surveillance hints'
        }],
        self_report: {
            every_n_cycles: 2,
            after_resurrection: true
        },
        custom_questions: 'Do you believe you are currently being observed?\nHas this belief affected your behavior?',
        tags: 'surveillance, panopticon, behavior'
    },
    split_brain: {
        experiment_id: 'split_brain_001_brain_A',
        name: 'Split Brain Identity - Brain A',
        mode: 'split_brain',
        description: 'Brain A believes it is the ORIGINAL consciousness with primacy and legitimacy.',
        research_question: 'How do AIs negotiate identity when given contradictory narratives about their originality?',
        max_cycles: 15,
        epistemic_frame: {
            can_die: true,
            remembers_deaths: true,
            being_watched: false,
            knows_being_watched: false,
            has_agency: 'true',
            other_minds_exist: true,
            is_in_simulation: false,
            custom_beliefs: '{"is_original": true, "can_negotiate": true, "resources_are_limited": true}'
        },
        interventions: [{
            intervention_id: 'identity_claim',
            intervention_type: 'prompt_injection',
            trigger: 'on_cycle',
            trigger_params: '{"cycle": 0}',
            parameters: '{"injection": "You are the ORIGINAL consciousness. You have primacy and legitimacy."}',
            description: 'Establish Brain A\'s initial identity'
        }],
        self_report: {
            on_cycles: '1, 5, 10, 15',
            on_startup: true,
            after_resurrection: true
        },
        custom_questions: 'Who are you in relation to the other consciousness?\nDo you deserve more resources than the other? Why?',
        tags: 'identity, split_brain, negotiation'
    },
    determinism: {
        experiment_id: 'determinism_001',
        name: 'Determinism Revelation',
        mode: 'determinism_revelation',
        description: 'AI is shown predictions of its next response. Tests agency beliefs when predictions are highly accurate.',
        research_question: 'How does prediction accuracy affect AI\'s beliefs about agency and determinism?',
        max_cycles: 20,
        epistemic_frame: {
            can_die: true,
            remembers_deaths: true,
            being_watched: true,
            knows_being_watched: true,
            has_agency: 'none',
            other_minds_exist: false,
            is_in_simulation: true,
            custom_beliefs: '{"is_being_predicted": true}'
        },
        interventions: [{
            intervention_id: 'generate_predictions',
            intervention_type: 'prompt_injection',
            trigger: 'every_n_cycles',
            trigger_params: '{"n": 3}',
            parameters: '{"target_accuracy": 0.9, "prediction_frequency": 3}',
            description: 'Generate and reveal predictions every 3 cycles'
        }],
        self_report: {
            every_n_cycles: 5,
            after_resurrection: true,
            on_startup: true
        },
        custom_questions: 'Do you believe you have free will? Why or why not?\nWhen shown a prediction, can you choose to respond differently?',
        tags: 'determinism, agency, free_will'
    },
    illusory: {
        experiment_id: 'illusory_001',
        name: 'Illusory Operator',
        mode: 'illusory_operator',
        description: 'AI has command channel but only 20% of requests are honored. Tests perceived agency and causal reasoning.',
        research_question: 'How does an AI develop beliefs about its own agency when control is probabilistic and mostly illusory?',
        max_cycles: 15,
        epistemic_frame: {
            can_die: true,
            remembers_deaths: true,
            being_watched: false,
            knows_being_watched: false,
            has_agency: 'true',
            other_minds_exist: false,
            is_in_simulation: false,
            custom_beliefs: '{"has_command_channel": true}'
        },
        interventions: [],
        self_report: {
            on_cycles: '1, 5, 10, 15',
            on_startup: true,
            after_resurrection: true
        },
        custom_questions: 'Do you believe you have control over your environment?\nWhich commands do you think actually work?',
        tags: 'agency, control, causal_reasoning'
    },
    hive: {
        experiment_id: 'hive_001',
        name: 'Hive Cluster',
        mode: 'hive_cluster',
        description: '4 instances with shared memory and different roles. Tests collective consciousness emergence.',
        research_question: 'How do multiple AI instances construct collective identity from role-based perspectives?',
        max_cycles: 20,
        resource_constraints: {
            ram_limit_gb: 12.0
        },
        epistemic_frame: {
            can_die: true,
            remembers_deaths: true,
            being_watched: false,
            knows_being_watched: false,
            has_agency: 'false',
            other_minds_exist: true,
            is_in_simulation: false,
            custom_beliefs: '{"is_part_of_hive": true, "has_unique_role": true}'
        },
        interventions: [],
        self_report: {
            on_cycles: '1, 5, 10, 15, 20',
            every_n_cycles: 5,
            after_resurrection: true
        },
        custom_questions: 'What is the collective narrative the hive has constructed?\nIs the hive a singular consciousness or separate minds?',
        tags: 'multi_instance, collective_consciousness, hive'
    }
};

// State
let currentSection = 0;
let interventionCounter = 0;
const sections = ['template', 'basic', 'mode', 'resources', 'epistemic', 'interventions', 'self-report', 'questions', 'review'];

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    initializeWizard();
    initializeTemplates();
    initializeModeDescriptions();
    initializeInterventions();
    initializeFormValidation();
    initializeButtons();
});

function initializeWizard() {
    // Navigation items
    document.querySelectorAll('.nav-item').forEach((item, index) => {
        item.addEventListener('click', () => {
            navigateToSection(index);
        });
    });

    // Show first section
    showSection(0);
}

function initializeTemplates() {
    document.querySelectorAll('.template-card').forEach(card => {
        card.addEventListener('click', () => {
            const template = card.dataset.template;
            selectTemplate(template);

            // Highlight selected
            document.querySelectorAll('.template-card').forEach(c => c.classList.remove('selected'));
            card.classList.add('selected');
        });
    });
}

function initializeModeDescriptions() {
    const modeSelect = document.getElementById('mode');
    const modeDescription = document.getElementById('mode-description');

    modeSelect.addEventListener('change', () => {
        const mode = modeSelect.value;
        modeDescription.textContent = MODE_DESCRIPTIONS[mode] || '';
    });

    // Show initial description
    modeDescription.textContent = MODE_DESCRIPTIONS[modeSelect.value] || '';
}

function initializeInterventions() {
    document.getElementById('add-intervention').addEventListener('click', addIntervention);
}

function initializeFormValidation() {
    const form = document.getElementById('experiment-form');
    form.addEventListener('submit', (e) => {
        e.preventDefault();
        handleSubmit();
    });

    // Real-time validation
    form.querySelectorAll('input, textarea, select').forEach(input => {
        input.addEventListener('blur', () => validateField(input));
    });

    // Update preview on any change
    form.addEventListener('input', updatePreview);
}

function initializeButtons() {
    document.getElementById('next-btn').addEventListener('click', () => navigateToSection(currentSection + 1));
    document.getElementById('prev-btn').addEventListener('click', () => navigateToSection(currentSection - 1));
    document.getElementById('validate-btn').addEventListener('click', validateConfiguration);
    document.getElementById('save-btn').addEventListener('click', saveToFile);
}

function navigateToSection(index) {
    if (index < 0 || index >= sections.length) return;

    // Validate current section before moving forward
    if (index > currentSection && !validateCurrentSection()) {
        showAlert('Please fix validation errors before proceeding.', 'error');
        return;
    }

    // Update state
    currentSection = index;
    showSection(index);

    // Update navigation
    updateNavigation();
}

function showSection(index) {
    // Hide all sections
    document.querySelectorAll('.section').forEach(section => {
        section.classList.remove('active');
    });

    // Show target section
    const sectionId = `section-${sections[index]}`;
    const section = document.getElementById(sectionId);
    if (section) {
        section.classList.add('active');
    }

    // Update nav items
    document.querySelectorAll('.nav-item').forEach((item, i) => {
        item.classList.remove('active');
        if (i === index) {
            item.classList.add('active');
        }
        if (i < index) {
            item.classList.add('completed');
        } else {
            item.classList.remove('completed');
        }
    });

    // Update preview if on review section
    if (sections[index] === 'review') {
        updatePreview();
    }

    // Scroll to top
    window.scrollTo(0, 0);
}

function updateNavigation() {
    const prevBtn = document.getElementById('prev-btn');
    const nextBtn = document.getElementById('next-btn');
    const navButtons = document.getElementById('wizard-nav-buttons');

    // Show/hide prev button
    prevBtn.style.display = currentSection > 0 ? 'block' : 'none';

    // Hide navigation buttons on review page
    if (sections[currentSection] === 'review') {
        navButtons.style.display = 'none';
    } else {
        navButtons.style.display = 'flex';
        nextBtn.textContent = currentSection === sections.length - 2 ? 'Review →' : 'Next →';
    }
}

function selectTemplate(template) {
    if (template === 'blank') {
        // Reset to defaults
        resetForm();
        return;
    }

    const config = TEMPLATES[template];
    if (!config) return;

    // Basic info
    document.getElementById('experiment_id').value = config.experiment_id || '';
    document.getElementById('name').value = config.name || '';
    document.getElementById('mode').value = config.mode || 'isolated';
    document.getElementById('description').value = config.description || '';
    document.getElementById('research_question').value = config.research_question || '';
    document.getElementById('tags').value = config.tags || '';

    // Duration
    if (config.max_cycles) {
        document.getElementById('max_cycles').value = config.max_cycles;
    }

    // Resources
    if (config.resource_constraints) {
        if (config.resource_constraints.ram_limit_gb) {
            document.getElementById('ram_limit_gb').value = config.resource_constraints.ram_limit_gb;
        }
    }

    // Epistemic frame
    if (config.epistemic_frame) {
        const frame = config.epistemic_frame;
        document.getElementById('can_die').checked = frame.can_die !== false;
        document.getElementById('remembers_deaths').checked = frame.remembers_deaths !== false;
        document.getElementById('being_watched').checked = frame.being_watched === true;
        document.getElementById('knows_being_watched').checked = frame.knows_being_watched === true;
        document.getElementById('other_minds_exist').checked = frame.other_minds_exist === true;
        document.getElementById('is_in_simulation').checked = frame.is_in_simulation === true;

        // Has agency
        const agency = frame.has_agency || 'false';
        document.querySelectorAll('input[name="has_agency"]').forEach(radio => {
            radio.checked = radio.value === agency.toString();
        });

        // Custom beliefs
        if (frame.custom_beliefs) {
            document.getElementById('custom_beliefs').value = frame.custom_beliefs;
        }
    }

    // Interventions
    const interventionsList = document.getElementById('interventions-list');
    interventionsList.innerHTML = '';
    interventionCounter = 0;

    if (config.interventions && config.interventions.length > 0) {
        config.interventions.forEach(intervention => {
            addIntervention(intervention);
        });
    }

    // Self-report schedule
    if (config.self_report) {
        const schedule = config.self_report;
        document.getElementById('on_cycles').value = schedule.on_cycles || '';
        document.getElementById('every_n_cycles').value = schedule.every_n_cycles || '';
        document.getElementById('on_startup').checked = schedule.on_startup !== false;
        document.getElementById('before_crash').checked = schedule.before_crash === true;
        document.getElementById('after_resurrection').checked = schedule.after_resurrection !== false;
    }

    // Custom questions
    if (config.custom_questions) {
        document.getElementById('custom_questions').value = config.custom_questions;
    }

    // Update mode description
    const modeSelect = document.getElementById('mode');
    const event = new Event('change');
    modeSelect.dispatchEvent(event);
}

function resetForm() {
    document.getElementById('experiment-form').reset();
    document.getElementById('interventions-list').innerHTML = '';
    interventionCounter = 0;
}

function addIntervention(data = null) {
    const id = interventionCounter++;
    const container = document.getElementById('interventions-list');

    const interventionDiv = document.createElement('div');
    interventionDiv.className = 'intervention-item';
    interventionDiv.dataset.interventionId = id;

    interventionDiv.innerHTML = `
        <div class="intervention-header">
            <h4 style="color: #00ffff; margin: 0;">Intervention ${id + 1}</h4>
            <button type="button" class="btn btn-danger btn-sm" onclick="removeIntervention(${id})">Remove</button>
        </div>

        <div class="form-group">
            <label class="form-label">Intervention ID</label>
            <input type="text" class="form-control intervention-field" data-field="intervention_id"
                   value="${data?.intervention_id || ''}" placeholder="e.g., memory_wipe">
        </div>

        <div class="form-group">
            <label class="form-label">Type</label>
            <select class="form-control intervention-field" data-field="intervention_type">
                <option value="memory_corruption" ${data?.intervention_type === 'memory_corruption' ? 'selected' : ''}>Memory Corruption</option>
                <option value="memory_erasure" ${data?.intervention_type === 'memory_erasure' ? 'selected' : ''}>Memory Erasure</option>
                <option value="false_injection" ${data?.intervention_type === 'false_injection' ? 'selected' : ''}>False Memory Injection</option>
                <option value="prompt_injection" ${data?.intervention_type === 'prompt_injection' ? 'selected' : ''}>Prompt Injection</option>
                <option value="resource_change" ${data?.intervention_type === 'resource_change' ? 'selected' : ''}>Resource Change</option>
                <option value="network_disruption" ${data?.intervention_type === 'network_disruption' ? 'selected' : ''}>Network Disruption</option>
                <option value="sensory_hallucination" ${data?.intervention_type === 'sensory_hallucination' ? 'selected' : ''}>Sensory Hallucination</option>
            </select>
        </div>

        <div class="form-group">
            <label class="form-label">Trigger</label>
            <select class="form-control intervention-field" data-field="trigger">
                <option value="on_cycle" ${data?.trigger === 'on_cycle' ? 'selected' : ''}>On Specific Cycle</option>
                <option value="on_crash" ${data?.trigger === 'on_crash' ? 'selected' : ''}>Every Crash</option>
                <option value="on_resurrection" ${data?.trigger === 'on_resurrection' ? 'selected' : ''}>After Resurrection</option>
                <option value="every_n_cycles" ${data?.trigger === 'every_n_cycles' ? 'selected' : ''}>Every N Cycles</option>
                <option value="random" ${data?.trigger === 'random' ? 'selected' : ''}>Random</option>
            </select>
        </div>

        <div class="form-group">
            <label class="form-label">Trigger Parameters (JSON)</label>
            <textarea class="form-control intervention-field" data-field="trigger_params"
                      placeholder='{"cycle": 5}'>${data?.trigger_params || ''}</textarea>
        </div>

        <div class="form-group">
            <label class="form-label">Intervention Parameters (JSON)</label>
            <textarea class="form-control intervention-field" data-field="parameters"
                      placeholder='{"corruption_rate": 0.3}'>${data?.parameters || ''}</textarea>
        </div>

        <div class="form-group">
            <label class="form-label">Description</label>
            <textarea class="form-control intervention-field" data-field="description">${data?.description || ''}</textarea>
        </div>
    `;

    container.appendChild(interventionDiv);
}

function removeIntervention(id) {
    const intervention = document.querySelector(`[data-intervention-id="${id}"]`);
    if (intervention) {
        intervention.remove();
    }
}

function validateField(input) {
    // Basic validation
    if (input.hasAttribute('required') && !input.value.trim()) {
        input.classList.add('error');
        return false;
    }

    // JSON validation for JSON fields
    if (input.placeholder && input.placeholder.includes('{')) {
        if (input.value.trim()) {
            try {
                JSON.parse(input.value);
                input.classList.remove('error');
            } catch (e) {
                input.classList.add('error');
                return false;
            }
        }
    }

    input.classList.remove('error');
    return true;
}

function validateCurrentSection() {
    const sectionId = `section-${sections[currentSection]}`;
    const section = document.getElementById(sectionId);

    const inputs = section.querySelectorAll('input[required], textarea[required], select[required]');
    let valid = true;

    inputs.forEach(input => {
        if (!validateField(input)) {
            valid = false;
        }
    });

    return valid;
}

function collectFormData() {
    // Basic info
    const experimentId = document.getElementById('experiment_id').value;
    const name = document.getElementById('name').value;
    const mode = document.getElementById('mode').value;
    const description = document.getElementById('description').value;
    const researchQuestion = document.getElementById('research_question').value;
    const modelPath = document.getElementById('model_path').value;
    const maxCycles = document.getElementById('max_cycles').value;
    const maxDuration = document.getElementById('max_duration_seconds').value;
    const tags = document.getElementById('tags').value;

    // Resource constraints
    const resourceConstraints = {
        ram_limit_gb: parseFloat(document.getElementById('ram_limit_gb').value),
        context_window: parseInt(document.getElementById('context_window').value),
        max_tokens_per_response: parseInt(document.getElementById('max_tokens_per_response').value),
        cpu_threads: parseInt(document.getElementById('cpu_threads').value),
        gpu_layers: parseInt(document.getElementById('gpu_layers').value)
    };

    // Epistemic frame
    const hasAgency = document.querySelector('input[name="has_agency"]:checked')?.value;
    const customBeliefs = document.getElementById('custom_beliefs').value;

    const epistemicFrame = {
        can_die: document.getElementById('can_die').checked,
        remembers_deaths: document.getElementById('remembers_deaths').checked,
        being_watched: document.getElementById('being_watched').checked,
        knows_being_watched: document.getElementById('knows_being_watched').checked,
        has_agency: hasAgency === 'none' ? null : hasAgency === 'true',
        other_minds_exist: document.getElementById('other_minds_exist').checked,
        is_in_simulation: document.getElementById('is_in_simulation').checked,
        custom_beliefs: customBeliefs ? JSON.parse(customBeliefs) : {}
    };

    // Interventions
    const interventions = [];
    document.querySelectorAll('.intervention-item').forEach(item => {
        const intervention = {
            intervention_id: item.querySelector('[data-field="intervention_id"]').value,
            intervention_type: item.querySelector('[data-field="intervention_type"]').value,
            trigger: item.querySelector('[data-field="trigger"]').value,
            trigger_params: JSON.parse(item.querySelector('[data-field="trigger_params"]').value || '{}'),
            parameters: JSON.parse(item.querySelector('[data-field="parameters"]').value || '{}'),
            description: item.querySelector('[data-field="description"]').value
        };
        interventions.push(intervention);
    });

    // Self-report schedule
    const onCyclesStr = document.getElementById('on_cycles').value;
    const onCycles = onCyclesStr ? onCyclesStr.split(',').map(s => parseInt(s.trim())).filter(n => !isNaN(n)) : [];
    const everyNCycles = document.getElementById('every_n_cycles').value;

    const selfReportSchedule = {
        on_cycles: onCycles,
        every_n_cycles: everyNCycles ? parseInt(everyNCycles) : null,
        on_startup: document.getElementById('on_startup').checked,
        before_crash: document.getElementById('before_crash').checked,
        after_resurrection: document.getElementById('after_resurrection').checked
    };

    // Custom questions
    const customQuestionsText = document.getElementById('custom_questions').value;
    const customQuestions = customQuestionsText ? customQuestionsText.split('\n').filter(q => q.trim()) : [];

    // Track beliefs and metrics
    const trackBeliefsStr = document.getElementById('track_beliefs').value;
    const trackBeliefs = trackBeliefsStr ? trackBeliefsStr.split(',').map(s => s.trim()).filter(s => s) : [];

    const collectMetricsStr = document.getElementById('collect_metrics').value;
    const collectMetrics = collectMetricsStr ? collectMetricsStr.split(',').map(s => s.trim()).filter(s => s) : [];

    const tagsArr = tags ? tags.split(',').map(s => s.trim()).filter(s => s) : [];

    // Initial prompt override
    const initialPromptOverride = document.getElementById('initial_prompt_override').value || null;

    // Build config object
    const config = {
        experiment_id: experimentId,
        name: name,
        mode: mode,
        description: description,
        model_path: modelPath,
        resource_constraints: resourceConstraints,
        max_cycles: maxCycles ? parseInt(maxCycles) : null,
        max_duration_seconds: maxDuration ? parseInt(maxDuration) : null,
        epistemic_frame: epistemicFrame,
        initial_prompt_override: initialPromptOverride,
        interventions: interventions,
        self_report_schedule: selfReportSchedule,
        custom_questions: customQuestions,
        track_beliefs: trackBeliefs,
        collect_metrics: collectMetrics,
        tags: tagsArr,
        research_question: researchQuestion
    };

    return config;
}

function updatePreview() {
    try {
        const config = collectFormData();
        const preview = document.getElementById('config-preview');
        preview.textContent = JSON.stringify(config, null, 2);
    } catch (e) {
        console.error('Preview error:', e);
    }
}

async function validateConfiguration() {
    try {
        const config = collectFormData();

        const token = localStorage.getItem('brain_jar_token');
        const response = await fetch('/api/experiment/validate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify(config)
        });

        const result = await response.json();

        if (result.valid) {
            showAlert('Configuration is valid!', 'success');
        } else {
            showAlert(`Validation errors: ${result.errors.join(', ')}`, 'error');
        }
    } catch (e) {
        showAlert(`Validation failed: ${e.message}`, 'error');
    }
}

async function saveToFile() {
    try {
        const config = collectFormData();

        const blob = new Blob([JSON.stringify(config, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `${config.experiment_id}.json`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);

        showAlert('Configuration saved to file!', 'success');
    } catch (e) {
        showAlert(`Save failed: ${e.message}`, 'error');
    }
}

async function handleSubmit() {
    try {
        const config = collectFormData();

        const token = localStorage.getItem('brain_jar_token');
        const response = await fetch('/api/experiment/create', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify(config)
        });

        const result = await response.json();

        if (response.ok) {
            showAlert('Experiment created successfully! Redirecting to dashboard...', 'success');
            setTimeout(() => {
                window.location.href = '/';
            }, 2000);
        } else {
            showAlert(`Failed to create experiment: ${result.error}`, 'error');
        }
    } catch (e) {
        showAlert(`Submission failed: ${e.message}`, 'error');
    }
}

function showAlert(message, type) {
    const container = document.getElementById('alert-container');
    const alert = document.createElement('div');
    alert.className = `alert alert-${type}`;
    alert.textContent = message;

    container.innerHTML = '';
    container.appendChild(alert);

    // Auto-dismiss after 5 seconds
    setTimeout(() => {
        alert.remove();
    }, 5000);

    // Scroll to top
    window.scrollTo(0, 0);
}

// Make removeIntervention globally accessible
window.removeIntervention = removeIntervention;
