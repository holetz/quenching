import { createEffect, createSignal, For, onCleanup, Show } from "solid-js"
import {
  Command,
  MenuItem,
  Panel,
  Plugin,
  Style,
  usePlugin,
  type PanelProps,
  type PanelTab,
} from "@opencode/plugin/gui"
import {
  Vitrine, type Composite, type Composition, type Detail, type Member, type Neighbor, type Quenching,
  type QuenchingUpdate, type Row, type TaskInfo, type Touch,
} from "./rpc.js"

const specsTab: PanelTab = { id: "specs", title: "Specs", closable: "hover" }
const EVIDENCE: Record<string, string> = {
  worktree: "worktree",
  commit: "commit",
  command: "escrita",
  mention: "citada",
  read: "leitura",
}

const STAGE_LABEL: Record<string, string> = {
  captured: "capturada",
  ready: "pronta",
  approved: "aprovada",
  executing: "em execução",
  blocked: "bloqueada",
  review: "em revisão",
  archived: "arquivada",
}

function ageDays(date: string): number | null {
  if (!date) return null
  const time = Date.parse(`${date}T00:00:00Z`)
  if (Number.isNaN(time)) return null
  return Math.max(0, Math.floor((Date.now() - time) / 86_400_000))
}

function ageLabel(date: string): string {
  const days = ageDays(date)
  if (days === null) return date
  if (days === 0) return "hoje"
  if (days === 1) return "ontem"
  if (days < 30) return `há ${days} d`
  const months = Math.floor(days / 30)
  return `há ${months} ${months === 1 ? "mês" : "meses"}`
}

/** Como no board, uma spec recente ganha peso no rótulo de idade. */
function ageFresh(date: string): string {
  const days = ageDays(date)
  if (days === null) return ""
  if (days <= 1) return " fresh-1"
  if (days <= 3) return " fresh-2"
  if (days <= 7) return " fresh-3"
  return ""
}

function runBad(spec: Detail): boolean {
  return spec.run === "failed" || spec.run === "blocked" || spec.verifier === "fail"
}

function quenchLabel(state: Quenching): string {
  if (state.missing) return state.available ? `Instalar ${state.available}` : "Instalar quenching"
  return `Atualizar ${state.version} → ${state.available}`
}

function quenchTitle(state: Quenching): string {
  if (state.error) return state.error
  const tool = state.available ? `cq ${state.available} no PATH` : "cq não encontrado no PATH"
  if (state.missing) return `quenching não instalado em ${state.root}; ${tool}`
  return `instalado ${state.version} em ${state.root}; ${tool}`
}

