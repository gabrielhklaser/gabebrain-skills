/* ==========================================================================
   GabeBrain Corp - RPG 16-Bit (Zelda SNES Aesthetic)
   Plugin para Obsidian que transforma os agentes e subagentes do GabeBrain
   em departamentos de uma guilda/empresa com detecção de conflitos
   e convocação do Agente Estagiário / Revisor.
   ========================================================================== */

const obsidian = require("obsidian");
const { Plugin, ItemView, Notice, Modal, TFile } = obsidian;
const fs = require("fs");
const path = require("path");

const VIEW_TYPE_GABEBRAIN_RPG = "gabebrain-company-rpg-view";

// 16-bit Retro Audio Synthesizer (Web Audio API)
class RetroAudio {
  static playFanfare() {
    try {
      const ctx = new (window.AudioContext || window.webkitAudioContext)();
      const notes = [440, 554.37, 659.25, 880]; // A4, C#5, E5, A5
      notes.forEach((freq, idx) => {
        const osc = ctx.createOscillator();
        const gain = ctx.createGain();
        osc.type = "square";
        osc.frequency.setValueAtTime(freq, ctx.currentTime + idx * 0.1);
        gain.gain.setValueAtTime(0.08, ctx.currentTime + idx * 0.1);
        gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + idx * 0.1 + 0.25);
        osc.connect(gain);
        gain.connect(ctx.destination);
        osc.start(ctx.currentTime + idx * 0.1);
        osc.stop(ctx.currentTime + idx * 0.1 + 0.3);
      });
    } catch (e) {
      console.log("Audio not supported or blocked", e);
    }
  }

  static playAlert() {
    try {
      const ctx = new (window.AudioContext || window.webkitAudioContext)();
      const notes = [440, 370, 311.13]; // Descending alert
      notes.forEach((freq, idx) => {
        const osc = ctx.createOscillator();
        const gain = ctx.createGain();
        osc.type = "sawtooth";
        osc.frequency.setValueAtTime(freq, ctx.currentTime + idx * 0.12);
        gain.gain.setValueAtTime(0.1, ctx.currentTime + idx * 0.12);
        gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + idx * 0.12 + 0.2);
        osc.connect(gain);
        gain.connect(ctx.destination);
        osc.start(ctx.currentTime + idx * 0.12);
        osc.stop(ctx.currentTime + idx * 0.12 + 0.25);
      });
    } catch (e) {
      console.log("Audio not supported or blocked", e);
    }
  }
}

