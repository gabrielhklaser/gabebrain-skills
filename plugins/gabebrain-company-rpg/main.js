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
  // Grandmaster / King of the Guild (Crown, royal indigo robe, gold trim, glowing loop scepter)
  loop: `<svg width="44" height="44" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg" style="image-rendering:pixelated">
    <!-- Crown -->
    <rect x="5" y="1" width="6" height="1" fill="#facc15"/>
    <rect x="5" y="2" width="1" height="1" fill="#facc15"/>
    <rect x="7" y="2" width="2" height="1" fill="#dc2626"/>
    <rect x="10" y="2" width="1" height="1" fill="#facc15"/>
    <!-- Face / Hair / White Beard -->
    <rect x="5" y="3" width="6" height="3" fill="#ffd199"/>
    <rect x="6" y="4" width="1" height="1" fill="#0b0f17"/>
    <rect x="9" y="4" width="1" height="1" fill="#0b0f17"/>
    <rect x="4" y="6" width="8" height="2" fill="#e2e8f0"/>
    <rect x="5" y="8" width="6" height="1" fill="#e2e8f0"/>
    <!-- Royal Mantle / Robe -->
    <rect x="4" y="8" width="8" height="5" fill="#312e81"/>
    <rect x="7" y="8" width="2" height="5" fill="#facc15"/>
    <rect x="3" y="9" width="1" height="4" fill="#991b1b"/>
    <rect x="12" y="9" width="1" height="4" fill="#991b1b"/>
    <!-- Glowing Loop Scepter -->
    <rect x="13" y="5" width="2" height="2" fill="#38bdf8"/>
    <rect x="13" y="7" width="1" height="6" fill="#facc15"/>
    <!-- Boots -->
    <rect x="5" y="13" width="2" height="2" fill="#1e1b4b"/>
    <rect x="9" y="13" width="2" height="2" fill="#1e1b4b"/>
  </svg>`,

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
    id: "loop",
    name: "🏛️ Torre de Governança, Orquestração & QA-Loop",
    lead: "LoopAgent",
    leadRole: "Diretor Executivo de Qualidade, Hive Mind & Handoff",
    desc: "Governança executiva do ecossistema, gates determinísticos, pontuação de rubricas com Jev, críticas de simplicidade (Bana) e roteamento Arena AI x Local.",
    sprite: "loop",
    rugClass: "rug-loop",
    hearts: 5,
    subagents: [
      { name: "loop-gatekeeper", role: "Portões Determinísticos & Gates" },
      { name: "loop-scorer", role: "Rubricas & Pontuação Jev" },
      { name: "hive-orchestrator", role: "Hive Mind, Skip & Bana" },
      { name: "prompt-router", role: "Roteador Híbrido (Arena x Local)" }
    ],
    skills: [
      "qa-loop",
      "jev",
      "prompt-router-coordinator",
      "ecc-harness-optimizer"
    ],
    intern: null
  },
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