const css = `
.qs { display: flex; flex-direction: column; gap: 8px; padding: 10px; font-size: 12px; height: 100%; min-height: 0; }
.qs-head { display: flex; gap: 6px; align-items: center; }
.qs-upgrade { flex: none; display: inline-flex; min-width: 0; }
.qs-quench { flex: none; display: inline-flex; align-items: center; gap: 5px; padding: 2px 8px; border: 1px solid var(--border); border-radius: 999px; font-size: 11px; font-variant-numeric: tabular-nums; white-space: nowrap; }
.qs-quench.warn { color: #fbbf24; border-color: color-mix(in srgb, #fbbf24 35%, var(--border)); }
.qs-health-dot { width: 6px; height: 6px; border-radius: 50%; background: #4ade80; flex: none; }
.qs-quench.warn .qs-health-dot { background: #fbbf24; }
.qs-input { flex: 1; min-width: 0; padding: 6px 8px; border: 1px solid var(--border); border-radius: 6px; background: transparent; color: inherit; font: inherit; }
.qs-label { font-size: 10px; text-transform: uppercase; letter-spacing: .08em; opacity: .6; margin-top: 2px; }
.qs-dot { width: 6px; height: 6px; border-radius: 50%; background: currentColor; opacity: .3; flex: none; }
.qs-dot.command, .qs-dot.commit { opacity: 1; }
.qs-dot.commit { background: #4ade80; }
.qs-dot.mention { opacity: .9; background: #60a5fa; }
.qs-dot.worktree { opacity: .75; }
.qs-list { overflow: auto; max-height: 38%; border: 1px solid var(--border); border-radius: 6px; }
.qs-row { display: grid; grid-template-columns: auto 1fr; gap: 2px 8px; width: 100%; padding: 6px 8px; border: 0; border-bottom: 1px solid var(--border); background: transparent; color: inherit; font: inherit; text-align: left; cursor: pointer; }
.qs-row:last-child { border-bottom: 0; }
.qs-row.picked { background: color-mix(in srgb, currentColor 8%, transparent); }
.qs-id { display: inline-flex; align-items: center; gap: 5px; font-variant-numeric: tabular-nums; opacity: .6; }
.qs-title { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.qs-meta { grid-column: 1 / -1; font-size: 11px; opacity: .55; }
.qs-detail { flex: 1; min-height: 0; overflow: hidden; display: flex; flex-direction: column; gap: 6px; }
.qs-detail-head { display: flex; gap: 8px; align-items: flex-start; justify-content: space-between; padding: 8px 10px; border: 1px solid color-mix(in srgb, var(--qs-stage, currentColor) 28%, var(--border)); border-left: 3px solid var(--qs-stage, var(--border)); border-radius: 8px; background: color-mix(in srgb, var(--qs-stage, currentColor) 7%, transparent); }
.qh-captured { --qs-stage: #8a857b; }
.qh-ready { --qs-stage: #2f6fd0; }
.qh-approved { --qs-stage: #1f6f43; }
.qh-executing { --qs-stage: #a86f00; }
.qh-blocked { --qs-stage: #c0392b; }
.qh-review { --qs-stage: #6b46a8; }
.qh-archived { --qs-stage: #7b766c; }
.qs-head-main { flex: 1; min-width: 0; display: flex; flex-direction: column; gap: 4px; }
.qs-top { display: flex; align-items: center; gap: 5px; flex-wrap: wrap; min-width: 0; }
.qs-spec-id { font-weight: 700; font-variant-numeric: tabular-nums; }
.qs-detail-title { font-weight: 600; font-size: 13px; line-height: 1.3; }
.qs-subject { font-size: 11px; opacity: .65; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.qs-mute { opacity: .6; font-size: 11px; }
.qs-stage, .qs-pri, .qs-chip { display: inline-flex; align-items: center; gap: 4px; padding: 0 6px; height: 16px; border: 1px solid transparent; border-radius: 999px; font-size: 10px; line-height: 1; white-space: nowrap; }
.qs-stage { font-weight: 600; background: color-mix(in srgb, var(--qs-stage, currentColor) 16%, transparent); border-color: color-mix(in srgb, var(--qs-stage, currentColor) 34%, transparent); color: color-mix(in srgb, var(--qs-stage, currentColor) 74%, currentColor); }
.qs-chip { background: color-mix(in srgb, currentColor 8%, transparent); border-color: color-mix(in srgb, currentColor 14%, transparent); opacity: .8; }
.qs-pri { font-weight: 700; font-variant-numeric: tabular-nums; background: color-mix(in srgb, currentColor 8%, transparent); }
.qs-pri.p1 { color: color-mix(in srgb, #c0392b 72%, currentColor); border-color: color-mix(in srgb, #c0392b 40%, transparent); }
.qs-pri.p2 { color: color-mix(in srgb, #a86f00 72%, currentColor); border-color: color-mix(in srgb, #a86f00 40%, transparent); }
.qs-pri.p3, .qs-pri.p4 { opacity: .6; }
.qs-age { margin-left: auto; font-size: 11px; opacity: .55; font-variant-numeric: tabular-nums; white-space: nowrap; }
.qs-age.fresh-1, .qs-age.fresh-2 { padding: 0 4px; border-radius: 4px; opacity: 1; background: color-mix(in srgb, currentColor 14%, transparent); }
.qs-age.fresh-1 { font-weight: 700; }
.qs-age.fresh-2 { font-weight: 600; }
.qs-age.fresh-3 { opacity: .8; }
.qs-why { display: flex; gap: 5px; font-size: 11px; color: color-mix(in srgb, #c0392b 74%, currentColor); }
.qs-why span:last-child { display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }
.qs-signal { display: flex; align-items: center; gap: 6px; }
.qs-progress-num { font-size: 11px; font-variant-numeric: tabular-nums; opacity: .8; }
.qs-bar { flex: 1; max-width: 220px; height: 5px; border-radius: 3px; overflow: hidden; background: color-mix(in srgb, currentColor 14%, transparent); }
.qs-bar i { display: block; height: 100%; border-radius: 3px; background: color-mix(in srgb, #1f6f43 82%, currentColor); }
.qs-foot { display: flex; flex-wrap: wrap; align-items: center; gap: 6px; font-size: 11px; }
.qs-who { display: inline-flex; align-items: center; gap: 4px; max-width: 180px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.qs-av { width: 14px; height: 14px; flex: none; display: inline-grid; place-items: center; border-radius: 50%; font-size: 8px; font-weight: 700; text-transform: lowercase; background: color-mix(in srgb, var(--qs-stage, currentColor) 24%, transparent); color: color-mix(in srgb, var(--qs-stage, currentColor) 74%, currentColor); }
.qs-run.pass, .qs-ready.ok { color: color-mix(in srgb, #1f6f43 66%, currentColor); }
.qs-run.bad { color: color-mix(in srgb, #c0392b 74%, currentColor); font-weight: 600; }
.qs-ready.warn { color: color-mix(in srgb, #a86f00 74%, currentColor); }
.qs-link { padding: 0; border: 0; background: transparent; color: color-mix(in srgb, #2f6fd0 74%, currentColor); font: inherit; font-size: 11px; text-decoration: underline; cursor: pointer; }
.qs-branch { max-width: 190px; font-family: ui-monospace, SFMono-Regular, monospace; font-size: 10px; overflow: hidden; text-overflow: ellipsis; display: inline-block; line-height: 16px; }
.qs-error { color: #f87171; font-size: 11px; }
.qs-tabs { display: flex; gap: 2px; overflow-x: auto; flex: none; padding-bottom: 4px; border-bottom: 1px solid var(--border); }
.qs-tab { flex: none; padding: 3px 7px; border: 0; border-radius: 4px; background: transparent; color: inherit; font: inherit; font-size: 11px; opacity: .6; cursor: pointer; }
.qs-tab.active { opacity: 1; background: color-mix(in srgb, currentColor 10%, transparent); }
.qs-section { flex: 1; min-height: 0; overflow: auto; padding-top: 6px; }
.qs-md { font-size: 12px; line-height: 1.55; }
.qs-md :is(h1, h2, h3) { font-size: 13px; margin: 10px 0 4px; }
.qs-task-list { display: flex; flex-direction: column; gap: 1px; padding-bottom: 6px; margin-bottom: 6px; border-bottom: 1px solid var(--border); }
.qs-task { display: flex; gap: 6px; align-items: flex-start; width: 100%; padding: 4px 6px; border: 0; border-radius: 4px; background: transparent; color: inherit; font: inherit; text-align: left; cursor: pointer; }
.qs-task:hover { background: color-mix(in srgb, currentColor 6%, transparent); }
.qs-task.done .qs-task-text { opacity: .5; text-decoration: line-through; }
.qs-task.blocked .qs-state { color: #f87171; }
.qs-state { width: 10px; flex: none; }
.qs-task-text { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.qs-dep-count { display: inline-flex; gap: 3px; margin-left: 5px; font-variant-numeric: tabular-nums; opacity: .75; }
.qs-deps { display: flex; flex-direction: column; gap: 10px; padding-bottom: 6px; }
.qs-dep-group { display: flex; flex-direction: column; gap: 4px; }
.qs-dep-label { font-size: 10px; text-transform: uppercase; letter-spacing: .08em; opacity: .6; }
.qs-dep-list { display: flex; flex-direction: column; border: 1px solid var(--border); border-radius: 6px; overflow: hidden; }
.qs-dep { display: grid; grid-template-columns: auto 1fr; gap: 2px 8px; width: 100%; padding: 5px 8px; border: 0; border-bottom: 1px solid var(--border); background: transparent; color: inherit; font: inherit; text-align: left; cursor: pointer; }
.qs-dep:last-child { border-bottom: 0; }
.qs-dep:hover { background: color-mix(in srgb, currentColor 6%, transparent); }
.qs-dep-id { font-variant-numeric: tabular-nums; opacity: .6; }
.qs-dep.critical .qs-dep-id { opacity: 1; font-weight: 600; color: color-mix(in srgb, #a86f00 78%, currentColor); }
.qs-dep-title { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.qs-dep-meta { grid-column: 1 / -1; font-size: 11px; opacity: .55; }
.qs-member.dropped .qs-dep-id, .qs-member.dropped .qs-dep-title { opacity: .45; text-decoration: line-through; }
.qs-member.done .qs-dep-id { opacity: 1; color: color-mix(in srgb, #2f8f4e 78%, currentColor); }
.qs-member.waiting .qs-dep-id { opacity: 1; color: color-mix(in srgb, #a86f00 78%, currentColor); }
`