// 16-Bit SVG Pixel Art Sprites (SNES Zelda Inspiration)
const SPRITES = {
  // Link-style Ranger (Green tunic, cap, sword)
  geo: `<svg width="40" height="40" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg" style="image-rendering:pixelated">
    <!-- Cap -->
    <rect x="5" y="1" width="6" height="2" fill="#2d8a4e"/>
    <rect x="4" y="3" width="8" height="2" fill="#2d8a4e"/>
    <!-- Face / Hair -->
    <rect x="5" y="5" width="6" height="3" fill="#ffd199"/>
    <rect x="4" y="5" width="1" height="2" fill="#d08770"/>
    <rect x="11" y="5" width="1" height="2" fill="#d08770"/>
    <rect x="6" y="6" width="1" height="1" fill="#0b0f17"/>
    <rect x="9" y="6" width="1" height="1" fill="#0b0f17"/>
    <!-- Tunic -->
    <rect x="5" y="8" width="6" height="4" fill="#2d8a4e"/>
    <!-- Belt -->
    <rect x="5" y="10" width="6" height="1" fill="#8f3d23"/>
    <rect x="7" y="10" width="2" height="1" fill="#ebcb8b"/>
    <!-- Hands & Sword -->
    <rect x="3" y="9" width="2" height="2" fill="#ffd199"/>
    <rect x="11" y="9" width="2" height="2" fill="#ffd199"/>
    <rect x="2" y="7" width="1" height="5" fill="#eceff4"/>
    <rect x="1" y="10" width="3" height="1" fill="#ebcb8b"/>
    <!-- Boots -->
    <rect x="5" y="12" width="2" height="3" fill="#5e4431"/>
    <rect x="9" y="12" width="2" height="3" fill="#5e4431"/>
  </svg>`,

  // Detective / Scout (Blue tunic, spyglass, scroll)
  research: `<svg width="40" height="40" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg" style="image-rendering:pixelated">
    <!-- Hat -->
    <rect x="4" y="2" width="8" height="2" fill="#0277bd"/>
    <rect x="3" y="4" width="10" height="1" fill="#01579b"/>
    <!-- Face -->
    <rect x="5" y="5" width="6" height="3" fill="#ffd199"/>
    <rect x="6" y="6" width="1" height="1" fill="#0b0f17"/>
    <rect x="9" y="6" width="1" height="1" fill="#0b0f17"/>
    <!-- Tunic & Coat -->
    <rect x="4" y="8" width="8" height="4" fill="#0277bd"/>
    <!-- Spyglass -->
    <rect x="11" y="7" width="3" height="2" fill="#ebcb8b"/>
    <rect x="14" y="6" width="1" height="4" fill="#88c0d0"/>
    <!-- Boots -->
    <rect x="5" y="12" width="2" height="3" fill="#374151"/>
    <rect x="9" y="12" width="2" height="3" fill="#374151"/>
  </svg>`,

  // Cyber / Iron Knight (Armor, visor, hammer)
  dev: `<svg width="40" height="40" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg" style="image-rendering:pixelated">
    <!-- Helmet -->
    <rect x="5" y="1" width="6" height="4" fill="#64748b"/>
    <rect x="4" y="3" width="8" height="2" fill="#475569"/>
    <!-- Visor (Glowing Amber) -->
    <rect x="6" y="4" width="4" height="1" fill="#fbbf24"/>
    <!-- Armor -->
    <rect x="4" y="6" width="8" height="6" fill="#64748b"/>
    <rect x="6" y="8" width="4" height="2" fill="#f59e0b"/>
    <!-- Shield / Hammer -->
    <rect x="2" y="7" width="2" height="4" fill="#334155"/>
    <rect x="12" y="6" width="2" height="2" fill="#d97706"/>
    <rect x="12" y="8" width="1" height="4" fill="#78350f"/>
    <!-- Greaves -->
    <rect x="5" y="12" width="2" height="3" fill="#334155"/>
    <rect x="9" y="12" width="2" height="3" fill="#334155"/>
  </svg>`,

  // Mage / Scholar (Purple robe, wizard hat, spellbook)
  science: `<svg width="40" height="40" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg" style="image-rendering:pixelated">
    <!-- Pointed Hat -->
    <rect x="7" y="1" width="2" height="2" fill="#7b1fa2"/>
    <rect x="6" y="3" width="4" height="2" fill="#7b1fa2"/>
    <rect x="4" y="5" width="8" height="1" fill="#ba68c8"/>
    <!-- Beard & Face -->
    <rect x="6" y="6" width="4" height="2" fill="#ffd199"/>
    <rect x="5" y="8" width="6" height="2" fill="#eceff4"/>
    <!-- Robe -->
    <rect x="5" y="8" width="6" height="6" fill="#7b1fa2"/>
    <!-- Glowing Spellbook -->
    <rect x="2" y="9" width="3" height="3" fill="#e1bee7"/>
    <rect x="3" y="10" width="1" height="1" fill="#ffd700"/>
    <!-- Shoes -->
    <rect x="6" y="14" width="4" height="1" fill="#4a148c"/>
  </svg>`,

  // Bard / Designer (Rose doublet, beret, paintbrush)
  design: `<svg width="40" height="40" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg" style="image-rendering:pixelated">
    <!-- Beret with Feather -->
    <rect x="5" y="2" width="6" height="3" fill="#c2185b"/>
    <rect x="10" y="1" width="2" height="2" fill="#ebcb8b"/>
    <!-- Face -->
    <rect x="5" y="5" width="6" height="3" fill="#ffd199"/>
    <rect x="6" y="6" width="1" height="1" fill="#0b0f17"/>
    <rect x="9" y="6" width="1" height="1" fill="#0b0f17"/>
    <!-- Doublet -->
    <rect x="5" y="8" width="6" height="4" fill="#e91e63"/>
    <!-- Palette & Brush -->
    <rect x="2" y="9" width="3" height="3" fill="#f5c542"/>
    <rect x="12" y="7" width="1" height="5" fill="#8d6e63"/>
    <rect x="12" y="6" width="1" height="1" fill="#00e5ff"/>
    <!-- Boots -->
    <rect x="5" y="12" width="2" height="3" fill="#4a148c"/>
    <rect x="9" y="12" width="2" height="3" fill="#4a148c"/>
  </svg>`,

  // Estagiário / Colega Revisor (Yellow apprentice cap, huge glasses, scroll & quill)
  intern: `<svg width="32" height="32" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg" style="image-rendering:pixelated">
    <!-- Apprentice Cap -->
    <rect x="5" y="2" width="6" height="2" fill="#f59e0b"/>
    <!-- Big Glasses -->
    <rect x="4" y="4" width="8" height="3" fill="#ffd199"/>
    <rect x="4" y="5" width="3" height="2" fill="#0284c7"/>
    <rect x="9" y="5" width="3" height="2" fill="#0284c7"/>
    <rect x="7" y="5" width="2" height="1" fill="#334155"/>
    <!-- Tunic -->
    <rect x="5" y="7" width="6" height="5" fill="#10b981"/>
    <!-- Notebook / Quill -->
    <rect x="11" y="8" width="3" height="4" fill="#f8fafc"/>
    <rect x="12" y="6" width="1" height="2" fill="#f59e0b"/>
    <!-- Feet -->
    <rect x="5" y="12" width="2" height="2" fill="#78350f"/>
    <rect x="9" y="12" width="2" height="2" fill="#78350f"/>
  </svg>`
};

