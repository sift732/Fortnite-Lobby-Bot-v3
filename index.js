"use strict"

const process = require("process")
const colors = require("./modules/colors")
const os = require("os")

let fnbr
let discord
let fnbrVersion

try {
    fnbr = require("fnbr")
    discord = require("discord.js")
    fnbrVersion = require("fnbr/package.json").version
} catch (e) {
    console.error(colors.red(e.stack))
    console.error(colors.red(`Node.js ${process.version}\n`))
    console.error(colors.red(
        "サードパーティーライブラリの読み込みに失敗しました。npm install を実行してください。\n" +
        "Failed to load third party library. Please run npm install.\n"
    ))
    console.error(colors.yellow(
        "問題が解決しない場合は以下までお問い合わせください\n" +
        "Discord: qwxia.\n" +
        "Support Server: https://discord.gg/DmG3P3Pwcg"
    ))
    process.exit(1)
}

let modules
try {
    modules = require("./modules")
} catch (e) {
    console.error(colors.red(e.stack))
    console.error(colors.red(`Node.js ${process.version}\n`))
    console.error(colors.red(
        "モジュールの読み込みに失敗しました。\n" +
        "Failed to load modules.\n"
    ))
    console.error(colors.yellow(
        "問題が解決しない場合は以下までお問い合わせください\n" +
        "Discord: qwxia.\n" +
        "Support Server: https://discord.gg/DmG3P3Pwcg"
    ))
    process.exit(1)
}

let mode
if (process.env.PROJECT_DOMAIN && process.cwd().startsWith("/app") && process.platform === "linux") {
    mode = "Glitch"
} else if (process.env.REPLIT_DB_URL && process.cwd().startsWith("/home/runner") && process.platform === "linux") {
    mode = "Repl.it"
} else {
    mode = "PC"

    const arch = os.arch()
    console.log(colors.cyan(`Architecture: ${arch}`))
    if (arch === "ia32") {
        console.error(colors.red("32bit環境では実行できません"))
        process.exit(1)
    }
}

console.log(colors.green(
    `V${modules.version}\n` +
    `Device ${mode}\n` +
    `Node.js ${process.version}\n` +
    `fnbr ${fnbrVersion}\n` +
    `discord.js ${discord.version}\n`
))

async function main() {
    const bots = [
        new modules.Bot(mode)
    ]
    for (const bot of bots) {
        await bot.setup()
    }
    await modules.Bot.startAllBots(bots)
}

main().catch(err => {
    console.error(colors.red(err.stack))
    console.error(colors.yellow(
        "問題が解決しない場合は以下までお問い合わせください\n" +
        "Discord: qwxia.\n" +
        "Support Server: https://discord.gg/DmG3P3Pwcg"
    ))
    process.exit(1)
})