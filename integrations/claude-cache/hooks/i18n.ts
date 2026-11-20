// The bar's words in the conversation language the repository declares on its root harness
// (`Language: pt-BR` in AGENTS.md, the contract quenching's agents/communication.md owns).
// Any tag starting with `pt` speaks Portuguese; everything else, English.

export type Lang = 'en' | 'pt'

export const HANDOFF = '/quenching-cache handoff'

export type Words = {
  waiting: string
  minLeft: (m: string) => string
  next: (money: string) => string
  nextNormal: string
  nextTimes: (r: number) => string
  nextMuch: string
  more: (r: number) => string
  later: (money: string) => string
  laterTimes: (r: number) => string
  laterNormal: string
  laterMuch: string
  expired: string
  reset: { model: string; compact: string }
  keepGoing: string
  replySoon: string
  suggestNew: string
  save: (tokens: string, money: string | null) => string
  smallChat: string
  sendWarning: (why: 'model' | 'compact' | 'expired') => string
  hidden: string
  shown: string
  help: string
  handoffWriting: string
  handoffNeedsCq: string
  handoffFailed: (why: string) => string
  handoffSaved: (locator: string) => string
  handoffFactsOnly: (why: string) => string
  handoffContinue: (copied: boolean, line: string) => string
  handoffCopied: (line: string) => string
  handoffSendLine: (line: string) => string
  statsNeedsCq: string
  statsNone: string
  statsTitle: (date: string) => string
  statsHeader: string
  statsThisChat: string
  statsProject: string
}

const en: Words = {
  waiting: '⚪️ quenching-cache starts after you send a message',
  minLeft: m => `${m} min left`,
  next: x => `next message ≈ ${x}`,
  nextNormal: 'next message: normal cost',
  nextTimes: r => `next message: ${r}× more`,
  nextMuch: 'next message: much more',
  more: r => ` (${r}× more)`,
  later: x => `, later ≈ ${x}`,
  laterTimes: r => `, later ${r}× more`,
  laterNormal: ', later normal cost',
  laterMuch: ', later much more',
  expired: 'cache expired',
  reset: { model: 'cache reset (model changed)', compact: 'cache reset (chat compacted)' },
  keepGoing: '✅ Keep going',
  replySoon: `⏳ Reply soon or try ${HANDOFF}`,
  suggestNew: `🔄 Try ${HANDOFF} or a new chat`,
  save: (t, x) => `🔄 Try ${HANDOFF} to save ${t} tokens${x ? ` | ${x}` : ''}`,
  smallChat: 'Small chat, fine to keep going',
  sendWarning: why => `Heads-up: ${why === 'model' ? 'the model changed' : why === 'compact' ? 'the chat was compacted' : "this chat's cache had expired"}, so this message rebuilds the cache. See the bar for the cost.`,
  hidden: 'quenching-cache bar hidden. Type /quenching-cache to show it.',
  shown: 'quenching-cache bar shown.',
  help: 'Use: /quenching-cache (show or hide the bar) · /quenching-cache handoff [focus] · /quenching-cache stats',
  handoffWriting: 'quenching-cache: writing the handoff…',
  handoffNeedsCq: 'quenching-cache: no handoff written: `cq` was not found (.agents/quenching/bin/cq or PATH). Deploy quenching here first. This chat is untouched.',
  handoffFailed: why => `quenching-cache: no handoff written (${why}). This chat is untouched.`,
  handoffSaved: loc => `Handoff saved to ${loc}. This command never resent the chat to the main model: no cache read, no rebuild.`,
  handoffFactsOnly: why => ` Facts only: ${why}.`,
  handoffContinue: (copied, line) => ` To continue, start a new chat and paste${copied ? ' (auto-copied)' : ''}: ${line}`,
  handoffCopied: line => `Handoff line copied. Paste it into a new chat: ${line}`,
  handoffSendLine: line => `Start a new chat and send: ${line}`,
  statsNeedsCq: 'quenching-cache: stats need `cq` (.agents/quenching/bin/cq or PATH); deploy quenching here first.',
  statsNone: 'quenching-cache: no request with usage in this project yet.',
  statsTitle: d => `quenching-cache stats (list prices of ${d}; an estimate, not a bill)`,
  statsHeader: '| | Model | Requests | Cache hit | Cache writes | ≈ USD |',
  statsThisChat: 'This chat',
  statsProject: 'This project',
}

