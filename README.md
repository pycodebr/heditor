<div align="center">

# 🎬 heditor

**Skill de edição criativa de vídeos para agentes de IA: Reels verticais e vídeos longos.**
Transforma uma gravação de alguém falando (aula, live, podcast, talking head) em um Reel/Short/TikTok 1080×1920 com motion graphics, legendas sincronizadas, efeitos sonoros e trilha emocional, ou em um **vídeo longo** (aula inteira, live, vídeo para o YouTube) em 16:9, 1:1, 4:5 ou 9:16, em estilos nomeados, em **modo criativo** ou em **modo criativo com referência** ("no estilo GTA 6").

[![License: MIT](https://img.shields.io/badge/license-MIT-yellow.svg)](LICENSE)
[![Agent Skills](https://img.shields.io/badge/Agent%20Skills-SKILL.md-blue)](skills/heditor/SKILL.md)
[![Claude Code](https://img.shields.io/badge/Claude%20Code-✓-black)](#instalação)
[![Codex](https://img.shields.io/badge/Codex-✓-black)](#instalação)
[![OpenCode](https://img.shields.io/badge/OpenCode-✓-black)](#instalação)
[![Hermes](https://img.shields.io/badge/Hermes-✓-black)](#instalação)
[![Cursor](https://img.shields.io/badge/Cursor-✓-black)](#instalação)

Feito pela [PycodeBR](https://github.com/pycodebr) · Felipe Azambuja · [English below](#english)

</div>

---

## O que é

O **heditor** é um pacote de skill no padrão aberto `SKILL.md` (Agent Skills). Você instala no seu agente (Claude Code, Codex, OpenCode, Cursor, Hermes e outros) e passa a pedir edições como:

> "Edite este vídeo no estilo **podcast**."
> "Use o **modo criativo** neste corte e me surpreenda."
> "Modo criativo com referência de **GTA 6** neste trecho de 12:30 a 13:40."

O agente faz o trabalho inteiro, sempre localmente:

1. analisa a gravação e encontra o enquadramento de quem fala;
2. transcreve com tempo por palavra e escolhe um raciocínio completo de 30 a 70 s, sem inventar fala;
3. corta fala e câmera com precisão de quadro, encurta pausas e trata a voz;
4. desenha um mundo visual para aquele vídeo (DESIGN.md), com o roteiro de cenas e de som;
5. monta a composição em HTML + GSAP e renderiza com [HyperFrames](https://github.com/heygen-com/hyperframes);
6. mixa com a voz sempre na frente (trilha e efeitos em segundo plano, −14 LUFS);
7. passa por verificações: lint, prévias revisadas por visão, testes, margem superior medida em pixels, loudness, true peak, transcrição do áudio final e folha de contato com 40 quadros.

O padrão de qualidade é alto: **cada vídeo ganha uma edição pensada para ele.** Um estilo é uma linguagem visual testada, nunca um molde a repetir.

## Estilos incluídos

| Estilo | Identidade |
|---|---|
| `cinema` | Uma metáfora visual por trecho da fala, troca de "mundo" nas viradas do argumento, câmera em cartão vivo, legendas cinéticas |
| `ruptura` | Abre com a frase mais forte, a própria câmera vira a metáfora e o fechamento é tipográfico |
| `impacto` | Layout organizado com picos coordenados de tipografia, som e zoom nas frases centrais |
| `game` | A tela vira um RPG retrô: HUD, legenda em caixa de diálogo, skill desbloqueada, inventário, tela de CONTINUE? |
| `thriller` | Fita de câmera de segurança: REC, batimento cardíaco, distorção líquida, apagão e reboot do sistema |
| `trailer` | Trailer de cinema e de lançamento: cortes secos entre o falante (cor fria de trailer, letterbox) e telas pretas em pausas dramáticas inseridas na fala, silêncio antes de cada impacto, palavras projetadas na parede atrás do falante, títulos letra a letra revelados pela luz, um objeto real do cenário revelando a data, trilha em camadas (suspense → crescendo → virada em silêncio → clímax) e cartaz final. Durações medidas em trailers reais |
| `ide` | Gravação de tela de editor de código: webcam em bolha, legenda digitada como comentário e CTA no terminal |
| `aeroporto` | Torre de controle: radar, painel de partidas com letras que viram e legenda como transmissão de rádio |
| `chat` | App de mensagens claro: as frases chegam como mensagens, o bot responde e a câmera vira videochamada |
| `documentario` | Minidocumentário: faixas de cinema, grão de filme, capítulos em serifa e créditos finais |
| `documentario-narrado` | Documentário narrado de grande produção (apelido atlas): a voz do falante narra a história sobre um globo noturno vivo, com luzes e rotas que acendem na palavra, pinturas de época geradas em parallax 2.5D, cartelas datadas com silêncio duro → impacto → revelação, narrador em placa de depoimento com película, medalhão sobre o mapa ou voz em off, e laço final com "próximo capítulo" |
| `podcast` | Talk show: cenário saturado, letreiro NO AR, onda sonora que reage à voz e legenda karaokê gigante |
| `missao` | Homenagem a jogo de mundo aberto: pôr do sol neon, vídeo vertical num app do "jogo", apresentação do personagem em imagem congelada, cartão de missão, rota no GPS, tela de atributos, MISSÃO CUMPRIDA e CTA no celular. Nasceu do pedido "modo criativo no estilo GTA 6" |
| `gravidade` | A fala tem peso: cada conceito é um bloco com a palavra impressa que cai e aterrissa na própria palavra (física real calculada antes do render); os problemas viram um monte, a virada cai como um bloco pesado que espalha tudo e a resposta sobe como uma torre reta |
| `tribunal` | Sketch de tribunal: o especialista depõe por videoconferência, a legenda é o termo datilografado, provas com etiquetas e carimbos, sentença e o júri é você |

Formatos de anúncio (tráfego pago, CTA "Saiba mais"):

| Estilo | Identidade |
|---|---|
| `keynote` | Palco de lançamento: apresentador recortado diante de um telão de LED, um slide ou objeto de palco por frase, prazo em close e slide final com o botão |
| `stories` | Bastidores em sequência de stories: barras de progresso, toque e troca em cubo, stickers feitos à mão e sticker de link |
| `predio-24h` | Empresa em maquete isométrica com ciclo de dia e noite: andares acendem por área, sala de servidores, volta de 24 h e torre da oferta |
| `bilheteria` | Bilheteria retrô: bilhetes numerados, guichê em arco, régua de bilhetes que ganha extras dourados, bilhete dourado e catraca que libera a entrada |
| `porta-de-aco` | Fachada de loja à noite: porta de aço que desce a cada virada, neon, vitrine com o que você leva e porta fechada como CTA |
| `lapidacao` | Comercial de joalheria: a ideia bruta vira uma pedra bruta, o refino é a lapidação (laser, facetas, flash) e o resultado é a joia com as partes nomeadas; uma lupa revisa o trabalho da máquina, uma vitrine tranca os passos não contados, o estojo da oferta fecha com estalo, a data vem numa etiqueta lacrada e o CTA abre um cordão de veludo; trilha mais presente. Build de referência: `heditor new <work> <vídeo> --style lapidacao` + `beats.json` |
| `manual-de-montagem` | Manual de montagem em planta técnica: peças numeradas que encaixam, as mesmas peças em todo projeto e o kit montado na virada |
| `carrinho` | Carrinho esquecido num app de loja: notificação, itens caindo no carrinho, bônus como presentes e checkout |
| `entrega` | Rastreio de pedido: a linha do tempo pula para "entregue agora", a caixa abre e os itens voam para o checklist |
| `auditorio` | Quiz de programa de auditório: cada dúvida é uma rodada, a resposta certa acende, placar e portas de veludo no CTA |
| `album` | Álbum de figurinhas: cada item citado vira figurinha colada na palavra, bandeja da coleção e "falta uma" no CTA |

Formatos de autoridade (tom sério, o falante como especialista):

| Estilo | Identidade |
|---|---|
| `cassino-de-precisao` | Cassino noir que vira bancada de precisão na virada; o especialista é o crupiê e a regra é gravada numa placa |
| `mesa-de-risco` | Terminal de mercado em dia de crash: o recurso é um ativo, replay da ordem, selo de falsa segurança, disjuntor e estratégia em verde |
| `turno-da-madrugada` | Sala de controle no turno da noite: monitor principal, painel anunciador, linha de processo, time-lapse até o amanhecer e passagem de turno |
| `arquivo-cofre` | Mesa de leitura de um arquivo à noite: o especialista como registro em passe-partout, gaveta de aço, relógio protocolador e rolo de microfilme que rebobina até o dia bom |
| `aduana-de-dados` | Posto de fronteira noturno entre o seu computador e a internet: declaração de saída, raio-X, cancela, regulamento grifado e carimbo LEIA OS TERMOS |
| `laudo-de-sinistro` | Laudo de perícia de um sinistro: o especialista na fotografia técnica, flash pericial, cláusula de cobertura preenchida na fala e caneta que troca PERDA TOTAL por RECUPERÁVEL |

Formatos didáticos (a tela ensina o que o falante diz, desenhada ao vivo na palavra):

| Estilo | Identidade |
|---|---|
| `circuito` | A explicação é uma placa de circuito: o falante vira o chip principal, cada conceito é um componente desenhado na palavra, cada relação é uma trilha de cobre, os dados viajam como pulsos de luz, ícones se transformam (nuvem → chip), LEDs e etiquetas dão o veredito e o CTA é um botão físico |
| `planta-de-acesso` | Quem pode usar o quê, como planta-baixa desenhada ao vivo atrás do falante recortado: cada módulo ou setor é uma sala com porta, crachás por função abrem ou trancam as portas na palavra, o dado proibido fica mascarado atrás de um cadeado, a proposta vira outra folha com traço tracejado de "a construir", a empresa inteira acende no fecho e o CTA é um leitor de crachá |
| `lousa-de-aula` | Aula interativa numa lousa de giz: cada traço nasce na palavra que o dispara, pauta com "?" que vira ✓, setas com o verbo da fala, apagador, quadro de RESUMO com a cadeia completa e "para casa" no CTA |

Formato nativo (edição simples e limpa):

| Estilo | Identidade |
|---|---|
| `nativo` | Só o essencial: cortes nas fronteiras das palavras, jump cuts que alternam o enquadramento e legenda animada palavra a palavra; sem música, efeitos, grafismos nem tela final. Build de referência: `heditor new <work> <vídeo> --style nativo` e `heditor produce <work> none 0` |

Formatos de criador (estudo de técnicas de Reels de tecnologia com alta retenção):

| Estilo | Identidade |
|---|---|
| `camadas` | Cada conceito desenhado entre o falante e a parede: palavras gigantes e “?” atrás da cabeça, linhas-guia no cenário, placa de vidro, cards flutuantes e CTA de comentário para DM |
| `raio-x` | A visão da máquina: HUD de pipeline ao vivo, scan de profundidade, camadas explodidas, nuvem de pontos, rastreamento de rosto e mãos, transcrição que vira prompt e montagem na timeline |
| `duelo` | Página de comparação A/B: o mesmo take em dois painéis sincronizados editados de formas diferentes, selo VS, checklist do veredito e votação no CTA |
| `bancada` | Prova na bancada: etiqueta no gancho, chicote para um monitor filmado ou simulado, dedo e punch-ins na tela, inserts do resultado |
| `manchete` | Manchete no topo: clipe ou post do assunto em cima, faixa sobre a emenda, o falante reagindo embaixo, pico em tela cheia e divisão em faixas |
| `reacao` | O falante na frente do post: o bruto em que ele só fala vira um recorte na base do quadro, com a notícia, o post, a página ou a gravação de tela atrás dele, aproximada, rolada e marcada (caixa, marca-texto, sublinhado, círculo) na palavra; manchete marca-texto no primeiro frame, cards com o assunto e CTA de perfil |
| `revista` | Páginas editoriais: palavra-chave condensada com linha em serifa itálica, janela de retrato arredondada, chips por item, páginas de data e respiros em tela cheia |

Efeitos em camadas para qualquer estilo ou modo criativo (`heditor matte|depth|look|hands|plane`): texto atrás da pessoa, legenda pintada na parede, objeto 3D passando entre o falante e o cenário, névoa de profundidade, scan de contorno, nuvem de pontos e objetos que seguem as mãos. Veja [`depth-and-3d.md`](skills/heditor/references/depth-and-3d.md) e [`technique-catalogue.md`](skills/heditor/references/technique-catalogue.md).

Ferramentas de movimento: os plugins do GSAP (SplitText, DrawSVG, MorphSVG, MotionPath, CustomEase e outros) funcionam offline com regras de render determinístico ([`gsap-craft.md`](skills/heditor/references/gsap-craft.md)); `heditor svg` limpa SVGs com SVGO para desenho ou morph e confere pixel a pixel que a arte não mudou; `heditor physics` pré-calcula física de corpos rígidos com Rapier para camadas three.js com bloom e profundidade de campo ([`physics-3d.md`](skills/heditor/references/physics-3d.md)). Os estilos `gravidade` (física) e `circuito` (DrawSVG, MorphSVG, MotionPath e SplitText) usam esses recursos e trazem build de referência: `heditor new <work> <vídeo> --style gravidade` (ou `circuito`), escreva o `beats.json` a partir da fala e rode `heditor produce`.

Vídeos de banco (B-roll) grátis do [Mixkit](https://mixkit.co/free-stock-video/), sem conta e sem chave de API: `heditor stock search "server room" --orientation portrait` lista os clipes (busca em inglês) e `heditor stock get <work> '#2'` baixa o escolhido para `composition/assets/stock/`, depois de conferir na página do clipe a licença gratuita (Mixkit Stock Video Free License, que libera anúncios, redes sociais e YouTube sem crédito obrigatório). A origem de cada arquivo fica registrada em `<work>/stock.json`. Veja [`stock-media.md`](skills/heditor/references/stock-media.md).

Vídeo com o seu avatar da HeyGen (opcional): quando só existe o roteiro, sem gravação, a fonte do corte pode ser o seu gêmeo digital da HeyGen falando o texto que você aprovou. Conecte a sua conta uma vez com `heditor heygen connect`, um assistente interativo que oferece dois caminhos: a conta HeyGen (OAuth), em que os vídeos usam os créditos da sua assinatura, ou uma chave de API, cobrada na carteira pré-paga da API. Em servidor ou via SSH, o assistente mostra um link para você aprovar no navegador do seu computador e pede o endereço de retorno. A credencial fica com o CLI oficial da HeyGen, e o heditor não lê nem guarda a sua chave. Depois, `heditor avatar <work> --look <id> --script roteiro.txt` mostra a estimativa de custo em créditos ou em dólar, pede confirmação, baixa o vídeo para `<work>/source/` e registra a origem em `<work>/avatar.json`. Daí em diante, a edição segue o fluxo normal. Para a voz soar humana, prepare antes uma versão falada do roteiro (números por extenso, siglas e abreviações resolvidas, frases ligadas e pausas pontuais) e cadastre os termos estrangeiros, siglas e nomes num glossário de pronúncia da HeyGen (`heditor heygen glossaries`, `--glossary ID`), escritos do jeito que você fala. Defina uma vez a sua voz clonada oficial em `~/.heditor/brand.json` (`"heygen": {"voice_id": "..."}`): o heditor usa sempre essa voz e recusa a voz padrão do look quando ela não é um clone seu. Nada disso é instalado ou exigido por padrão. Veja [`heygen-avatar.md`](skills/heditor/references/heygen-avatar.md).

Detalhes de cada um em [`skills/heditor/references/styles/`](skills/heditor/references/styles/).

## Modo de vídeo longo (aulas, lives, YouTube)

Para editar minutos ou horas de gravação, em qualquer formato (`heditor formats`: 16:9 1920×1080, 16:9 4K opcional, 1:1, 4:5 e 9:16):

```text
Edite esta aula inteira para o YouTube em 16:9 no estilo lousa-de-aula, com capítulos e legendas.
Faça a live de ontem em 16:9 no modo criativo, tirando as pausas, e me dê também prévias em 4:5.
```

- **Transcrição em blocos com retomada:** horas de áudio em pedaços de 5 min com fronteiras no silêncio; se cair, continua de onde parou.
- **EDL proposta e revisável:** remove pausas mortas, falsos começos, repetições ("a gente a gente") e hesitações sem cortar palavras (o corte sempre cai no vale de energia entre palavras); você revisa `qa/edl-proposal.md` antes de aplicar e pode excluir trechos inteiros (perguntas do chat com nomes, dados privados).
- **Layouts para tela + câmera:** câmera em PiP, foco na tela com zoom numa região, falante em tela cheia e lado a lado, alternados por trecho (há sugestão automática pela atividade da tela).
- **Capítulos** com cartões, tag do capítulo atual e timestamps prontos para a descrição do YouTube; **legendas** queimadas (opcional) e exportação **SRT/VTT**; **lower thirds**; **cartão de abertura** e **encerramento** com Seguir → Seguindo ou Inscrever-se → Inscrito + "Assista o próximo".
- **Os 43 estilos como style packs** (paleta, tipografia, legenda, transições, cartões, lower third, grade da câmera, som) com regras de adaptação vertical → horizontal; **modo criativo** com set pieces (tipografia gigante da fala, mapa de conceitos desenhado nas palavras, checklist, zoom com destaque, HTML próprio) nos momentos-chave e dispositivos de retenção na cadência de cada tipo (aula, live, YouTube).
- **Render segmentado e retomável:** cada trecho é uma composição própria, segmentos prontos são pulados, os vídeos são concatenados sem recompressão e um único master de áudio contínuo é aplicado no fim (sem emendas de áudio). Estimativa de tempo e log de progresso.
- **QA do longo:** duração, decodificação, loudness (−14 LUFS padrão, configurável), sincronia câmera × tela × voz contra a gravação original, ASR por amostragem, capítulos, emendas entre segmentos (sem quadro preto ou repetido) e folhas de quadros.

Guia completo em [`long-form.md`](skills/heditor/references/long-form.md).

## Modos

- **Estilo fixo:** "edite no estilo `aeroporto`". O agente aplica a linguagem do estilo, mas reconstrói as cenas a partir da fala do novo vídeo.
- **Modo criativo:** "modo criativo". O agente estuda o vídeo, gera de 6 a 8 conceitos de formato, pesquisa referências, escolhe o mais surpreendente que sirva à fala e constrói tudo sob medida, com mudanças na tela a cada 1,5–2 s e efeitos sonoros em cada ação. Veja [`creative-mode.md`](skills/heditor/references/creative-mode.md).
- **Modo criativo + referência:** "modo criativo no estilo GTA 6", "abertura de anime", "telejornal", "documentário de natureza". O agente pesquisa a paleta, a tipografia, o HUD, os movimentos e os sons da referência e cria uma homenagem com equivalentes licenciados, sem logos, marcas, personagens ou músicas protegidas.
- **Pré-produção:** "analise estes roteiros e monte o plano de gravação e de edição". Antes de gravar, o agente mede os roteiros, faz o inventário do cenário pelas fotos, confere as gravações de tela que já existem e os estudos citados, monta os setups com gestos amarrados às palavras, gera o teleprompter a partir do documento e escolhe um estilo diferente para cada vídeo do lote. Veja [`pre-production.md`](skills/heditor/references/pre-production.md).
- **Gravação roteirizada e erros de gravação (triagem):** "gravei lendo o teleprompter, cuidado com as pausas, com os erros e com o que falei para o editor". Antes de editar, `heditor triage` corta o bruto nos silêncios, transcreve cada trecho sozinho e marca o que não entra: retomadas, falsas partidas, gaguejadas, autocorreções, frases proibidas, ruídos que o Whisper transforma em palavras e falhas de gravação (áudio estourado, batidas e notificações, quadros duplicados, câmera ou luz que mudou entre as tomadas). Quando você quebra a quarta parede e fala com o editor ("corta aí", "vamos de novo", "vamos editar essa parte"), a fala vira uma instrução (cortar, refazer, marcador ou nota de edição) que o agente segue e relata, e nunca entra no corte. Veja [`raw-takes.md`](skills/heditor/references/raw-takes.md).
- **Teste de gancho:** "edite estas três aberturas novas no anúncio que já converte". Só a abertura muda: ela é renderizada à parte e emendada no arquivo que está no ar com `heditor splice`, com o corpo intacto, trilha contínua, loudness casada na emenda e um relatório que prova o corpo idêntico (correlação do áudio, atraso zero, contagem de quadros). Veja [`hook-variants.md`](skills/heditor/references/hook-variants.md).

Gostou de um resultado do modo criativo? Peça para salvar como estilo nomeado. A skill documenta como fazer isso em [`adding-styles.md`](skills/heditor/references/adding-styles.md).

## Instalação

### Opção 1: instalador (recomendado)

```bash
curl -fsSL https://raw.githubusercontent.com/pycodebr/heditor/main/install.sh | bash
```

O instalador detecta os agentes instalados (Claude Code, Codex, OpenCode, Cursor e Hermes), cria o link da skill em cada um e roda o `setup.sh`, que:

- instala o que faltar: ffmpeg, Node.js ≥ 22, Python 3.10–3.13, git e curl (via apt, brew, dnf ou pacman);
- cria o ambiente Python em `~/.heditor/venv` com faster-whisper, MediaPipe, Playwright, NumPy, Pillow e pytest;
- prepara o HyperFrames 0.8.147 e o Chrome de renderização;
- baixa fontes (OFL), GSAP, o modelo de rosto, o modelo de transcrição e a biblioteca de 18 trilhas e 85 efeitos (Mixkit);
- cria `~/.heditor/env.sh`, `~/.heditor/brand.json` e o comando `heditor`;
- roda o `heditor doctor`.

Opções: `--agent claude|codex|opencode|cursor|hermes|all`, `--copy` (copia em vez de criar link), `--no-audio`, `--no-setup`.

### Opção 2: Skills CLI (Vercel)

```bash
npx skills add pycodebr/heditor -g          # instala a skill nos agentes detectados
bash ~/.agents/skills/heditor/scripts/setup.sh   # ou o caminho onde a skill foi instalada
```

### Opção 3: manual

```bash
git clone https://github.com/pycodebr/heditor.git
cd heditor && bash install.sh --agent claude      # ou copie skills/heditor para a pasta de skills do seu agente
```

Na primeira vez que for usar, o agente roda `setup.sh` sozinho se o `heditor doctor` acusar falta de alguma ferramenta.

### Configure sua marca

Edite `~/.heditor/brand.json`:

```json
{
  "name": "Sua Marca",
  "handle": "@seuperfil",
  "logo": "/caminho/para/logo.png",
  "lang": "pt",
  "follow": "Seguir",
  "following": "Seguindo",
  "comment": "Conta nos comentários",
  "colors": { "bg": "#050a14", "bg2": "#081626", "accent": "#edc580", "accent2": "#7dd3fc", "alert": "#ff3d57", "ok": "#7dffb0" }
}
```

## Como usar

Converse com o seu agente:

```text
Edite /videos/aula-03.mp4 no estilo documentario. Use o trecho em que eu falo sobre transição de carreira.
Modo criativo: transforme o minuto 12 deste podcast em um Reel e me surpreenda.
Modo criativo com referência de telejornal para este vídeo sobre a notícia da semana.
Faça três cortes deste vídeo, cada um com um formato diferente.
```

Vídeo longo pelo CLI:

```bash
heditor new --long aulas/a03 aula-03.mp4 --format 16:9 --style lousa-de-aula --kind aula --range 600,2400
heditor long transcribe aulas/a03              # ASR em blocos, retomável
heditor long edl aulas/a03                     # proposta de cortes -> revise qa/edl-proposal.md
heditor long apply aulas/a03                   # tela, câmera e voz montadas, palavras remapeadas
heditor long chapters aulas/a03 --suggest      # escreva chapters.json com os títulos
heditor long produce aulas/a03 music:282       # composição, segmentos e mixagem
heditor long preview aulas/a03 5,60,300 && heditor test aulas/a03
heditor long render aulas/a03 2 && heditor long finalize aulas/a03 a03-1920x1080.mp4
```

Ou use o CLI diretamente para Reels:

```bash
. ~/.heditor/env.sh
heditor probe aula.mp4 5 60 300                 # quadros para achar quem fala
heditor transcribe aula.mp4 0 3600 qa/asr.json  # transcrição com tempo por palavra
heditor triage bruto.mp4 --out triagem          # gravação roteirizada: retomadas, falas ao editor, ruídos
heditor new cortes/c01 aula.mp4                 # prepare.py, build.py e DESIGN.md
heditor prepare cortes/c01                      # corta fala e câmera, já sem pausas mortas
heditor gaps cortes/c01                         # confere: nenhuma pausa > 0,45 s na fala montada
heditor words cortes/c01                        # palavras do corte montado
heditor stock search "typing on laptop" --orientation portrait   # B-roll grátis do Mixkit (busca em inglês)
heditor stock get cortes/c01 '#1'               # baixa para composition/assets/stock e registra em stock.json
heditor produce cortes/c01 music:955 30         # composição + mixagem
heditor lint cortes/c01 && heditor preview cortes/c01 0.1,2,5,9,14,20 && heditor test cortes/c01
heditor render cortes/c01 && heditor finalize cortes/c01 c01-1080x1920.mp4 && heditor asr-check cortes/c01
```

Avatar da HeyGen (opcional):

```bash
heditor heygen connect                          # você mesmo, no seu terminal: conta HeyGen (OAuth) ou chave de API
heditor heygen status                           # conta, forma de cobrança, plano e créditos ou saldo
heditor heygen avatars                          # seus looks: id, orientação e motores (v, iv, iii)
heditor heygen glossaries                       # glossários de pronúncia (termo -> como a voz fala)
heditor avatar cortes/a01 --look <id> --script roteiro-fala.txt --glossary <id> --dry-run   # estimativa, sem gastar
heditor avatar cortes/a01 --look <id> --script roteiro-fala.txt --glossary <id>             # confirma, gera e baixa
heditor new cortes/a01 cortes/a01/source/avatar-<video_id>.mp4         # e segue o fluxo normal
```

## Requisitos

- Linux ou macOS (Windows via WSL2), 4 núcleos e 8 GB de RAM recomendados.
- Cerca de 1,6 GB em disco (ambiente Python, modelos e biblioteca de áudio); mais 99 MB se usar o mapa de profundidade.
- Um vídeo de 60 s leva de 5 a 15 min para renderizar em CPU comum. No modo longo, medimos cerca de 7,5 min de render por minuto de vídeo 1080p (2 workers, VPS de 4 núcleos compartilhada); o render é segmentado e retomável e `heditor long estimate` mede na sua máquina.

## Estrutura

```
skills/heditor/
├── SKILL.md                     # instruções que o agente lê
├── references/                  # workflow, modo criativo, som, legendas, gates, estilos
│   └── styles/                  # um arquivo por estilo nomeado
├── scripts/
│   ├── setup.sh · doctor.py · fetch_assets.py · heditor (CLI)
│   └── reelkit/                 # kit Python: corte, legendas, página HyperFrames, mixagem, QA; depthkit (recorte, profundidade, mãos, planos);
│                                #   formats (perfis de formato), stylepacks, longform/longkit/longmix/longqa/long_cli (modo longo)
├── templates/                   # prepare.py, build.py, DESIGN.md, brand.example.json; long/ (long.json, build.py, DESIGN.md, chapters.json)
└── assets/catalog.json          # catálogo de trilhas e efeitos (baixados no setup)
```

## Licenças e créditos

- Código e documentação: [MIT](LICENSE) © PycodeBR.
- Renderização: [HyperFrames](https://github.com/heygen-com/hyperframes) (Apache-2.0, HeyGen). Animação: [GSAP](https://gsap.com) (licença standard gratuita). Transcrição: [faster-whisper](https://github.com/SYSTRAN/faster-whisper) (MIT). Rosto, recorte e mãos: [MediaPipe](https://github.com/google-ai-edge/mediapipe) (Apache-2.0). Profundidade: [Depth Anything V2 Small](https://github.com/DepthAnything/Depth-Anything-V2) (Apache-2.0). 3D: [three.js](https://threejs.org) (MIT). Física: [Rapier](https://rapier.rs) (Apache-2.0). Limpeza de SVG: [SVGO](https://github.com/svg/svgo) (MIT).
- Fontes: [Google Fonts](https://github.com/google/fonts) (SIL OFL 1.1). Ícones: [Lucide](https://lucide.dev) (ISC).
- Trilhas e efeitos: [Mixkit](https://mixkit.co/license/) (Free License). Os arquivos **não** estão neste repositório; o setup baixa cada um do CDN oficial para a sua máquina.
- Vídeos de banco: [Mixkit](https://mixkit.co/license/#videoFree) (Stock Video Free License), baixados um a um sob demanda por `heditor stock get`, nunca em massa e nunca redistribuídos aqui.
- Avatar (opcional): o [CLI da HeyGen](https://developers.heygen.com/cli) é instalado só se você pedir, pelo instalador oficial, e o uso segue os termos da sua conta HeyGen. O heditor não cria avatares nem clona vozes.
- Tabela completa em [`references/licenses.md`](skills/heditor/references/licenses.md).

O heditor não publica nada em redes sociais sozinho e não usa logos ou marcas de terceiros nos estilos de homenagem.

## Contribuindo

Issues e PRs são bem-vindos: novos estilos (com a ficha completa em `references/styles/`), correções do kit, suporte a outras plataformas. Veja [CONTRIBUTING.md](CONTRIBUTING.md).

---

## English

**heditor** is an open Agent Skill (SKILL.md) that lets AI coding agents edit talking-head footage (classes, lives, podcasts) into vertical 1080×1920 Reels/Shorts/TikToks with motion graphics, word-synced captions, sound design and an emotional soundtrack, or into long-form videos (whole classes, lives, YouTube videos) in 16:9, 1:1, 4:5 or 9:16.

- **Forty-three named styles:** `cinema`, `ruptura`, `impacto`, `game`, `thriller`, `gravidade` (the speech has weight: labelled blocks land on their words with baked physics, a heavy turn, a tower for the answer), `trailer` (suspense/launch trailer: dramatic pauses, silence before hits, words on the wall behind the speaker), `ide`, `aeroporto` (control tower), `chat`, `documentario`, `documentario-narrado` (large-scale narrated documentary on a living globe), `podcast`, `missao` (open-world game homage), `tribunal` (courtroom sketch); paid-ad formats with a "Learn more" CTA: `keynote`, `stories`, `predio-24h`, `bilheteria`, `porta-de-aco`, `lapidacao` (luxury jewellery commercial: the raw idea as a rough stone, the cut, the gem, the case that slams shut), `manual-de-montagem`, `carrinho`, `entrega`, `auditorio`, `album`; authority formats: `cassino-de-precisao`, `mesa-de-risco`, `turno-da-madrugada`, `arquivo-cofre`, `aduana-de-dados`, `laudo-de-sinistro`; didactic formats: `lousa-de-aula` (interactive chalkboard lesson), `circuito` (the explanation as a circuit board: components drawn on their words, copper traces, data pulses, morphing icons, LEDs), `planta-de-acesso` (who may use what as a floor plan drawn live: rooms with doors, role badges that open or lock them); native format: `nativo` (clean edit: cuts + animated captions only); creator formats: `camadas`, `raio-x`, `duelo`, `bancada`, `manchete`, `reacao` (the speaker cut out in front of the post/news he reacts to, the subject pushed in, scrolled and marked on his words), `revista`.
- **Layered 2.5D/3D effects (depthkit):** speaker matte, depth map, text behind the speaker, captions painted on the set, three.js objects passing behind the speaker, depth fog, contour scans, point clouds, hand-anchored objects (`heditor matte|depth|look|hands|plane`).
- **Motion tools:** GSAP plugins offline with seek-safe rules (`gsap-craft.md`), SVGO clean-up with a pixel check (`heditor svg`), baked Rapier rigid-body physics for three.js layers with bloom and depth of field (`heditor physics`, `physics-3d.md`).
- **Creative mode:** the agent analyses the video, researches, invents a world for that specific speech and builds it with retention-focused motion and sound.
- **Creative mode + reference:** e.g. "creative mode in the style of GTA 6". The agent researches the reference and builds a licence-safe homage.
- **Long-form mode:** `heditor new --long` + `heditor long ...`: chunked resumable ASR, a reviewable EDL proposal that removes dead pauses, false starts, repetitions and fillers without cutting words, screen + camera layouts (PiP, screen zoom, speaker, side by side), chapters (cards + YouTube timestamps), burned captions and SRT/VTT, lower thirds, intro and end cards (Follow or YouTube Subscribe), every named style as a *style pack*, creative set pieces at key moments with a retention cadence per kind (class, live, YouTube), a segmented resumable render with one continuous master audio, and a long-form QA report (loudness, sync against the source, sampled ASR, chapters, segment seams). See [`long-form.md`](skills/heditor/references/long-form.md).
- **Hook tests and raw takes:** `heditor triage` labels the chunks of a raw teleprompter take (keep, retake, false start, aside to the editor, noise), reads the speaker breaking the fourth wall as notes to the editor (cut, redo, marker, editing note), flags stumbles, self-corrections, forbidden phrases and recording failures (clipping, knocks, duplicated frames, the set moving between takes) before cutting; `heditor splice` joins a new rendered opening to a video that is already running, body untouched (audio decoded whole and cut by sample, one encode, report proving the body identical). See [`hook-variants.md`](skills/heditor/references/hook-variants.md).
- **Free stock B-roll:** `heditor stock search|get` finds and downloads Mixkit clips (no account, no API key), checks the Mixkit Stock Video Free License on the clip page and records provenance in `<work>/stock.json`. See [`stock-media.md`](skills/heditor/references/stock-media.md).
- **Optional AI avatar source (HeyGen):** `heditor heygen connect` is an interactive assistant that connects your own HeyGen account by OAuth (videos use your subscription credits; on servers it prints a link and asks for the return address) or by API key (prepaid API wallet). The credential stays with the official HeyGen CLI. `heditor avatar <work> --look ID --script FILE` shows a cost estimate, asks for confirmation, downloads the twin video into `<work>/source/` and records provenance in `<work>/avatar.json`; the edit then follows the normal workflow. A pronunciation glossary (`heditor heygen glossaries`, `--glossary ID`) and a spoken version of the script keep the clone sounding human. Nothing is installed or required by default. See [`heygen-avatar.md`](skills/heditor/references/heygen-avatar.md).
- **Pipeline:** word-timed ASR (faster-whisper), frame-accurate cuts, voice chain, HyperFrames (HTML + GSAP) composition, voice-first mix profiles (`voice` for organic cuts, `presence` for ads and creative mode, with a music presence floor) at −14 LUFS, and automatic QA (lint, vision-reviewed previews, tests, pixel safe-margin, loudness/true peak, ASR of the final mix, 40-frame contact sheet).

**Install:** `curl -fsSL https://raw.githubusercontent.com/pycodebr/heditor/main/install.sh | bash`, or `npx skills add pycodebr/heditor -g` followed by `bash <skill>/scripts/setup.sh`. Then edit `~/.heditor/brand.json` and ask your agent: *"edit this video in creative mode"*.

MIT © PycodeBR (Felipe Azambuja). Music and SFX are downloaded from Mixkit under its free licence and are not redistributed here.
