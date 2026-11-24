/**
 * A origem do deploy: a última release remota, a árvore do repositório-fonte e o desligamento.
 * Sem rede: a listagem de tags é texto fixo.
 *
 *   node --experimental-strip-types integrations/opencode-vitrine/bench/remote.check.mjs
 */
import { mkdirSync, mkdtempSync, writeFileSync } from "node:fs"
import { tmpdir } from "node:os"
import { join } from "node:path"
import { latestTag, remoteEnabled, remoteLaunch, remoteRepo, sourceCq, toolCq } from "../src/cq.ts"

const ok = (condition, message) => {
  if (!condition) {
    console.error(`FALHOU: ${message}`)
    process.exit(1)
  }
}

const listing = [
  "a\trefs/tags/7.9.0",
  "b\trefs/tags/7.16.0",
  "c\trefs/tags/7.10.3",
  "d\trefs/tags/8.0.0-rc1",
  "e\trefs/tags/v9.0.0",
  "f\trefs/tags/6.99.99",
].join("\n")
ok(latestTag(listing) === "7.16.0", "a maior tag X.Y.Z vence pela ordem numérica, sem pré-release nem prefixo")
ok(latestTag("") === "", "sem tags não há versão")

delete process.env.QUENCHING_REPO
const launch = remoteLaunch("7.16.0")
ok(launch.command === "uvx" && launch.source === "remote" && launch.tag === "7.16.0", "o lançamento remoto é o uvx preso à tag")
ok(launch.prefix.join(" ") === "--from git+https://github.com/holetz/quenching@7.16.0#subdirectory=quenching cq", "o uvx aponta para o subdiretório quenching da tag")
process.env.QUENCHING_REPO = "https://example.invalid/fork"
ok(remoteRepo() === "https://example.invalid/fork", "QUENCHING_REPO troca o repositório")
delete process.env.QUENCHING_REPO

for (const value of ["0", "off", "FALSE", "no"]) {
  process.env.QUENCHING_REMOTE = value
  ok(!remoteEnabled(), `QUENCHING_REMOTE=${value} desliga o remoto`)
}
delete process.env.QUENCHING_REMOTE
ok(remoteEnabled(), "o remoto é o padrão")

// O repositório-fonte faz o deploy da própria árvore, antes de qualquer remoto.
const source = mkdtempSync(join(tmpdir(), "vitrine-source-"))
mkdirSync(join(source, "quenching/assets/bin"), { recursive: true })
mkdirSync(join(source, "quenching/skills"), { recursive: true })
writeFileSync(join(source, "quenching/assets/bin/cq"), "#!/usr/bin/env python3\n")
ok(sourceCq(source) === join(source, "quenching/assets/bin/cq"), "a árvore do quenching é reconhecida como fonte")
ok(sourceCq(tmpdir()) === undefined, "um projeto comum não é a fonte")
delete process.env.QUENCHING_CQ
const chosen = await toolCq(source)
ok(chosen.source === "source" && chosen.file === join(source, "quenching/assets/bin/cq"), "no repositório-fonte o deploy usa a própria árvore, nunca a release")

// Desligado, o deploy de um projeto comum volta ao checkout do plugin ou ao PATH.
process.env.QUENCHING_REMOTE = "0"
const local = await toolCq(mkdtempSync(join(tmpdir(), "vitrine-target-")))
ok(local.source === "plugin" || local.source === "path", "com o remoto desligado a origem é local")

console.log("ok: origem do deploy (release remota, fonte, desligamento)")