/** O que o `schedule` sabe de uma vizinha, numa linha: entrega, caminho crítico, atraso e janela. */
function depMeta(node: Neighbor): string {
  const bits: string[] = []
  if (node.phase === "archive") bits.push("arquivada")
  if (node.critical) bits.push("caminho crítico")
  if (node.slip > 0) bits.push(`+${node.slip}d`)
  if (node.start || node.target) bits.push(`${node.start || "?"} → ${node.target || "?"}`)
  return bits.join(" · ")
}

const MEMBER_MARK: Record<string, string> = { done: "✓", dropped: "×", "in-progress": "▸", waiting: "!" }

/** O que o épico já sabe de um membro: o estado dele, a etapa da spec e o que ele espera dentro do épico. */
function memberMeta(member: Member): string {
  const bits: string[] = []
  if (member.stage) bits.push(STAGE_LABEL[member.stage] ?? member.stage)
  if (member.after.length > 0) bits.push(`espera ${member.after.join(", ")}`)
  return bits.join(" · ")
}

function memberClass(member: Member): string {
  if (member.status === "done") return "done"
  if (member.status === "dropped") return "dropped"
  return member.waitingOn.length > 0 ? "waiting" : ""
}

/** Os membros do épico, na ordem declarada: o que ele é feito, e não o que ele espera. */
function CompositionView(props: { composition: Composition; onPick: (id: number) => void }) {
  const progress = () => props.composition.progress
  return (
    <div class="qs-dep-group">
      <div
        class="qs-dep-label"
        title="as specs que este épico declara no próprio documento, na ordem em que ele as lista"
      >
        Specs deste épico
        <span class="qs-dep-count">
          <span>{progress().done}/{progress().total} concluídas</span>
          <Show when={progress().blocked > 0}><span>· {progress().blocked} bloqueada{progress().blocked > 1 ? "s" : ""}</span></Show>
        </span>
      </div>
      <div class="qs-dep-list">
        <For each={props.composition.items}>{(member) => (
          <button
            class="qs-dep qs-member"
            classList={{ done: memberClass(member) === "done", dropped: memberClass(member) === "dropped", waiting: memberClass(member) === "waiting" }}
            title={`${member.spec} — ${member.title}`}
            onClick={() => props.onPick(member.spec)}
          >
            <span class="qs-dep-id">{MEMBER_MARK[member.status] ?? "·"} {member.label}</span>
            <span class="qs-dep-title">{member.spec} · {member.title}</span>
            <Show when={memberMeta(member)}>{(meta) => <span class="qs-dep-meta">{meta()}</span>}</Show>
          </button>
        )}</For>
      </div>
    </div>
  )
}