const pt: Words = {
  waiting: '⚪️ o quenching-cache começa depois da sua primeira mensagem',
  minLeft: m => `${m} min restantes`,
  next: x => `próxima mensagem ≈ ${x}`,
  nextNormal: 'próxima mensagem: custo normal',
  nextTimes: r => `próxima mensagem: ${r}× mais`,
  nextMuch: 'próxima mensagem: muito mais',
  more: r => ` (${r}× mais)`,
  later: x => `, depois ≈ ${x}`,
  laterTimes: r => `, depois ${r}× mais`,
  laterNormal: ', depois custo normal',
  laterMuch: ', depois muito mais',
  expired: 'cache expirado',
  reset: { model: 'cache zerado (modelo trocado)', compact: 'cache zerado (chat compactado)' },
  keepGoing: '✅ Pode seguir',
  replySoon: `⏳ Responda logo ou use ${HANDOFF}`,
  suggestNew: `🔄 Use ${HANDOFF} ou um chat novo`,
  save: (t, x) => `🔄 Use ${HANDOFF} e economize ${t} tokens${x ? ` | ${x}` : ''}`,
  smallChat: 'Chat pequeno, pode seguir',
  sendWarning: why => `Atenção: ${why === 'model' ? 'o modelo mudou' : why === 'compact' ? 'o chat foi compactado' : 'o cache deste chat expirou'}, então esta mensagem reconstrói o cache. O custo está na barra.`,
  hidden: 'Barra do quenching-cache escondida. Digite /quenching-cache para mostrar.',
  shown: 'Barra do quenching-cache visível.',
  help: 'Uso: /quenching-cache (mostra ou esconde a barra) · /quenching-cache handoff [foco] · /quenching-cache stats',
  handoffWriting: 'quenching-cache: escrevendo o handoff…',
  handoffNeedsCq: 'quenching-cache: nenhum handoff escrito: o `cq` não foi encontrado (.agents/quenching/bin/cq ou PATH). Faça o deploy do quenching aqui antes. Este chat não foi tocado.',
  handoffFailed: why => `quenching-cache: nenhum handoff escrito (${why}). Este chat não foi tocado.`,
  handoffSaved: loc => `Handoff salvo em ${loc}. Este comando não reenviou o chat ao modelo principal: nenhuma leitura de cache, nenhuma reconstrução.`,
  handoffFactsOnly: why => ` Só fatos: ${why}.`,
  handoffContinue: (copied, line) => ` Para continuar, abra um chat novo e cole${copied ? ' (já copiado)' : ''}: ${line}`,
  handoffCopied: line => `Linha do handoff copiada. Cole num chat novo: ${line}`,
  handoffSendLine: line => `Abra um chat novo e envie: ${line}`,
  statsNeedsCq: 'quenching-cache: as estatísticas precisam do `cq` (.agents/quenching/bin/cq ou PATH); faça o deploy do quenching aqui antes.',
  statsNone: 'quenching-cache: ainda não há requisição com uso neste projeto.',
  statsTitle: d => `estatísticas do quenching-cache (preços de tabela de ${d}; uma estimativa, não uma conta)`,
  statsHeader: '| | Modelo | Requisições | Acerto de cache | Escritas de cache | ≈ USD |',
  statsThisChat: 'Este chat',
  statsProject: 'Este projeto',
}

export const WORDS: Record<Lang, Words> = { en, pt }

const LANGUAGE = /^Language:\s*([A-Za-z0-9-]+)/m

/** The language a root harness file declares; English when it declares none. */
export function langOf(harness: string | undefined): Lang {
  const m = harness ? LANGUAGE.exec(harness) : null
  return m && m[1]!.toLowerCase().startsWith('pt') ? 'pt' : 'en'
}
