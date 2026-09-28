---
name: canva-image-agent
description: >-
  Agente de manipulação e criação de imagens com o Canva Pro e processamento local
  de mídia no ecossistema GabeBrain. Oferece controle automatizado da plataforma Canva Pro
  via navegador persistente (Playwright) com sessão autenticada, criação de designs,
  redimensionamento, otimização, corte e transformação local via Pillow.
allowed-tools:
  - bash
  - read
  - write
  - fetch
  - env
---

# Canva Image Agent (GabeBrain) — v1.0

Agente especialista em **design gráfico, criação e manipulação visual** do ecossistema GabeBrain, integrando o **Canva Pro** automatizado via Playwright e o motor de manipulação de mídia em alta fidelidade.

---

## 🏛️ Diretrizes de Operação Híbrida

1. **Credenciais e Sessão Segura**:
   - Configure `CANVA_EMAIL` e `CANVA_PASSWORD` no ambiente ou copie `.env.example` para `.env` nesta pasta. O `.env` é local e ignorado pelo Git; nunca versione credenciais reais.
   - O perfil persistente do navegador fica, por padrão, no diretório de estado do usuário fora do repositório. `CANVA_USER_DATA_DIR` pode apontar para outro diretório privado. Não compartilhe nem versione esse perfil: ele contém cookies de sessão reutilizáveis.
   - Rotacione imediatamente qualquer senha que já tenha aparecido no histórico público do Git; removê-la do código atual não invalida cópias antigas.

2. **Criação e Design no Canva Pro**:
   - Automação de login e controle de templates para mídias sociais, pranchas de apresentação, capas de relatórios técnicos e diagramas.
   - Abertura do painel e gestão de designs.

3. **Processamento Local de Imagens**:
   - Inspeção de metadados, dimensões, canais de cor e aspect ratio.
   - Redimensionamento inteligente com filtro Lanczos.
   - Otimização e compressão para web / relatórios técnicos.

---

## 🛠️ Comandos da CLI (`canva_agent.py`)

Execute a partir da raiz do repositório; o script está em `skills/canva-image-agent/scripts/canva_agent.py`.

### 1. Verificar Estado da Sessão no Canva Pro
```bash
python skills/canva-image-agent/scripts/canva_agent.py status
```

### 2. Autenticar no Canva Pro
```bash
python skills/canva-image-agent/scripts/canva_agent.py login
```

### 3. Inspecionar Imagem Local
```bash
python skills/canva-image-agent/scripts/canva_agent.py inspect --image "caminho/para/imagem.png"
```

### 4. Redimensionar Imagem Local
```bash
python skills/canva-image-agent/scripts/canva_agent.py resize --image "origem.png" --output "destino.png" --width 1200
```

### 5. Otimizar / Comprimir Imagem
```bash
python skills/canva-image-agent/scripts/canva_agent.py optimize --image "origem.png" --output "otimizada.jpg" --quality 85
```