/** Onde esta spec é membro: o épico que a declara no próprio documento, com o rótulo que ele lhe deu. */
function MembershipView(props: { epics: Composite[]; onPick: (id: number) => void }) {
  return (
    <div class="qs-dep-group">
      <div class="qs-dep-label" title="os épicos que nomeiam esta spec no `## Tasks` deles">
        Parte de
      </div>
      <div class="qs-dep-list">
        <For each={props.epics}>{(epic) => (
          <button
            class="qs-dep"
            title={`${epic.epic} — ${epic.title}`}
            onClick={() => props.onPick(epic.epic)}
          >
            <span class="qs-dep-id">{epic.label || "·"}</span>
            <span class="qs-dep-title">{epic.epic} · {epic.title}</span>
            <Show when={epic.group > 0}>{(group) => <span class="qs-dep-meta">onda {group()}</span>}</Show>
          </button>
        )}</For>
      </div>
    </div>
  )
}

function hasView(spec: Detail): boolean {
  return spec.deps.up.length > 0 || spec.deps.down.length > 0 || spec.deps.cycle.length > 0
    || Boolean(spec.composition) || spec.epics.length > 0
}

function DependencyGroup(props: {
  label: string
  hint: string
  nodes: Neighbor[]
  empty: string
  onPick: (id: number) => void
}) {
  return (
    <div class="qs-dep-group">
      <div class="qs-dep-label" title={props.hint}>{props.label}</div>
      <Show when={props.nodes.length > 0} fallback={<div class="qs-mute">{props.empty}</div>}>
        <div class="qs-dep-list">
          <For each={props.nodes}>{(node) => (
            <button
              class="qs-dep"
              classList={{ critical: node.critical }}
              title={`${node.id} — ${node.title}`}
              onClick={() => props.onPick(node.id)}
            >
              <span class="qs-dep-id">{node.id}</span>
              <span class="qs-dep-title">{node.title}</span>
              <Show when={depMeta(node)}>{(meta) => <span class="qs-dep-meta">{meta()}</span>}</Show>
            </button>
          )}</For>
        </div>
      </Show>
    </div>
  )
}