// Initial Department Blueprint (Matches GabeBrain 5-Cluster Architecture)
const INITIAL_DEPARTMENTS = [
  {
    id: "geo",
    name: "🌍 Geociências & Licenciamento",
    lead: "GeoAgent",
    leadRole: "Chefe de Geoprocessamento e Regulação",
    desc: "Cartografia digital, bacias hidrográficas, enquadramento ambiental municipal e acervo técnico do Drive.",
    sprite: "geo",
    cssClass: "dept-geo",
    hearts: 5,
    subagents: [
      { name: "geo-gis", role: "Cartografia & Folium" },
      { name: "geo-hidro", role: "Vazões & Recursos Hídricos" },
      { name: "geo-licencia", role: "Regulatório & Campo Bom" },
      { name: "geo-acervo", role: "Busca no Acervo do Drive" }
    ],
    skills: [
      "gis-multicamadas",
      "paleomap-refiner",
      "flow-report",
      "hydro-context",
      "licenciamento-campo-bom",
      "environmentalist-analyst",
      "biblioteca-pesquisavel",
      "biblioteca-triagem",
      "biblioteca-mapa-documento"
    ],
    intern: null
  },
  {
    id: "research",
    name: "🔍 Investigação & Inteligência Web",
    lead: "DeepResearchAgent",
    leadRole: "Comandante de Busca Profunda e Varredura",
    desc: "Pesquisa sistemática em 3 fases, extração estruturada de dados na web, issues do GitHub e síntese sem ruído.",
    sprite: "research",
    cssClass: "dept-research",
    hearts: 5,
    subagents: [
      { name: "research-lead", role: "Fase 1: Outline & Matriz" },
      { name: "web-scout", role: "Fase 2: Varredura Paralela" },
      { name: "report-synth", role: "Fase 3: Síntese e Validação" },
      { name: "gh-researcher", role: "Mineração GitHub CLI" }
    ],
    skills: [
      "deep-research",
      "research",
      "research-add-items",
      "research-add-fields",
      "research-deep",
      "research-report",
      "github-research",
      "web-para-nota"
    ],
    intern: null
  },
  {
    id: "dev",
    name: "💻 Engenharia de Software & AppSec",
    lead: "DevAgent",
    leadRole: "Líder Técnico, Guardião TDD e Anti-Alucinação",
    desc: "Desenvolvimento disciplinado com TDD Red/Green/Refactor, blindagem oficial Context7 e paridade Git Local/Nuvem.",
    sprite: "dev",
    cssClass: "dept-dev",
    hearts: 5,
    subagents: [
      { name: "coder-tdd", role: "TDD & Testes Automatizados" },
      { name: "context7-verifier", role: "Blindagem Anti-Alucinação" },
      { name: "appsec-auditor", role: "Auditoria AppSec & YARA" },
      { name: "vcs-sync", role: "Paridade GitHub & Arena AI" }
    ],
    skills: [
      "superpowers-coding-agent",
      "run-tests",
      "context7-mcp",
      "context7-cli",
      "find-docs",
      "skillspector-auditor",
      "karpathy-guidelines",
      "vcs-version-agent",
      "arena-ai-controller",
      "ecc-harness-optimizer"
    ],
    intern: null
  },
  {
    id: "science",
    name: "🎓 Produção Científica & PPGCA",
    lead: "ScienceAgent",
    leadRole: "Orientador de Pesquisa e Parecerista Acadêmico",
    desc: "Gestão do acervo Docling do mestrado, redação científica sem clichês (anti-AI slop) e peer review rigoroso.",
    sprite: "science",
    cssClass: "dept-science",
    hearts: 5,
    subagents: [
      { name: "ppgca-corpus", role: "Docling & Acervo PPGCA" },
      { name: "paper-writer", role: "Redação SBC/IEEE k-dense" },
      { name: "peer-reviewer", role: "Revisão Cega & Triagem Jev" }
    ],
    skills: [
      "computacao-aplicada",
      "anydoc",
      "scientific-writing",
      "scientific-writing-kdense",
      "no-ai-slop",
      "revisor-cientifico-peer-review",
      "scientific-thinking-scholar-evaluation",
      "jev"
    ],
    intern: null
  },
  {
    id: "design",
    name: "🎨 Criação, Design & Mídia",
    lead: "DesignAgent",
    leadRole: "Diretor de Arte e Ativos Digitais",
    desc: "Automação com Canva Pro via Playwright, banners, capas de artigos e suíte completa de favicons e Open Graph.",
    sprite: "design",
    cssClass: "dept-design",
    hearts: 5,
    subagents: [
      { name: "canva-designer", role: "Playwright & Canva Pro" },
      { name: "web-asset-maker", role: "Favicons & PWA Icons" }
    ],
    skills: [
      "canva-image-agent",
      "web-asset-generator"
    ],
    intern: null
  }
];

