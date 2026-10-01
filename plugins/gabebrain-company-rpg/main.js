/* ==========================================================================
   GabeBrain Corp - RPG 16-Bit (Zelda SNES Office Chamber & Work Desks)
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
  geo: `<svg width="44" height="44" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg" style="image-rendering:pixelated">
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
  research: `<svg width="44" height="44" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg" style="image-rendering:pixelated">
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
  dev: `<svg width="44" height="44" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg" style="image-rendering:pixelated">
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
  science: `<svg width="44" height="44" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg" style="image-rendering:pixelated">
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
  design: `<svg width="44" height="44" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg" style="image-rendering:pixelated">
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

  // Estagiário / Colega Revisor (Yellow apprentice cap, big glasses, parchment)
  intern: `<svg width="36" height="36" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg" style="image-rendering:pixelated">
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

// Initial Departments Definition (Matching the GabeBrain 5-Cluster System)
const INITIAL_DEPARTMENTS = [
  {
    id: "geo",
    name: "🌍 Divisão de Geociências & Licenciamento",
    lead: "GeoAgent",
    leadRole: "Chefe de Cartografia, Hidrogeologia & Regulação",
    desc: "Cartografia digital, bacias hidrográficas, enquadramento ambiental municipal e acervo técnico do Drive.",
    sprite: "geo",
    rugClass: "rug-geo",
    hearts: 5,
    subagents: [
      { name: "geo-gis", role: "Cartografia & Folium" },
      { name: "geo-hidro", role: "Vazões & Outorgas" },
      { name: "geo-licencia", role: "Regulatório & Campo Bom" },
      { name: "geo-acervo", role: "Busca Acervo Drive" }
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
    name: "🔍 Central de Inteligência & Deep Research",
    lead: "DeepResearchAgent",
    leadRole: "Comandante de Varredura Web & Mineração",
    desc: "Pesquisa sistemática em 3 fases, extração estruturada de dados na web, issues do GitHub e síntese sem ruído.",
    sprite: "research",
    rugClass: "rug-research",
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
    name: "💻 Laboratório de Engenharia & AppSec",
    lead: "DevAgent",
    leadRole: "Arquiteto Chefe, Guardião TDD e Anti-Alucinação",
    desc: "Desenvolvimento disciplinado com TDD Red/Green/Refactor, blindagem oficial Context7 e paridade Git Local/Nuvem.",
    sprite: "dev",
    rugClass: "rug-dev",
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
    name: "🎓 Academia Científica & Mestrado PPGCA",
    lead: "ScienceAgent",
    leadRole: "Orientador de Pesquisa & Parecerista Sênior",
    desc: "Gestão do acervo Docling do mestrado, redação científica sem clichês (anti-AI slop) e peer review rigoroso.",
    sprite: "science",
    rugClass: "rug-science",
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
    name: "🎨 Estúdio de Criação, Design & Mídia",
    lead: "DesignAgent",
    leadRole: "Diretor de Arte, Identidade Visual & Assets",
    desc: "Automação com Canva Pro via Playwright, banners, capas de artigos e suíte completa de favicons e Open Graph.",
    sprite: "design",
    rugClass: "rug-design",
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

class GabeBrainCompanyPlugin extends Plugin {
  async onload() {
    console.log("Loading GabeBrain Corp - RPG 16-Bit Office Plugin");

    // Sincronizar skills e salas automaticamente ao abrir o Obsidian
    await this.syncAllSkills(false);

    this.registerView(
      VIEW_TYPE_GABEBRAIN_RPG,
      (leaf) => new GabeBrainCompanyView(leaf, this)
    );

    this.addRibbonIcon("shield", "GabeBrain Corp (RPG 16-Bit)", () => {
      this.activateView();
    });

    this.addCommand({
      id: "open-gabebrain-company-rpg",
      name: "Abrir GabeBrain Corp (Visão RPG 16-Bit)",
      callback: () => this.activateView(),
    });

    this.addCommand({
      id: "sync-gabebrain-company-rpg",
      name: "Sincronizar Skills e Salas Departamentais",
      callback: async () => {
        await this.syncAllSkills(true);
      },
    });

    // Hook no evento beforeunload para sincronizar e salvar ao fechar o Obsidian
    this.beforeUnloadHandler = () => {
      this.syncAllSkillsSync();
    };
    window.addEventListener("beforeunload", this.beforeUnloadHandler);
  }

  async onunload() {
    console.log("Unloading GabeBrain Corp - RPG 16-Bit Office Plugin");
    if (this.beforeUnloadHandler) {
      window.removeEventListener("beforeunload", this.beforeUnloadHandler);
    }
    // Sincronizar e salvar ao descarregar/fechar o Obsidian
    await this.syncAllSkills(false);
  }

  // Sincronização síncrona executada no fechamento da janela
  syncAllSkillsSync() {
    try {
      const basePath = this.app.vault.adapter.basePath;
      if (!basePath) return;
      const dataFile = path.join(basePath, ".obsidian", "plugins", "gabebrain-company-rpg", "data.json");
      let departments = JSON.parse(JSON.stringify(INITIAL_DEPARTMENTS));

      if (fs.existsSync(dataFile)) {
        try {
          const raw = fs.readFileSync(dataFile, "utf-8");
          const parsed = JSON.parse(raw);
          if (parsed && parsed.departments) departments = parsed.departments;
        } catch (e) {}
      }

      departments = this.scanAndMergeSkills(departments);
      fs.writeFileSync(dataFile, JSON.stringify({ departments: departments }, null, 2), "utf-8");
      console.log("GabeBrain Corp: Salvo com sucesso ao fechar o Obsidian.");
    } catch (e) {
      console.log("Error during beforeunload sync", e);
    }
  }

  // Sincronização assíncrona executada na inicialização ou via comando
  async syncAllSkills(notify = false) {
    try {
      let data = await this.loadData();
      let depts = (data && data.departments) ? data.departments : JSON.parse(JSON.stringify(INITIAL_DEPARTMENTS));
      depts = this.scanAndMergeSkills(depts);
      await this.saveData({ departments: depts });

      // Atualizar a view se estiver aberta
      const { workspace } = this.app;
      const leaf = workspace.getLeavesOfType(VIEW_TYPE_GABEBRAIN_RPG)[0];
      if (leaf && leaf.view) {
        leaf.view.departments = depts;
        leaf.view.renderView();
      }

      if (notify) {
        new Notice("⚔️ GabeBrain Corp: Skills e salas atualizadas com o acervo!");
      }
    } catch (err) {
      console.log("Error syncing skills", err);
    }
  }

  // Algoritmo de varredura e agrupamento de skills do sistema e cofre
  scanAndMergeSkills(departments) {
    const homeDir = process.env.USERPROFILE || process.env.HOME || "C:\\Users\\Gabriel";
    const geminiSkillsDir = path.join(homeDir, ".gemini", "config", "skills");
    const basePath = this.app.vault.adapter.basePath || "";
    const vaultSkillsDir = path.join(basePath, "20-Skills");
    const vaultAgentsDir = path.join(basePath, ".claude", "agents");

    const foundSkills = new Set();

    // 1. Ler ~/.gemini/config/skills
    if (fs.existsSync(geminiSkillsDir)) {
      try {
        const entries = fs.readdirSync(geminiSkillsDir, { withFileTypes: true });
        for (const entry of entries) {
          if (entry.isDirectory() && !entry.name.startsWith(".")) {
            foundSkills.add(entry.name);
          }
        }
      } catch (e) {}
    }

    // 2. Ler 20-Skills no cofre
    if (fs.existsSync(vaultSkillsDir)) {
      try {
        const files = fs.readdirSync(vaultSkillsDir);
        for (const file of files) {
          if (file.endsWith(".md") && !file.startsWith("00")) {
            foundSkills.add(file.replace(/\.md$/, ""));
          }
        }
      } catch (e) {}
    }

    // 3. Mapeamento Canônico de Domínios
    const DOMAIN_MAP = {
      // Geo
      "gis-multicamadas": "geo",
      "paleomap-refiner": "geo",
      "flow-report": "geo",
      "hydro-context": "geo",
      "licenciamento-campo-bom": "geo",
      "environmentalist-analyst": "geo",
      "biblioteca-pesquisavel": "geo",
      "biblioteca-triagem": "geo",
      "biblioteca-mapa-documento": "geo",
      // Research
      "deep-research": "research",
      "research": "research",
      "research-add-items": "research",
      "research-add-fields": "research",
      "research-deep": "research",
      "research-report": "research",
      "github-research": "research",
      "web-para-nota": "research",
      "web-search-agent": "research",
      // Dev
      "superpowers-coding-agent": "dev",
      "run-tests": "dev",
      "context7-mcp": "dev",
      "context7-cli": "dev",
      "find-docs": "dev",
      "skillspector-auditor": "dev",
      "karpathy-guidelines": "dev",
      "vcs-version-agent": "dev",
      "arena-ai-controller": "dev",
      "ecc-harness-optimizer": "dev",
      "desktop-screenshot": "dev",
      "sprout-cli": "dev",
      // Science
      "computacao-aplicada": "science",
      "anydoc": "science",
      "scientific-writing": "science",
      "scientific-writing-kdense": "science",
      "no-ai-slop": "science",
      "revisor-cientifico-peer-review": "science",
      "scientific-thinking-scholar-evaluation": "science",
      "jev": "science",
      // Design
      "canva-image-agent": "design",
      "web-asset-generator": "design"
    };

    // Alocar skills
    for (const skill of foundSkills) {
      let targetDeptId = DOMAIN_MAP[skill];

      if (!targetDeptId) {
        const sLower = skill.toLowerCase();
        if (sLower.includes("geo") || sLower.includes("gis") || sLower.includes("hidro") || sLower.includes("map")) {
          targetDeptId = "geo";
        } else if (sLower.includes("search") || sLower.includes("crawl") || sLower.includes("research")) {
          targetDeptId = "research";
        } else if (sLower.includes("dev") || sLower.includes("code") || sLower.includes("test") || sLower.includes("git")) {
          targetDeptId = "dev";
        } else if (sLower.includes("science") || sLower.includes("paper") || sLower.includes("docling") || sLower.includes("review")) {
          targetDeptId = "science";
        } else if (sLower.includes("design") || sLower.includes("canva") || sLower.includes("asset") || sLower.includes("icon")) {
          targetDeptId = "design";
        }
      }

      if (targetDeptId) {
        const dept = departments.find(d => d.id === targetDeptId);
        if (dept && !dept.skills.includes(skill)) {
          dept.skills.push(skill);
        }
      }
    }

    // 4. Reconhecer estagiários existentes em .claude/agents/
    if (fs.existsSync(vaultAgentsDir)) {
      try {
        const agentFiles = fs.readdirSync(vaultAgentsDir);
        for (const file of agentFiles) {
          if (file.endsWith("-estagiario-revisor.md")) {
            const deptId = file.split("-estagiario-revisor.md")[0];
            const dept = departments.find(d => d.id === deptId);
            if (dept) {
              if (!dept.intern || !dept.intern.active) {
                dept.intern = {
                  name: `${deptId}-estagiario-revisor`,
                  title: `Estagiário Revisor (${dept.lead})`,
                  active: true,
                  reason: `Mesa ativa e preservada para mediação contínua.`
                };
              }
              if (!dept.subagents.some(s => s.name === `${deptId}-estagiario-revisor`)) {
                dept.subagents.push({
                  name: `${deptId}-estagiario-revisor`,
                  role: "Colega Revisor & Mediação"
                });
              }
            }
          }
        }
      } catch (e) {}
    }

    return departments;
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

    // Top Office Master Signboard
    const header = root.createDiv({ cls: "gb-rpg-header" });
    const titleWrap = header.createDiv({ cls: "gb-rpg-title-wrap" });
    const crest = titleWrap.createDiv({ cls: "gb-rpg-crest" });
    crest.innerHTML = `<span>👑</span>`;

    const titleText = titleWrap.createDiv();
    titleText.createEl("h1", { text: "GABEBRAIN CORP • ESCRITÓRIO DOS AGENTES" });
    titleText.createEl("p", { text: "Ambiente 16-Bit SNES Zelda • 5 Salas Departamentais • Mesas de Trabalho & Quadros Negros" });

    const stats = header.createDiv({ cls: "gb-rpg-header-stats" });
    stats.createDiv({ cls: "stat-pill" }).innerHTML = `SALAS: <strong>5</strong>`;
    
    let totalSkills = 0;
    let totalInterns = 0;
    this.departments.forEach(d => {
      totalSkills += d.skills.length;
      if (d.intern && d.intern.active) totalInterns++;
    });

    stats.createDiv({ cls: "stat-pill" }).innerHTML = `SKILLS NO QUADRO: <strong>${totalSkills}</strong>`;
    stats.createDiv({ cls: "stat-pill" }).innerHTML = `ESTAGIÁRIOS NA MESA: <strong>${totalInterns}</strong>`;

    // Departments Grid (Office Chambers with Wooden Divisórias)
    const grid = root.createDiv({ cls: "gb-departments-grid" });

    this.departments.forEach((dept) => {
      this.renderOfficeChamber(grid, dept);
    });
  }

  // Renders each Department as a 16-bit Office Chamber with partition walls, desk, rug and blackboard
  renderOfficeChamber(parent, dept) {
    const chamber = parent.createDiv({ cls: "gb-office-cubicle" });

    // Drag-over event listeners on the entire cubicle
    chamber.addEventListener("dragover", (e) => {
      e.preventDefault();
      e.stopPropagation();
      chamber.addClass("drag-over");
    });

    chamber.addEventListener("dragleave", (e) => {
      e.preventDefault();
      e.stopPropagation();
      chamber.removeClass("drag-over");
    });

    chamber.addEventListener("drop", async (e) => {
      e.preventDefault();
      e.stopPropagation();
      chamber.removeClass("drag-over");

      let droppedSkillName = "";
      let droppedSkillContent = "";

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
        new Notice("Por favor, arraste um arquivo .md válido!");
        return;
      }

      this.processNewSkill(dept, droppedSkillName, droppedSkillContent);
    });

    // 1. Hanging Wall Signboard (Room Name & Readiness Hearts)
    const sign = chamber.createDiv({ cls: "cubicle-signboard" });
    const titleEl = sign.createEl("h3");
    titleEl.innerHTML = `<span>🚪</span> ${dept.name}`;

    const heartsWrap = sign.createDiv({ cls: "hearts-container" });
    for (let i = 0; i < dept.hearts; i++) {
      heartsWrap.createSpan({ text: "❤️" });
    }

    // 2. Office Floor Area: Decorative Rug with Character Sprite + Interactive Work Desk Button
    const floorArea = chamber.createDiv({ cls: "cubicle-floor-area" });

    // Carpet / Rug where the Lead Agent Sprite stands
    const rug = floorArea.createDiv({ cls: `cubicle-rug ${dept.rugClass}` });
    const actorBox = rug.createDiv({ cls: "sprite-actor" });
    actorBox.innerHTML = SPRITES[dept.sprite] || SPRITES.geo;
    rug.createDiv({ cls: "actor-label", text: dept.lead });

    // The Interactive Work Desk (Mesa de Trabalho) - Serves as action button and drop target!
    const desk = floorArea.createDiv({ cls: "rpg-work-desk" });
    desk.title = `Mesa de trabalho de ${dept.lead}. Clique para adicionar uma nova skill ou arraste o .md para cá!`;

    const deskSurface = desk.createDiv({ cls: "desk-surface" });
    deskSurface.createSpan({ cls: "desk-icon", text: "🪑" });

    const deskTexts = deskSurface.createDiv();
    deskTexts.createDiv({ cls: "desk-text-title", text: `Mesa de ${dept.lead}` });
    deskTexts.createDiv({ cls: "desk-text-subtitle", text: "Clique para examinar ou solte uma nova skill aqui." });

    const actionPill = desk.createDiv({ cls: "desk-action-pill" });
    actionPill.innerHTML = `<span>📜</span> ALOCAR NOVA SKILL`;

    // Clicking the work desk opens the modal
    desk.addEventListener("click", () => {
      this.openAddSkillModal(dept);
    });

    // 3. The Blackboard for Skills (Quadro Negro de Giz)
    const blackboard = chamber.createDiv({ cls: "rpg-blackboard" });
    const bbHeader = blackboard.createDiv({ cls: "blackboard-header" });
    
    const bbTitle = bbHeader.createDiv({ cls: "blackboard-title" });
    bbTitle.innerHTML = `<span>📋</span> QUADRO DE SKILLS ATIVAS`;

    bbHeader.createDiv({ cls: "chalk-count", text: `${dept.skills.length} skills inscritas` });

    const chalkGrid = blackboard.createDiv({ cls: "blackboard-skills-grid" });
    dept.skills.forEach((skill) => {
      const isNew = dept.intern && dept.intern.reviewedSkills && dept.intern.reviewedSkills.includes(skill);
      const tag = chalkGrid.createSpan({ cls: `chalk-tag ${isNew ? "new-chalk" : ""}` });
      tag.innerHTML = `<span>✏️</span> ${skill}`;
    });

    // 4. Subagents Team Roster
    const subSection = chamber.createDiv({ cls: "cubicle-subagents-section" });
    subSection.createDiv({ cls: "subagents-header", text: "👥 SUBAGENTES NA SALA:" });
    
    const subRoster = subSection.createDiv({ cls: "subagents-roster" });
    dept.subagents.forEach((sa) => {
      const badge = subRoster.createDiv({ cls: "subagent-badge" });
      badge.innerHTML = `<strong>sub: ${sa.name}</strong> <span>${sa.role}</span>`;
    });

    // 5. Intern's Workstation (Appears when the Estagiário is summoned!)
    if (dept.intern && dept.intern.active) {
      const internStation = chamber.createDiv({ cls: "intern-workstation" });
      
      const internDeskSprite = internStation.createDiv({ cls: "intern-desk-sprite" });
      internDeskSprite.innerHTML = SPRITES.intern;

      const internDetails = internStation.createDiv({ cls: "intern-desk-details" });
      internDetails.createDiv({ cls: "intern-desk-title" }).innerHTML = `🎓 <span>${dept.intern.title} Ativo!</span>`;
      internDetails.createDiv({ cls: "intern-desk-desc", text: dept.intern.reason });
    }
  }

  // Conflict Detection Algorithm
  checkSkillConflict(dept, newSkillName, content = "") {
    const nameLower = newSkillName.toLowerCase();
    const contentLower = content.toLowerCase();

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

  processNewSkill(dept, newSkillName, content = "") {
    if (dept.skills.includes(newSkillName)) {
      new Notice(`A skill "${newSkillName}" já está no quadro negro desta sala.`);
      return;
    }

    const check = this.checkSkillConflict(dept, newSkillName, content);

    if (check.hasConflict) {
      RetroAudio.playAlert();
      this.showConflictDialogue(dept, newSkillName, check.conflictingSkill, check.reason, content);
    } else {
      RetroAudio.playFanfare();
      dept.skills.push(newSkillName);
      this.savePluginData();
      this.renderView();
      new Notice(`✨ Skill "${newSkillName}" escrita com giz no quadro negro do ${dept.name}!`);
    }
  }

  // Zelda SNES Dialogue Box Modal
  showConflictDialogue(dept, newSkillName, conflictingSkill, reason, content) {
    const overlay = document.body.createDiv({ cls: "gb-dialogue-overlay" });
    const box = overlay.createDiv({ cls: "gb-dialogue-box" });

    const top = box.createDiv({ cls: "gb-dialogue-top" });
    const portrait = top.createDiv({ cls: "gb-dialogue-portrait" });
    portrait.innerHTML = SPRITES.intern;

    const contentDiv = top.createDiv({ cls: "gb-dialogue-content" });
    contentDiv.createDiv({ cls: "gb-dialogue-speaker", text: "📜 O MESTRE DA GUILDA DIZ:" });
    
    const dialogText = contentDiv.createDiv({ cls: "gb-dialogue-text" });
    dialogText.innerHTML = `
      ⚔️ <b>CONFLITO DETECTADO NA SALA!</b><br><br>
      A nova skill <b>"${newSkillName}"</b> interfere diretamente com a ferramenta <b>"${conflictingSkill}"</b> (${reason}).<br><br>
      Na GabeBrain Corp, nenhuma ferramenta é descartada. Em vez disso, montamos uma <b>Mesa de Trabalho para o Estagiário Revisor</b> (${dept.id}-estagiario-revisor)!<br><br>
      Ele atuará como colega de equipe, testará o que o agente titular fez, auditará os resultados e proporá melhorias ou abordagens alternativas!
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
      text: "🎓 MONTAR MESA DO ESTAGIÁRIO REVISOR"
    });

    summonBtn.addEventListener("click", async () => {
      overlay.remove();
      await this.summonInternAgent(dept, newSkillName, conflictingSkill, reason);
    });
  }

  async summonInternAgent(dept, newSkillName, conflictingSkill, reason) {
    const internName = `${dept.id}-estagiario-revisor`;
    const internTitle = `Estagiário Revisor (${dept.lead})`;

    dept.intern = {
      name: internName,
      title: internTitle,
      active: true,
      reason: `Mesa montada para auditar e mediar entre "${conflictingSkill}" e "${newSkillName}".`,
      reviewedSkills: [conflictingSkill, newSkillName]
    };

    dept.skills.push(newSkillName);

    if (!dept.subagents.some(s => s.name === internName)) {
      dept.subagents.push({
        name: internName,
        role: "Colega Revisor & Mediação"
      });
    }

    const internMdContent = `---
name: ${internName}
description: Subagente Estagiário e Revisor do departamento ${dept.name}. Atua como colega de trabalho que inspeciona a execução de ${conflictingSkill} e ${newSkillName}, audita resultados e propõe melhorias arquiteturais.
model: inherit
---

# ${internTitle} 🎓

Você é o **${internName}**, o colega estagiário/revisor na sala de **${dept.name}**.

### 🎯 Missão de Mediação:
Você foi alocado em sua mesa de trabalho devido à sobreposição de escopo entre:
- \`${conflictingSkill}\` (Skill Titular Prévia)
- \`${newSkillName}\` (Nova Skill Integrada)

### 📋 Suas Atribuições de Colega de Trabalho:
1. **Auditar Execuções:** Sempre que uma das skills for acionada, inspecione as saídas e confira se há incoerências ou limitações.
2. **Propor Alternativas Construtivas:** Se a skill titular falhar ou tiver custos altos de processamento, recomende a execução da nova skill como fallback cirúrgico.
3. **Harmonização de Contexto:** Garantir que o departamento nunca perca consistência funcional, emitindo pareceres de melhoria contínua.

### 🌐 Sala Departamental:
- **Líder Titular:** \`${dept.lead}\`
- **Guilda:** GabeBrain Corp
`;

    try {
      const vaultPath = this.app.vault.adapter.basePath;
      if (vaultPath) {
        const agentDestDir = path.join(vaultPath, ".claude", "agents");
        if (!fs.existsSync(agentDestDir)) {
          fs.mkdirSync(agentDestDir, { recursive: true });
        }
        fs.writeFileSync(path.join(agentDestDir, `${internName}.md`), internMdContent, "utf-8");

        const mastersDir = path.join(vaultPath, "📚 Biblioteca de Agentes");
        if (fs.existsSync(mastersDir)) {
          const masterNote = `# Master ${internName} 🎓\n\nSubagente estagiário revisor de ${dept.name}.\n\n[[00 - Índice da Biblioteca de Agentes|Voltar]]`;
          fs.writeFileSync(path.join(mastersDir, `Master_${internName}.md`), masterNote, "utf-8");
        }
      }
    } catch (err) {
      console.log("Could not write local agent file directly", err);
    }

    RetroAudio.playFanfare();
    await this.savePluginData();
    this.renderView();

    new Notice(`🎓 A mesa de trabalho do Estagiário Revisor "${internName}" foi montada na sala!`);
  }

  openAddSkillModal(dept) {
    const modal = new Modal(this.app);
    modal.titleEl.setText(`🪑 Alocar Skill na Mesa de ${dept.lead}`);

    const content = modal.contentEl;
    content.createEl("p", {
      text: "Digite o nome da skill ou função a ser inscrita no quadro negro da sala:"
    });

    const inputWrap = content.createDiv({ cls: "setting-item" });
    const input = inputWrap.createEl("input", {
      type: "text",
      placeholder: "Ex: geo-raster-analyzer, semantic-scholar-api, etc."
    });
    input.style.width = "100%";
    input.style.padding = "8px";
    input.style.marginBottom = "14px";
    input.style.background = "#1a0f0a";
    input.style.border = "2px solid #854d0e";
    input.style.color = "#fde047";

    const btnWrap = content.createDiv({ style: "display: flex; justify-content: flex-end; gap: 8px;" });

    const cancelBtn = btnWrap.createEl("button", { text: "Cancelar" });
    cancelBtn.addEventListener("click", () => modal.close());

    const submitBtn = btnWrap.createEl("button", {
      text: "🔍 Analisar e Escrever no Quadro",
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