/** A aba de dependências: as specs que esta espera e as que esperam por ela, ambas clicáveis. */
function DependencyView(props: { spec: Detail; onPick: (id: number) => void }) {
  const edges = () => props.spec.deps.up.length > 0 || props.spec.deps.down.length > 0
  return (
    <div class="qs-deps">
      <Show when={props.spec.epics.length > 0}>
        <MembershipView epics={props.spec.epics} onPick={props.onPick} />
      </Show>
      <Show when={props.spec.composition}>
        {(composition) => <CompositionView composition={composition()} onPick={props.onPick} />}
      </Show>
      <Show when={props.spec.deps.cycle.length > 0}>
        <div class="qs-why" title="ciclo de dependência">
          <span>⚠</span>
          <span>ciclo: {props.spec.deps.cycle.join(" → ")} — nada é agendado enquanto ele existir</span>
        </div>
      </Show>
      {/* Sem aresta, e com composição ou membresia acima, as duas listas não têm o que dizer. */}
      <Show when={edges() || (!props.spec.composition && props.spec.epics.length === 0)}>
        <DependencyGroup
          label="Acima — esta spec espera por"
          hint="as specs nomeadas no dependsOn desta"
          nodes={props.spec.deps.up}
          empty="nada acima: nenhuma dependência declarada"
          onPick={props.onPick}
        />
        <DependencyGroup
          label="Abaixo — esperam por esta"
          hint="as specs que nomeiam esta no dependsOn delas"
          nodes={props.spec.deps.down}
          empty="nada abaixo: nenhuma spec declara que depende desta"
          onPick={props.onPick}
        />
      </Show>
    </div>
  )
}