// Main Obsidian Plugin Class
class GabeBrainCompanyPlugin extends Plugin {
  async onload() {
    console.log("Loading GabeBrain Corp - RPG 16-Bit Plugin");

    this.registerView(
      VIEW_TYPE_GABEBRAIN_RPG,
      (leaf) => new GabeBrainCompanyView(leaf, this)
    );

    // Ribbon icon: Shield / Castle
    this.addRibbonIcon("shield", "GabeBrain Corp (RPG 16-Bit)", () => {
      this.activateView();
    });

    // Command in palette
    this.addCommand({
      id: "open-gabebrain-company-rpg",
      name: "Abrir GabeBrain Corp (Visão RPG 16-Bit)",
      callback: () => this.activateView(),
    });
  }

  async activateView() {
    const { workspace } = this.app;
    let leaf = workspace.getLeavesOfType(VIEW_TYPE_GABEBRAIN_RPG)[0];

    if (!leaf) {
      const newLeaf = workspace.getLeaf("tab");
      await newLeaf.setViewState({
        type: VIEW_TYPE_GABEBRAIN_RPG,
        active: true,
      });
      leaf = newLeaf;
    }
    workspace.revealLeaf(leaf);
  }
}

// Custom ItemView for GabeBrain Company RPG
class GabeBrainCompanyView extends ItemView {
  constructor(leaf, plugin) {
    super(leaf);
    this.plugin = plugin;
    this.departments = JSON.parse(JSON.stringify(INITIAL_DEPARTMENTS));
  }

  getViewType() {
    return VIEW_TYPE_GABEBRAIN_RPG;
  }

  getDisplayText() {
    return "GabeBrain Corp (16-Bit RPG)";
  }

  getIcon() {
    return "shield";
  }

  async onOpen() {
    await this.loadPluginData();
    this.renderView();
  }

  async loadPluginData() {
    const data = await this.plugin.loadData();
    if (data && data.departments) {
      this.departments = data.departments;
    }
  }

  async savePluginData() {
    await this.plugin.saveData({ departments: this.departments });
  }

  renderView() {
    const container = this.containerEl.children[1];
    container.empty();

    const root = container.createDiv({ cls: "gb-rpg-container" });

    // Header Banner
    const header = root.createDiv({ cls: "gb-rpg-header pixel-box-gold" });
    const titleWrap = header.createDiv({ cls: "gb-rpg-title-wrap" });
    const crest = titleWrap.createDiv({ cls: "gb-rpg-crest" });
    crest.innerHTML = `<span style="font-size:24px;">👑</span>`;

    const titleText = titleWrap.createDiv();
    titleText.createEl("h1", { text: "GABEBRAIN CORP • GUILDA DOS AGENTES" });
    titleText.createEl("p", { text: "Visão Departamental 16-Bit • SNES Zelda Style • 5 Clusters & Subagentes" });

    const stats = header.createDiv({ cls: "gb-rpg-header-stats" });
    stats.createDiv({ cls: "stat-pill" }).innerHTML = `DEPARTAMENTOS: <strong>5</strong>`;
    
    let totalSkills = 0;
    let totalInterns = 0;
    this.departments.forEach(d => {
      totalSkills += d.skills.length;
      if (d.intern && d.intern.active) totalInterns++;
    });

    stats.createDiv({ cls: "stat-pill" }).innerHTML = `SKILLS ATIVAS: <strong>${totalSkills}</strong>`;
    stats.createDiv({ cls: "stat-pill" }).innerHTML = `ESTAGIÁRIOS REVISORES: <strong>${totalInterns}</strong>`;

    // Departments Grid
    const grid = root.createDiv({ cls: "gb-departments-grid" });

    this.departments.forEach((dept) => {
      this.renderDepartmentCard(grid, dept);
    });
  }