// Detalhamento de cada Subagente com lista de skills e explicação de para que servem
const SUBAGENTS_DETAILS = {
  "geo-gis": {
    name: "geo-gis",
    title: "Subagente de Cartografia, Folium & Geoprocessamento",
    deptId: "geo",
    deptName: "Divisão de Geociências & Licenciamento",
    sprite: "geo",
    role: "Cartografia & Folium",
    bio: "Especialista em geoprocessamento digital, estruturação de camadas vetoriais e geração de mapas interativos para licenciamento e perícias ambientais.",
    skills: [
      {
        name: "gis-multicamadas",
        purpose: "Gera mapas interativos Folium/Leaflet com camadas individuais (geologia, solos, poços, drenagem, raio de segurança), controle de visibilidade (LayerControl), alternância de mapa base (Satélite Esri, OSM, CartoDB) e régua de medição métrica."
      },
      {
        name: "paleomap-refiner",
        purpose: "Refina e suaviza fronteiras vetoriais de zonas climáticas em mapas paleoclimáticos exportados em PDF sem deslocar pontos amostrais, mantendo 100% da integridade científica dos dados geológicos."
      }
    ]
  },
  "geo-hidro": {
    name: "geo-hidro",
    title: "Subagente de Hidrologia, Vazões & Outorgas",
    deptId: "geo",
    deptName: "Divisão de Geociências & Licenciamento",
    sprite: "geo",
    role: "Vazões & Outorgas",
    bio: "Responsável pelo cálculo de disponibilidade hídrica, consistência de séries pluviométricas e fluviométricas e enquadramento de outorga superficial e subterrânea.",
    skills: [
      {
        name: "flow-report",
        purpose: "Executa relatório padronizado de qualidade em 5 etapas para séries temporais de vazão fluviométrica, consistência de dados, curvas de permanência e cálculo de vazões de referência (Q95, Q7,10)."
      },
      {
        name: "hydro-context",
        purpose: "Aplica o vocabulário conceitual, fórmulas matemáticas, fatores de conversão e convenções hidrológicas oficiais dos manuais da ANA (Brasil) e USGS."
      }
    ]
  },
  "geo-licencia": {
    name: "geo-licencia",
    title: "Subagente Regulatório & Licenciamento Campo Bom",
    deptId: "geo",
    deptName: "Divisão de Geociências & Licenciamento",
    sprite: "geo",
    role: "Regulatório & Campo Bom",
    bio: "Especialista na conformidade locacional de empreendimentos, análise de impactos ecológicos e legislação ambiental de Campo Bom/RS.",
    skills: [
      {
        name: "licenciamento-campo-bom",
        purpose: "Automatiza a conferência de enquadramento pela Resolução CONSEMA 372/2018 (CODRAM x Porte x Potencial Poluidor), zoneamento do Plano Diretor (Lei 5.329/2022) e resoluções COMDEMA vigentes."
      },
      {
        name: "environmentalist-analyst",
        purpose: "Analisa projetos sob a ótica ecológica sistêmica, avaliando capacidade de suporte, conectividade de habitats, poluição e propostas de medidas mitigadoras e compensatórias."
      }
    ]
  },
  "geo-acervo": {
    name: "geo-acervo",
    title: "Subagente Guardião do Acervo Técnico & Drive",
    deptId: "geo",
    deptName: "Divisão de Geociências & Licenciamento",
    sprite: "geo",
    role: "Busca Acervo Drive",
    bio: "Guardião da Biblioteca Geológica e Técnica no Google Drive, indexador de obras longas e operador de leitura cirúrgica com citação exata de página.",
    skills: [
      {
        name: "biblioteca-pesquisavel",
        purpose: "Realiza busca léxica por termos e leitura cirúrgica por página em PDFs do acervo técnico através do CLI 'biblioteca.py ler <COTA> <PAGS>', com citação exata de página."
      },
      {
        name: "biblioteca-triagem",
        purpose: "Faz a triagem e destilação de PDFs técnicos (até 50k tokens), validando autoria/ano na folha de rosto, nível de confiança (A-E) e gerando nota destilada no Obsidian."
      },
      {
        name: "biblioteca-mapa-documento",
        purpose: "Extrai o esqueleto estrutural de livros, teses e relatórios com mais de 50 mil tokens sem consumir tokens com o PDF inteiro, fazendo mergulhos seletivos apenas em seções densas."
      }
    ]
  },
  "research-lead": {
    name: "research-lead",
    title: "Subagente Coordenador de Pesquisa & Matriz Analítica",
    deptId: "research",
    deptName: "Central de Inteligência & Deep Research",
    sprite: "research",
    role: "Fase 1: Outline & Matriz",
    bio: "Líder da Fase 1 da metodologia Deep Research. Mapeia o universo de entidades e define a matriz multidimensional de campos analíticos antes do disparo das buscas.",
    skills: [
      {
        name: "deep-research",
        purpose: "Conduz e orquestra o ciclo completo de pesquisa profunda em 3 fases estruturadas (arquitetura inspirada no paper RhinoInsight)."
      },
      {
        name: "research",
        purpose: "Formula o outline inicial de entidades ('outline.yaml') e define os campos analíticos necessários ('fields.yaml') com alinhamento prévio antes de disparar buscas."
      }
    ]
  },
  "web-scout": {
    name: "web-scout",
    title: "Subagente de Varredura Web & Coleta Paralela",
    deptId: "research",
    deptName: "Central de Inteligência & Deep Research",
    sprite: "research",
    role: "Fase 2: Varredura Paralela",
    bio: "Explorador da Fase 2 da metodologia Deep Research. Coordena agentes paralelos para minerar dados da web com módulos temáticos para papers, GitHub e fóruns.",
    skills: [
      {
        name: "research-deep",
        purpose: "Dispara subagentes paralelos em container para investigar cada item da matriz de pesquisa de forma independente e simultânea."
      },
      {
        name: "research-add-items",
        purpose: "Expande dinamicamente a lista de entidades a serem pesquisadas no plano sem perder o progresso já coletado."
      },
      {
        name: "research-add-fields",
        purpose: "Insere novos campos e dimensões analíticas na matriz de investigação sem invalidar os registros já obtidos."
      }
    ]
  },
  "report-synth": {
    name: "report-synth",
    title: "Subagente de Síntese, Validação & Notas Limpas",
    deptId: "research",
    deptName: "Central de Inteligência & Deep Research",
    sprite: "research",
    role: "Fase 3: Síntese e Validação",
    bio: "Especialista da Fase 3 do Deep Research. Audita a consistência de cada campo, mascara incertezas e sintetiza relatórios e notas de pesquisa sem ruído.",
    skills: [
      {
        name: "research-report",
        purpose: "Valida 100% de conformidade dos dados coletados em JSON via script 'validate_json.py', mascara dados incertos como '[uncertain]' e gera o relatório final em Markdown estruturado com sumário executivo e links ancorados."
      },
      {
        name: "web-para-nota",
        purpose: "Converte páginas web, notícias e artigos técnicos em notas Markdown limpas no vault do Obsidian via Defuddle CLI, removendo poluição visual e anúncios."
      }
    ]
  },
  "gh-researcher": {
    name: "gh-researcher",
    title: "Subagente de Mineração de Repositórios & GitHub CLI",
    deptId: "research",
    deptName: "Central de Inteligência & Deep Research",
    sprite: "research",
    role: "Mineração GitHub CLI",
    bio: "Especialista em auditoria de repositórios open-source, extração de histórico de commits, triagem de PRs e busca cirúrgica de bugs via GitHub CLI.",
    skills: [
      {
        name: "github-research",
        purpose: "Pesquisa e minera issues, pull requests fechados/abertos, discussões e arquivos de código no ecossistema GitHub utilizando a CLI oficial 'gh'."
      }
    ]
  },
  "coder-tdd": {
    name: "coder-tdd",
    title: "Subagente de Engenharia Disciplinada & TDD Rigoroso",
    deptId: "dev",
    deptName: "Laboratório de Engenharia & AppSec",
    sprite: "dev",
    role: "TDD & Testes Automatizados",
    bio: "Engenheiro de software rigoroso. Aplica a metodologia Superpowers: testes primeiro (Red), código cirúrgico (Green) e refatoração com suíte 100% verde.",
    skills: [
      {
        name: "superpowers-coding-agent",
        purpose: "Metodologia disciplinada de engenharia: brainstorming prévio, planos atômicos de implementação e ciclo Red/Green/Refactor estrito antes de qualquer alteração de código."
      },
      {
        name: "run-tests",
        purpose: "Executa baterias de testes unitários e de integração com pytest e relata sumários detalhados de aprovação e falhas para validação contínua."
      }
    ]
  },
  "context7-verifier": {
    name: "context7-verifier",
    title: "Subagente de Blindagem Oficial & Anti-Alucinação",
    deptId: "dev",
    deptName: "Laboratório de Engenharia & AppSec",
    sprite: "dev",
    role: "Blindagem Anti-Alucinação",
    bio: "Guardião da precisão técnica. Bloqueia alucinações de métodos obsoletos consultando a documentação oficial atualizada e assinaturas de APIs em tempo real.",
    skills: [
      {
        name: "context7-mcp",
        purpose: "Consulta a documentação oficial atualizada, assinaturas exatas e snippets reais via servidor MCP antes de escrever código com bibliotecas modernas."
      },
      {
        name: "context7-cli",
        purpose: "Interface de linha de comando ('ctx7') para buscar docs, bibliotecas externas e gerenciar skills de programação no ecossistema local."
      },
      {
        name: "find-docs",
        purpose: "Ferramenta de busca de documentação atualizada para APIs, frameworks e bibliotecas, evitando alucinações de métodos obsoletos em dados de treino estáticos."
      }
    ]
  },
  "appsec-auditor": {
    name: "appsec-auditor",
    title: "Subagente de Auditoria AppSec, YARA & Regras Karpathy",
    deptId: "dev",
    deptName: "Laboratório de Engenharia & AppSec",
    sprite: "dev",
    role: "Auditoria AppSec & YARA",
    bio: "Auditor de segurança de código e skills. Bloqueia injeções de prompt e backdoors com SkillSpector, e combate a sobre-engenharia com Karpathy Guidelines.",
    skills: [
      {
        name: "skillspector-auditor",
        purpose: "Varredura estática de skills e scripts contra 71 categorias de vulnerabilidades (prompt injection, command execution desprotegida, exfiltração de dados e assinaturas YARA de malware)."
      },
      {
        name: "karpathy-guidelines",
        purpose: "Diretrizes comportamentais para evitar complexidade desnecessária, exigir mudanças cirúrgicas e definir critérios de validação verificáveis antes da conclusão."
      }
    ]
  },
  "vcs-sync": {
    name: "vcs-sync",
    title: "Subagente de Paridade Local/GitHub & Arena AI Controller",
    deptId: "dev",
    deptName: "Laboratório de Engenharia & AppSec",
    sprite: "dev",
    role: "Paridade GitHub & Arena AI",
    bio: "Controlador do fluxo híbrido Local <-> Nuvem. Garante snapshots offline seguros, sincronização com GitHub e despacho de tarefas pesadas para a Arena AI.",
    skills: [
      {
        name: "vcs-version-agent",
        purpose: "Garante paridade estrita entre o ambiente local e o GitHub, reconciliando branches automáticas 'origin/arena/*' e gerenciando snapshots offline seguros."
      },
      {
        name: "arena-ai-controller",
        purpose: "Despacha comandos e prompts para execução no container na nuvem da plataforma Arena AI, economizando tokens locais do Antigravity."
      },
      {
        name: "ecc-harness-optimizer",
        purpose: "Sistema operacional Everything Claude Code (ECC) gerenciando o ciclo de 6 fases (Plan-Test-Implement-Review-Verify-Remember) e memória durável em SQLite."
      }
    ]
  },
  "ppgca-corpus": {
    name: "ppgca-corpus",
    title: "Subagente do Acervo PPGCA & Ingestão Docling",
    deptId: "science",
    deptName: "Academia Científica & Mestrado PPGCA",
    sprite: "science",
    role: "Docling & Acervo PPGCA",
    bio: "Especialista no acervo estruturado do Mestrado em Computação Aplicada (PPGCA/Unisinos), fichas catalográficas e conversão universal de relatórios de escritório.",
    skills: [
      {
        name: "computacao-aplicada",
        purpose: "Consulta e pesquisa obras estruturadas via Docling do mestrado e 10 Master Skills consolidadas (IHC, Ontologias, ML Espacial, Geoestatística, Arquitetura de Software, etc.)."
      },
      {
        name: "anydoc",
        purpose: "Conversor ultrarrápido de documentos corporativos e técnicos (.docx, .xlsx, .pptx, .odt, .rtf, .pdf) para Markdown GitHub-Flavored."
      }
    ]
  },
  "paper-writer": {
    name: "paper-writer",
    title: "Subagente de Redação Científica & Voz Ativa (Anti-Slop)",
    deptId: "science",
    deptName: "Academia Científica & Mestrado PPGCA",
    sprite: "science",
    role: "Redação SBC/IEEE k-dense",
    bio: "Redator acadêmico focado em alta densidade técnica, pirâmide invertida na introdução, rastreabilidade de evidências e eliminação de clichês sintéticos de IA.",
    skills: [
      {
        name: "scientific-writing",
        purpose: "Estrutura formalmente artigos e dissertações seções por seção (Abstract, Pirâmide Invertida na Introdução, Taxonomia de Trabalhos Relacionados e Metodologia Rigorosa)."
      },
      {
        name: "scientific-writing-kdense",
        purpose: "Redação com alta densidade de conhecimento (k-dense), rastreabilidade de evidências e conformidade com diretrizes de publicação internacionais (IEEE, ACM, SBC)."
      },
      {
        name: "no-ai-slop",
        purpose: "Detector e removedor de 20+ padrões de clichês sintéticos de IA ('delve', 'testament', 'tapestry', 'in summary', etc.), preservando autoridade autêntica."
      }
    ]
  },
  "peer-reviewer": {
    name: "peer-reviewer",
    title: "Subagente Parecerista Sênior & Triagem Jev",
    deptId: "science",
    deptName: "Academia Científica & Mestrado PPGCA",
    sprite: "science",
    role: "Revisão Cega & Triagem Jev",
    bio: "Parecerista rigoroso de conferências científicas e auditor epistêmico. Executa análise de ameaças à validade e triagem semântica ultrarrápida via Jev.",
    skills: [
      {
        name: "revisor-cientifico-peer-review",
        purpose: "Simula um revisor acadêmico sênior (padrão IEEE Transactions, ACM, SBC e Elsevier), auditando novidade, metodologia, reprodutibilidade e apontando major flaws."
      },
      {
        name: "scientific-thinking-scholar-evaluation",
        purpose: "Avaliação epistêmica rigorosa de experimentos, ameaças à validade, formulação de contra-hipóteses e prevenção de viés de confirmação."
      },
      {
        name: "jev",
        purpose: "Modelo classificador ultrarrápido tipo System One (TypeSafe) que avalia e pontua trechos textuais, probabilidades sim/não e triagens em milissegundos sem alocar tokens de geração."
      }
    ]
  },
  "canva-designer": {
    name: "canva-designer",
    title: "Subagente de Automação Canva Pro & Mídia Visual",
    deptId: "design",
    deptName: "Estúdio de Criação, Design & Mídia",
    sprite: "design",
    role: "Playwright & Canva Pro",
    bio: "Operador de automação visual para criação de banners, capas científicas e infográficos de alta fidelidade usando Canva Pro e processamento local.",
    skills: [
      {
        name: "canva-image-agent",
        purpose: "Controla a interface do Canva Pro via navegador persistente autenticado (Playwright) e executa processamento local de imagens (Pillow) para redimensionamento e corte de alta resolução."
      }
    ]
  },
  "web-asset-maker": {
    name: "web-asset-maker",
    title: "Subagente de Ativos Web, Favicons & PWA",
    deptId: "design",
    deptName: "Estúdio de Criação, Design & Mídia",
    sprite: "design",
    role: "Favicons & PWA Icons",
    bio: "Especialista em preparação de ativos digitais para publicação web, empacotando favicons em todas as dimensões padrão e tags Open Graph para redes sociais.",
    skills: [
      {
        name: "web-asset-generator",
        purpose: "Gera suíte completa de favicons (16x16 até 512x512), ícones para PWA (Progressive Web Apps), imagens Open Graph para redes sociais (Facebook, Twitter/X, LinkedIn) e as respectivas tags HTML <meta>."
      }
    ]
  }
};

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

    // Carpet / Rug where the Lead Agent Sprite stands (Clickable to open Master Note)
    const rug = floorArea.createDiv({ cls: `cubicle-rug ${dept.rugClass}` });
    rug.style.cursor = "pointer";
    rug.title = `Clique para abrir a Master Note de ${dept.lead}`;
    rug.addEventListener("click", () => {
      this.openMasterNote(dept.id);
    });

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
      tag.title = `Clique para abrir o arquivo .md da skill "${skill}"`;
      tag.addEventListener("click", (e) => {
        e.stopPropagation();
        this.openSkillFile(skill);
      });
    });

    // 4. Subagents Team Roster (Clickable to open subagent profile)
    const subSection = chamber.createDiv({ cls: "cubicle-subagents-section" });
    subSection.createDiv({ cls: "subagents-header", text: "👥 SUBAGENTES NA SALA:" });
    
    const subRoster = subSection.createDiv({ cls: "subagents-roster" });
    dept.subagents.forEach((sa) => {
      const badge = subRoster.createDiv({ cls: "subagent-badge" });
      badge.innerHTML = `<strong>sub: ${sa.name}</strong> <span>${sa.role}</span>`;
      badge.title = `Clique para abrir o perfil e ver as skills de "${sa.name}"`;
      badge.addEventListener("click", (e) => {
        e.stopPropagation();
        this.openSubagentProfileModal(dept, sa.name);
      });
    });

    // 5. Intern's Workstation (Appears when the Estagiário is summoned!)
    if (dept.intern && dept.intern.active) {
      const internStation = chamber.createDiv({ cls: "intern-workstation" });
      internStation.style.cursor = "pointer";
      internStation.title = `Clique para abrir o parecer e perfil do ${dept.intern.name}`;
      internStation.addEventListener("click", () => {
        this.openSubagentProfileModal(dept, dept.intern.name);
      });
      
      const internDeskSprite = internStation.createDiv({ cls: "intern-desk-sprite" });
      internDeskSprite.innerHTML = SPRITES.intern;

      const internDetails = internStation.createDiv({ cls: "intern-desk-details" });
      internDetails.createDiv({ cls: "intern-desk-title" }).innerHTML = `🎓 <span>${dept.intern.title} Ativo!</span>`;
      internDetails.createDiv({ cls: "intern-desk-desc", text: dept.intern.reason });
    }
  }

  // Opens the Markdown file corresponding to a skill
  async openSkillFile(skillName) {
    const { vault, workspace } = this.app;
    
    const candidates = [
      `20-Skills/Skill_${skillName}.md`,
      `20-Skills/${skillName}.md`,
      `.claude/skills/${skillName}/SKILL.md`,
      `.agents/skills/${skillName}/SKILL.md`
    ];

    let targetFile = null;
    for (const cand of candidates) {
      const file = vault.getAbstractFileByPath(cand);
      if (file instanceof TFile) {
        targetFile = file;
        break;
      }
    }

    if (!targetFile) {
      const allFiles = vault.getMarkdownFiles();
      targetFile = allFiles.find(f => 
        f.basename.toLowerCase() === `skill_${skillName.toLowerCase()}` ||
        f.basename.toLowerCase() === skillName.toLowerCase() ||
        (f.path.includes(skillName) && (f.basename === "SKILL" || f.basename.endsWith(".md")))
      );
    }

    if (targetFile) {
      RetroAudio.playFanfare();
      const leaf = workspace.getLeaf("tab");
      await leaf.openFile(targetFile);
      new Notice(`📖 Abrindo nota da skill "${skillName}"...`);
    } else {
      // Check filesystem in ~/.gemini/config/skills/<skillName>/SKILL.md
      const homeDir = process.env.USERPROFILE || process.env.HOME || "C:\\Users\\Gabriel";
      const localSkillPath = path.join(homeDir, ".gemini", "config", "skills", skillName, "SKILL.md");

      if (fs.existsSync(localSkillPath)) {
        try {
          const content = fs.readFileSync(localSkillPath, "utf-8");
          const newVaultPath = `20-Skills/Skill_${skillName}.md`;
          const created = await vault.create(newVaultPath, content);
          RetroAudio.playFanfare();
          const leaf = workspace.getLeaf("tab");
          await leaf.openFile(created);
          new Notice(`📖 Importada e aberta nota da skill "${skillName}"!`);
          return;
        } catch (e) {
          console.log("Could not import skill file", e);
        }
      }

      new Notice(`Arquivo da skill "${skillName}" não foi localizado no cofre.`);
    }
  }


  // Opens the 16-Bit Zelda SNES Profile Modal of a Subagent with full skills & purposes explanation
  openSubagentProfileModal(dept, agentName) {
    RetroAudio.playFanfare();

    let profile = SUBAGENTS_DETAILS[agentName];

    if (!profile) {
      if (agentName.endsWith("-estagiario-revisor")) {
        const reviewed = (dept.intern && dept.intern.reviewedSkills) ? dept.intern.reviewedSkills : [];
        profile = {
          name: agentName,
          title: `Estagiário Revisor (${dept.lead})`,
          deptId: dept.id,
          deptName: dept.name,
          sprite: "intern",
          role: "Colega Revisor & Mediação Arquitetural",
          bio: `Subagente estagiário alocado na sala para resolver sobreposição funcional de ferramentas, auditar a execução das skills titulares, testar alternativas e propor melhorias contínuas para a equipe.`,
          skills: reviewed.map(s => ({
            name: s,
            purpose: `Ferramenta sob auditoria e supervisão comparativa. O estagiário avalia os resultados de "${s}", compara com alternativas e sugere melhorias contínuas para a tarefa.`
          }))
        };
        if (profile.skills.length === 0) {
          profile.skills = dept.skills.slice(0, 3).map(s => ({
            name: s,
            purpose: `Skill sob acompanhamento e auditoria de qualidade na sala de ${dept.name}.`
          }));
        }
      } else {
        profile = {
          name: agentName,
          title: `Subagente Especializado`,
          deptId: dept.id,
          deptName: dept.name,
          sprite: dept.sprite || "geo",
          role: "Operador Especializado",
          bio: `Subagente atuando na sala de ${dept.name} para execução de rotinas dedicadas do ecossistema GabeBrain.`,
          skills: dept.skills.slice(0, 2).map(s => ({
            name: s,
            purpose: `Ferramenta técnica mobilizada para execução de tarefas na divisão.`
          }))
        };
      }
    }

    // Create Modal Overlay
    const overlay = document.body.createDiv({ cls: "gb-profile-overlay" });
    const modalBox = overlay.createDiv({ cls: "gb-profile-box" });

    // Close on overlay backdrop click
    overlay.addEventListener("click", (e) => {
      if (e.target === overlay) {
        overlay.remove();
      }
    });

    // Close on Escape key
    const onKeydown = (e) => {
      if (e.key === "Escape") {
        overlay.remove();
        document.removeEventListener("keydown", onKeydown);
      }
    };
    document.addEventListener("keydown", onKeydown);

    // 1. Header (Banner with Sprite, Name, Dept, Role and Close Button)
    const header = modalBox.createDiv({ cls: "gb-profile-header" });
    
    const leftWrap = header.createDiv({ cls: "gb-profile-header-left" });
    const avatar = leftWrap.createDiv({ cls: `gb-profile-avatar rug-${profile.deptId || dept.id}` });
    avatar.innerHTML = SPRITES[profile.sprite] || SPRITES[dept.sprite] || SPRITES.geo;

    const meta = leftWrap.createDiv({ cls: "gb-profile-meta" });
    meta.createDiv({ cls: "gb-profile-dept-pill", text: `🚪 ${profile.deptName}` });
    
    const nameRow = meta.createDiv({ cls: "gb-profile-name-row" });
    nameRow.createEl("h2", { text: profile.name });
    nameRow.createSpan({ cls: "gb-profile-role-tag", text: profile.role });

    meta.createDiv({ cls: "gb-profile-title-text", text: profile.title });

    const closeBtn = header.createEl("button", {
      cls: "gb-profile-close-btn",
      text: "✕"
    });
    closeBtn.title = "Fechar Perfil (ESC)";
    closeBtn.addEventListener("click", () => {
      overlay.remove();
      document.removeEventListener("keydown", onKeydown);
    });

    // 2. Character Bio & Mission Box
    const bioBox = modalBox.createDiv({ cls: "gb-profile-bio-box" });
    bioBox.createDiv({ cls: "gb-profile-box-label", text: "📜 PERFIL & MISSÃO DO SUBAGENTE:" });
    bioBox.createDiv({ cls: "gb-profile-bio-text", text: profile.bio });

    // 3. Skills & Explanations Section
    const skillsSection = modalBox.createDiv({ cls: "gb-profile-skills-section" });
    
    const skillsHeader = skillsSection.createDiv({ cls: "gb-profile-skills-header" });
    skillsHeader.createDiv({
      cls: "gb-profile-box-label",
      text: `⚔️ ARSENAL DE SKILLS UTILIZADAS (${profile.skills.length}) & PARA QUE SERVEM:`
    });

    const skillsList = skillsSection.createDiv({ cls: "gb-profile-skills-list" });

    profile.skills.forEach(skill => {
      const card = skillsList.createDiv({ cls: "gb-profile-skill-card" });
      
      const cardTop = card.createDiv({ cls: "gb-profile-skill-top" });
      
      const skillTag = cardTop.createDiv({ cls: "gb-profile-skill-tag" });
      skillTag.innerHTML = `<span>✏️</span> <strong>${skill.name}</strong>`;
      skillTag.title = `Clique para abrir a nota da skill "${skill.name}"`;
      skillTag.addEventListener("click", () => {
        overlay.remove();
        document.removeEventListener("keydown", onKeydown);
        this.openSkillFile(skill.name);
      });

      const openSkillBtn = cardTop.createEl("button", {
        cls: "gb-btn-retro gb-btn-skill-open",
        text: "📖 ABRIR NOTA .MD"
      });
      openSkillBtn.title = `Abrir Skill_${skill.name}.md no Obsidian`;
      openSkillBtn.addEventListener("click", () => {
        overlay.remove();
        document.removeEventListener("keydown", onKeydown);
        this.openSkillFile(skill.name);
      });

      const purposeBox = card.createDiv({ cls: "gb-profile-skill-purpose" });
      purposeBox.createDiv({ cls: "purpose-label", text: "📌 Para que serve:" });
      purposeBox.createDiv({ cls: "purpose-text", text: skill.purpose });
    });

    // 4. Modal Actions (Bottom Buttons)
    const actions = modalBox.createDiv({ cls: "gb-profile-actions" });

    const openAgentBtn = actions.createEl("button", {
      cls: "gb-btn-retro gb-btn-gold",
      text: `📖 ABRIR NOTA .MD COMPLETA (${profile.name})`
    });
    openAgentBtn.addEventListener("click", () => {
      overlay.remove();
      document.removeEventListener("keydown", onKeydown);
      this.openAgentFile(profile.name);
    });

    const dismissBtn = actions.createEl("button", {
      cls: "gb-btn-retro",
      text: "⚔️ FECHAR PERFIL"
    });
    dismissBtn.addEventListener("click", () => {
      overlay.remove();
      document.removeEventListener("keydown", onKeydown);
    });
  }

  // Opens the Markdown file of a subagent
  async openAgentFile(agentName) {
    const { vault, workspace } = this.app;
    const candidates = [
      `📚 Biblioteca de Agentes/Subagente_${agentName}.md`,
      `📚 Biblioteca de Agentes/Master_${agentName}.md`,
      `.claude/agents/${agentName}.md`,
      `agents/${agentName}.md`
    ];

    for (const cand of candidates) {
      const file = vault.getAbstractFileByPath(cand);
      if (file instanceof TFile) {
        const leaf = workspace.getLeaf("tab");
        await leaf.openFile(file);
        new Notice(`👤 Abrindo perfil do subagente "${agentName}"...`);
        return;
      }
    }

    // Check disk in .claude/agents or user home
    const vaultPath = vault.adapter.basePath;
    if (vaultPath) {
      const diskCandidates = [
        path.join(vaultPath, ".claude", "agents", `${agentName}.md`),
        path.join(process.env.USERPROFILE || "C:\\Users\\Gabriel", ".claude", "agents", `${agentName}.md`)
      ];

      for (const diskPath of diskCandidates) {
        if (fs.existsSync(diskPath)) {
          try {
            const content = fs.readFileSync(diskPath, "utf-8");
            const vaultSubagentPath = `📚 Biblioteca de Agentes/Subagente_${agentName}.md`;
            let existing = vault.getAbstractFileByPath(vaultSubagentPath);
            if (existing instanceof TFile) {
              const leaf = workspace.getLeaf("tab");
              await leaf.openFile(existing);
              new Notice(`👤 Abrindo perfil do subagente "${agentName}"...`);
              return;
            }
            const created = await vault.create(vaultSubagentPath, content);
            const leaf = workspace.getLeaf("tab");
            await leaf.openFile(created);
            new Notice(`👤 Perfil do subagente "${agentName}" criado na Biblioteca e aberto!`);
            return;
          } catch (e) {
            console.error("Error creating vault subagent note:", e);
          }
        }
      }
    }

    new Notice(`Perfil do subagente "${agentName}" não encontrado.`);
  }


  // Opens the Master Note of a department
  async openMasterNote(deptId) {
    const { vault, workspace } = this.app;
    const MASTER_MAP = {
      loop: "📚 Biblioteca de Agentes/Master_LoopAgent_Governanca_e_QALoop.md",
      geo: "📚 Biblioteca de Agentes/Master_GeoAgent_Geociencias_e_Licenciamento.md",
      research: "📚 Biblioteca de Agentes/Master_DeepResearchAgent_Investigacao_Web.md",
      dev: "📚 Biblioteca de Agentes/Master_DevAgent_Engenharia_AppSec_e_Context7.md",
      science: "📚 Biblioteca de Agentes/Master_ScienceAgent_PPGCA_e_Producao_Cientifica.md",
      design: "📚 Biblioteca de Agentes/Master_DesignAgent_Identidade_e_Assets.md"
    };

    const target = MASTER_MAP[deptId];
    if (target) {
      const file = vault.getAbstractFileByPath(target);
      if (file instanceof TFile) {
        const leaf = workspace.getLeaf("tab");
        await leaf.openFile(file);
        new Notice(`👑 Abrindo Master Note do Departamento...`);
      }
    }
  }

  // Conflict Detection Algorithm
  checkSkillConflict(dept, newSkillName, content = "") {
    const nameLower = newSkillName.toLowerCase();
    const contentLower = content.toLowerCase();

    const CONFLICT_RULES = {
      loop: [
        {
          terms: ["qa", "loop", "gate", "qualidade", "rubrica", "inspecao"],
          conflictsWith: "qa-loop",
          reason: "ambas implementam loops ou medições de qualidade para entregas"
        },
        {
          terms: ["jev", "classifica", "score", "pontuacao", "typesafe"],
          conflictsWith: "jev",
          reason: "ambas realizam classificação e pontuação semântica ultrarrápida"
        },
        {
          terms: ["router", "orquestra", "despacho", "hive", "skip"],
          conflictsWith: "prompt-router-coordinator",
          reason: "ambas coordenam handoff e roteamento de contexto entre ambientes"
        }
      ],
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