function SpecsPanel(props: PanelProps) {
  const ctx = usePlugin()
  const rpc = () => ctx.client.rpc(Vitrine)
  const [query, setQuery] = createSignal("")
  const [rows, setRows] = createSignal<Row[]>([])
  const [touched, setTouched] = createSignal<Touch[]>([])
  const [picked, setPicked] = createSignal<number>()
  const [detail, setDetail] = createSignal<Detail>()
  const [tab, setTab] = createSignal(0)
  const [error, setError] = createSignal("")
  const [busy, setBusy] = createSignal(false)
  const [quench, setQuench] = createSignal<Quenching>()
  const [upgrading, setUpgrading] = createSignal(false)
  const directory = () => props.session.directory
  const searching = () => query().trim().length > 0
  // Só existe botão quando há o que consertar: ausente ou atrás do cq do PATH.
  const stale = () => {
    const state = quench()
    return state && (state.missing || state.outdated) ? state : undefined
  }
  // Com a superfície em dia o painel mostra o estado, não um botão.
  const healthy = () => {
    const state = quench()
    return state && !state.missing && !state.outdated ? state : undefined
  }

  const loadTouched = () => {
    const dir = directory()
    if (!dir) return
    void rpc().touched({ sessionID: props.session.id, directory: dir }).then((value) => {
      const list = value as Touch[]
      setTouched(list)
      // A spec mais forte da sessão já abre com o documento à vista.
      if (!picked() && list.length > 0) pick(list[0].id)
    }).catch((cause) => setError(String(cause)))
  }

  const loadQuenching = async () => {
    const dir = directory()
    if (!dir) return
    try {
      const value = await rpc().quenching({ directory: dir })
      setQuench(value as Quenching)
    } catch (cause) {
      setError(String(cause))
    }
  }

  // A sessão roteada muda: o ledger é dela, não do plugin.
  createEffect(() => {
    props.session.id
    props.session.directory
    setQuench(undefined)
    loadTouched()
    void loadQuenching()
  })

  createEffect(() => {
    const dir = props.session.directory
    const text = query()
    if (!dir) return
    const timer = setTimeout(() => {
      void rpc().search({ directory: dir, query: text, limit: 40 }).then((value) => setRows(value as Row[])).catch((cause) => setError(String(cause)))
    }, 150)
    onCleanup(() => clearTimeout(timer))
  })

  onCleanup(rpc().events.on("changed", (event) => {
    if ((event.data as { sessionID?: string }).sessionID === props.session.id) loadTouched()
  }))

  const pick = (id: number) => {
    const dir = directory()
    if (!dir) return
    setPicked(id)
    setDetail(undefined)
    setTab(0)
    void rpc().detail({ directory: dir, id }).then((value) => setDetail(value as Detail)).catch((cause) => setError(String(cause)))
  }

  const attach = async (id: number, taskID?: string) => {
    const dir = directory()
    if (!dir) return
    const composer = props.screen.composer
    try {
      if (taskID) {
        const [info, spec] = await Promise.all([
          rpc().task({ directory: dir, id, task: taskID }),
          rpc().detail({ directory: dir, id }),
        ]) as [TaskInfo, Detail]
        composer.attach({
          type: "note",
          origin: "quenching-vitrine",
          commentID: `spec-${id}-${taskID}`,
          label: `${id} · ${taskID}`,
          title: spec.title,
          subject: spec.title,
          subtitle: `${spec.stage} · ${info.verify ? `verify: ${info.verify}` : "sem verify"}`,
          icon: "checklist",
          comment: `spec ${id} task ${taskID} — ${info.text}\nfiles: ${info.files || "-"}\nverify: ${info.verify || "-"}`,
        })
      } else {
        const spec = await rpc().detail({ directory: dir, id }) as Detail
        const next = spec.tasks.find((item) => item.state !== "x" && !item.blocked)
        composer.attach({
          type: "note",
          origin: "quenching-vitrine",
          commentID: `spec-${id}`,
          label: `${id}`,
          title: spec.title,
          subject: spec.title,
          subtitle: `${spec.stage} · ${spec.checked}/${spec.total}${next ? ` · próxima ${next.id}` : ""}`,
          icon: "checklist",
          comment: `spec ${id} — ${spec.title}\nstage: ${spec.stage} · tasks: ${spec.checked}/${spec.total}${spec.blocked ? ` · blocked: ${spec.blocked}` : ""}\n${next ? `next: ${next.id} ${next.text}` : ""}`,
        })
      }
      composer.focus()
    } catch (cause) {
      setError(String(cause))
    }
  }

  const openBoard = async () => {
    const dir = directory()
    if (!dir) return
    setBusy(true)
    try {
      const found = await rpc().board({ directory: dir }) as { url: string }
      if (found.url) ctx.system.openExternal(found.url)
      else setError("o portal não publicou uma URL")
    } catch (cause) {
      setError(String(cause))
    } finally {
      setBusy(false)
    }
  }

  const upgrade = async () => {
    const state = quench()
    const dir = directory()
    if (!state || !dir || !state.available) return
    const verb = state.missing ? "Instalar" : "Atualizar"
    const question = state.missing
      ? `Instalar quenching ${state.available}?`
      : `Atualizar quenching ${state.version} → ${state.available}?`
    const description = state.missing
      ? `O cq deploy instala a superfície OpenCode em ${state.root} (.agents/ e .opencode/agents/). As specs não são alteradas.`
      : `O cq deploy reescreve a superfície já instalada em ${state.root}, preservando os harnesses do manifesto. As specs não são alteradas.`
    const ok = await ctx.dialogs.confirm({
      title: question,
      description,
      confirm: verb,
      cancel: "Cancelar",
    })
    if (!ok) return
    setUpgrading(true)
    setError("")
    try {
      const result = await rpc().upgrade({ directory: dir }) as QuenchingUpdate
      if (!result.ok) {
        const detail = result.output.slice(-500) || "cq deploy recusou o pedido"
        setError(detail)
        ctx.toast.show({
          title: `Falha ao ${verb.toLowerCase()} o quenching`,
          description: detail,
          variant: "error",
          duration: 10_000,
        })
        return
      }
      const next = result.version || result.available
      ctx.toast.show({
        title: state.missing ? `quenching ${next} instalado` : `quenching ${next}`,
        description: state.missing ? state.root : `${state.version} → ${next}`,
        variant: "success",
      })
      await loadQuenching()
      loadTouched()
      const id = picked()
      if (id) {
        setDetail(undefined)
        void rpc().detail({ directory: dir, id }).then((value) => setDetail(value as Detail)).catch((cause) => setError(String(cause)))
      }
    } catch (cause) {
      setError(String(cause))
      ctx.toast.show({ title: `Falha ao ${verb.toLowerCase()} o quenching`, description: String(cause), variant: "error" })
    } finally {
      setUpgrading(false)
    }
  }

  return (
    <div class="qs">
      <div class="qs-head">
        <input
          class="qs-input"
          placeholder="buscar id, título, tag…"
          value={query()}
          onInput={(event) => setQuery(event.currentTarget.value)}
        />
        <Show when={stale()} keyed>
          {(state) => (
            <span class="qs-upgrade" title={quenchTitle(state)}>
              <ctx.ui.Button
                size="small"
                busy={upgrading()}
                disabled={!state.available}
                onClick={() => void upgrade()}
              >
                {quenchLabel(state)}
              </ctx.ui.Button>
            </span>
          )}
        </Show>
        <Show when={healthy()} keyed>
          {(state) => (
            <span class="qs-quench" classList={{ warn: !state.available }} title={quenchTitle(state)}>
              <span class="qs-health-dot" />
              {state.available ? `OK ${state.version}` : "sem cq"}
            </span>
          )}
        </Show>
        <ctx.ui.Button size="small" busy={busy()} onClick={() => void openBoard()}>Board</ctx.ui.Button>
      </div>
      <Show when={error()}><div class="qs-error">{error()}</div></Show>
      <Show when={!searching()}>
        <div class="qs-label">Nesta sessão</div>
        <div class="qs-list">
          <For each={touched()}>{(row) => (
            <button class="qs-row" classList={{ picked: picked() === row.id }} onClick={() => pick(row.id)}>
              <span class="qs-id"><span class={`qs-dot ${row.kind}`} />{row.id}</span>
              <span class="qs-title">{row.title}</span>
              <span class="qs-meta">
                <Show when={row.workItemType === "epic"}><span class="qs-chip">épico</span> </Show>
                {EVIDENCE[row.kind] ?? row.kind} · {STAGE_LABEL[row.stage] ?? row.stage} · {row.checked}/{row.total}
              </span>
            </button>
          )}</For>
          <Show when={touched().length === 0}>
            <div class="qs-mute" style={{ padding: "8px" }}>
              nenhuma spec ainda — ela entra quando a conversa cita um id ou roda um comando <code>cq specs</code>
            </div>
          </Show>
        </div>
      </Show>
      <Show when={searching()}>
        <div class="qs-label">Busca</div>
        <div class="qs-list">
          <For each={rows()}>{(row) => (
            <button class="qs-row" classList={{ picked: picked() === row.id }} onClick={() => pick(row.id)}>
              <span class="qs-id">{row.id}</span>
              <span class="qs-title">{row.title}</span>
              <span class="qs-meta">
                <Show when={row.workItemType === "epic"}><span class="qs-chip">épico</span> </Show>
                {STAGE_LABEL[row.stage] ?? row.stage} · {row.checked}/{row.total}
              </span>
            </button>
          )}</For>
          <Show when={rows().length === 0}><div class="qs-mute" style={{ padding: "8px" }}>nenhuma spec</div></Show>
        </div>
      </Show>
      <Show when={detail()} keyed>{(spec) => (
        <div class="qs-detail">
          <div class={`qs-detail-head qh-${spec.stage}`}>
            <div class="qs-head-main">
              <div class="qs-top">
                <span class="qs-spec-id">{spec.id}</span>
                <span class={`qs-stage ${spec.stage}`} title={`etapa: ${STAGE_LABEL[spec.stage] ?? spec.stage}`}>
                  {STAGE_LABEL[spec.stage] ?? spec.stage}
                </span>
                <Show when={spec.priority}>
                  <span class={`qs-pri ${spec.priority.toLowerCase()}`} title={spec.priorityHint}>{spec.priority}</span>
                </Show>
                <Show when={spec.complexity}>
                  <span class="qs-chip" title="complexidade">{spec.complexity}</span>
                </Show>
                <Show when={spec.date}>
                  <span class={`qs-age${ageFresh(spec.date)}`} title={spec.date}>{ageLabel(spec.date)}</span>
                </Show>
              </div>
              <div class="qs-detail-title">{spec.title}</div>
              <Show when={spec.subject}>
                <div class="qs-subject" title={spec.subject}>{spec.subject}</div>
              </Show>
              <Show when={spec.blocked > 0}>
                <div class="qs-why" title={spec.blockedReason}>
                  <span>⚠</span>
                  <span>{spec.blockedTask ? `${spec.blockedTask}: ` : ""}{spec.blockedReason || "sem motivo escrito"}</span>
                </div>
              </Show>
              <Show when={spec.blocked === 0 && spec.total > 0}>
                <div class="qs-signal">
                  <span class="qs-progress-num">{spec.checked}/{spec.total}</span>
                  <span class="qs-bar">
                    <i style={{ width: `${Math.round(100 * spec.checked / Math.max(1, spec.total))}%` }} />
                  </span>
                  <span class="qs-mute">tarefas</span>
                </div>
              </Show>
              <div class="qs-foot">
                <Show when={spec.assignee}>
                  <span class="qs-who" title={spec.assignee}>
                    <span class="qs-av" aria-hidden="true">{spec.assignee.slice(0, 2).toLowerCase()}</span>
                    {spec.assignee}
                  </span>
                </Show>
                <Show when={spec.run || spec.verifier}>
                  <span class={`qs-run ${runBad(spec) ? "bad" : "pass"}`} title="último passo do runner">
                    {runBad(spec) ? "⚠" : "✓"} run: {spec.run || "-"}{spec.verifier ? `, ${spec.verifier}` : ""}
                  </span>
                </Show>
                <Show when={spec.phase === "plans"}>
                  <span class={`qs-chip qs-ready ${spec.ready ? "ok" : "warn"}`} title={spec.missing ? `falta: ${spec.missing}` : "pronta"}>
                    {spec.ready ? "✓ pronta" : `falta: ${spec.missing || "-"}`}
                  </span>
                </Show>
                <Show when={spec.pr}>
                  <button class="qs-link" onClick={() => spec.prUrl && ctx.system.openExternal(spec.prUrl)} title={spec.prUrl || spec.pr}>
                    PR {spec.pr}
                  </button>
                </Show>
                <For each={spec.tags}>{(tag) => <span class="qs-chip qs-tag">#{tag}</span>}</For>
                <Show when={spec.work}>
                  <span class="qs-chip qs-branch" title={spec.work}>{spec.work}</span>
                </Show>
              </div>
            </div>
            <ctx.ui.Button size="small" onClick={() => void attach(spec.id)}>Anexar</ctx.ui.Button>
          </div>
          <div class="qs-tabs">
            <For each={spec.sections}>{(section, index) => (
              <button
                class="qs-tab"
                classList={{ active: tab() === index() }}
                onClick={() => setTab(index())}
              >
                {section.heading}
              </button>
            )}</For>
            <Show when={hasView(spec)}>
              <button
                class="qs-tab"
                classList={{ active: tab() === spec.sections.length }}
                title="quem esta spec espera, quem espera por ela e, num épico, as specs que ele compõe"
                onClick={() => setTab(spec.sections.length)}
              >
                Dependências
                <span class="qs-dep-count">
                  <Show when={spec.composition}>{(composition) => (
                    <span title="specs deste épico">{composition().items.length}</span>
                  )}</Show>
                  <Show when={spec.deps.up.length}><span>↑{spec.deps.up.length}</span></Show>
                  <Show when={spec.deps.down.length}><span>↓{spec.deps.down.length}</span></Show>
                </span>
              </button>
            </Show>
          </div>
          <div class="qs-section">
            <Show
              when={spec.sections[tab()]}
              keyed
              fallback={<Show when={hasView(spec)}><DependencyView spec={spec} onPick={pick} /></Show>}
            >
              {(section) => (
                <>
                  <Show when={section.heading === "Tasks"}>
                    <div class="qs-task-list">
                      <For each={spec.tasks}>{(item) => (
                        <button
                          class="qs-task"
                          classList={{ done: item.state === "x", blocked: item.blocked }}
                          title={item.text}
                          onClick={() => void attach(spec.id, item.id)}
                        >
                          <span class="qs-state">{item.state === "x" ? "✓" : item.blocked ? "!" : "·"}</span>
                          <span class="qs-task-text">{item.text}</span>
                        </button>
                      )}</For>
                    </div>
                  </Show>
                  <ctx.ui.Markdown text={section.body || "_sem conteúdo_"} class="qs-md" />
                </>
              )}
            </Show>
          </div>
        </div>
      )}</Show>
    </div>
  )
}

export default Plugin.define({
  setup(ctx) {
    const openSpecs = () => {
      const session = ctx.sessions.current()
      if (session) ctx.layout.open(`${ctx.id}:specs`, session)
      else ctx.toast.show({ title: "Specs", description: "Abra uma sessão para ver as specs." })
    }

    ctx.add(Style, css)

    ctx.add(Panel, {
      id: "specs",
      region: "side",
      wide: true,
      list: (input) => (input.open.includes("specs") ? [specsTab] : []),
      render: (props) => <SpecsPanel {...props} />,
    })

    ctx.add(MenuItem, { id: "specs", menu: "session.panel", title: "Specs", icon: "checklist", run: openSpecs })
    ctx.add(Command, () => ({
      id: "specs",
      title: "Specs: abrir navegador",
      description: "Buscar qualquer spec e ver as que esta sessão tocou",
      keywords: "spec specs buscar board quenching",
      slash: { name: "specs" },
      run: openSpecs,
    }))
  },
})