  renderDepartmentCard(parent, dept) {
    const card = parent.createDiv({ cls: `gb-dept-card pixel-box ${dept.cssClass}` });

    // Drag and drop event listeners
    card.addEventListener("dragover", (e) => {
      e.preventDefault();
      e.stopPropagation();
      card.addClass("drag-over");
    });

    card.addEventListener("dragleave", (e) => {
      e.preventDefault();
      e.stopPropagation();
      card.removeClass("drag-over");
    });

    card.addEventListener("drop", async (e) => {
      e.preventDefault();
      e.stopPropagation();
      card.removeClass("drag-over");

      let droppedSkillName = "";
      let droppedSkillContent = "";

      // Check if file was dropped from desktop or obsidian file tree
      if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
        const file = e.dataTransfer.files[0];
        droppedSkillName = file.name.replace(/\.md$/, "");
        droppedSkillContent = await file.text();
      } else {
        const text = e.dataTransfer.getData("text/plain");
        if (text) {
          droppedSkillName = text.trim().replace(/^\[\[/, "").replace(/\]\]$/, "").replace(/\.md$/, "");
        }
      }

      if (!droppedSkillName) {
        new Notice("Arraste um arquivo .md válido!");
        return;
      }

      this.processNewSkill(dept, droppedSkillName, droppedSkillContent);
    });

    // Card Header (Sprite, Name, Hearts)
    const header = card.createDiv({ cls: "gb-dept-header" });
    const spriteBox = header.createDiv({ cls: "gb-sprite-box sprite-anim" });
    spriteBox.innerHTML = SPRITES[dept.sprite] || SPRITES.geo;

    const info = header.createDiv({ cls: "gb-dept-info" });
    info.createEl("h3", { text: dept.name });
    info.createDiv({ cls: "gb-lead-badge", text: `👑 Líder: ${dept.lead}` });

    const heartsWrap = info.createDiv({ cls: "hearts-container" });
    for (let i = 0; i < dept.hearts; i++) {
      heartsWrap.createSpan({ text: "❤️" });
    }

    // Subagents List
    const teamSection = card.createDiv({ cls: "gb-team-section" });
    teamSection.createDiv({ cls: "gb-section-label" }).innerHTML = `<span>👥</span> Equipe de Subagentes:`;
    
    const subList = teamSection.createDiv({ cls: "gb-subagents-list" });
    dept.subagents.forEach((sa) => {
      const row = subList.createDiv({ cls: "gb-subagent-row" });
      row.createSpan({ cls: "gb-subagent-name", text: `sub: ${sa.name}` });
      row.createSpan({ cls: "gb-subagent-role", text: sa.role });
    });

    // Intern / Estagiário Box (if summoned!)
    if (dept.intern && dept.intern.active) {
      const internBox = card.createDiv({ cls: "gb-intern-box" });
      const internAvatar = internBox.createDiv({ cls: "gb-intern-avatar" });
      internAvatar.innerHTML = SPRITES.intern;

      const internText = internBox.createDiv({ cls: "gb-intern-text" });
      internText.createDiv({ cls: "gb-intern-title" }).innerHTML = `🎓 <span>${dept.intern.title} Ativo!</span>`;
      internText.createDiv({ cls: "gb-intern-desc", text: dept.intern.reason });
    }

    // Skills Badges Section
    const skillsSection = card.createDiv({ cls: "gb-skills-section" });
    skillsSection.createDiv({ cls: "gb-section-label" }).innerHTML = `<span>🛠️</span> Skills Alocadas (${dept.skills.length}):`;
    
    const skillsWrap = skillsSection.createDiv({ cls: "gb-skills-wrap" });
    dept.skills.forEach((skill) => {
      const isNew = dept.intern && dept.intern.reviewedSkills && dept.intern.reviewedSkills.includes(skill);
      const tag = skillsWrap.createSpan({ cls: `gb-skill-tag ${isNew ? "new-skill" : ""}` });
      tag.innerHTML = `⚙️ ${skill}`;
    });

    // Drop Zone Banner
    const dropZone = card.createDiv({ cls: "gb-drop-zone" });
    dropZone.innerHTML = `📥 <b>ARRASTE UM ARQUIVO .MD AQUI</b><br><span style="font-size:8.5px; opacity:0.8;">O departamento verificará conflitos antes de aceitar</span>`;
    dropZone.addEventListener("click", () => {
      this.openAddSkillModal(dept);
    });

    // Action Button
    const btn = card.createEl("button", {
      cls: "gb-btn-retro gb-btn-green",
      text: "➕ ADICIONAR NOVA SKILL"
    });
    btn.addEventListener("click", () => {
      this.openAddSkillModal(dept);
    });
  }

  // Conflict Detection Logic
  checkSkillConflict(dept, newSkillName, content = "") {
    const nameLower = newSkillName.toLowerCase();
    const contentLower = content.toLowerCase();

    // Map of conflicting categories
    const CONFLICT_RULES = {
      geo: [
        {
          terms: ["gis", "map", "folium", "qgis", "cartografia", "camadas", "leaflet"],
          conflictsWith: "gis-multicamadas",
          reason: "ambas geram ou estilizam mapas e camadas vetoriais"
        },
        {
          terms: ["hidro", "flow", "vazao", "chuva", "rio", "bacia", "q95"],
          conflictsWith: "flow-report",
          reason: "ambas processam séries de vazão e cálculos de outorga"
        },
        {
          terms: ["licencia", "consema", "campo-bom", "codram", "art", "plano-diretor"],
          conflictsWith: "licenciamento-campo-bom",
          reason: "ambas realizam enquadramento ambiental e conformidade locacional"
        },
        {
          terms: ["biblioteca", "pesquisa-pdf", "acervo", "triagem", "leitura-pdf"],
          conflictsWith: "biblioteca-pesquisavel",
          reason: "ambas indexam ou leem trechos da Biblioteca Geológica"
        }
      ],
      research: [
        {
          terms: ["search", "crawl", "scrap", "web", "busca", "pesquisa-profunda"],
          conflictsWith: "web-search-agent",
          reason: "ambas executam crawling e varredura de múltiplos sites na internet"
        },
        {
          terms: ["github", "gh", "pull-request", "issue", "repositorio"],
          conflictsWith: "github-research",
          reason: "ambas mineram o histórico de issues e commits do GitHub"
        },
        {
          terms: ["relatorio", "sintese", "report", "nota-limpa", "defuddle"],
          conflictsWith: "research-report",
          reason: "ambas sintetizam achados web em relatórios Markdown com citação"
        }
      ],
      dev: [
        {
          terms: ["test", "pytest", "tdd", "green", "red", "refactor", "unit"],
          conflictsWith: "superpowers-coding-agent",
          reason: "ambas orquestram o ciclo Red/Green/Refactor e suítes de testes"
        },
        {
          terms: ["docs", "documentacao", "context7", "ctx7", "api-lookup"],
          conflictsWith: "context7-verifier",
          reason: "ambas consultam APIs e documentações oficiais de bibliotecas"
        },
        {
          terms: ["security", "seguranca", "audit", "vulnerability", "yara", "owasp"],
          conflictsWith: "skillspector-auditor",
          reason: "ambas analisam segurança estática e padrões de vulnerabilidade"
        },
        {
          terms: ["git", "vcs", "branch", "sync", "arena", "harness"],
          conflictsWith: "vcs-version-agent",
          reason: "ambas gerenciam sincronização de branches e paridade de versões"
        }
      ],
      science: [
        {
          terms: ["docling", "pdf-convert", "corpus", "ficha", "anydoc", "word"],
          conflictsWith: "computacao-aplicada",
          reason: "ambas convertem ou indexam documentos científicos no acervo PPGCA"
        },
        {
          terms: ["write", "redacao", "slop", "humanizada", "artigo", "paper"],
          conflictsWith: "scientific-writing",
          reason: "ambas redigem manuscritos científicos e formatam voz ativa"
        },
        {
          terms: ["review", "peer", "revisor", "parecer", "epistemico", "jev"],
          conflictsWith: "revisor-cientifico-peer-review",
          reason: "ambas simulam avaliação cega de manuscritos para congressos"
        }
      ],
      design: [
        {
          terms: ["canva", "banner", "capa", "playwright-design", "infografico"],
          conflictsWith: "canva-image-agent",
          reason: "ambas criam artes gráficas automatizadas no Canva Pro"
        },
        {
          terms: ["favicon", "icon", "pwa", "open-graph", "og-image"],
          conflictsWith: "web-asset-generator",
          reason: "ambas redimensionam e exportam metatags e ativos para sites"
        }
      ]
    };

    const rules = CONFLICT_RULES[dept.id] || [];

    for (const rule of rules) {
      // Check if incoming skill matches keywords AND conflicting skill exists in dept
      const matchesKeyword = rule.terms.some(t => nameLower.includes(t) || contentLower.includes(t));
      if (matchesKeyword && dept.skills.includes(rule.conflictsWith)) {
        return {
          hasConflict: true,
          conflictingSkill: rule.conflictsWith,
          reason: rule.reason
        };
      }
    }

    return { hasConflict: false };
  }

  // Handle addition of a skill (with Zelda dialogue if conflict occurs)
  processNewSkill(dept, newSkillName, content = "") {
    // If skill is already present
    if (dept.skills.includes(newSkillName)) {
      new Notice(`A skill "${newSkillName}" já está alocada neste departamento.`);
      return;
    }

    const check = this.checkSkillConflict(dept, newSkillName, content);

    if (check.hasConflict) {
      // PLAY 16-BIT ALERT SOUND
      RetroAudio.playAlert();

      // OPEN ZELDA DIALOGUE BOX
      this.showConflictModal(dept, newSkillName, check.conflictingSkill, check.reason, content);
    } else {
      // NO CONFLICT -> ACCEPT DIRECTLY
      RetroAudio.playFanfare();
      dept.skills.push(newSkillName);
      this.savePluginData();
      this.renderView();
      new Notice(`✨ Skill "${newSkillName}" aceita e integrada com sucesso ao ${dept.name}!`);
    }
  }

  // Zelda SNES Dialogue Box Modal for Conflict & Intern Summoning
  showConflictModal(dept, newSkillName, conflictingSkill, reason, content) {
    const overlay = document.body.createDiv({ cls: "gb-dialogue-overlay" });
    const box = overlay.createDiv({ cls: "gb-dialogue-box pixel-box-gold" });

    const top = box.createDiv({ cls: "gb-dialogue-top" });
    const portrait = top.createDiv({ cls: "gb-dialogue-portrait" });
    portrait.innerHTML = SPRITES.intern;

    const contentDiv = top.createDiv({ cls: "gb-dialogue-content" });
    contentDiv.createDiv({ cls: "gb-dialogue-speaker", text: "📜 Mestre da Guilda GabeBrain:" });
    
    const dialogText = contentDiv.createDiv({ cls: "gb-dialogue-text" });
    dialogText.innerHTML = `
      ⚔️ <b>ALERTA DE CONFLITO FUNCIONAL!</b><br><br>
      A nova skill <b>"${newSkillName}"</b> interfere diretamente na função da skill existente <b>"${conflictingSkill}"</b> (${reason}).<br><br>
      Nas diretrizes da GabeBrain Corp, nunca descartamos ferramentas úteis nem deixamos que uma sobrescreva a outra de forma destrutiva.<br><br>
      <b>Solução Proposta:</b> Convocaremos um <b>Subagente Estagiário / Revisor</b> (${dept.id}-estagiario-revisor) para atuar como colega de trabalho, auditar os resultados de ambas as ferramentas e propor a melhor integração!
    `;

    const actions = box.createDiv({ cls: "gb-dialogue-actions" });
    
    const cancelBtn = actions.createEl("button", {
      cls: "gb-btn-retro",
      text: "CANCELAR"
    });
    cancelBtn.addEventListener("click", () => {
      overlay.remove();
    });

    const summonBtn = actions.createEl("button", {
      cls: "gb-btn-retro gb-btn-gold",
      text: "🎓 CONVOCAR ESTAGIÁRIO REVISOR"
    });

    summonBtn.addEventListener("click", async () => {
      overlay.remove();
      await this.summonInternAgent(dept, newSkillName, conflictingSkill, reason);
    });
  }

  // Summon the Estagiário / Revisor Subagent!
  async summonInternAgent(dept, newSkillName, conflictingSkill, reason) {
    const internName = `${dept.id}-estagiario-revisor`;
    const internTitle = `Estagiário Revisor (${dept.lead})`;

    // 1. Update State
    dept.intern = {
      name: internName,
      title: internTitle,
      active: true,
      reason: `Mediação e revisão entre "${conflictingSkill}" e "${newSkillName}".`,
      reviewedSkills: [conflictingSkill, newSkillName]
    };

    // Add skill to department alongside existing
    dept.skills.push(newSkillName);

    // Add subagent entry if not already present
    if (!dept.subagents.some(s => s.name === internName)) {
      dept.subagents.push({
        name: internName,
        role: "Colega Revisor & Mediação"
      });
    }

    // 2. Generate actual Subagent Markdown file in vault and system
    const internMdContent = `---
name: ${internName}
description: Subagente Estagiário e Revisor do departamento ${dept.name}. Atua como colega de trabalho que inspeciona a execução de ${conflictingSkill} e ${newSkillName}, audita resultados e propõe melhorias arquiteturais.
model: inherit
---

# ${internTitle} 🎓

Você é o **${internName}**, o colega estagiário/revisor alocado no **${dept.name}**.

### 🎯 Missão de Mediação:
Você foi convocado devido a uma sobreposição de escopo entre:
- \`${conflictingSkill}\` (Skill Titular Prévia)
- \`${newSkillName}\` (Nova Skill Integrada)

### 📋 Suas Atribuições de Colega de Trabalho:
1. **Auditar Execuções:** Sempre que uma das skills for acionada, inspecione as saídas e confira se há incoerências ou limitações.
2. **Propor Alternativas Construtivas:** Se a skill titular falhar ou tiver custos altos de processamento, recomende a execução da nova skill como fallback cirúrgico.
3. **Harmonização de Contexto:** Garantir que o departamento nunca perca consistência funcional, emitindo pareceres de melhoria contínua.

### 🌐 Departamento:
- **Cluster Líder:** \`${dept.lead}\`
- **Guilda:** GabeBrain Corp
`;

    // Write file in vault's .claude/agents/
    try {
      const vaultPath = this.app.vault.adapter.basePath;
      if (vaultPath) {
        const agentDestDir = path.join(vaultPath, ".claude", "agents");
        if (!fs.existsSync(agentDestDir)) {
          fs.mkdirSync(agentDestDir, { recursive: true });
        }
        fs.writeFileSync(path.join(agentDestDir, `${internName}.md`), internMdContent, "utf-8");

        // Also write a Master Note in 📚 Biblioteca de Agentes
        const mastersDir = path.join(vaultPath, "📚 Biblioteca de Agentes");
        if (fs.existsSync(mastersDir)) {
          const masterNote = `# Master ${internName} 🎓\n\nSubagente estagiário revisor de ${dept.name}.\n\n[[00 - Índice da Biblioteca de Agentes|Voltar]]`;
          fs.writeFileSync(path.join(mastersDir, `Master_${internName}.md`), masterNote, "utf-8");
        }
      }
    } catch (err) {
      console.log("Could not write local agent file directly", err);
    }

    // 3. Play fanfare and update UI
    RetroAudio.playFanfare();
    await this.savePluginData();
    this.renderView();

    new Notice(`🎓 O Estagiário Revisor "${internName}" foi contratado e alocado com sucesso!`);
  }

  // Modal to Add Skill Manually or from Vault
  openAddSkillModal(dept) {
    const modal = new Modal(this.app);
    modal.titleEl.setText(`➕ Adicionar Skill ao ${dept.name}`);

    const content = modal.contentEl;
    content.createEl("p", {
      text: "Digite o nome da skill ou selecione um arquivo Markdown do seu cofre para o departamento analisar:"
    });

    const inputWrap = content.createDiv({ cls: "setting-item" });
    const input = inputWrap.createEl("input", {
      type: "text",
      placeholder: "Ex: geo-raster-analyzer, semantic-scholar-api, etc."
    });
    input.style.width = "100%";
    input.style.padding = "8px";
    input.style.marginBottom = "14px";
    input.style.background = "#111622";
    input.style.border = "2px solid #3b4252";
    input.style.color = "#eceff4";

    const btnWrap = content.createDiv({ style: "display: flex; justify-content: flex-end; gap: 8px;" });

    const cancelBtn = btnWrap.createEl("button", { text: "Cancelar" });
    cancelBtn.addEventListener("click", () => modal.close());

    const submitBtn = btnWrap.createEl("button", {
      text: "🔍 Analisar e Incorporar",
      cls: "mod-cta"
    });

    submitBtn.addEventListener("click", () => {
      const val = input.value.trim();
      if (!val) {
        new Notice("Por favor, digite o nome da skill!");
        return;
      }
      modal.close();
      this.processNewSkill(dept, val);
    });

    modal.open();
    input.focus();
  }
}

module.exports = GabeBrainCompanyPlugin;
